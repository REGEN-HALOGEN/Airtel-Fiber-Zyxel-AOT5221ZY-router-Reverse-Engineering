# Work file — Blockers 8, 9, 10 + Part-4 extra-blocker hunt

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, RTL9607C, AArch64) — LAN4 Ethernet WAN + PPPoE via external Syrotech ONT. ISP service name `3jglobal`, MTU/MRU 1480, auth `AUTO_AUTH` (from brief; no credentials anywhere in this file).
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **STATIC ANALYSIS ONLY** — no router/runtime access used or attempted; nothing here is a runtime result.
- **Confidence legend:** CONFIRMED STATIC = decoded from binaries/image this session · STRONGLY INFERRED = cross-function reconstruction, one unobserved link · UNKNOWN = not settled statically · DISPROVEN = contradicted by artifacts.
- **Tools:** Python 3.12 venv (`/tmp/revenv`) + Capstone 5 + pyelftools; `strings`/`readelf`/`nm` (host objdump is x86-only). Disassembler with PLT resolution from `.rela.plt` and adrp/add string annotation.
- **Artifact identity (sha256, verified this session):** `DUMPFILES/libcccbe.so` == `rootfs/lib/MSTC/libcccbe.so` (`ddacad88…`), `libbemodules.so` == rootfs copy (`1de450de…`), `libbeEvents.so` == rootfs copy (`cc9d2374…`), `DUMPFILES/ccc_be` == `rootfs/usr/bin/ccc_be` (`1da56bc3…`). **Exception:** rootfs `lib/MSTC/libCmd.so` hashes `ef06db889ab919ee57df7c2e4f95b30b3c5dd631e19353305f88588dc6b03371`, which does **not** match the `fa8ecd…` hash quoted in prior reports' tables — the libCmd.so in this repo is a different build than the one prior reports hashed. Its PPPoE templates (below) were re-read from the actual file.

Rootfs prefix below: `R = full-router-dump/filesystem/rootfs`.

---

## BLOCKER 8 — PPP config generation

Functions located in the actual binaries (all addresses CONFIRMED STATIC):

| Function | File | Address | Size |
|---|---|---|---|
| `libcccBeWan_getPPPPdUnitNum_wrapper` | `R/lib/MSTC/libcccbe.so` | 0x38264 | — |
| `setWanIpPppInterfaceName` | `R/lib/MSTC/libcccbe.so` | 0x346d0 | 0x224 |
| `libccc_executePPPv4Client` | `R/lib/MSTC/libcccbe.so` | 0x348f4 | 0x88 |
| `beConfigWANByPPPoE` | `R/lib/MSTC/libbemodules.so` | 0x664a8 | 1712 |
| `createWANPPPConnectionCfgFile` | `R/lib/MSTC/libbemodules.so` | 0x6a7c0 | 544 |
| `beWanEnablePPPv4Client` (pppd launcher) | `R/lib/MSTC/libbemodules.so` | 0x66ee4 | 0x30 |
| `libcccBeWan_createWANPPPConnectionCfgFile_wrapper` | `R/lib/MSTC/libcccbe.so` | 0x373a4 | stub, see §8.7 |

### 8(a) PPP unit formula — CONFIRMED STATIC (claim verified exactly)
`libcccBeWan_getPPPPdUnitNum_wrapper` @0x38264 (libcccbe):
```
0x38290  ubfx x7, x0, #0x28, #8      ; IA byte 5 = WANPPPConnection instance
0x38294  ubfx x6, x0, #0x30, #8      ; IA byte 6 = WANConnectionDevice instance
0x38298  lsr  x5, x0, #0x38          ; IA byte 7 = WANDevice instance
0x3829c  adrp/add x4 -> "%d%d%d" @0x4c3b8
0x382b4  bl __snprintf_chk           ; snprintf(tmp, 8, "%d%d%d", wanDev, connDev, pppInst)
0x382c4  bl strtol                   ; -> *intOut (when int-out requested)
0x38334  snprintf("%s") variant      ; -> strOut (when string-out requested)
```
Argument order is (WANDevice, ConnDev, PPPInst), so IA **1.3.1 → "131" → unit 131 → ppp131**; IA 1.1.1 → "111". String concatenation, not arithmetic. **Verdict: claim TRUE.**

Caller side in `beConfigWANByPPPoE` @0x66628–0x66654: wrapper called with the connection IA (x22), string-out buffer; result written with `fprintf(fp, "unit %s\n")` (fmt @0xbd650) — pppd receives `unit 131` as text in the options file.

