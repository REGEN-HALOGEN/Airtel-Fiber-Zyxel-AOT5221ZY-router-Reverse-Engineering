# Work file — Blockers 3, 5, 6, 7 (STATIC ONLY)

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, RTL9607C, AArch64) — LAN4 Ethernet WAN + PPPoE via external Syrotech ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Safety boundary:** STATIC ANALYSIS ONLY. No router/runtime access. No PPPoE credentials reproduced (presence-only, `[REDACTED]`).
- **Confidence legend:** CONFIRMED STATIC = decoded from binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = prior runtime logs/reports · STRONGLY INFERRED = cross-function reconstruction, one unobserved link · HYPOTHESIS · UNKNOWN · DISPROVEN.
- **Tools:** Python venv `/tmp/revenv/bin/python` (Capstone 5 + pyelftools + LIEF); fresh disassembly this session of: libcccbe.so, libbemodules.so, libwebutil.so, rootfs libCmd.so, linkdetection (full `linkdetect_switch_WanMode` + main gate), broadband.cgi (RESTART branch + PLT xref scan). Prior reports read first: MASTER_FINDINGS, WAN_ACTIVATION_CALL_GRAPH, BOOT_INITIALIZATION_ANALYSIS, IMPLEMENTATION_PLAN, ROLLBACK_PLAN, OPEN_QUESTIONS, PPP_PARAMETER_VALIDATION (+ RDM_OBJECT_CREATION_ANALYSIS, ETHERNET_PPPOE_LIFECYCLE for cross-checks).
- **Corrections to prior reports produced by this pass** (details inline): (a) OPEN_QUESTIONS **U14 is now RESOLVED** and FAILED_EXPERIMENTS **C-11 is settled** — the OID operands of the link-type function are the GPON/Ethernet *interface-config* objects, and its return value is a **media link type**, not PPP-vs-IP; ETHERNET_PPPOE_LIFECYCLE step 6's "return 1 = PPP" is **DISPROVEN**. (b) MASTER **ETH-3 upgraded**: reboot requirement for the hardware remap is now CONFIRMED STATIC (complete PLT caller enumeration, §7.2). (c) ROLLBACK_PLAN step 4 (WanAutoDetect rollback = 1) **conflicts** with both preserved rollback scripts and with linkdetection's own GPON switch, which leave it **0** — flagged in §5.4. (d) `ether-rollback.ccc` has **no SAVE** — flagged in §5.5.

---

# Blocker 3 — Coexistence: `.3.WANPPPConnection.1` alongside intact `.1` GPON PPP

## 3.1 The two named functions — where they live

Two distinct symbols exist; they are **near-identical clones**, not the same function (CONFIRMED STATIC, dynsym via pyelftools):

| Symbol | Defining library | Address / size | Importers (UND) |
|---|---|---|---|
| `libcccBeWan_getWANDeviceObjectRequestedLinkType` | `DUMPFILES/libcccbe.so` (== rootfs `lib/MSTC/libcccbe.so`) | **0x34334, 244 B** | libbemodules.so, libbeEvents.so, rootfs libbestatus.so |
| `getWANDeviceObjectRequestedLinkType` | `DUMPFILES/libwebutil.so` | **0xbfc0, 0x12c B** | broadband.cgi, wanRemoteNode_ETH_Edit.cgi |
| `getWANDeviceObjectRequestedLinkType` (3rd clone) | rootfs `lib/MSTC/libCmd.so` (sha in MASTER table) | **0x97950, 0xf0 B** | — (CLI/debug library) |

Call sites (CONFIRMED STATIC): in libbemodules the libcccbe variant has exactly **10 BL call sites** in the whole `.text` (full PLT-xref scan this session): 0x4ce60 (L4ObjectChanged region), 0x4f4dc (L3ConfigInit), 0x4fed0 (L2ObjectChanged), 0x5312c, 0x535dc, 0x679b0 (`checkWANDeviceObjectRequestedLinkIsUp`), 0x6c0d8 (`beWanDoLayer3InterfaceAction`), 0x6d82c (`beWanDoLayer2InterfaceAction` region), 0x6db3c, 0x6e17c (`startAllWanConnection`/`stopAllWanConnection` region). In broadband.cgi the libwebutil variant has exactly **one** BL call site in the whole `.text`, at **0x408678 — outside `cgiMain`** (0x403390–0x406924), i.e. in a page-render/helper function; the mutation path (`cgiMain`) never calls it.

## 3.2 Logic — identical in all three clones (CONFIRMED STATIC, fresh disassembly)

Signature: `(rdmHandle, IA)`. Only the **top byte of the IA** is used (`IA >> 0x38 & 0xff` = the WANDevice index, "1"), formatted with `"%d"` via `rdmConstructIAValue`. **The WANConnectionDevice index and the connection index are never read.** Pseudocode (libcccbe @0x34334; PLT: `rdmConstructIAValue` @stub 0x19890, `cccRdmGetObjectByOID` @stub 0x1a140):

```
if (rdm == NULL) return 2;                       // + syslog
obj = cccRdmGetObjectByOID(rdm, 0xc7, IA_wandevice, 1);   // X_5067F0_GponInterafceConfig
if (obj && obj[0] != 0) return 1;                          // Gpon Enable byte @ +0
obj = cccRdmGetObjectByOID(rdm, 0xca, IA_wandevice, 1);   // WANEthernetInterfaceConfig
if (!obj) return 2;
return obj[4] != 0 ? 0 : 2;                                // Eth Enable byte @ +4
   // libcccbe encodes this as cset(eq)+lsl#1; libwebutil/libCmd as branch — same semantics
```

Return-value meaning — **proven, not guessed** (CONFIRMED STATIC): `libcccBeWan_getActiveWANDevice` (libcccbe @0x34428) reads the WANStatus object (OID 0x4c), compares its CurrentLinkType string against `"XGPON"` (@0x4adf0) → expected value **1**, and `"Ethernet"` (@0x471c8) → expected value **0**, then iterates the WANDevice list (OID 0xc3) and returns the first WANDevice whose `…RequestedLinkType(...)` equals that value. `updateCurrentLinkType` (libbemodules @0x6ef0c) does the inverse write: global current-type dword ==1 → copies `"XGPON"` (@0xb4c60) into the OID-0x4c object, ==0 → copies `"Ethernet"` (@0xb42a0). Therefore:

- **0 = Ethernet requested, 1 = GPON requested, 2 = neither / unknown / error.** This is a **per-WANDevice media selection**, not a PPP-vs-IP decision.