### 8(b) PPPoEServiceName serialization — CONFIRMED STATIC, WITH A CRITICAL DEFECT
`beConfigWANByPPPoE` tail @0x66968:
```
0x66968  ldrb w0, [x20, #0x532]        ; first byte of PPPoEServiceName field
0x6696c  cbnz w0, #0x66b34             ; non-empty -> write it
0x66b34  fprintf(fp, "pppoe_srv_name %s", obj+0x532)   ; fmt @0xbd808
0x66b4c  b #0x66970
0x66970  fprintf(fp, "linkname %s\n", obj+0x3e7)       ; fmt @0xbd820, InterfaceName
0x66988  fclose
```
- The service name **is** serialized: line `pppoe_srv_name <name>`, using the exact option name the plugin registers (`pppoe_srv_name` is a global + option in `R/lib/MSTC/libpppoe.so`, with description string "PPPoE service name"; `setdevname_pppoe` @0x2c00, `pppoe_plugin_init` @0x2f98 in same lib). For the deployment this produces the token pair `pppoe_srv_name 3jglobal`. **No** `plugin rp-pppoe` / `rp-pppoe.so` / `service` option strings exist anywhere — the plugin option in the template is literally `plugin pppoe` (see 8.8).
- **DEFECT (new, CONFIRMED STATIC at code level):** the format string at 0xbd808 is `pppoe_srv_name %s` with **no trailing newline** (raw bytes verified: `pppoe_srv_name %s\x00`, unlike `unit %s\n`, `linkname %s\n` etc.). It is written **immediately before** `linkname %s\n`, so a generated file with a non-empty service name contains the single line:
  `pppoe_srv_name 3jgloballinkname ppp131`
  pppd tokenises options files on whitespace, so it will read service name = `3jgloballinkname` and then meet the stray word `ppp131`. This pppd contains the error string `In file %s: unrecognized option '%s'` (in `R/bin/pppd`), and upstream pppd 2.4.7 treats an unrecognized option in a file as fatal. Impact on session bring-up is therefore **STRONGLY INFERRED severe** (pppd exits on the bad token, or at minimum negotiates the wrong service name). The defect is **invisible on the factory GPON profile** because factory config never sets PPPoEServiceName (0 occurrences in both PDM XMLs — see PPP_PARAMETER_VALIDATION), so the branch is skipped and `linkname` lands on its own line. It bites exactly and only when a service name is configured — the deployment case.
  - Detection (future runtime): `cat /etc/ppp/options_nas0_notag` after enable; check `/tmp/pppd-info.tmp` / syslog for `unrecognized option 'ppp131'`.
  - Mitigations: (i) leave PPPoEServiceName empty if the BSS accepts an empty service in PADI (any-service) — CONTRADICTS the ISP data in the brief, must be tested, not assumed; (ii) accept that first bring-up may fail and diagnose via the generated file; (iii) no config-side fix exists — the file is regenerated by `cp`+append on every enable (see 8.8), so hand-editing the generated file is not durable across re-enables (it may survive until the next enable/disable cycle only).

### 8(c) MTU/MRU serialization — CONFIRMED STATIC
In `beConfigWANByPPPoE`, after `unit`, `user %s\n` (obj+0x324), `password %s\n` (obj+0x365) [values never reproduced here], `logfile /tmp/%sLog\n` (obj+0x3e7 InterfaceName → `/tmp/ppp131Log`):
```
0x666a4  ldrh w3, [x20, #0x18]  ; fprintf "mru %d\n"  fmt @0xbd698
0x666bc  ldrh w3, [x20, #0x1a]  ; fprintf "mtu %d\n"  fmt @0xbd6a0
0x666d4  ldrh w3, [x20, #0x20]  ; fprintf "lcp-echo-interval %d\n"
0x666ec  ldrh w3, [x20, #0x22]  ; fprintf "lcp-echo-failure %d\n"
```
MTU/MRU are **not** in the template files; they are appended per-connection from the u16 fields. Deployment values 1480/1480 → literal lines `mru 1480` / `mtu 1480`. **Verdict: claim TRUE.**

### 8(d) AUTO_AUTH mapping — CONFIRMED STATIC (full auth table decoded)
Auth string field = obj+0x649 (X_5067F0_PPPAuthenticationProtocol), compared with `strcmp` @0x66714/0x66728/0x6673c:
| Configured value | Lines written (fwrite, in order) |
|---|---|
| `PAP` (→0x668a4) | `refuse-chap`, `refuse-mschap`, `refuse-mschap-v2`, `refuse-eap` |
| `CHAP` (→0x669a8) | `refuse-pap`, `refuse-mschap`, `refuse-mschap-v2`, `refuse-eap` |
| `MS-CHAP` (→0x66744) | `refuse-pap`, `refuse-chap`, `refuse-mschap-v2`, `refuse-eap` (note: plain `refuse-mschap` NOT written) |
| anything else, incl. `AUTO_AUTH` (fallthrough →0x66904) | **no refuse-\* lines at all** |
Format strings @0xbd6d8 `PAP`, @0xbd728 `CHAP`, @0xbd740 `MS-CHAP`; refuse literals @0xbd6e0/0xbd6f0/0xbd700/0xbd718/0xbd730. **Verdict: claim TRUE** — AUTO_AUTH ⇒ PAP/CHAP/MS-CHAP all left negotiable.
Also decoded in the same function: ConnectionType field (obj+0x633) `OnDemand` → `demand\n` (+ `idle %u`, random IPv6 IID block); `AlwaysOn` → `persist\n` + `passive\n`, plus `+ipv6\n`/`ipv6cp-use-persistent\n` (and `noip\n` when [obj+0x42]==2) when byte [obj+0x43] is set.

### 8(e) VLAN-dependent naming — CONFIRMED STATIC (both variants)
`setWanIpPppInterfaceName` @0x346d0 (libcccbe):
```
0x34744  ldrb w0, [x19, #0x18]          ; VLAN-enable byte
0x34748  cbz w0, #0x3481c               ; 0 -> untagged
0x3481c  literal "_notag" @0x4aea8 copied as suffix
0x3474c  (enabled) ldr w5, [x19, #0x20] ; VLAN ID
         snprintf suffix with "_%d" @0x4d990
0x348a8  PPP branch (LinkType [x19]==1):
         [x19+0x28] = snprintf("%s%s", base, suffix)        ; L2 name
         [x19+0x30] = snprintf("ppp%d" @0x4aeb0, [x19+0x48]) ; unit int
```
So untagged ⇒ `nas0_notag`; tagged ⇒ `nas0_<vid>` (e.g. `nas0_100`). Production data corroborates both forms — factory PDM XML `X_5067F0_InterfaceName` values: ConnDev.1 PPP = `ppp111`, ConnDev.2 IP = `nas0_660`, ConnDev.3 IP = `nas0_notag`, ConnDev.4 IP = `nas0_100`, ConnDev.5 IP = `nas0_100` (parsed from `DUMPFILES/aot-current-pdm-config.xml` this session). The literal `nas0_100` inside libcccbe (@0x44be0) is **not** in this path — see Blocker 9 classification (PCAP default).