OID naming — **U14 RESOLVED** (CONFIRMED STATIC): OID 0xc7 = `X_5067F0_GponInterafceConfig` (vendor typo verified three ways: librdm OIDTable per MASTER RDM-1; schema image string `X_5067F0_GponInterafceConfig` at file offset 0x35fc5 of `config_rdm_decompressed.bin`, whose parameter list is `Enable, IfName, BiasCurrent, …`; the literal PDM tag `<X_5067F0_GponInterafceConfig>` in `aot-current-pdm-config.xml`). OID 0xca = `WANEthernetInterfaceConfig` (schema image @0x3696c; params `ShapingBurstSize, Enable, X_5067F0_PortID, MaxBitRate, DuplexMode, X_5067F0_IfName, MACAddress, Status, …`). Struct offsets cross-confirmed at three independent call sites: **Gpon Enable @ +0, Gpon IfName @ +2; Eth Enable @ +4, Eth IfName @ +0x8a** (Boot @0x50e7c/0x50ea8 and failure-log arguments @0x50f28/0x50ff4; L3ConfigInit GPON branch copies the L2 name from Gpon obj+2 @0x4f6ec, ETHER branch from Eth obj+0x8a @0x4f730; the link-type clones above). The prior "PPP/IP count objects" operand naming is **DISPROVEN**.

**Consequence for the factory state** (STRONGLY INFERRED): the PDM configures **no** `Enable` under GponInterafceConfig (only `IfName=nas0`), yet the factory unit requests GPON — so the Gpon Enable schema default must be **1** (if it were 0, the function would fall through to Eth Enable=1 and request Ethernet). The exact default byte in the template image was not isolated this session; the inference rests on the function's priority order + factory behaviour.

## 3.3 GPON-vs-Ethernet precedence at WANDevice level (CONFIRMED STATIC)

GPON is tested **first and wins unconditionally**: if Gpon Enable ≠ 0 the result is 1 (GPON) **regardless of Eth Enable**. Ethernet (0) is reachable only when Gpon Enable == 0 (or the Gpon object is missing) **and** Eth Enable ≠ 0. Both vendor switch paths honour this by construction: broadband.cgi RESTART and both linkdetection branches always write the two Enables as a complementary pair (GPON mode: Gpon=1/Eth=0; ETHER mode: Gpon=0/Eth=1 — §6.2, §6.4). **There is no representation for ".1 requests GPON while .3 requests Ethernet"** — requested link type is a single scalar per WANDevice. Any Ethernet deployment that leaves Gpon Enable effectively 1 leaves the whole L3 link-type machinery (L3ConfigInit's mode branches, `checkWANDeviceObjectRequestedLinkIsUp`, `updateDefaultRouteByLinkType`) believing the requested media is GPON, even if `WANMode="ETHER"` correctly drives the Boot hardware gate (§7). WANMode and the Enable pair are ** separate, both load-bearing** inputs; they must be set consistently.

## 3.4 PPP-vs-IP precedence *within* one connection device (CONFIRMED STATIC at dispatcher level)

There is **no PPP-vs-IP arbitration function** analogous to §3.2. The L3 layer is dispatched **per connection object**:

- `OID_…_WANDevice_i_ConfigLoaderFunc_L3ConfigLoad` (libbemodules @0x4fcb0, fresh disassembly): reads the event object's OID from the node struct — OID **0xcd** (WANIPConnection instance) → `L3ConfigInit(…, isPPP=0)` (@0x4fd98); OID **0xe3** (WANPPPConnection instance) → `L3ConfigInit(…, isPPP=1)` (@0x4fe0c); OID 0xd7 (the WANConnectionDevice itself) → forwards to `L3ObjectChanged` only if the child OID is 0xcd/0xe3 (@0x4fe94); OID 0xed → ignored. Each invocation carries that object's **full IA** (WANDevice, ConnDev, instance).
- `L3ConfigInit` (@0x4f440) fetches the triggering object (0xcd first if isPPP=0 @0x4f490, 0xe3 first if isPPP=1 @0x4f608; missing object → distinct log lines `"No WANIPConnection is found. connEntryIA=%llx"` @0xb3e00 / `"No WANPPPConnection is found…"` @0xb3e38), then a `prepareObjs()` helper (@0x4f4a4) also obtains the sibling object pointer and the interface-config objects — both pointers are passed to `beWanDoLayer3InterfaceAction` (@0x4f51c) together with isPPP, the full IA, the L2 name selected by requested link type, and the link type itself. The tail of L3ConfigInit then acts **only on the triggering type**: IP → `createWANIPConnectionCfgFile` paths (@0x4f79c/0x4fc44); PPP → if PPP `Enable` byte [obj+0x2c] is 0, release-and-return (@0x4fb34), else `createWANPPPConnectionCfgFile` (@0x4f9c4) and stamps the ConnDev index byte into [obj+0x73b] (@0x4fa14).
- RDM creation layer: `cccRdmAddIndexChildObject` contains **no sibling-type check, no parent-instance whitelist, no link-type check** (RDM_OBJECT_CREATION_ANALYSIS, CONFIRMED STATIC there). The schema places no constraint either (PPP class 0xf1 flags 0x2, max 8, child of any WANConnectionDevice.i).

So within ConnDev.3, a WANPPPConnection and the existing WANIPConnection are **independent objects with independent Enable flags and independent L3 invocations**. Nothing in the dispatcher, the RDM layer, or L3ConfigInit suppresses one because the other exists. What *does* arbitrate between them operationally is external and singular: `Layer3Forwarding.DefaultConnectionService` (which connection the default route follows) and the Event-206 / `updateDefaultRouteByLinkType` machinery (§3.6). If both children of .3 were Enable=1, both would be processed by the L3 walk; the resulting session/interface contention is **UNKNOWN** (no static oracle; the vendor never ships that state — §3.7).

## 3.5 `WANPPPConnectionNumberOfEntries` / `WANIPConnectionNumberOfEntries` semantics (CONFIRMED STATIC + STRONGLY INFERRED)

- Both are **per-WANConnectionDevice-instance computed count parameters** in the WANConnectionDevice template (schema image: `WANIPConnectionNumberOfEntries` at file offset 0x36f51, `WANPPPConnectionNumberOfEntries` at 0x36f95 of `config_rdm_decompressed.bin`, adjacent entries in the ConnDev block). They are **not** configured in the PDM XML (zero configured occurrences under any WANConnectionDevice — they are runtime-maintained, like all `NumberOfEntries` in this data model).
- They count the committed child instances **of that one ConnDev only**: factory state is .1 → PPP 1 / IP 0; .2 → 0/1; .3 → **0/1**; .4 → 0/1; .5 → 0/1 (derived from the PDM child lists, CONFIRMED STATIC as config state).
- Maintenance: a successful ADD's tail calls `cccRdmCheckIndexChildParents` (librdm @0x136e0) which updates the parent (RDM report, CONFIRMED STATIC); an ADD under parent IA {1,3} therefore touches **only .3's counts** — .1's counts are structurally unreachable from that call. DELETE decrementing the count is STRONGLY INFERRED (prior SAF-004 analysis, per ROLLBACK_PLAN). A rolled-back (NACKed) transaction leaves the count unchanged — exactly the observed FE-2 symptom (count stayed 0).
- Rollback cleanliness consequence (from ROLLBACK_PLAN, endorsed): `Enable=0` leaves .3 PPP count at 1; only native DELETE returns it to the factory value 0.

## 3.6 Does creating/enabling `.3` PPP trigger callbacks affecting `.1`?

**Direct callbacks: NO** (CONFIRMED STATIC at dispatcher level). CMSG commit dispatch is per changed object: L3ConfigLoad/L3ObjectChanged act on the OID+IA in the event; an ADD/SET transaction naming only `.3.WANPPPConnection…` enqueues no `.1` object event, and no handler enumerated in §3.1 iterates sibling ConnDevs to rewrite them. `libcccBeWan_getActiveWANDevice` *reads* across WANDevices but writes nothing. Neither broadband.cgi's conversion nor linkdetection's ETHER transaction deletes or SETs any parameter of `.1.WANPPPConnection.1` **except its `Enable` flag** (next bullet).

**Indirect/global couplings — three, all CONFIRMED STATIC as mechanisms:**

1. **Vendor switch transactions deliberately flip `.1`'s Enable.** linkdetection ETHER Tx B sets `.1.WANPPPConnection.1.Enable = 0` (and `.2` IP Enable = 0) — §6.2. broadband.cgi's *conversion* path does **not** touch .1 at all (it deletes/recreates only under .3); the broadband *RESTART* path touches only the interface-config Enables + WANMode. Whether `.1` PPP is disabled during Ethernet deployment is therefore a **path choice**, not a firmware inevitability.
2. **Default route is a singleton.** `Layer3Forwarding.DefaultConnectionService` (+ IPv6 twin) names exactly one connection. Pointing it at `.3.WANPPPConnection.1` (required for Ethernet Internet) by construction de-defaults `.1`. Additionally, `updateDefaultRouteByLinkType` (libbemodules @0x6f2d8, fresh string scan) reads `Layer3Forwarding`, `X_5067F0_IPv6Layer3Forwarding` **and** the `MultiLinkTypeDefaultConnectionService` pointer and rewrites the active DCS from the per-mode stored keys on link-type changes (log strings `"change IPv4 default route to GPON link type"` @0xbe988 / `"…to Ethernet link type"` @0xbe9c0, IPv6 twins). If `DefaultConnectionService_ETHER` still holds `.3.WANIPConnection.1` (factory value), any later link-type-flip event rewrites DCS back to the **IP** object — the deployment must set DCS *after* the mode settles and be aware the per-mode keys, not the live DCS, are what survives a flip.
3. **Shared L2 / shared link-type state.** Both profiles hang off WANDevice.1 / `nas0`. The L3 *change* gate, `checkWANDeviceObjectRequestedLinkIsUp` (libbemodules @0x67964, fresh disassembly), is per-WANDevice: it requires the global WANStatus flag byte ==1, the global current-link-type dword (@GOT 0xe6cf0 +4) == the expected type, **and** `RequestedLinkType(rdm, IA) == expected`. It never inspects which ConnDev the changed object belongs to. In `L3ObjectChanged` (@0x4ddc4) it is called at @0x4df00 (and @0x4e6a4) with the changed object's IA; on failure the handler exits (@0x4ee4c) without acting. Consequence: in a correctly switched ETHER state, a change to **.1's** PPP object passes this gate just as a change to .3's does — the gate cannot protect .1 from being (re)started in Ethernet mode if its Enable is left 1, nor protect .3 in GPON mode. The only thing keeping the inactive profile dormant in vendor flows is its **Enable=0**.

## 3.7 Separate profile or conversion — what the firmware "expects"

- **Vendor Web expectation = conversion** (CONFIRMED STATIC): broadband.cgi has no ADD path at all; its only WANPPPConnection creation deletes the existing WANIPConnection under the *same* ConnDev and creates the PPP child in its place (MASTER CGI-1). linkdetection likewise only ever creates the **IP** child under .3 (ETHER Tx A, §6.2).
- **Factory data model = one connection child per ConnDev** (CONFIRMED STATIC): all five factory ConnDevs (.1 PPP, .2 IP, .3 IP, .4 IP, .5 IP) carry exactly one connection child each; no factory example of PPP+IP siblings exists.
- **Code tolerance = coexistence permitted** (CONFIRMED STATIC): schema, RDM creation, and L3 dispatch all accept a PPP child added *alongside* the IP child under .3 (§3.4, §3.5). The minimal-ccctest ADD path (IMPLEMENTATION_PLAN Path B) is therefore not fighting any structural rule; its only known enemy is the unexplained commit-phase NACK (Blocker 1/2 scope, not re-litigated here).

**⚠ Conversion destroys the .3 IP profile; ADD preserves it.** This matters for rollback symmetry (§5): after broadband conversion, rollback must re-convert (PPP→IP) or DELETE the PPP child and re-create the IP profile; after a pure ADD, rollback is a single DELETE and the factory IP profile was never touched.

## 3.8 Coexistence verdict (Blocker 3)

> **`.3.WANPPPConnection.1` CAN exist while `.1.WANPPPConnection.1` stays fully intact and untouched — CONFIRMED STATIC at the schema, RDM, and L3-dispatch layers.** No creation gate, count, or callback couples the two ConnDevs; ADD under .3 changes only .3's counts. **Caveats:** (1) coexistence of the *objects* is proven; simultaneous *Enable=1 on both PPP profiles* is a state the vendor never ships — both would be processed by the L3 walk over the shared `nas0` L2, and their runtime interaction is **UNKNOWN**, which is why both vendor switch paths set the inactive profile's Enable=0. The safe deployment shape is: .3 PPP present + enabled, .1 PPP present + **disabled-but-never-deleted**. (2) The default route can name only one of them (DCS singleton + per-mode keys, §3.6.2). (3) Requested link type is WANDevice-global with GPON priority (§3.3) — Gpon Enable must be cleared for the Ethernet state to be coherent. **The factory GPON profile must never be deleted** — evidence: no vendor path deletes it (switch paths only toggle its Enable); factory DCS (v4+v6), both `DefaultConnectionService_GPON` keys, `IPv6PDWanConnection.Interface`, and the `X_TELEFONICA_Firewall` DEFAULTWAN/DEFAULTWANv6 bindings all point at `.1.WANPPPConnection.1` / `ppp111` as *data* (§5.3), so deleting it would dangle five independent factory references and destroy the only GPON rollback target.

---

# Blocker 5 — GPON restoration matrix

## 5.1 Sources located in the repo (inventory)

| Source | Path | Nature | This pass |
|---|---|---|---|
| Factory PDM XML | `DUMPFILES/aot-current-pdm-config.xml` (583,313 B) | PDM export: schema template + `PARAMETER="configured"` values | Parsed in full (ET) |
| Factory PDM XML (copy) | `DUMPFILES/aot-current-pdm-backup.xml` | **Byte-identical** to the above (md5 `85b4f361…`, CONFIRMED STATIC) | diff = empty |
| ROM/default file | `DUMPFILES/aot-current-romfile` (LZMA) → `analysis/romfile_decoded.txt` | Decodes to **byte-identical XML** to the factory PDM (same md5) — i.e. the ROM default config and the "current" PDM export carry identical content; the unit was in factory state when exported, or the export *is* the ROM file | diff = empty |
| Live RDM dump | `DUMPFILES/config.rdm` == `DUMPFILES/runtime-config.rdm` (62 KB, sha `fb50191e…`) → `DUMPFILES/config_rdm_decompressed.bin` (3,145,728 B) | Decompressed image is the **schema/template+defaults image**: it contains the WANMode default `"GPON"` (file off. 0x22869/0x2288a) but **no configured ACS URL string at all** (zero hits for `tms.airtel`, `testacs`, `airtelbroadband` — CONFIRMED STATIC). Per-parameter *live* string values are **not** independently readable from it | strings/offsets extracted |
| Phase-0 live baseline | `DUMPFILES/ether-backup.lz` (23,485 B) → `analysis/ether_backup_decoded.txt` (583,551 B); timestamp file `DUMPFILES/ether-backup.timestamp` = `202406031227.01` | Pre-Ethernet-experiment live backup (LZMA PDM XML). **The only live-baseline config in the repo** | full diff vs factory (§5.4) |
| (empty) | `DUMPFILES/config-before-ether.lz` | **0 bytes** — contains no baseline; do not cite as evidence | — |
| Rollback script 1 | `DUMPFILES/ether-rollback.ccc` (1,222 B) | ccctest script, plain `SET` (BE), **no SAVE** (§5.5) | read in full |
| Rollback script 2 | `DUMPFILES/rollback.ccc` (1,210 B) | ccctest script, `SET_NO_BE` + `SAVE; SEND;` (§5.5) | read in full |
| Firmware default RDM/PDM (on-device) | rootfs `etc/init.d/ccc_init.sh` symlinks `/var/rdm/config.rdm → /var/default-rdm/config.rdm`, `/var/pdm/config.rom → /var/pdm/config.xml`, `/var/pdm/config.default.xml → /var/default-pdm/config.xml` after `cp -rf /usr/var/* /var/` | The `/usr/var` payload itself is **not in the rootfs dump** (it lives on the piubi/apps volume); its PDM content is STRONGLY INFERRED to be the ROM file above | script read |

No other `*.xml`, `*rdm*`, `*default*`, `*baseline*`, `*rollback*`, `*.sh` config sources exist in the repo beyond these and the rootfs scripts in §7.3 (find across repo, CONFIRMED STATIC).

## 5.2 The matrix

Notation: path abbreviations — `WANDevice.1` = `InternetGatewayDevice.WANDevice.1`; `CD.n` = `WANConnectionDevice.n`; "absent" = parameter/object **not configured** in that source (schema default applies); Ethernet-target = IMPLEMENTATION_PLAN end state (vendor-path values in parentheses where they differ).

| # | Parameter (exact path) | Factory PDM / ROM | Phase-0 live baseline (`ether-backup`) | Ethernet target | Rollback value | Evidence |
|---|---|---|---|---|---|---|
| 1 | `X_5067F0_Ext.WANSwitch.WANMode` | **absent**; schema default `"GPON"` (image @0x22869) | absent (⇒ GPON) | `"ETHER"` | `"GPON"` (or un-configure → default) | Schema image dump §5.1; PDM ET parse: 0 `WANMode` elements. CONFIRMED STATIC |
| 2 | `X_5067F0_Ext.WANSwitch.WanAutoDetect` | `1` | `1` | `1` during deployment; `0` only after success (Plan Phase 5) | **`1` per factory — but see ⚠ §5.4(c)** | PDM; linkdetection §6.2. CONFIRMED STATIC |
| 3 | `WANDevice.1.WANEthernetInterfaceConfig.Enable` | `1` | **absent ⚠** | `1` | Baseline state = **absent** (restore the backup, or delete the configured value; writing factory `1` is *not* the baseline) | PDM vs ether-backup diff hunk 2. CONFIRMED STATIC |
| 4 | `WANDevice.1.WANEthernetInterfaceConfig.X_5067F0_IfName` | `nas0` | `nas0` | untouched | `nas0` | PDM. CONFIRMED |
| 5 | `WANDevice.1.X_5067F0_GponInterafceConfig.Enable` — **exact typo'd spelling `GponInterafceConfig` CONFIRMED** in PDM tag, schema image @0x35fc5, linkdetection SEL strings (@0x403a08), broadband OID 0xc7 | **absent** (only `IfName` configured); effective default = 1 (STRONGLY INFERRED, §3.2) | absent | `0` (both vendor switch paths write 0; a conversion-only path that leaves it untouched leaves requested-type = GPON — §3.3 hazard) | absent / effective 1 (scripts write explicit `1`) | PDM ET parse; §3.2, §6. CONFIRMED STATIC (absence) |
| 6 | `WANDevice.1.X_5067F0_GponInterafceConfig.IfName` | `nas0` | `nas0` | **untouched** | `nas0` | PDM. CONFIRMED |
| 7 | `WANDevice.1.WANCommonInterfaceConfig.WANAccessType` | **absent** — not a configured parameter anywhere in PDM; schema template lists it among status params with enum strings `Ethernet`/`Unconfigured` nearby (image @0x35921 region) | absent | n/a — runtime-derived status, **not a deployment knob** | n/a | PDM count 0; schema strings. Effective live value **UNKNOWN** |
| 8 | `WANDevice.1.WANCommonInterfaceConfig.EnabledForInternet` | `1` | `1` | untouched | `1` | PDM. CONFIRMED |
| 9 | `Layer3Forwarding.DefaultConnectionService` | `…CD.1.WANPPPConnection.1` | same | `…CD.3.WANPPPConnection.1` | `…CD.1.WANPPPConnection.1` | PDM. CONFIRMED |
| 10 | `Layer3Forwarding.X_5067F0_DefaultConnectionService.DefaultConnectionService_GPON` | `…CD.1.WANPPPConnection.1` | same | **untouched** | (already correct) | PDM. CONFIRMED |
| 11 | `…DefaultConnectionService_ETHER` (v4 key) | `…CD.3.WANIPConnection.1` | same | **untouched** ⚠ — while it holds the IP path, a link-type flip rewrites live DCS to the IP object (§3.6.2); deployment must re-assert row 9 after any flip | (already correct for GPON rollback) | PDM. CONFIRMED |
| 12 | `X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` — **the exact IPv6 default-forwarding pointer** (sibling keys `.MultiLinkTypeDefaultConnectionService.DefaultConnectionService_GPON` / `_ETHER` beneath it) | `…CD.1.WANPPPConnection.1`; `_GPON` key = .1 PPP; `_ETHER` key = .3 IP | same | `…CD.3.WANPPPConnection.1` (linkdetection would set the **IP** object — must be overwritten, Plan Phase 2) | `…CD.1.WANPPPConnection.1` | PDM. CONFIRMED |
| 13 | `LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.IPv6PDWanConnection.Interface` | `…CD.1.WANPPPConnection.1` | same | `…CD.3.WANPPPConnection.1` for IPv6 PD (linkdetection sets .3 **IP**; retargeting is U15-conditional) | `…CD.1.WANPPPConnection.1` | PDM. CONFIRMED |
| 14 | `LANDevice.1.…IPv6LANHostConfigManagement.NDPPD.Enabled` | **absent** (no `NDPPD` element in PDM at all) | absent | `1` (linkdetection ETHER value) | `0` (linkdetection GPON value) / absent | PDM count 0; §6.2 value map. CONFIRMED STATIC |
| 15 | `ManagementServer.URL` | `http://tms.airtelbroadband.in:8103` (**no trailing slash**) | **same** (§6.3) | side effect → testacs (§6); **restore production** | `http://tms.airtelbroadband.in:8103` | PDM + ether-backup + romfile, 1 occurrence each. CONFIRMED |
| 16 | `ManagementServer.X_5067F0_OverIPv6` | absent | absent | linkdetection ETHER sets `1` (side effect; deployment may leave) | `0` (linkdetection GPON value) / absent | §6.2. CONFIRMED STATIC |
| 17 | `ManagementServer` other params (`Username`, `Password`, `ConnectionRequestUsername/Password`, `PeriodicInformEnable=1`, `PeriodicInformInterval=86400`, `X_5067F0_CheckCertificateCN=0`) | present (values `[REDACTED]`) | identical | **untouched** — no vendor path writes them (§6.4) | (already correct) | PDM (attrs `EXTATTR=0x0800`). CONFIRMED |
| 18 | `WANDevice.1.CD.1.WANPPPConnection.1` (GPON PPP, whole object) | present: `Enable=1`, `Name=Internet`, `X_5067F0_InterfaceName=ppp111`, `X_5067F0_VLANID=100`, `X_5067F0_SERVICELIST=TR069`, `X_5067F0_RIPVersion=RIPv2`, `X_5067F0_IPv6Enabled=1`, `X_5067F0_DualStack=1`, `X_5067F0_DHCP6cForAddress=1`, `X_5067F0_IPv6PrefixDelegationEnabled=1`, `X_5067F0_IGMPEnabled=1`, `X_5067F0_ResponseICMP=1`, `X_5067F0_NAT.Loopback=1`, `NATEnabled` **absent**, `X_5067F0_Enable_VLANID` **absent**, Username/Password present `[REDACTED]` | identical | **object untouched; at most `Enable→0` on the vendor-switch path** (§3.6.1) | `Enable=1`, everything else as factory | PDM full subtree dump. CONFIRMED |
| 19 | `WANDevice.1.CD.2.WANIPConnection.1` (VoIP) | present: `Enable=1`, `Name=VoIP`, IfName `nas0_660`, `X_5067F0_VLANID=660`, `AddressingType=Static`, `ExternalIPAddress=10.1.1.1`, `SubnetMask=255.255.255.0`, `DefaultGateway=10.1.1.2`, `NATEnabled=0`, SERVICELIST `VOIP` | identical | **untouched by plan** ⚠ linkdetection ETHER sets its `Enable=0` (VoIP side effect of the vendor path) | `Enable=1` | PDM. CONFIRMED |
| 20 | `WANDevice.1.CD.3.WANIPConnection.1` (`Eth_Internet`) | present: `Enable=1`, IfName `nas0_notag`, `Name=Eth_Internet`, SERVICELIST `TR069`, RIP `N/A`, `X_5067F0_VLANID=0`, `X_5067F0_Enable_VLANID=0`, `X_5067F0_IGMPEnabled=0`, `X_5067F0_IPv6Enabled=1`, `X_5067F0_DualStack=1`, `ExternalIPAddress=` (empty), no Gateway/SubnetMask elements | present **but `Enable` absent ⚠**, and `DefaultGateway=0.0.0.0`, `SubnetMask=0.0.0.0`, `ExternalIPAddress=0.0.0.0` **added** (§5.4) | conversion path: **deleted, replaced by PPP**; ADD path: kept as-is | IP object present, PPP absent; `Enable` per baseline = absent ⚠ | PDM + diff. CONFIRMED STATIC |
| 21 | `WANDevice.1.CD.3.WANPPPConnection.1` | **absent** (CD.3 counts PPP 0 / IP 1) | absent | present: `Enable=1`, service `3jglobal`, MTU/MRU 1480, `AUTO_AUTH`, `NATEnabled=1`, VLAN off, `ConnectionType=IP_Routed` (ISP values per brief, CONFIRMED FROM EXISTING RUNTIME EVIDENCE) | **absent** (native DELETE; count back to 0) | PDM; PPP_PARAMETER_VALIDATION. CONFIRMED |
| 22 | `WANDevice.1.CD.4.WANIPConnection.1` (`Internet_IPoE`, nas0_100, VLAN 100) / `CD.5.WANIPConnection.1` (`Internet_Bridge`, `IP_Bridged`, VLAN 100, `NATEnabled=0`) | present; `Enable` **absent** in both | identical | **untouched** | (already correct) | PDM. CONFIRMED |
| 23 | Firewall state | `InternetGatewayDevice.Firewall.Enable=1`, `AdvancedLevel=Firewall.Level.1`, Level.1 `DefaultPolicy=Drop`; `X_TELEFONICA_Firewall` chains: DEFAULTLAN (br0, Permit), **DEFAULTWAN i2: `Interface=…CD.1.WANPPPConnection.1`, `X_5067F0_IfName=ppp111`, DefaultAction=Drop, Enable=1**, DEFAULTLANv6, **DEFAULTWANv6 i4: same binding, IPv6** | identical | **untouched by every vendor path** ⚠ — the Ethernet session (ppp131) is therefore *not* the object these factory chains bind; a deployment gap to note, **not** a rollback item | factory values (already correct — bindings point at .1/ppp111) | PDM subtree dump. CONFIRMED |
| 24 | NAT state | per-connection `NATEnabled`: CD.1 PPP **absent**, CD.2 IP `0`, CD.5 IP `0`; CD.1 PPP `X_5067F0_NAT.Loopback=1`; a per-connection NAT status mapping table references CD.1 PPP, CD.2 IP, CD.3 IP, CD.4 IP (no CD.3 PPP row exists in factory) | identical | CD.3 PPP `NATEnabled=1` (new object); runtime MASQUERADE is interface-name-driven (MASTER NET-1) | CD.3 PPP deleted ⇒ factory state; nothing else to restore | PDM grep/subtree. CONFIRMED |
| 25 | pppd / interface cleanup (no RDM parameter) | runtime artifacts only: `/etc/ppp/options_nas0_notag` (generated), `/var/wan-pid/<if>.pid`, smux L3 interface `nas0_notag` | — | generated for ppp131 at L3 init | Backend-automatic on disable/delete: `beWanDisableClient` (libbemodules @0x6722c, **fresh CONFIRMED STATIC**) reads `/var/wan-pid/%s.pid` and runs `kill -15 %d > /dev/null 2>&1 && sleep 2 && kill -9 %d > /dev/null 2>&1 &` via `cccBeDoSystem`, then removes the pidfile; smux `--if-delete` of nas0_notag on the L3 disable path is STRONGLY INFERRED (prior disasm). Options files are regenerated each L3 load — nothing to restore by hand. Verify `ps \| grep pppd` post-rollback instead of manual kills | §7.4. CONFIRMED/INFERRED as marked |

## 5.3 GPON values that must remain UNTOUCHED during Ethernet deployment (CONFIRMED STATIC — all are factory *data* references or the rollback target itself)

1. The **entire `CD.1.WANPPPConnection.1` object** (row 18) — credentials, VLAN 100, `ppp111`, IPv6/DualStack flags. At most its `Enable` may be toggled by the chosen path; never DELETE, never re-type.
2. `X_5067F0_GponInterafceConfig.IfName = nas0` (row 6).
3. Both `DefaultConnectionService_GPON` keys (v4 row 10, v6 row 12) — they *are* the GPON rollback route.
4. `CD.2` VoIP profile in full (row 19) — note linkdetection's ETHER switch **would** flip its Enable to 0; avoiding the linkdetection path (or re-asserting Enable=1) is required to honour this.
5. `CD.4` / `CD.5` profiles (row 22).
6. `X_TELEFONICA_Firewall` DEFAULTWAN / DEFAULTWANv6 bindings (`Interface=…CD.1.WANPPPConnection.1`, `IfName=ppp111`) and `Firewall.Enable/Level` (row 23).
7. All `ManagementServer` parameters except the URL side effect (row 17), and the production URL value itself as the restore target (row 15).
8. `X_5067F0_Bras.BrasList` + `Enable=1` (PDM, untouched by every path examined).

## 5.4 Every factory ≠ live-baseline difference (full diff: 8 lines, CONFIRMED STATIC)

`diff aot-current-pdm-config.xml ether_backup_decoded.txt` — the complete delta is:

- **(a) WAN-RELEVANT ⚠** `CD.3.WANIPConnection.1.Enable=1` (factory) → **absent** (live baseline).
- **(b) WAN-RELEVANT ⚠** `WANEthernetInterfaceConfig.Enable=1` (factory) → **absent** (live baseline).
- **(c) WAN-RELEVANT** `CD.3.WANIPConnection.1` gains `DefaultGateway=0.0.0.0`, `SubnetMask=0.0.0.0`, `ExternalIPAddress=0.0.0.0` (factory: ExternalIPAddress empty, other two absent). These three values are *exactly* the field set linkdetection ETHER Tx A writes when it (re)creates the Eth_Internet profile (§6.2) — STRONGLY INFERRED: a linkdetection ETHER Tx A (or equivalent profile normalisation) had already executed on the live unit before this backup was taken. It does **not** prove a full ETHER switch occurred (WANMode/DCS/ACS in the same backup are all GPON/production values).
- **(d) Non-WAN:** `LoginPrivilegeMgmt.i1.UserLevel=0` added; `SSH.Interface=LAN` added. No other differences anywhere in 583 KB — in particular **WANMode, WanAutoDetect, DCS (all keys), ACS URL, CD.1/CD.2/CD.4/CD.5, firewall and NAT states are identical** between factory and live baseline.
- **(e) WanAutoDetect rollback discrepancy ⚠:** factory *and* live baseline both say `1`, and ROLLBACK_PLAN step 4 says restore `1`; **but** linkdetection's own GPON switch writes `0` (§6.2) and preserved `rollback.ccc` writes `0` (`SET_NO_BE WanAutoDetect boolean 0`). Two different "GPON end states" exist in the artifacts: *factory state* (AutoDetect=1, daemon armed) vs *post-switch state* (AutoDetect=0, daemon disarmed). A rollback must choose deliberately; restoring the Phase-0 **backup file** yields 1. This pass does not resolve which the operator wants — flagged, not guessed.

Consequence of (a)+(b): in the live baseline, both Enable parameters that the Boot gate and the link-type function read were **unconfigured**, so their effective values were the schema defaults. Factory-configured `1`s must not be assumed to be the live rollback target for these two parameters; the only faithful rollback is restoring the backup (or deleting the configured values created during deployment).

## 5.5 The two preserved rollback scripts — reconciliation (CONFIRMED STATIC, read in full)

- `DUMPFILES/ether-rollback.ccc`: plain `SET` (BE) for: Gpon Enable=1, Eth Enable=1, CD.1 PPP Enable=1, CD.2 IP Enable=1, CD.3 IP Enable=1, NDPPD Enabled=0, IPv6PD Interface→CD.1 PPP, DCS (v4+v6)→CD.1 PPP, WANMode=GPON. **No `SAVE`** — persistence relies on the commit; unlike `rollback.ccc` it does not append the save action, a defect risk if the WANMode-triggered reboot (§7.2) races persistence. It does **not** delete any CD.3 PPP object, does **not** restore the ACS URL, and does **not** touch WanAutoDetect. It matches the GPON *switch* end-state for Enables (except Eth Enable=1, where linkdetection-GPON writes 0 — the script's 1 matches the **factory** value instead).
- `DUMPFILES/rollback.ccc`: `SET_NO_BE` for everything (WANMode=GPON is plain `SET`), plus `WanAutoDetect=0` (see §5.4e), NDPPD Enabled=0, IPv6PD→CD.1 PPP, DCS v4+v6→CD.1 PPP, CD.1/CD.2/CD.3 Enables=1, Eth Enable=1; ends `SAVE; SEND;` (correct vendor order). Also does **not** delete a CD.3 PPP object and does **not** restore the ACS URL.
- **Neither script is a complete rollback** against §5.2: both miss (i) CD.3 PPP deletion, (ii) ACS URL restoration, (iii) the baseline-absent state of the two Enables in §5.4(a)(b). ROLLBACK_PLAN.md steps 1–5 cover (i) and (ii); the scripts must be reconciled line-by-line before use, exactly as ROLLBACK_PLAN already warns.

---

# Blocker 6 — ACS / TR-069 side effects

## 6.1 Method (fresh this session)

Full Capstone disassembly of `linkdetect_switch_WanMode` in `DUMPFILES/linkdetection` @**0x402454** (size ≈0x10d8, stripped EXEC, VA = file VA), with PLT resolution from `.rela.plt` and adrp/add string tracking. Boolean SET values are passed by pointer to two stack bytes initialised in the prologue (@0x402474–0x402480): **`sp+0x327` = byte 1 (true), `sp+0x326` = byte 0 (false)**, `sp+0x324` = uint16 0. Every `cmsgRequestSet`/`cmsgRequestSetNoBE` below was mapped to its SEL target, parameter name, and value pointer — the enumeration is complete for all three branches. Type word `0x20000001` = boolean SetNoBE; `0xc0000000`-family (`mov w2,#-0x40000000`) = string.

## 6.2 Branch tables (CONFIRMED STATIC)

**GPON branch** (`strcmp` arg vs `"GPON"` @0x4039b8, taken @0x4025d0) — **one** transaction, `cmsgRequestSave` @0x402abc, `cmsgSendRecv(...,60000)` @0x402acc:

| SEL | Parameter | Value | Kind |
|---|---|---|---|
| `X_5067F0_Ext.WANSwitch` | `WANMode` | `"GPON"` | Set (BE) |
| `X_5067F0_Ext.WANSwitch` | `WanAutoDetect` | **0** | SetNoBE |
| `WANDevice.1.X_5067F0_GponInterafceConfig` | `Enable` | 1 | SetNoBE |
| `WANDevice.1.WANEthernetInterfaceConfig` | `Enable` | **0** | SetNoBE |
| `WANDevice.1.CD.1.WANPPPConnection.1` | `Enable` | 1 | SetNoBE |
| `WANDevice.1.CD.2.WANIPConnection.1` | `Enable` | 1 | SetNoBE |
| `WANDevice.1.CD.3.WANIPConnection.1` | `Enable` | **0** | SetNoBE |
| `LANDevice.1.…IPv6LANHostConfigManagement.NDPPD` | `Enabled` | 0 | SetNoBE |
| `LANDevice.1.…IPv6PDWanConnection` | `Interface` | `…CD.1.WANPPPConnection.1` | SetNoBE |
| `Layer3Forwarding` | `DefaultConnectionService` | `…CD.1.WANPPPConnection.1` | SetNoBE |
| `X_5067F0_IPv6Layer3Forwarding` | `DefaultConnectionService` | `…CD.1.WANPPPConnection.1` | SetNoBE |
| `ManagementServer` | **`URL`** | **`http://tms.airtelbroadband.in:8103`** (string @0x403cf0; SET @0x402a30) | SetNoBE |
| `ManagementServer` | `X_5067F0_OverIPv6` | 0 | SetNoBE |
| `X_5067F0_DeviceRecognition` | `Enable` | 0 | SetNoBE |

**ETHER branch** (`strcmp` vs `"ETHER"` @0x403d70, @0x402b10) — **two** transactions:

Tx A (creation; `cmsgRequestSave` @0x402eb8, SendRecv @0x402ec8) runs only when `CD.3.WANIPConnection.1` is missing; a second gate `access("/tmp/ADD_WAN_update_181DM_done",…)` @0x402f1c guards Tx B. Tx A creates the IP child (`cmsgRequestSetIndexedObj(...,1)` @0x402b94) and sets: `Enable=`**0**, `X_5067F0_InterfaceName="nas0_notag"`, `DefaultGateway="0.0.0.0"`, `X_5067F0_SERVICELIST="TR069"`, `SubnetMask="0.0.0.0"`, `ExternalIPAddress="0.0.0.0"`, `Name="Eth_Internet"`, `X_5067F0_RIPVersion="N/A"`, `X_5067F0_ExternalIPv6AddressPrefixLength=0`, `X_5067F0_IPv6Enabled=1`, `X_5067F0_DualStack=1`, `X_5067F0_Enable_VLANID=0`, `X_5067F0_IGMPEnabled=0`, `X_5067F0_VLANID=0`, plus `X_5067F0_DNS.1/.2/.3` indexed children. (Compare §5.4(c).)

Tx B (`cmsgRequestSave` @0x4033c0, SendRecv @0x4033d0):

| SEL | Parameter | Value | Kind |
|---|---|---|---|
| `X_5067F0_Ext.WANSwitch` | `WANMode` | `"ETHER"` | Set (BE) |
| `WANDevice.1.X_5067F0_GponInterafceConfig` | `Enable` | **0** | SetNoBE |
| `WANDevice.1.WANEthernetInterfaceConfig` | `Enable` | 1 | SetNoBE |
| `WANDevice.1.CD.1.WANPPPConnection.1` | `Enable` | **0** | SetNoBE |
| `WANDevice.1.CD.2.WANIPConnection.1` | `Enable` | **0** | SetNoBE |
| `WANDevice.1.CD.3.WANIPConnection.1` | `Enable` | 1 | SetNoBE |
| `LANDevice.1.…NDPPD` | `Enabled` | **1** | SetNoBE |
| `LANDevice.1.…IPv6PDWanConnection` | `Interface` | `…CD.3.WANIPConnection.1` | SetNoBE |
| `Layer3Forwarding` | `DefaultConnectionService` | `…CD.3.WANIPConnection.1` | SetNoBE |
| `X_5067F0_IPv6Layer3Forwarding` | `DefaultConnectionService` | `…CD.3.WANIPConnection.1` | SetNoBE |
| `ManagementServer` | **`URL`** | **`http://testacs.airtelbroadband.in:8103/`** (string @0x404018 — **trailing slash**; SET @0x40338c) | SetNoBE |
| `ManagementServer` | `X_5067F0_OverIPv6` | **1** | SetNoBE |

Note the ETHER transaction does **not** write `WanAutoDetect` at all (it keeps its prior value), while the GPON transaction writes it **0** — an asymmetry with the consequence in §6.3.

**DISABLE branch** (`strcmp` vs `"DISABLE"` @0x404040, @0x403434) — one transaction (Save @0x4034c4): only `WANSwitch.WanAutoDetect = 0` (SetNoBE).

## 6.3 ACS answers

- **ETHER ACS URL (exact):** `http://testacs.airtelbroadband.in:8103/` — CONFIRMED STATIC (string @0x404018 in linkdetection; also present in libbemodules strings). Note the **trailing slash**.
- **GPON ACS URL (exact):** `http://tms.airtelbroadband.in:8103` — CONFIRMED STATIC (string @0x403cf0 in linkdetection; SET @0x402a08–0x402a30). **No trailing slash** — and this exactly matches the configured production value (next bullet), so the GPON branch restores the URL *byte-for-byte*.
- **Actual Phase-0 / live ACS URL — KNOWN, not UNKNOWN:** `http://tms.airtelbroadband.in:8103` appears exactly once in **each** of: factory PDM (`ManagementServer.URL`, `EXTATTR=0x0800`), the Phase-0 live baseline `ether_backup_decoded.txt`, and the ROM decode `romfile_decoded.txt` (CONFIRMED STATIC, grep). `testacs` appears **zero** times in every config/backup/image in the repo. The one source that contains **no** ACS value is the decompressed RDM image (§5.1) — it is a schema/defaults image, so the absence there is expected and does not make the live value unknown.
- **Other TR-069 / ManagementServer parameters changed:** exactly **one** — `ManagementServer.X_5067F0_OverIPv6` (GPON→0, ETHER→1), SET in the same transactions immediately after the URL. **Nothing else**: the complete SEL/SET enumeration (§6.2) contains no `PeriodicInformEnable/Interval`, `Username`, `Password`, `ConnectionRequest*`, `UpgradesManaged`, or any other ManagementServer parameter, in any branch (CONFIRMED STATIC).
- **Auto-restore on mode flip back?** **YES, by construction** (CONFIRMED STATIC): the GPON branch unconditionally SETs the production URL in the same transaction as `WANMode="GPON"`. Two conditions caveat the *daemon actually running that branch*: (i) linkdetection's main reads the WANSwitch object at startup (`rdmGetObjectByName` @0x401a18; WANMode string at obj+1, defaulting to `"GPON"` @0x401a90 if empty; the byte at obj+0 — WanAutoDetect — is compared to 1 @0x401acc and logged as `PonActivated:[%d] WanMode:[%s]` @0x4037b8) and the switching checks are gated on that flag (STRONGLY INFERRED from prior analysis @0x401a08–0x401e10, consistent with the fresh gate reads); since the GPON switch itself writes WanAutoDetect=0 and the ETHER switch leaves it untouched, a unit switched to ETHER *by linkdetection* still has WanAutoDetect=1 and can flip back; a unit whose WanAutoDetect was manually set 0 (Plan Phase 5 hardening, or `rollback.ccc`) will **not** auto-restore anything. (ii) A manual RDM/broadband mode change does not pass through linkdetection at all — ACS restoration then is the operator's explicit step (ROLLBACK_PLAN step 5). Do not rely on auto-restore as the rollback mechanism.
- **Notifications:** every ACS-affecting SET in linkdetection is `cmsgRequestSetNoBE` — **NoBE = no backend event**: the URL/OverIPv6 changes generate no ccc_be ObjectChanged processing and no BE-driven TR-069 value-change handling at commit time (the new URL simply takes effect for the CWMP client's next session; the parameter's PDM `EXTATTR=0x0800` marking is a data-model attribute, not something linkdetection acts on). The **only** BE (`cmsgRequestSet`) write in either branch is `WANSwitch.WANMode` — which is precisely the write that reaches ccc_be's L0 dispatcher and its reboot path (§7.2). CONFIRMED STATIC (call-variant enumeration); the CWMP client's internal reaction to a URL change is **UNKNOWN** (its binary was not in scope).

## 6.4 Does the broadband.cgi Web UI path touch ManagementServer?

**NO — CONFIRMED STATIC.** `strings DUMPFILES/broadband.cgi` contains **zero** occurrences of `ManagementServer`, `acs`, `tms`, or `testacs` (grep this session), and the fresh full disassembly of `cgiMain` (@0x403390) shows its RESTART branch (@0x4036cc–0x40387c) writing exactly three things, all via `cmsgRequestSet` (BE) + `cmsgRequestSave` in the single end-of-handler transaction: `GponInterafceConfig.Enable` (OID 0xc7 SelId @0x403794; value = `wanMode=="GPON"`), `WANEthernetInterfaceConfig.Enable` (OID 0xca SelId @0x403810; value = `wanMode=="ETHER"`), and `WANSwitch.WANMode` (OID 0x4d SelId @0x40384c; value = the submitted `wanMode` form string, `"GPON"`/`"ETHER"`). The IP→PPP conversion path likewise contains no ManagementServer SEL/SET (prior full analysis, MASTER CGI-1). **The Web UI mode switch is ACS-safe; only linkdetection clobbers the ACS URL.**

---

# Blocker 7 — Boot vs config-change behaviour

## 7.1 Which WAN init functions run where (CONFIRMED STATIC unless marked)

| Function | Address | Runs at boot | Runs on config change | Evidence |
|---|---|---|---|---|
| `OID_…_WANDevice_i_ConfigLoaderFunc_Boot` (libbemodules) | 0x50d08 | **Yes** — framework Boot callback | No (Boot-registered) | Fresh full disassembly §7.3 |
| `libcccBeWan_eth_Init` (libcccbe) | 0x38074 | **Yes, iff** Eth Enable≠0 **and** `WANMode=="ETHER"` | **Never** — exactly **one** call site in all of libbemodules: Boot @0x50ed4 | PLT-xref enumeration (whole .text scan) + fresh eth_Init disasm: `EthPhyEnable(1)`; `smuxctl --if %s --set-if-rsmux …` (@0x4c1e0); `echo switch_on/enable/refresh > /proc/rtk_smuxdev/hw_vlan_filter`; `rtk_wan_port_mapping(0, name)` @0x381a8 |
| `libcccBeWan_gpon_Init` (libcccbe) | 0x37e5c | **Yes, iff** Gpon byte≠0 **and** `WANMode=="GPON"` (Boot @0x50fb8) | **Never** — one call site only | Same enumeration |
| `libcccBeWan_eth_Disabled` (libcccbe) | 0x36c78 | Yes — Boot @0x50f5c when Eth Enable≠0 but mode ≠ ETHER | Never — one call site only | Same enumeration |
| `linkdetection` daemon spawn | — | **Yes** — Boot @0x50d50–0x50d84: `sprintf("%s &", "/usr/sbin/linkdetection")` → `cccBeDoSystem`, *before* any mode dispatch | n/a (daemon persists; it polls link state itself) | Fresh Boot disasm |
| `…_ConfigLoaderFunc_L0ConfigLoad` (dispatcher) | 0x50348 | Yes — initial load: dispatches L1→L2→L3→L4 per object (calls @0x50494/0x5062c/0x50694/0x507e0) | **Yes** — same dispatcher receives change events (it contains the WANSwitch-change branch, §7.2, which is dead code at boot when old==new) — STRONGLY INFERRED for the change-event routing, CONFIRMED STATIC for the code | Fresh disasm |
| `…_L1ConfigInit` / L2 / **L3ConfigInit** / L4 | 0x50858 / 0x4feb0 / **0x4f440** / 0x4f400 | Yes (via L0 load; L1ConfigInit is additionally called directly in the Boot loop per WANDevice, @0x50dfc) | Yes — via `L3ConfigLoad` forwarding OID 0xd7 changes to `L3ObjectChanged` (@0x4fea0), and L2/L4 ObjectChanged siblings | §3.4 |
| `createLayer3Interface` (libcccbe) — creates `nas0_notag` | 0x35348 | **Yes** (via L3 path) | **Yes** (via L3ObjectChanged → same action function), gated by §3.6.3 | Exactly 3 call sites, all inside `beWanDoLayer3InterfaceAction` (@0x6c558, 0x6c63c, 0x6c710, libbemodules). Fresh string scan: `/bin/smuxctl` + `"%s --if-create-name %s %s --set-if-rsmux"` @0x4b088; untagged branch appends `" --tags 0"` @0x4b0e8 (vs tagged `" --tags 1 --filter-vid 0x%x 1"` @0x4b0c8); `ifconfig %s mtu 1500` @0x4af20, `ifconfig %s txqueuelen 10` @0x4b2b8 |
| `libcccBeWan_doWanModeChange` (libcccbe) | 0x36d3c | No (old==new at load) | **Yes — the mode-change handler**: exactly one call site, L0 @0x505a8 | §7.2 |
| `beWanDisableClient` (pppd teardown) | 0x6722c | On L3 load of a disabled object | Yes, on disable/delete changes | §5.2 row 25 |

## 7.2 The reboot question — now settled statically (CONFIRMED STATIC)

1. `eth_Init`/`gpon_Init`/`eth_Disabled` are reachable **only** from the Boot callback (complete PLT-xref enumeration of libbemodules `.text` this session — one call site each, §7.1). **No config-change path can apply the port remapping** (`/proc/ni/dev_port_mapping`, `/proc/fc/ctrl/wan_port_mask`). Prior ETH-3's downgrade ("exclusivity not proven") is **lifted**: the exclusivity is now proven for libbemodules, the only importer that matters (libcccbe exports the functions; no other binary in the dump imports them — dynsym scan).
2. The change path instead **forces a reboot**: L0ConfigLoad (@0x50348) special-cases the WANSwitch node (OID **0x4d** compare @0x504d8): it takes the node's old/new value strings ([node+0x20]+1, [node+0x28]+1), and if they differ (`strcmp` @0x50598) calls `libcccBeWan_doWanModeChange(old, new)` @0x505a8. That function (libcccbe @0x36d3c, fresh disassembly) returns 0 silently only if the first argument is `"ANY"` (@0x4b9a8); otherwise it calls `write_omd_reboot_log(0x40)`, `write_sub_reboot_Reason("WAN_MODE_CHANGE_REBOOT")` (@0x4b9b0), and `cccBeDoSystem("reboot")` (@0x4b9c8). Failure of the change logs `"%s@%d: fa
...[truncated 7373 chars]