### 8(f) pppd launch args — CONFIRMED STATIC (claim true, with the redirect the claim omitted)
`libccc_executePPPv4Client` @0x348f4 (libcccbe):
```
0x3493c  adrp/add x4 -> "%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &" @0x4aee0
0x34954  bl __snprintf_chk   ; args: x5=x0 (arg0), x6=x7=x1 (arg1 used twice)
0x3496c  bl cccBeSystemQueue
```
Caller `beWanEnablePPPv4Client` @0x66ee4 (libbemodules) passes arg0 = literal `/bin/pppd` (@0xbd888, xref @0x66ef8) and arg1 = the connection's IfName; it then calls `beWanEnableAllMulti`. Exact generated command for the deployment:
`/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`
No `-d` in this path. **Verdict: claim TRUE** (the claimed string was the prefix of the real one).

### 8.7 `createWANPPPConnectionCfgFile` @0x6a7c0 — role now resolved (updates prior "UNKNOWN product", closes most of U6)
CONFIRMED STATIC from full disassembly (544 B): returns −1 if Enable byte [obj+0x2c]==0 (branch @0x6a7fc→0x6a9d8). Otherwise: zeroes IPv6/DNS-adjacent fields (+0x66a, +0x876, +0x2d3, +0x3a6…), calls `cleanWANvalue4IPv6` and `cleanDNSv6`, writes the literal `"Disabled"` (immediate-built @0x6a898) at obj+0x951 on the non-IPv6 branch, then calls **beConfigWANByPPPoE@plt @0x6a8b8** (the options-file writer of §8(b–d)), then `libcccBeWan_createWANPPPConnectionCfgFile_wrapper@plt` @0x6a8cc, then `processDNSofPPPConnection`.
Notable: that libcccbe wrapper @0x373a4 is a **no-op stub** in this build (`mov w0,#0; ret`, 20 B incl. two sibling stubs) — so the name-setting/launch work is *not* done through it; launch happens via `beWanEnablePPPv4Client` (§8(f)). Prior report wording "not the options writer" is imprecise: the function itself doesn't fprintf, but it is the orchestrator that invokes the options writer.

### 8.8 Template files — correction to prior reports (CONFIRMED STATIC, files read this session)
`beConfigWANByPPPoE` start: builds `/etc/ppp/options_%s` (fmt @0xbd598, %s = IfName), then:
- AddressingType field (obj+0x2c8) == `"Static"` **and** byte [obj+0x92] != 0 → `cp -rf /etc/ppp/_options_static <options>` (fmt `cp -rf %s %s` @0xbd5d8, @0x667a8);
- otherwise → `cp -rf /etc/ppp/default_options <options>` (@0x66568);
then `fopen(options, "a+")` and the appends of §8(b–d). Static-with-no-address sub-case (@0x6685c) first appends a `%s:\n` line (static IP field at obj+0x92).
Actual template contents in **this** rootfs (both populated — the prior claim "default_options is 0 bytes / contents look swapped" is **DISPROVEN for this dump**; only one copy of each file exists in the repo):
- `R/etc/ppp/default_options` (90 B): `plugin pppoe` / `noipdefault` / `ipcp-accept-remote` / `usepeerdns` / `hide-password` / `holdoff 3 ` / `maxfail 0`
- `R/etc/ppp/_options_static` (94 B): `plugin pppoe` / `noipdefault` / `ipcp-accept-remote` / `nodetach` / `usepeerdns` / `hide-password` / `holdoff 3` / `debug`
So the dynamic-PPPoE generated file = default_options + appended lines (`unit 131`, user/password, logfile, mru/mtu, lcp-echo-*, [refuse lines], [persist/passive], [pppoe_srv_name…], linkname). `usepeerdns` comes from the template (relevant to Blocker 9 DNS).

### 8.9 Plugin reality (needed by 8(b) and Part 4)
There is **no** `lib/pppd/2.4.7/rp-pppoe.so` anywhere in the repo (prior lifecycle report's path claim is wrong), and `R/usr/bin/pppoe-start` is a 0-byte file. The mechanism is different and proven: `R/bin/pppd` (2.4.7, MSTC build) has DT_NEEDED `libpppoe.so`, RPATH `/lib/MSTC:/usr/lib/MSTC`, and an undefined import of `pppoe_plugin_init`, which `R/lib/MSTC/libpppoe.so` exports (@0x2f98). pppd's plugin loader (function around 0x414d8c in pppd) does `strcmp(name, "pppoe")` @0x414da8 and on match calls `pppoe_plugin_init@plt` @0x414db4 directly (`pppoa` also accepted; anything else → `Invalid plugin %s`). Kernel side: `R/lib/modules/5.10.138/pppoe.ko` (+ `pppox.ko`, `ppp_generic.ko`) present, and `R/etc/modules.d/pppoe` lists `pppoe`. **The `plugin pppoe` line therefore works without any plugin .so file.**

---

## BLOCKER 9 — Routing / NAT / firewall

### 9.1 Hardcoded-literal sweep — every hit, classified
Swept: all of `R/` (text+binary grep) and `DUMPFILES/`.

| Pattern | Hit | Classification |
|---|---|---|
| `ppp111` | `R/usr/bin/hachi` @0x404648 (string VA) | **Generic-with-GPON-default fallback.** In hachi's firewall watchdog (~0x4026xx–0x402844): WAN ifname is first resolved dynamically (helper @0x402bdc fills the name buffer when the source pointer is non-NULL); `ppp111` is snprintf'd **only as the fallback when resolution yields nothing** (@0x4027b4), then used for TR181FrwlInput/Forward checks (v4+v6). Not a data-path dependency; worst case it monitors/repairs rules for a dead interface while missing ppp131 (see 9.4). |
| `ppp111` | `DUMPFILES/aot-current-pdm-config.xml`, `-backup.xml` | **Data** — stored `X_5067F0_InterfaceName` of the GPON PPP object. Not code. |
| `ppp131` | *none anywhere* | — (name is computed, §8(a)) |
| `nas0_100` | `R/lib/MSTC/libcccbe.so` @0x44be0 | **Benign debug default.** Sole xref @0x2a72c in `libcccbepcap_get_PCAP_Monitor_Interface` path: used as the capture interface **only when the resolved interface pointer is NULL** (csel @0x2a73c). Packet-capture feature, not WAN data path. |
| `nas0_100`, `nas0_660` | PDM XMLs | **Data** — stored IfNames of factory IP profiles (ConnDev.4/.5 and ConnDev.2). |
| `WANConnectionDevice.1` (full GPON PPP path) | `R/usr/bin/ccc_be` @0x419f90 | **Generic mechanism, GPON default value.** Xrefs @0x414eb8/@0x414f0c are an init routine that *writes the per-mode slots*: param `DefaultConnectionService_GPON` := `…WANConnectionDevice.1.WANPPPConnection.1` and `DefaultConnectionService_ETHER` := `…WANConnectionDevice.3.WANIPConnection.1`, on both the OID-0x87 and OID-0x83 objects. It is the stored factory default for GPON mode, not a runtime assumption in the Ethernet path. Confirms DCS_ETHER factory value is the **IP** object — for PPPoE the effective DCS must name ConnDev.3.WANPPPConnection.1 (config task, already in the plan). |
| `WANConnectionDevice.1…` | `R/lib/MSTC/libCmd.so` strings | **GPON-shaped CLI templates.** e.g. `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.%d` (+ `.X_5067F0_DNS.%d` twin, and WANIPConnection twins) — RDM-path templates in the CLI/debug library with the ConnDev.1 prefix literal and only the PPP instance parameterised. Dangerous only if a libCmd helper is used to act on the *Ethernet* connection's DNS object; the main enable path (§8) does not use them. Flagged, not on the proven path. |
| `WANConnectionDevice.1…` | `DUMPFILES/linkdetection` strings | **GPON-only code path by design** — the mode switcher's hardcoded object paths: `…WANConnectionDevice.1.WANPPPConnection.1`, `…WANConnectionDevice.2.WANIPConnection.1`, `…WANConnectionDevice.3.WANIPConnection.1` (+ its DNS.1–.3 children), `X_5067F0_GponInterafceConfig` (vendor spelling), `WANEthernetInterfaceConfig`. Known from prior reports. |
| `WANConnectionDevice.1…` | `DUMPFILES/rollback.ccc`, `ether-rollback.ccc` | **Restore tooling (data/scripts)** — SEL/SET scripts that restore the GPON profile + DCS to ConnDev.1 PPP. Expected; not executed by the Ethernet path. |
| `WANConnectionDevice` generic | `bin/obuspa`, `libTree.so`, `libcccrdm.so`, `librdm.so`, `libbestatus.so`, `libdasmodules.so`, `sbin/udhcpc`, … | Parameterised (`%d`) path formats — generic. |

**No `ppp111`/`ppp131`/`omci*`/`veip*` literal exists in any PPP-path binary (libcccbe, libbemodules, libbeEvents, ccc_be, pppd, libpppoe).**

### 9.2 Event 206 chain — CONFIRMED STATIC
`R/etc/ppp/ip-up` (614 B, read verbatim): takes `$1`=ppp ifname (REALNAME), `$2`=nas0_x (REALDEV); writes `/var/wan_connection_notify/<REALDEV>_connection_is_up` containing `RDMNAME config;` and `EVENTNOTIFY 206 string $REALNAME;`, then runs `ccctest -f <file>`. Fully generic in `$REALNAME` → fires `EVENTNOTIFY 206 string ppp131` for the deployment.
Handlers in `R/lib/MSTC/libbeEvents.so` (dynsym): `Route_EventHandlerFunc` @0x9028, `NAT_EventHandlerFunc` @0x9298, `DNS_EventHandlerFunc` @0xe220, `L3Forwarding_Connection_EventHandlerFunc` @0xb370, `Firewall_EventHandlerFunc` @0xbd38, `Firewall_TR181_WanConnectionUpEventHandle` @0xbcb8, plus `WANConnection_EventHandlerFunc` @0x1048c. Spot-decoded:
- `L3Forwarding_Connection_EventHandlerFunc`: on CEVENT_WAN_CONNECTION_UP → `layer3Forwarding_wanConnectionUp` (PLT); on DOWN → `layer3Forwarding_wanConnectionDown`; IPv6 up/down → `layer3Forwarding_v6WanConnectionUpDown`. Event-content string is passed through — interface comes from the event, not a literal.
- `NAT_EventHandlerFunc` on WAN_CONNECTION_UP: `initialNatChain` → `resetNatConfig` → `FullNatControl` (object-driven).
- `Firewall_TR181_WanConnectionUpEventHandle` @0xbcb8 (128 B): simply re-runs `OID_InternetGatewayDevice_Firewall_ConfigLoaderFunc(obj, NULL)` — a full config-driven firewall reload, no interface literal.
- `eventRouteIPChange` @0x8ca8 (libbeEvents): iterates RDM route objects by OID list (`cccRdmGetObjListByOID`), calls `DelRouteRule`/`AddRouteRule` per object — object-driven, no interface literal.

### 9.3 Default route — CONFIRMED STATIC generic (v4 + v6)
`layer3Forwarding_wanConnectionUp` @0x56d10 (libbemodules, 512 B): templates `route add default dev %s` @0xb56b8, `route add default gw %s dev %s` @0xb56d8, `route del default dev %s` @0xb56f8, `route del default > /dev/null 2>&1` @0xb5660; gateway from `libcccBeCommon_getV4DefaultGatewayAddr`; gated by `libcccBeCommon_isDefaultGw`. IPv6: `ip -6 ro add` / `ip -6 ro del` templates and `libcccBeCommon_addDelIPv6DefaultRouter` / `removeIPv6DefaultRouter` exist in libbemodules; IPv6 twin of the up/down handler above.
`updateDefaultRouteByLinkType` @0x6f2d8 (libbemodules): the mode machinery — reads DefaultConnectionServicePtr (+ IPv6 twin OID 0x84/0x87 family, + MultiLinkType variant), logs `change IPv4 default route to GPON link type` / `…to Ethernet link type` (@0xbe988/@0xbe9c0; IPv6 twins @0xbe9f8/@0xbea30), calls `updateIPv6RelatedPath`. **ppp131 conclusion:** the route target is the UP connection's own interface name; whether *this* connection is treated as the default gateway is decided by config lookups (isDefaultGw/DCS). So DCS correctness remains load-bearing at the config level (STRONGLY INFERRED — the isDefaultGw internals were not fully disassembled), but there is **no GPON/interface literal anywhere in the route path**. U7's runtime test is still the cleanest proof.

### 9.4 NAT / firewall / MSS — CONFIRMED STATIC generic
- NAT templates exist **only** in libbemodules (libbeEvents: 0, libcccbe: 0 — re-verified by grep this session): `iptables -t nat -A NAT_POSTROUTING -o %s -j MASQUERADE`, `… -o %s -s %s/24 -j MASQUERADE`, iprange variant, SNAT variants `iptables -t nat -%s ADDRMAP_POST_%d … -o %s -j SNAT --to %s`. All keyed on `%s` interface name + the connection's NATEnabled. The prior "-o ppp111 in FullNatControl" claim remains DISPROVEN.
- Firewall: forwarding/ACL templates in libbemodules are `-i %s`/`-o %s` parameterised. The concrete RELATED/ESTABLISHED insurance mechanism was located this session — it is **hachi's watchdog** (§9.1): templates `%s -L %s -vn | grep RELATED | grep %s | wc -l` @0x404760 and `%s -I %s -p ALL -i %s -m state --state ESTABLISHED,RELATED -j ACCEPT` @0x404790 over chains `TR181FrwlInput`/`TR181FrwlForward`, gated on `/tmp/state_wan_up` (@0x402898 access()). With the dynamic name resolution working, ppp131 is covered; with the `ppp111` fallback it is not (watchdog would babysit a nonexistent interface). Whether the *primary* firewall config loader (config-driven, §9.2) installs the ppp131 forward rules is STRONGLY INFERRED yes (it rebuilds from the connection object on WAN-up); exact rule list remains a runtime observation (U8).
- MSS: `addTCPMSSDefaultRule` @0x66f18 / `delTCPMSSDefaultRule` @0x66f9c (libbemodules) re-decoded: `-D` then `-I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu` for iptables **and** ip6tables (@0xbd898/0xbd8f8/0xbd958/0xbd9b8). Global, interface-agnostic, no MTU literal (PMTU-derived ⇒ 1440 for MTU 1480). Call timing still UNKNOWN (U10).

### 9.5 DNS — STRONGLY INFERRED generic
`ip-up` does nothing for DNS (verbatim read). Chain: template `usepeerdns` (§8.8) → pppd writes `/etc/ppp/resolv_%s.conf` (string in `R/bin/pppd`, %s = ifname) → ccc side `configDNSServers` @0x11cbc (libbeEvents, 2116 B) resolves the **default WAN** via the Layer3Forwarding object and handles both branches (log strings `Find Default Wan. WANIPConnection` / `Find Default Wan. WANPPPConnection`), feeding `Dnsmasq_Conf_Creation`, `Add_Static_Route_For_DNS_Servers`, `Restart_Dnsmasq`. No interface-specific code. Runtime confirmation still U9.

### 9.6 Disconnect cleanup — CONFIRMED STATIC generic
`R/etc/ppp/ip-down` (793 B, read verbatim): same pattern as ip-up with `EVENTNOTIFY 207 string $REALNAME;` → `_connection_is_down` file → ccctest. (It also writes leftover "Sean debug" syslog lines — cosmetic.) IPv6 twins: `ipv6-up` → Event **213**, `ipv6-down` → Event **214**, keyed on `$DEVICE`; `ipcp_down` → Event **780**. Down-path handlers call `layer3Forwarding_wanConnectionDown` (§9.2) whose `route del default dev %s` template exists. NAT/firewall teardown on down is via the same config/event reload machinery (STRONGLY INFERRED; exact flush list = runtime, part of U8).

### 9.7 Fastpath — UNKNOWN (unchanged, now with fuller string evidence)
libcccbe references `/proc/fc/ctrl/wan_port_mask` (init only, Blocker 10), `hwnat` on/off, `flow_flush`, and the QoS `skbmark_*` family — all QoS/flow-classification plumbing, none tied to a PPP interface name or to Event 206 in anything examined. No string/disasm supports "Event 206 programs ASIC flow tables for the session". Whether ppp131 flows are hardware-offloaded is UNKNOWN (runtime U10).

### 9.8 ppp131 proof status
**PROVEN generic (CONFIRMED STATIC) for:** unit/name derivation (§8a/e), options generation (§8b–d), pppd launch (§8f), ip-up/ip-down event emission (verbatim scripts, `$REALNAME`), route add/del templates (interface is a `%s` argument), NAT MASQUERADE templates (`-o %s`), MSS clamp (global), DNS resolver branch (dual IP/PPP handling). **No mechanism in the chain names ppp111 or any GPON object; every one consumes the interface name or the RDM object of the connection that came up.** Remaining runtime-only links: DCS/isDefaultGw decision for this profile (U7), exact FORWARD rule list (U8), DNS propagation (U9), hachi's dynamic name resolution succeeding for ppp131 (§9.1).

---

## BLOCKER 10 — LAN3 / Wi-Fi

### 10.1 Port mapping — CONFIRMED STATIC, re-disassembled this session
`rtk_wan_port_mapping` @0x37c84 (libcccbe), signature (mode, ifname), NULL ifname → −1:
- Mode 0 (Ethernet) @0x37d68: `mov w5,#3`; fmt `echo %d %s > %s` @0x4c188 with path `/proc/ni/dev_port_mapping` @0x4c168 → **`echo 3 <ifname> > /proc/ni/dev_port_mapping`**; `mov w0,#8; str w0,[0x6bc04]` (mask global = **0x08**).
- Mode 1 (GPON) @0x37dd8: port **7**, mask **0x80**.
- Shared tail @0x37e0c: if mask global > 0 → `echo %d > /proc/fc/ctrl/wan_port_mask` (fmt @0x4c1b8).
Exactly **one** port is written and the mask is a single-port selector (0x08 = port 3). Port 2 / mask 0x04 (LAN3) appears nowhere in this function, nor in `libcccBeWan_eth_Init` @0x38074 or `createLayer3Interface` @0x35348 (per prior session's decode, corroborated by string absence). **Claim TRUE: LAN3 = port 2 / 0x04; WAN mask 0x08 covers port 3 (LAN4) only; the mapping operation cannot touch LAN3.**

### 10.2 Bridge membership — CONFIRMED STATIC (config) + CONFIRMED absence (code)
- Default config (factory PDM XML, parsed this session): the Layer2Bridge `FilterInterface` set contains `LANDevice.1.LANEthernetInterfaceConfig.1`, `.2`, **`.3`**, `.4`, `LANDevice.1.WLANConfiguration.1`–`.8`, and `LANHostConfigManagement.IPInterface.1` (plus one WAN-side bridge profile, ConnDev.5 IP). I.e. **by default config, br0's member set includes LAN3 and all Wi-Fi SSIDs.**
- Bridge membership is applied by RDM Layer2Bridge code (`cccbeBridgeLayer2_addInterface2bridge`, `brctl addbr %s` in libcccbe; `Layer2Bridge_EventHandlerFunc`/`addBridge` @0xea7c in libbeEvents) — driven by those config objects, not by WAN mode.
- `linkdetection` contains **zero** bridge/brctl/br0 strings (grep this session) and its known function set only rewrites WAN objects/DCS/ACS/IPv6PD pointers. **ETHER mode switching does not touch bridge membership in any code examined.** WAN-init/PPP functions examined contain no bridge manipulation either.
- Caveat (honest): the factory XML is a GPON-mode snapshot; whether LAN4's *logical* LAN interface is pruned from br0 by some ETHER-mode path not examined (e.g. a LAN-object event handler reacting to the port remap) is not positively excluded — but no such code was found, and the switch-level remap (§10.1) is below the bridge layer. LAN3 has no such caveat: nothing references its removal.

### 10.3 Wi-Fi — CONFIRMED STATIC
Wi-Fi interfaces are members of the default bridge via `WLANConfiguration.1–.8` FilterInterfaces (§10.2). No WAN/PPP function examined references WLAN objects (the only WLAN-adjacent item found anywhere in scope is hachi's unrelated Wi-Fi-chip watchdog strings). **No static path from WAN mode change to Wi-Fi.**

### 10.4 DHCP / LAN addressing — CONFIRMED STATIC (config), no WAN coupling found
Factory `LANHostConfigManagement`: LAN IP `192.168.1.1`, mask `255.255.255.0`, DHCP pool `MinAddress 192.168.1.2` – `MaxAddress 192.168.1.254` (PDM XML, this session). These live under LANDevice only; no WAN-mode parameter feeds them in the config, and dnsmasq is (re)configured by the DNS event path (§9.5) for upstream resolvers — LAN scope unchanged. **DHCP scope/LAN addressing is not affected by WAN mode in anything examined.**

### 10.5 Regression check list — FUTURE RUNTIME OBSERVATIONS ONLY (none performed; for the human validation phase)
1. `bridge link` (and `brctl show br0`) captured in GPON mode (Phase 0) and again after Ethernet PPPoE is up (Phase 4): LAN3's port and both Wi-Fi interfaces still listed as br0 members; no member lost.
2. `cat /proc/ni/dev_port_mapping`: shows `3 nas0` (port 3 = LAN4 → WAN); no entry remapping port 2.
3. `cat /proc/fc/ctrl/wan_port_mask`: reads `8`.
4. LAN3 client test: plug a host into LAN3 → gets a 192.168.1.x DHCP lease, reaches the router UI, and reaches the internet via ppp131.
5. Wi-Fi client test on 2.4 GHz and 5 GHz SSIDs: association, DHCP lease in 192.168.1.2–.254, internet via ppp131.
6. `ip addr show br0`: still 192.168.1.1/24; `ip route`: LAN route 192.168.1.0/24 dev br0 intact alongside `default … dev ppp131`.
7. DHCP pool check in UI/dnsmasq config after activation: pool still 192.168.1.2–192.168.1.254 (no scope shrink/change).
8. LAN-to-LAN traffic LAN3 ↔ Wi-Fi client works (same-bridge forwarding unaffected).
9. LAN4 behaviour: a host plugged into LAN4 gets **no** DHCP lease and no LAN access (port is WAN now) — negative check that the remap took effect.
10. After a router reboot with the Ethernet profile active: repeat checks 1–5 (persistence of bridge/Wi-Fi/LAN3 state).

---

## PART 4 — Extra-blocker hunt (only items with evidence are rated; the rest are UNKNOWN)

### FOUND — with evidence

**P4-1. Service-name/linkname concatenation defect** — see §8(b). Evidence: fmt @0xbd808 lacks `\n`; write order srv_name→linkname in `beConfigWANByPPPoE`. **Likelihood: certain** (deterministic when PPPoEServiceName non-empty). **Impact: HIGH** (wrong service name negotiated and/or pppd `unrecognized option 'ppp131'` exit — pppd binary contains that exact error string). **Detection:** inspect generated `/etc/ppp/options_nas0_notag` + `/tmp/pppd-info.tmp` at first enable. **Mitigation:** none config-side; test empty-service-name fallback only as a diagnostic, since ISP data specifies `3jglobal`. *This is the single most important new finding of this pass.*

**P4-2. rp-pppoe plugin mismatch — REFUTED as a blocker.** The claimed `rp-pppoe.so` does **not** exist (nor does any `lib/pppd/` dir; `pppoe-start` is 0 bytes), but the mechanism is proven sound: pppd is linked against `libpppoe.so` and its loader special-cases the name `pppoe` → `pppoe_plugin_init` (§8.9). Likelihood of plugin failure: **LOW**. Residual risk is only that `libpppoe.so` itself misbehaves against the ONT (protocol-level, unknowable statically).

**P4-3. FullNAT auxiliary PPP family (`options_FN%d%d`) — resolved, not a competing path (closes U5).** Xrefs: `CreatePPPByFullNAT` @0x91d30 (xrefs @0x91dbc/0x91e78) and `beFullNatEnablePPPv4Client` @0x92200 (xref @0x9227c), strings @0xc1fd8 `options_FN%d%d`, @0xc1ff0 `unit %d%d\n`, @0xc2058 `cat %s/ppp%d%d.pid`, @0xc2028 `%s file %s %s > /tmp/pppd-info.tmp…`. This is the FullNAT (1:1-NAT) slave-pppd feature with two-component unit numbers; reachable only when a FullNAT PPP client is configured. **Likelihood of interfering with the main connection: LOW** (feature off by default; note both writers share `/tmp/pppd-info.tmp` as the redirect target — cosmetic log collision only).

**P4-4. hachi watchdog GPON-default fallback** — §9.1/§9.4. Evidence: `ppp111` fallback @0x4027b4 in `R/usr/bin/hachi`. **Likelihood:** fires only if hachi's dynamic WAN-ifname resolution returns nothing for the Ethernet connection. **Impact: LOW–MEDIUM** (missed firewall-rule repair for ppp131; spurious ppp111 rule inserts). **Detection:** after session up, `iptables -S TR181FrwlForward` — check the RELATED rule's `-i` is ppp131, not ppp111. **Mitigation:** none needed if primary config loader installs the rules; verify via U8 capture.

**P4-5. Editor vs activation mismatch — evidence FOR.** `wanRemoteNode_ETH_Edit.cgi` strings contain only the bare token `PPPoE` — **no** `PPPoEServiceName`, `MaxMTUSize`/`MaxMRUSize`, or `PPPAuthenticationProtocol` field names, whereas `broadband.cgi` references all of them (and per BROADBAND_CGI analysis maps `RN_ServiceName`→PPPoEServiceName etc.). So the per-connection ETH editor cannot be relied on to set PPP parameters; the broadband.cgi conversion path (or ccctest) must. **Likelihood: HIGH** that the ETH edit page lacks the fields (string-level). **Impact: MEDIUM** (wrong tool → parameters silently unset → defaults: no service name (which, per P4-1, ironically avoids the concatenation defect), MTU/MRU defaults unknown per U16).

**P4-6. IPv6 PD retargeting on mode switch — evidence FOR (config side-effect).** `linkdetection` strings include `LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.NDPPD` and `…IPv6PDWanConnection` object paths — it rewrites the IPv6 PD WAN pointer on mode switch (to the Ethernet **IP** object per prior analysis). **Likelihood: certain** on any linkdetection-driven switch. **Impact: LOW for this deployment** (ISP profile in the brief is IPv4 PPPoE; IPv6 is U15) — MEDIUM if IPv6 is later required: PD would point at the IP object, not the PPP object, until manually retargeted.

**P4-7. TR-069 auto-revert — mechanism present, behaviour UNKNOWN.** `R/usr/bin/ztr69` + `ztr69cmd` exist; `TR069_EventHandlerFunc` @0xcccc in libbeEvents; prior reports established linkdetection rewrites the ACS URL (to a test ACS) on its ETHER branch and the plan restores the production ACS. A live ACS could in principle push the GPON-era config back. **Likelihood: LOW–MEDIUM** (depends entirely on the operator ACS, not observable statically). **Impact: HIGH if it fires** (profile/DCS revert). **Detection:** post-deployment, re-read WANMode/DCS/profile after 24–48 h and after any TR-069 session in syslog. **Mitigation:** the plan's ACS preservation; consider it an operational watch item, not a code blocker.

**P4-8. Default-route conflict with a still-enabled GPON profile — mechanism evidence FOR, guarded.** Route install is gated by `isDefaultGw` (§9.3) and DCS selects a single default connection, so two simultaneous defaults are prevented *by the config machinery*, provided the GPON PPP connection is disabled / DCS points at ConnDev.3 PPP. **Likelihood: LOW** if the plan's disable+DCS steps are followed; **Impact: MEDIUM** (wrong egress) if both profiles end up enabled with DCS ambiguous. **Detection:** `ip route` after bring-up (U7/U8 captures).

**P4-9. Stale options-file accumulation — REFUTED for the normal path.** Each enable re-copies the template over `/etc/ppp/options_<IfName>` (`cp -rf`, §8.8) before fopen("a+"), so lines cannot accumulate across enables. Residual: if the `cp` itself fails (e.g. template deleted), "a+" silently appends onto the stale file → duplicates. **Likelihood: LOW. Impact: LOW** (pppd tolerates most duplicate options; last-wins for unit/linkname).

**P4-10. Unit-allocation collision — REFUTED by construction.** Unit is a pure function of the object IA (§8a); two distinct PPP objects cannot share an IA, and the factory config has exactly one PPP object. A collision would require a second PPP object with IA 1.3.1, which the RDM tree forbids. Residual runtime variant: a *stale* pppd still holding ppp131 when a new pppd launches with `unit 131` — pppd would fail to create the interface. Watchdog/restart templates in libCmd.so guard restarts by pidfile (`/bin/ls /var/run | grep ppp%s.pid || /bin/pppd …` @0xcaf08/@0xcaeb8 in rootfs libCmd.so). **Likelihood: LOW. Detection:** `/var/run/ppp131.pid` + `ps` before re-enable.

**P4-11. Kernel/driver dependency — evidence AGAINST a blocker.** All required modules are present in `R/lib/modules/5.10.138/`: `pppoe.ko`, `pppox.ko`, `ppp_generic.ko`, `ppp_async.ko`, `smuxdev.ko`, `ca-rtk.ko` (switch), `ca-phy-mdio-access.ko`, `ca-rtk-epon-drv.ko`; `bin/smuxctl` exists; `/etc/modules.d/pppoe` lists `pppoe`. (No `modules.dep` file exists in the dump, so load *order* is handled by init scripts/modules.d — not fully traced.) **Likelihood of a missing-driver blocker: LOW.**

**P4-12. Web UI validation limits — partially answered.** libpppoe's own service-name cap is 256 chars (`Service name too long (maximum allowed 256 chars)` in libpppoe.so); `3jglobal` is 8 chars — no plausible limit is approached. `X_5067F0_VLANID` schema MAX is 5000 (prior decode). MTU/MRU schema type words were not decoded this session (see UNKNOWN list). **Likelihood of a validation-limit blocker for the deployment values: LOW.**

**P4-13. Connection-device instance limits — not on the critical path.** WANPPPConnection max instances = 8 (prior schema decode). The WANConnectionDevice descriptor in the schema image contains an `0x08` word in the analogous position (raw bytes at decompressed image 0x36e74 region, **not** layout-decoded this session — treated as UNKNOWN-grade). Either way the plan *reuses* ConnDev.3 and adds at most one PPP child under it, so limits cannot bind. **Likelihood: LOW.**

### UNKNOWN — no sufficient static evidence either way (with what would detect each)
- **Switch port isolation / SMUX creation failure / `/proc` node absence** — `smuxdev.ko`, `smuxctl`, and the `/proc/ni`, `/proc/fc/ctrl`, `/proc/rtk_smuxdev` writers all exist, but whether the nodes appear and `smuxctl --if-create-name` succeeds for port 3 in ETHER mode is a kernel/runtime property. Detect: at Phase 3 boot, `ls /proc/ni/dev_port_mapping /proc/fc/ctrl/wan_port_mask /proc/rtk_smuxdev/`, syslog around eth_Init, `ip link show nas0_notag`.
- **ONT-side VLAN requirement** — no firmware evidence can settle what the Syrotech ONT/BSS expects on this path (U13). The factory config proves tagged profiles exist (VLAN 100, 660) for *other* connections, not for this one. Detect: Phase-4 fallback F2 (enable VLAN on the PPP object → `nas0_<vid>`) if untagged PADI gets no PADO.
- **NAT rule ordering** — templates append/insert into `NAT_POSTROUTING`/custom chains (object-driven rebuild on WAN-up); interaction order vs FullNAT/DMZ chains is a runtime iptables listing question (U8 capture covers it).
- **Fastpath bypass of ppp131** — §9.7. Detect: fc flow counters under load (U10).
- **RDM callbacks failing post-commit / config save failure modes** — the ccctest ADD commit-phase failure is another blocker's scope; for the *conversion* path, no static evidence of a save-failure mode was found in the binaries examined here, and none can be produced statically. Detect: read back the full ConnDev.3 PPP object + reboot persistence check.
- **PPPoE code unreachable via dispatcher** — evidence is against it (the identical create→config→launch chain serves the factory GPON PPP object, and `WANConnection_EventHandlerFunc` + `createWANPPPConnectionCfgFile` are connection-type-driven, not ConnDev-driven), but a per-instance dispatch quirk cannot be excluded statically. Grade: STRONGLY INFERRED reachable. Detect: syslog on first enable of the converted profile.
- **Startup scripts regenerating the WAN profile** — none found: grep of `R/etc/init.d`, `R/etc/rc.d`, `R/etc/scripts` for `linkdetection|WANConnectionDevice|DefaultConnectionService` = 0 hits. (linkdetection is a binary daemon, presumably spawned by the CCC init, and *it* can rewrite DCS/ACS on mode detection — that risk is P4-7/U-adjacent, and is a *runtime daemon behaviour*, not a startup script.) Grade: no evidence FOR; cannot prove a negative for all boot paths.
- **WANAccessType hidden dependency** — the literal `WANAccessType` does not appear in the factory PDM XML at all (grep = 0); whether some code path keys off an access-type field on WANDevice.1 for ConnDev.3 activation was not traced. Detect: if the converted profile never activates despite Enable=1, compare all WANDevice.1 fields between GPON-working and Ethernet states.
- **Factory vs live default mismatch** — one concrete instance found and corrected in §8.8 (template files populated in this dump vs "0 bytes" in a prior report); whether the *live* unit's `/etc/ppp/default_options` matches this dump is U3's runtime `cat`.
- **MTU/MRU schema type/range** (Web-validation completeness) — the schema type words for MaxMRUSize/X_5067F0_MaxMTUSize were not decoded (prior session also left this open); broadband.cgi uses its own typed tables, so the Web path is insulated. ccctest SETs with wrong type tokens remain a plausible transaction poison (other blocker's scope).

---

## Corrections to prior reports surfaced by this pass
1. `ETHERNET_PPPOE_LIFECYCLE.md` §7/§9: "default_options is 0 bytes / contents look swapped" — **DISPROVEN for this repo's dump** (§8.8): both templates populated, dynamic path uses `default_options` (90 B, contains `plugin pppoe`, `usepeerdns`). "rootfs lib/pppd/2.4.7/rp-pppoe.so" — **does not exist**; plugin is the linked `libpppoe.so` (§8.9).
2. `ETHERNET_PPPOE_LIFECYCLE.md` on `createWANPPPConnectionCfgFile`: "not the options writer… exact product UNKNOWN (U6)" — superseded by §8.7 (it orchestrates and calls the options writer; the libcccbe wrapper it also calls is a no-op stub).
3. Prior reports' artifact table hashes `libCmd.so` as `fa8ecd…` — the repo's rootfs libCmd.so is `ef06db88…` (different build); its templates were re-read from the actual file for this pass.
4. `ROUTING_NAT_FIREWALL_ANALYSIS.md` MSS attribution stands (global rule, not Event 206), now with function-level decode (§9.4). Its "FORWARD RELATED pair not found" gap is now explained: the pair lives in **hachi's watchdog** over the TR181 chains, not in libbeEvents (§9.4).
