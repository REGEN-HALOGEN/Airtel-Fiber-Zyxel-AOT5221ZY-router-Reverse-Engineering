# Concrete Implementation Check and Rollback — LAN4 Ethernet WAN + PPPoE

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT. ISP: PPPoE, service name `3jglobal`, MTU/MRU 1480, `AUTO_AUTH`, VLAN unresolved (untagged is the working hypothesis; the existing TP-Link connects through the same ONT with no VLAN configured).
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Follow-up mission** — supersedes the *procedural* parts of IMPLEMENTATION_PLAN.md / ROLLBACK_PLAN.md where they conflict (differences are recorded in those files and in §11/§12 here). Prior reports are preserved; this document is the single operational reference.
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted in either mission. No PPPoE credentials appear anywhere — `[OPERATOR ENTERS]` placeholders only. Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = from prior runtime logs/observations recorded in the repo, not re-measured · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools:** Capstone 5.0.7 + pyelftools + LIEF (venv `/tmp/revenv`); host objdump is x86-only, all AArch64 disassembly is Capstone with PLT resolved from `.rela.plt`. This mission additionally decoded `ccc_das` (the DAS backend, barely used by the prior mission) and `libwebutil.so`.
- **Companion evidence files (this mission, in `research/`):** `_work_b124.md` (Blockers 1/2/4), `_work_b3567.md` (Blockers 3/5/6/7), `_work_b8910.md` (Blockers 8/9/10 + Part-4 hunt). Every address cited below is traced there or in the first mission's reports.

---

## 1. Executive verdict

**The firmware statically supports the target topology — with one critical firmware defect standing in the way of the ISP profile as specified.**

- The complete native path exists and is proven link-by-link (§2): Ethernet WAN hardware mapping (port 3 / mask 0x08), boot-time `nas0_notag` creation, a vendor PPPoE profile mechanism under `WANConnectionDevice.3`, generic PPP config generation producing `ppp131`, generic Event-206 routing/NAT/DNS handling, and LAN3/Wi-Fi preservation by construction.
- **Preferred route (one route, not a combination): the vendor Web UI conversion** — `broadband.cgi`'s IP→PPP type-conversion of the factory `Eth_Internet` profile (Approach A, whose mechanism is Approach C; §5). It is the only creation path whose full transaction sequence is proven. The direct-RDM ADD (Approach B) is **rejected as a primary path**: the exact commit-phase rejector of the earlier failed ADD is still unproven (Blocker 2), so no "corrected ADD" can be honestly offered. `linkdetection` activation (Approach D) is **rejected**: it creates only an IP profile, points the default route at that IP object, and clobbers the ACS URL.
- **CRITICAL BLOCKER B-NEW-1 (new this mission, CONFIRMED STATIC):** `beConfigWANByPPPoE` writes the PPPoE service name with a format string that has **no trailing newline**, immediately before the `linkname` line. With service name `3jglobal` configured, the generated `/etc/ppp/options_nas0_notag` deterministically contains the merged line `pppoe_srv_name 3jgloballinkname ppp131`. pppd tokenises on whitespace: the negotiated service name becomes `3jgloballinkname` and the stray token `ppp131` is expected to trigger pppd's `unrecognized option` failure (that error string is present in this pppd; fatal in upstream 2.4.7 semantics — runtime severity STRONGLY INFERRED). There is **no configuration-side mitigation**: the file is regenerated on every enable. This defect is invisible on factory GPON (service name never set there) and bites exactly this deployment.
- **Gate U12 (UNKNOWN, operator-observable in seconds):** zero `.html` files exist in the repo, so whether the shipped Ethernet edit page actually exposes the PPPoE/encapsulation option that triggers the proven conversion branch cannot be proven statically. If it does not, the preferred route is inoperable and no proven fallback exists yet.
- **Readiness: NOT READY** (§13) — solely because of B-NEW-1 and U12. Every other blocker from the brief is resolved below. The procedure in §4 is complete and exact for all steps that are proven; the steps gated by B-NEW-1/U12 are marked `NOT PROVEN — DO NOT EXECUTE` beyond their verification gate. Do not claim 100% success before physical validation.
- **Still requiring runtime confirmation even after B-NEW-1/U12 clear:** live PPPoE discovery/auth against the Syrotech ONT + ISP BRAS, VLAN reality (U13), Event-206 default-route behaviour for this profile (U7), exact FORWARD rule set (U8), peer-DNS propagation (U9), fastpath offload (U10), and pppd's actual reaction to the merged options line.

## 2. Confirmed technical architecture

Complete call chain, Ethernet WAN → PPPoE → routing/NAT. All entries CONFIRMED STATIC unless labelled.

| Stage | Mechanism | Binary / address | Object / file |
|---|---|---|---|
| Boot entry | rcS S10 → S20 netifd → S99 zz_rc4mstcinit → rc4_mstc.d S06 `ccc_init` (`ccc_mr/das/be`) | rootfs init scripts | — |
| Boot gate | `OID_…_WANDevice_i_ConfigLoaderFunc_Boot` spawns `/usr/sbin/linkdetection &`, then mode dispatch: Eth Enable && `WANMode=="ETHER"` (strcmp @0x50ec8) → eth init; GPON likewise | libbemodules.so @0x50d08 | `WANSwitch.WANMode`, `WANEthernetInterfaceConfig.Enable` (OID 0xca), `X_5067F0_GponInterafceConfig.Enable` (OID 0xc7) |
| HW mapping | `rtk_wan_port_mapping(0, if)`: `echo 3 <if> > /proc/ni/dev_port_mapping`, mask 0x08 → `/proc/fc/ctrl/wan_port_mask`. GPON: port 7 / 0x80. LAN3 port 2 never referenced | libcccbe.so @0x37c84 | `/proc/ni/dev_port_mapping`, `/proc/fc/ctrl/wan_port_mask` |
| Eth init | `libcccBeWan_eth_Init` = EthPhyEnable(1) + smuxctl rsmux + hw_vlan_filter + port mapping. Does **not** create nas0_notag | libcccbe.so @0x38074 | — |
| L2/L3 interface | `createLayer3Interface`: smuxctl `--if-create-name` / `--tags 0` → `nas0`, `nas0_notag` (untagged) or `nas0_<vid>` (VLAN byte set). Runs at boot and on the ObjectChanged path (gated by link-is-up check @0x4df00) | libcccbe.so @0x35348 | `nas0_notag` |
| Profile creation (vendor) | broadband.cgi conversion: delete WANIPConnection (OID 0xcd) + create WANPPPConnection (OID 0xe3) in ONE transaction (§3 of `_work_b124.md`) | broadband.cgi cgiMain @0x403390 | `…WANConnectionDevice.3.WANPPPConnection.1` |
| Requested link type | `libcccBeWan_getWANDeviceObjectRequestedLinkType` @0x34334 (libcccbe) / `getWANDeviceObjectRequestedLinkType` @0xbfc0 (libwebutil): Gpon Enable≠0 → **1 (GPON)**; else Eth Enable≠0 → **0 (Ethernet)**; else 2. WANDevice-global, connection index never read. (Resolves U14/C-11; prior "1 = PPP" reading DISPROVEN) | libcccbe.so @0x34334 | OIDs 0xc7 / 0xca |
| PPP unit / name | `libcccBeWan_getPPPPdUnitNum_wrapper`: `snprintf("%d%d%d", wanDev, connDev, pppInst)`; `setWanIpPppInterfaceName`: `snprintf("ppp%d", unit)` → **1.3.1 → `ppp131`** (GPON 1.1.1 → `ppp111`). No `ppp111`/`ppp131` literal exists in any binary | libcccbe.so @0x38264 / @0x346d0 | `ppp131` |
| Config generation | `createWANPPPConnectionCfgFile` (orchestrator) → `beConfigWANByPPPoE`: `cp -rf /etc/ppp/default_options` (or `_options_static`) then appends `unit 131`, `user`, `password`, `logfile`, `mru %d` [obj+0x18], `mtu %d` [obj+0x1a], lcp-echo, auth refuse-lines (AUTO_AUTH → **none**), persist/passive (AlwaysOn), `pppoe_srv_name %s` **[no `\n` — B-NEW-1]**, `linkname ppp131` | libbemodules.so @0x6a7c0 / @0x664a8; libcccbe wrapper @0x373a4 is a no-op stub | `/etc/ppp/options_nas0_notag`, template has `plugin pppoe`, `usepeerdns` |
| PPP launch | `beWanEnablePPPv4Client` → `libccc_executePPPv4Client`: `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`. pppd is DT_NEEDED-linked to `libpppoe.so` (`pppoe_plugin_init`); no rp-pppoe.so exists or is needed | libbemodules.so @0x66ee4; libcccbe.so @0x348f4 | pppd + libpppoe.so |
| Session-up events | `/etc/ppp/ip-up` (verbatim): writes `EVENTNOTIFY 206 string $REALNAME;` via a ccctest script → ccc_be Event 206; ip-down → 207; ipv6-up/down → 213/214 | rootfs `etc/ppp/ip-up` sha256 `3fcaa848…` | Event 206/207 |
| Route | `L3Forwarding_Connection_EventHandlerFunc` @0xb370 → `layer3Forwarding_wanConnectionUp` @0x56d10: `route add default dev %s` / `gw %s dev %s`, gated by isDefaultGw / DefaultConnectionService. IPv6 twin family `ip -6 ro add/del` | libbeEvents.so @0xb370; libbemodules.so @0x56d10 | `Layer3Forwarding.DefaultConnectionService` (OID 0x80); IPv6 twin `X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` |
| DCS flip hazard | `updateDefaultRouteByLinkType` @0x6f2d8 rewrites live DCS from per-mode keys (`DefaultConnectionService_GPON` / `_ETHER`, OID 0x83 family) on link-type changes. Factory `_ETHER` key = `.3.WANIPConnection.1` — a flip event can silently repoint the default route at the (deleted) IP object unless the keys are managed (§4 S7, §7 F-6) | libbemodules.so @0x6f2d8 | per-mode DCS keys |
| NAT | Templates only in libbemodules, all interface-parameterised: `iptables -t nat -A NAT_POSTROUTING -o %s -j MASQUERADE` (+ `-s %s/24`, SNAT variants). Zero MASQUERADE strings in libbeEvents/libcccbe | libbemodules.so | NAT_POSTROUTING |
| MSS | `addTCPMSSDefaultRule` @0x66f18: global `iptables/ip6tables -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu`. No literal 1440; MTU 1480 ⇒ effective MSS 1440 | libbemodules.so @0x66f18 | FORWARD |
| DNS | `usepeerdns` → pppd writes `/etc/ppp/resolv_%s.conf` → `configDNSServers` @0x11cbc handles WANIP and WANPPP default-WAN branches | libbemodules.so @0x11cbc | resolv/dnsmasq (runtime propagation U9) |
| Firewall watchdog caveat | `hachi` @0x404648 resolves the WAN ifname dynamically; only if resolution returns nothing does it fall back to literal `ppp111` for TR181FrwlInput/Forward rule checks/repair. With ppp131 up, verify the rules reference ppp131 (§6) | rootfs `usr/bin/hachi` | TR181Frwl chains |
| Teardown | `beWanDisableClient` @0x6722c: `kill -15 <pppd pid> && sleep 2 && kill -9 …`, removes pidfile. `deleteLayre3Interface` @0x35f60: `smuxctl --if-delete nas0_notag`. ip-down Event 207 removes route/NAT state. **Options file is NOT deleted** (stale but inert — regenerated by copy-overwrite each enable; P4-9 refuted as a hazard) | libbemodules.so @0x6722c; libcccbe.so @0x35f60 | — |

**GPON-specific-assumption sweep (Blocker 9):** full rootfs + DUMPFILES string sweep. `ppp131`: **zero hits anywhere**. `ppp111`: only (i) PDM XML stored GPON object *data*, (ii) the hachi fallback above. `nas0_100` in libcccbe @0x44be0: benign PCAP-monitor default when an interface pointer is NULL (not on the WAN path). `WANConnectionDevice.1` literals: ccc_be init writing the per-mode DCS slots (by design); libCmd.so GPON-prefixed CLI templates (off the proven path, flagged); linkdetection (GPON-only by design). **Conclusion: every mechanism on the Ethernet path is generic — CONFIRMED STATIC. ppp131 is handled by the same code as ppp111.**

## 3. Pre-implementation checklist

Every item must pass **before** any configuration change. Items marked [READ] are observations (UI/CCC read or physical look) — no writes.

| # | Check | Expected (Phase-0 baseline) | Evidence / source |
|---|---|---|---|
| P-1 | Config backup exists and is restorable via UI backup/restore | A fresh export taken now, stored off-router; repo already holds `ether-backup.lz` (Phase-0, timestamp 202406031227.01) as an older fallback | `DUMPFILES/ether-backup.lz` decode = `analysis/ether_backup_decoded.txt` |
| P-2 | GPON profile integrity [READ] | `…WANConnectionDevice.1.WANPPPConnection.1` present, `Enable=1`, `Name=Internet`, `X_5067F0_InterfaceName=ppp111`, `X_5067F0_VLANID=100`, credentials present [REDACTED — presence only] | Factory PDM subtree (CONFIRMED STATIC); live presence CONFIRMED FROM EXISTING RUNTIME EVIDENCE |
| P-3 | Ethernet profile state [READ] | `…WANConnectionDevice.3.WANIPConnection.1` (`Eth_Internet`, IfName `nas0_notag`) present; **note:** in the Phase-0 live baseline its `Enable` element is *absent* and `DefaultGateway/SubnetMask/ExternalIPAddress=0.0.0.0` were added — linkdetection Tx-A fingerprints (STRONGLY INFERRED: linkdetection already ran once on this unit) | ether-backup diff §5.4 of `_work_b3567.md` |
| P-4 | Object counts [READ] | Under .3: `WANPPPConnectionNumberOfEntries=0`, `WANIPConnectionNumberOfEntries=1`. Under .1: PPP count 1 | Prior runtime evidence + factory PDM |
| P-5 | Default route baseline [READ] | `Layer3Forwarding.DefaultConnectionService` = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1`; IPv6 twin (`X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService`) same; per-mode `_GPON` keys = .1 PPP; `_ETHER` keys = .3 **IP** (factory — will need management, §4 S7) | Factory PDM (CONFIRMED STATIC) |
| P-6 | ACS baseline [READ] | `InternetGatewayDevice.ManagementServer.URL` = `http://tms.airtelbroadband.in:8103` (**no trailing slash — byte-exact**). Present in factory PDM, Phase-0 baseline and ROM decode; `testacs` appears in zero configs | `_work_b3567.md` §6 (CONFIRMED STATIC) |
| P-7 | WAN mode baseline [READ] | `WANSwitch.WANMode`: absent from both PDM XMLs (schema default `"GPON"`); prior runtime evidence recorded `WANMode=ETHER`, `WanAutoDetect=0`, `WANAccessType=Ethernet` at some point during earlier experiments — **record the actual current values; do not assume** | Prior runtime evidence (not current) |
| P-8 | LAN3 bridge baseline [READ] | br0/FilterInterface set includes `LANEthernetInterfaceConfig.1–.4` (LAN3 = .3 of the LAN set) and `WLANConfiguration.1–.8`; LAN3 client + Wi-Fi client associated and working | Factory XML (CONFIRMED STATIC) |
| P-9 | LAN baseline [READ] | LAN 192.168.1.1/24, DHCP pool .2–.254 under LANHostConfigManagement only; no WAN-mode coupling exists in code | `_work_b8910.md` Blocker 10 |
| P-10 | Rollback prerequisites | §8 rollback path for the chosen creation world (conversion vs ADD) identified **before** creating anything; `ether-backup.lz` + fresh P-1 export both present; preserved scripts `ether-rollback.ccc`/`rollback.ccc` are **not** to be executed as-is (defects: no SAVE in ether-rollback.ccc; neither deletes a .3 PPP nor restores ACS — §8) | `_work_b124.md` Blocker 4; `_work_b3567.md` §5 |
| P-11 | ONT/ISP baseline | TP-Link still connects through the same Syrotech ONT port (isolates ONT/BRAS from AOT config later); ONT Ethernet will be moved to AOT **LAN4** only at §4 S9 | Brief (runtime evidence) |
| P-12 | B-NEW-1 acknowledgement | Operator has read §1 B-NEW-1: if a service name is configured, the generated options file **will** contain the merged line; §4 S10 is a hard stop gate, not a formality | This document |

## 4. Exact implementation procedure

Order is load-bearing: **profile first, default route second, WAN mode third, reboot fourth** — the inverse of the earlier plan's risk (no GPON disable before a valid Ethernet profile exists; no DCS change before the PPP object is committed). GPON profile is never deleted in any step. Credentials are entered by the operator in the UI password fields at execution time; they appear nowhere in this procedure.

### S1 — Backup and baseline record
- **Objective:** restorable Phase-0-equivalent state + written baseline.
- **Action:** Web UI config export; record P-2…P-8 values verbatim (esp. ACS URL byte-exact, both DCS pointers, per-mode DCS keys, .3 counts).
- **Evidence:** ether-backup proves the export format/mechanism exists on this unit. **Expected:** export file saved off-router.
- **Gate:** export exists and baseline sheet is complete. **Failure:** stop — no rollback media, no deployment. **Reboot:** no. **Rollback action:** n/a.

### S2 — Precondition verification (read-only)
- **Objective:** confirm §3 P-2…P-9 all hold on the live unit *now* (prior observations are not current measurements).
- **Gate:** any mismatch → stop and reconcile against §9 matrix before proceeding. **Reboot:** no.

### S3 — Path gate (U12 observation)
- **Objective:** decide the creation path by direct observation (§5 tree).
- **Action [READ]:** open the Web UI Ethernet WAN edit page for `Eth_Internet`. Does it expose a connection-type/encapsulation control offering PPPoE?
- **Evidence:** the conversion branch in broadband.cgi is CONFIRMED STATIC (Blocker 1); the shipped HTML's exposure of its trigger fields is UNKNOWN (zero .html in repo).
- **Gate:** option present → S4. Option absent → **STOP. Path B is NOT PROVEN — DO NOT EXECUTE (§5).** Record the observation; it closes U12 for this unit.

### S4 — Vendor UI conversion of Eth_Internet to PPPoE (preferred path)
- **Objective:** create `…WANConnectionDevice.3.WANPPPConnection.1` via the vendor conversion.
- **Exact mechanism (CONFIRMED STATIC, Blocker 1):** on the ETH edit page, set connection type to PPPoE and save. The form posts to `/cgi-bin/broadband.cgi` with the save flag for the Ethernet form (`RN_WANETHformSaveFlag`=="1"), encap flag `RN_EncapFlag`=="1", mode flag `RN_ModeFlag`=="0", and `wanIA` naming the existing connection. `cgiMain` @0x403390 then queues **one** transaction: SelId(OID 0xcd, wanIA) + `cmsgRequestSetIndexedObj(req,0)` @0x403e34 (delete the IP object) → `rdmGetAvaliableIAByOID(rdm, 0xe3, parentIA)` @0x403e8c (lowest free instance) + SelId(0xe3) + `SetIndexedObj(req,1)` @0x403f10 (create PPP) → all PPP parameter SETs → PortTriggering re-adds → NAT tail → `cmsgRequestSave` @0x4066d4 → single `cmsgSendRecv(60000)` @0x4068b8.
- **Values to enter:** Username `[OPERATOR ENTERS]` (string); Password `[OPERATOR ENTERS]` (string — note the masked-sentinel trap: a field left as `****************` means *unchanged*); `PPPoEServiceName` = `3jglobal` (string) — **see S10 hard gate: this value triggers B-NEW-1 at config-generation time**; `X_5067F0_PPPAuthenticationProtocol` = `AUTO_AUTH` (string); `MaxMRUSize` = 1480; `X_5067F0_MaxMTUSize` = 1480 (numeric types per schema, PPP_PARAMETER_VALIDATION.md); `ConnectionType` = `IP_Routed` (set by CGI tail); `NATEnabled` = 1 via the NAT control (`RN_SelNAT` ≠ "Disabled"); `X_5067F0_Enable_VLANID` = 0 (untagged hypothesis); `Enable` = 1. If the page offers a "default WAN" control, set it (it drives `RN_Default_WAN_H`=="1", the CGI's DCS block @0x404738).
- **Why this path:** it is the vendor's only creation mechanism; it deletes the sibling IP object *first, in the same transaction* — the exact precondition the DAS apply phase appears to require (Blocker 2's leading hypothesis for the ccctest failure is a PPP pre-object coexisting with the sibling IP .1).
- **Destructiveness (explicit):** the `.3.WANIPConnection.1` profile is **deleted** by this transaction (not disabled). It is recreatable by the verified reverse conversion (§8 R-A). The GPON profile under .1 is not touched (different ConnDev; conversion addresses only the wanIA target).
- **Failure behaviour (CONFIRMED STATIC):** the CGI checks **nothing** — all builder return values are ignored, the SendRecv reply is only freed, `cmsgGetExecResult` is called 0 times in cgiMain. A backend NACK is **invisible in the UI**. The transaction is atomic at the DAS apply phase (changelist NACK ⇒ pre-objects discarded — STRONGLY INFERRED + corroborated by the ccctest failure evidence); whether BE side effects / flash persistence can partially survive a NACK is UNKNOWN. **Therefore S5 read-back is mandatory, not optional.**
- **Expected result:** UI returns normally (this proves nothing by itself). **Reboot:** no (the CGI requests none; no reboot/system import is called). **Rollback action:** §8 R-A (conversion-back) or R-C (backup restore).

### S5 — Conversion commit verification (read-only, mandatory)
- **Objective:** prove S4 committed — the UI cannot tell you.
- **Checks [READ]:** under .3: `WANPPPConnectionNumberOfEntries` = **1** and `WANIPConnectionNumberOfEntries` = **0**; `.3.WANPPPConnection.1` reads back with the S4 values (Name, service name, MTU/MRU 1480, AUTO_AUTH, NATEnabled=1, VLAN disabled, Enable=1); under .1: GPON PPP still present, values unchanged.
- **Gate:** counts/values wrong → the transaction NACKed or partially applied: **stop**, go to §7 F-1. Do not re-submit blindly (a second conversion attempt against a now-missing IP profile has no source object — Blocker 1 Q19: total dependence on the existing IP profile).

### S6 — GPON profile park (do not delete)
- **Objective:** safe coexistence shape (Blocker 3, CONFIRMED STATIC): `.1` PPP present but `Enable=0`; `.3` PPP enabled. Both-enabled is a vendor-never-shipped state over shared `nas0` — runtime interaction UNKNOWN.
- **Action:** set `…WANConnectionDevice.1.WANPPPConnection.1.Enable` = 0 (boolean) in its own transaction/UI edit. **Nothing else under .1 changes.** Five factory references point at this object (DCS v4+v6, both `_GPON` keys, IPv6PD interface, firewall DEFAULTWAN bindings) — deletion would dangle all five and destroy the only GPON rollback target.
- **Reboot:** no. **Rollback action:** set Enable back to 1 (§8).

### S7 — Default route pointers (after PPP object is committed — never before)
- **Objective:** `Layer3Forwarding.DefaultConnectionService` (string) = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`; IPv6 twin `X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` = same (IPv6 relevance is U15-conditional; setting it keeps v4/v6 coherent).
- **Also required (new this mission):** the per-mode key `DefaultConnectionService_ETHER` (and its IPv6 sibling) must be set to the **PPP** object, not left at the factory `.3.WANIPConnection.1` — `updateDefaultRouteByLinkType` @0x6f2d8 rewrites live DCS from these keys on any link-type-flip event. If S4's default-WAN control already set them (CGI writes the per-mode markers on OID 0x83), verify by read-back; correct only what's wrong.
- **Method:** UI default-WAN control if it demonstrably set all four values at S5/S7 read-back; otherwise a dedicated RDM SET transaction (SET of an existing scalar parameter is the ordinary ccctest/UI operation class used throughout the prior runtime work — STRONGLY INFERRED as a procedure, mechanism CONFIRMED STATIC).
- **Gate:** all four pointers read back as the .3 PPP object. **Reboot:** no. **Rollback action:** §8 R-DCS.

### S8 — WAN mode ETHER via the UI RESTART branch (not linkdetection)
- **Objective:** `WANSwitch.WANMode` = `ETHER` with the Enable pair coherent: `WANEthernetInterfaceConfig.Enable` = 1, `X_5067F0_GponInterafceConfig.Enable` = 0 (exact vendor spelling — the correctly-spelled name does not exist). Gpon Enable must be 0: requested-link-type resolution gives GPON unconditional priority while it is non-zero (Blocker 3).
- **Mechanism (CONFIRMED STATIC):** broadband.cgi's RESTART branch (`RestartBtn`=="RESTART"): SelId(0xc7)/SelId(0xca) Enable SETs + SelId(0x4d) WANMode SET + Save + the common SendRecv. **This path never touches ManagementServer** (zero ACS strings in broadband.cgi) — unlike linkdetection's ETHER branch, which writes `ManagementServer.URL` = `http://testacs.airtelbroadband.in:8103/` and `X_5067F0_OverIPv6` = 1. **Do not invoke linkdetection's switch and do not rely on auto-detect for this transition.**
- **Reboot (CONFIRMED STATIC, Blocker 7):** a WANMode write through the BE path forces a reboot itself (`doWanModeChange` @0x36d3c → `WAN_MODE_CHANGE_REBOOT` → `cccBeDoSystem("reboot")`). A write through a no-BE (SET_NO_BE) channel does **not** — manual reboot is then mandatory. Either way, plan for exactly one reboot here; eth/gpon init each have exactly one call site, the Boot callback @0x50d08.
- **Post-reboot ACS check [READ]:** `ManagementServer.URL` must still read `http://tms.airtelbroadband.in:8103`. If it reads the testacs value (something ran linkdetection's switch), restore the Phase-0 value in its own transaction (§8 R-ACS) before proceeding.

### S9 — Physical connection + boot verification
- **Action:** move the Syrotech ONT Ethernet cable to **LAN4**. (Reboot already occurred at S8; if the mode write used a no-BE channel, reboot now.)
- **Checks [READ]:** `/proc/ni/dev_port_mapping` shows port 3 → nas0; `/proc/fc/ctrl/wan_port_mask` reads 8 (0x08); `nas0` and `nas0_notag` exist. **Gate:** mask still 128 / mapping on port 7 → the Boot gate did not take the ETHER branch: re-check S8 values (WANMode string, Eth Enable byte) — do not proceed to S10. LAN3/Wi-Fi must still be up at this point (failed Ethernet startup leaves LAN working — STRONGLY INFERRED, Blocker 7); if LAN is down, §7 F-7.

### S10 — PPP enable and the B-NEW-1 hard gate
- **Objective:** bring up the PPP client and inspect the generated configuration **before** judging session success.
- **Action:** ensure `.3.WANPPPConnection.1.Enable` = 1. On enable, the backend generates `/etc/ppp/options_nas0_notag` and launches pppd (§2).
- **HARD GATE [READ]:** read the generated file. Expected lines include `unit 131`, `mru 1480`, `mtu 1480`, `linkname ppp131`, and — because a service name is configured — the merged line `pppoe_srv_name 3jgloballinkname ppp131` (B-NEW-1, deterministic).
  - **If the merged line is present (expected): STOP the session attempt here.** The remaining session steps are **NOT PROVEN — DO NOT EXECUTE** as a production configuration. The operator's options at this point are exactly two, both outside the proven procedure: (a) roll back (§8) and await a firmware-side fix or new evidence; (b) as a *diagnostic experiment only*, clear `PPPoEServiceName` to empty (the defect branch is then skipped and the file is clean — CONFIRMED STATIC) and observe whether the BRAS accepts an empty service name (HYPOTHESIS — many BRAS accept "any service"; this ISP's behaviour is UNKNOWN, U13-adjacent). A diagnostic success would flip this document's verdict (§13) only when recorded as runtime evidence.
  - If the merged line is somehow absent (different firmware build than the dumped binaries), proceed to S11 and record the file contents as evidence.
- **Reboot:** no. **Rollback action:** §8 (the profile can be parked with Enable=0 at any point; pppd teardown on disable is `beWanDisableClient`, §2).

### S11 — Session verification (verification only; full list in §6)
- PPPoE discovery/auth in `/tmp/pppd-info.tmp` + syslog (PADI→PADR, AUTO_AUTH ⇒ PAP or CHAP as offered); `ppp131` exists with ISP address; default route via ppp131; peer DNS present; NAT MASQUERADE `-o ppp131`. Any failure → §7.

### S12 — Routing / NAT / firewall verification (§6 table)
### S13 — LAN3 and Wi-Fi regression (§6 table)
### S14 — Hardening (only after S11–S13 pass)
- Set `WANSwitch.WanAutoDetect` = 0 (boolean) so linkdetection cannot flip the unit back or clobber ACS on a transient GPON-side signal. Record that this disables automatic GPON fall-back; rollback restores the Phase-0 value 1 (§9 — note the deliberate factory-vs-script discrepancy documented there). Re-verify ACS URL one final time. Export the working config as a new, distinctly-labelled known-good backup.

## 5. Deployment decision tree and approach comparison (Part 5)

### 5.1 Comparison of approaches

| Criterion | A — Vendor Web UI (broadband.cgi) | B — Minimal RDM creation (ccctest ADD) | C — Existing IP profile conversion | D — Native WAN activation routine (linkdetection) | E — Other native mechanisms found |
|---|---|---|---|---|---|
| Firmware support | CONFIRMED STATIC — cgiMain @0x403390 is the shipped mutation path | Engine support CONFIRMED STATIC; end-to-end commit **unproven** (Blocker 2) | CONFIRMED STATIC — it *is* A's mechanism (see below) | CONFIRMED STATIC for mode switching only; **cannot create PPP** | Backup/restore (config import) CONFIRMED as a mechanism class; TR-069 push — out of operator control |
| Exact object paths | Creates `…CD.3.WANPPPConnection.1` via numeric SelId(OID 0xe3, IA from wanIA) | Same target path, dotted-name form | Same as A | Touches CD.3 **IP** object, DCS, WANMode, ACS | Whole-config only; no per-object creation |
| Side effects | Silent on failure (no result check); PortTriggering preserved (saved + re-added); DCS only if default-WAN flag submitted | Unknown commit behaviour; prior attempt rolled back | Identical to A (same code) | **ACS URL → testacs**, OverIPv6=1, DCS → IP object, disables CD.2 VoIP profile Enable, sets .1/.3 enables, WanAutoDetect handling | Restore overwrites *everything* incl. unrelated settings |
| Destructiveness | Deletes the .3 IP profile (in-transaction, recreatable via reverse conversion) | Non-destructive to .3 IP (coexistence) — its one advantage | Same as A | Modifies profiles + ACS; creates nothing needed | Total (by design) |
| Reversibility | Conversion-back PPP→IP verified in-binary (@0x403f70) | DELETE audited (§8 R-B) — execution proven, sweep timing UNKNOWN | Same as A | GPON branch restores mode/DCS/production ACS *if* it runs (autodetect-gated) | Backup restore is the rollback floor |
| LAN3 risk | None found (no bridge/port-2 code) | None found | None found | None found for LAN3; ACS/VoIP side effects instead | None specific |
| ACS risk | **None** — broadband.cgi never touches ManagementServer | None (ccctest writes only what's scripted) | None | **HIGH** — testacs clobber is by design | None |
| Required reboot | Only for the mode switch (S8), not for creation | Same | Same as A | Same (mode change forces reboot via BE path) | Reboot after restore |
| Evidence quality | Full transaction reconstructed instruction-by-instruction | Parser + DAS chain reconstructed; the one failing link (apply-phase callback) unobserved | Same as A | Full branch disassembly, both directions | Mechanism existence only |
| Unresolved runtime deps | U12 (HTML exposure), B-NEW-1 at enable time | The unproven rejector itself | Same as A | ACS restore depends on daemon running its GPON switch | None |

**A ≡ C, stated plainly:** the brief lists them separately, but the binary evidence shows there is exactly one conversion mechanism and the Web UI is its only caller. "Approach A" and "Approach C" are the same firmware path viewed from the interface and from the mechanism. They are selected **once**, below — this is not a combination of two methods.

### 5.2 Preferred strategy

**SELECTED: Approach A/C — vendor Web UI conversion of `Eth_Internet`, followed by the UI RESTART-branch mode switch (S8), with §4's read-back gates.** Reasons: (1) it is the only creation path whose complete SEL/ADD/SET/SAVE/SEND sequence is proven; (2) it satisfies the DAS apply phase's apparent precondition (sibling IP deleted first, same transaction) that the failed ccctest ADD did not; (3) zero ACS side effects; (4) its rollback (conversion-back) is verified in the same binary. **Rejected:** B as a primary path (Blocker 2 cause unproven — §5.3), D for activation (creates the wrong object type, clobbers ACS, disables VoIP), E for creation (blunt whole-config tool; retained as rollback floor only). **Do not combine:** no ADD before/after a conversion (would create a duplicate/coexisting profile the plan does not call for), no linkdetection switch on top of the UI switch.

### 5.3 Approach B status (Blocker 2, full verdict)

Chain fully reconstructed this mission: ccctest ADD (@0x402ca8) only *queues* Sel + `cmsgRequestSetIndexedObj(req,1)` into a local buffer — libcmsg builders perform **zero validation**, so the parser's per-action "ADD …: success" (reply printer @0x4017dc, bit 0x40000000 of the action word) means only "executed in DAS", while the header verdict (bits 30/31/25) is printed independently — "ADD success + transaction fail" is one consistent observation, not a paradox. New trace: the failed `.1` spelling resolves via `cccRdmGetObjListByName` (librdm @0x12324) to (OID 0xe3, IA {1,3,1}) and is created in `cccDasHandleSetIndexObject` (ccc_das @0x412810) via `cccRdmAddObjectWithAssignIA`; the no-`.1` spelling takes the class path (OID 0xf1) via `cccRdmAddIndexChildObject` @0x134a0. **Both primitives pass every static gate** (VerifyIAValue @0x11e48, maxima, empty child list). The NACK is issued in `cccDasHandleApply` (ccc_das): it walks the changelist, dispatches per-class callbacks (table @0x4162a8) plus BE linkage (`cccDasLianDong`), and on failure sets header bits 25+30, logs `CCC_MSG_VALIDATE_FAIL`, cleans up, returns −1. **Exact rejecting callback/reason: UNKNOWN** — the original failed script, its full stdout, and the device syslog from that SEND are not in the repo. Leading HYPOTHESIS: a sibling changelist entry failed apply — top candidate being the PPP pre-object coexisting with the sibling IP `.1` that the vendor conversion deletes first; other candidates: a mistyped bundled SET, a DCS SET referencing the uncommitted object, a bundled SEL. DISPROVEN causes: trailing `.1`, schema/parent/max/already-exists, missing SAVE, parser abort. (The older audits' "validation error code 0x00000002" appears in **no artifact** — uncorroborated; do not quote it.) **Consequence:** no corrected ADD is offered as a fix. A minimal ADD-alone transaction remains legitimate **only as a diagnostic** (its NACK/success plus syslog would close this blocker), never as a deployment step in §4.

### 5.4 Decision tree

```
S3: Does the shipped ETH edit page expose PPPoE (connection-type/encap)?
 ├─ YES → Approach A/C: S4 conversion → S5 gate → S6 park → S7 DCS → S8 mode → S9 → S10 gate
 │         ├─ S10 merged-line present (expected) → STOP (B-NEW-1). Roll back (§8) or
 │         │   operator-elected empty-service-name DIAGNOSTIC (not a deployment step).
 │         └─ S10 clean → S11–S14.
 └─ NO  → STOP. No proven creation path remains (B unproven, D cannot create PPP).
          Record U12 answer; mission re-opens on new evidence (e.g. syslog from a
          diagnostic ADD-alone transaction, or a firmware variant with exposed UI).
```

## 6. Post-deployment verification

All items are **future runtime observations** — none were performed in this mission. "Local" = checkable on the router/LAN without ISP cooperation; "ISP" = requires the live PPPoE path.

| # | Check | Expected | Type |
|---|---|---|---|
| V-1 | `/proc/ni/dev_port_mapping` | port 3 → nas0 | Local |
| V-2 | `/proc/fc/ctrl/wan_port_mask` | 8 (0x08) | Local |
| V-3 | Interface list | `nas0`, `nas0_notag` present; no `nas0_100`-style tagged interface (untagged config) | Local |
| V-4 | Generated options file | `unit 131`, `mru 1480`, `mtu 1480`, `linkname ppp131`; **B-NEW-1 merged line = STOP (§4 S10)** | Local |
| V-5 | PPP interface | `ppp131` exists (not ppp111) with ISP-assigned address; `/var/run/ppp131.pid` present | ISP |
| V-6 | Discovery/auth | `/tmp/pppd-info.tmp` + syslog: PADI→PADO→PADR completes; authentication succeeds (AUTO_AUTH ⇒ PAP or CHAP as offered) | ISP |
| V-7 | Default route | default via ppp131 / dev ppp131 | ISP |
| V-8 | DNS | peer DNS in `/etc/ppp/resolv_ppp131.conf` and propagated to resolv.conf/dnsmasq (U9) | ISP |
| V-9 | NAT | `iptables -t nat -S` shows MASQUERADE `-o ppp131` | Local-after-up |
| V-10 | Firewall | FORWARD includes TCPMSS clamp; TR181FrwlInput/Forward rules reference `-i ppp131` (hachi fallback check, P4-4) | Local-after-up |
| V-11 | DCS stability | after session up *and* after a link flap, `Layer3Forwarding.DefaultConnectionService` still = .3 PPP (flip-hazard check, §2) | Local |
| V-12 | LAN3 bridge | LAN3 still in br0 (`bridge link` vs P-8 baseline); LAN3 client gets DHCP 192.168.1.x and reaches Internet | Local/ISP |
| V-13 | Wi-Fi | WLAN clients associated, DHCP, Internet | Local/ISP |
| V-14 | LAN4 negative check | a DHCP client plugged into LAN4 gets **no** LAN lease (WAN port isolation) | Local |
| V-15 | ACS | `ManagementServer.URL` = `http://tms.airtelbroadband.in:8103` | Local |
| V-16 | Post-reboot repeat | V-1…V-13 re-verified after one clean reboot (boot reconstruction of nas0_notag + session re-establishment) | Local/ISP |

## 7. Failure diagnosis

| ID | Symptom | Likely causes (evidence) | Non-destructive diagnostic | Corrective action | Stop / rollback trigger |
|---|---|---|---|---|---|
| F-1 | After S4, counts unchanged (PPP 0 / IP 1) | Transaction NACKed at DAS apply (CGI is silent — Blocker 1 Q17); same class of failure as Blocker 2 | Read back full .3 subtree; capture syslog around the save (`CCC_MSG_VALIDATE_FAIL`, cccRdm lines) | Do **not** resubmit identically. Record syslog; the creation question re-opens with that evidence | Immediate — no further writes |
| F-2 | After S9, mask still 128 / mapping port 7 | Boot gate didn't take ETHER branch: WANMode string ≠ "ETHER", Eth Enable byte ≠ 1, or mode write used SET_NO_BE and no reboot happened | Read back WANMode + both Enable values; confirm a reboot actually occurred after S8 | Correct values via UI RESTART branch; reboot manually if a no-BE channel was used | If values read back correct yet gate still fails → stop, §8 rollback |
| F-3 | Options file merged line (B-NEW-1) | Firmware defect, deterministic with service name set | `cat /etc/ppp/options_nas0_notag` (V-4) | None config-side. §5.4 branch: rollback, or operator-elected empty-service diagnostic | Production stop — see S10 |
| F-4 | pppd exits / "unrecognized option 'ppp131'" in pppd-info | B-NEW-1 runtime manifestation (STRONGLY INFERRED) | `/tmp/pppd-info.tmp` | As F-3 | Production stop |
| F-5 | No PADI response / discovery timeout | ONT not on LAN4; nas0_notag no carrier; ISP actually requires VLAN (U13) | TP-Link re-test on same ONT port (P-11 isolation); check carrier on nas0_notag | If all local checks pass and an **authoritative** VLAN ID is known: tagged variant (Enable_VLANID=1 + VLANID; expect `nas0_<vid>`, `options_nas0_<vid>`, still ppp131). Never guess-scan VLAN IDs | One tagged attempt max, then §8 |
| F-6 | Session up but no LAN Internet; or default route reverts to IP object after a flap | DCS or per-mode `_ETHER` key still points at .3 IP (deleted) — `updateDefaultRouteByLinkType` rewrite (§2); Event-206 route follows event ifname vs DCS ambiguity (U7); NAT rule absent | Read all four DCS values (V-11); `ip route`; `iptables -t nat -S`; check `/var/wan_connection_notify/nas0_notag_connection_is_up` exists (Event 206 fired) | Correct the DCS keys (§4 S7) in their own transaction | If DCS correct + 206 fired + NAT present yet no forwarding → §8 |
| F-7 | LAN3/Wi-Fi down after mode switch | Not predicted by any code path (bridge is netifd/Layer2Bridge-driven, independent of WAN init — STRONGLY INFERRED survival); would indicate an unmodelled coupling | `bridge link` vs P-8; LAN DHCP check | §8 rollback immediately; preserve captures for analysis | Immediate |
| F-8 | ACS URL = testacs after deployment | linkdetection's ETHER switch ran (autodetect or manual invocation) despite S8 precautions | Read ManagementServer.URL + OverIPv6 | §8 R-ACS restore; set WanAutoDetect=0 (S14) once stable | Not a rollback trigger by itself |
| F-9 | Auth failure (PADR ok, auth rejected) | Wrong credentials entered; masked-sentinel trap left password "unchanged"; service-name corruption (F-3/F-4 class) | Re-enter credentials deliberately (overwrite the sentinel); check V-4 first | Correct credentials at UI; explicit PAP then CHAP only if syslog shows AUTO_AUTH negotiation failing | Two failures → §8 |
| F-10 | Rollback DELETE/conversion-back does not commit | Same DAS apply class as Blocker 2 (unproven rejector) | Syslog capture; counts read-back | Fall to §8 R-C (backup restore) — the rollback floor that does not depend on DAS object ops | — |

## 8. Complete GPON rollback procedure

Rollback is **world-dependent**: how the PPP object was created determines how it is removed. Both worlds are covered; mixing them (e.g. conversion-back when an IP profile already coexists) creates a duplicate `WANIPConnection.2` — check the .3 subtree first [READ] and pick exactly one of R-A / R-B.

### R-0 — Pre-rollback reads [READ]
Record: .3 PPP count, .3 IP count, all four DCS values, WANMode, both Enables, WanAutoDetect, ManagementServer.URL. Decide R-A vs R-B from the counts: IP count 0 + PPP count 1 ⇒ conversion world (R-A). IP count 1 + PPP count 1 ⇒ ADD world (R-B).

### R-A — Conversion world: vendor conversion-back (preferred here)
- **Mechanism (CONFIRMED STATIC):** broadband.cgi's PPP→IP conversion branch @0x403f70 — the verified mirror of S4: deletes the PPP object and recreates `WANIPConnection.1` (`Eth_Internet`) atomically in one transaction, via the same UI edit flow (set the Ethernet connection type back to IP and save).
- Then continue at R-DCS. **Do not also run R-B's DELETE** (the PPP object no longer exists; a DELETE of a nonexistent instance is a clean per-action fail — harmless, but pointless).

### R-B — ADD world: audited ccctest DELETE (Blocker 4 verdict)
- **Parser/mechanism (CONFIRMED STATIC):** `DELETE InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;` — ccctest @0x402da8 lowers it to Sel(full path) + `SetIndexedObj(0)`; **no parent SEL required**; the `.1` spelling is the canonical DELETE form (vendor help @0x403c78). It is fully transactional: SEND required to execute, **SAVE required to persist**. Backend (ccc_das sub==0 path) requires an existing instance (else clean per-action fail), marks the target **and all children** pre-delete (flag 0x80000000); physical purge is mark-and-sweep (`cccRdmDelObject`/`cccRdmCheckDelObject` in libcccrdm) — **sweep trigger/timing UNKNOWN**, so the count→0 read-back (below) is the only acceptable proof, and it may lag the SEND.
- **As its own transaction:** `REQUEST; DELETE …WANPPPConnection.1; SAVE; SEND;` — nothing bundled with it. (The preserved `ether-rollback.ccc` must not be reused for this: it contains **no SAVE** and no DELETE at all.)
- **Gate [READ]:** `.3 WANPPPConnectionNumberOfEntries` reads **0**. If still 1 after a reasonable interval → F-10 → R-C.
- **GPON safety (CONFIRMED STATIC):** DELETE addresses an exact (OID, IA) and sweeps downward only — it **cannot** touch ConnDev.1 objects.
- **Cleanup expectations:** pppd teardown via the L3-down path (`beWanDisableClient`: SIGTERM, sleep 2, SIGKILL, pidfile removed; `deleteLayre3Interface`: `smuxctl --if-delete nas0_notag`) — the deletion→down hop is STRONGLY INFERRED; **verify** `ps | grep pppd` shows no nas0_notag pppd rather than killing anything manually. Route/NAT cleanup flows from ip-down's Event 207. The stale `/etc/ppp/options_nas0_notag` file is **not** deleted by any code path — inert (overwritten on any future enable); leave it. **`DefaultConnectionService` is never auto-repaired** — R-DCS is mandatory.

### R-DCS — Restore default route pointers (mandatory, both worlds)
Set, each verified by read-back: `Layer3Forwarding.DefaultConnectionService` = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1`; IPv6 twin `X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` = same. Per-mode keys need **no** action: `_GPON` keys already hold .1 PPP and the `_ETHER` keys reverting to .3 IP is the factory state (§9).

### R-MODE — Restore WAN mode and enables
- `X_5067F0_GponInterafceConfig.Enable` = Phase-0 baseline state (**absent** in the baseline export — i.e. remove the configured value / restore the backup line; effective default is enabled, STRONGLY INFERRED); `WANEthernetInterfaceConfig.Enable` = baseline state (**absent** in baseline; factory XML says 1 — **baseline wins**, §9).
- `.1.WANPPPConnection.1.Enable` = 1 (undo S6's park). Nothing else under .1 is touched — it was never modified.
- `WANSwitch.WANMode` = `GPON`, preferably via the UI RESTART branch (BE path). **Reboot (CONFIRMED STATIC):** a BE-path WANMode write forces the reboot itself; a SET_NO_BE write does not — reboot manually in that case. Exactly one reboot.
- `WANSwitch.WanAutoDetect`: restore the **Phase-0 baseline value 1** (factory and baseline agree). Deliberate-choice warning: preserved `rollback.ccc` and linkdetection's GPON switch both write **0** — following them leaves auto-detect disarmed, which is *not* the Phase-0 state. This plan restores 1; if the operator prefers the disarmed state, record the deviation explicitly.

### R-ACS — Restore ACS (verify, then fix only if needed)
[READ] `ManagementServer.URL` must equal `http://tms.airtelbroadband.in:8103` (no trailing slash) and `ManagementServer.X_5067F0_OverIPv6` = 0/absent. The UI path never changed them; linkdetection's GPON switch would also restore them *if it runs* (autodetect-gated) — do not rely on it: if either value is wrong, SET it explicitly in its own transaction.

### R-C — Rollback floor: config-backup restore
If any of R-A/R-B/R-DCS/R-MODE fails to commit (F-10): restore the S1 export (or `ether-backup.lz`) through the UI backup/restore, reboot, and run §10. This path does not depend on DAS object operations. **Factory reset is the last resort only** (config store corruption): it would erase the provisioned GPON credentials profile and is **not** part of this plan.

### R-V — Reboot and verify
After R-MODE's reboot, run §10 in full.

## 9. Factory versus baseline restoration matrix

Sources: factory PDM XML = backup copy = ROM decode (byte-identical, md5 `85b4f361…`); Phase-0 live baseline = `ether-backup.lz` decode (timestamp 202406031227.01). The decompressed RDM image is a schema/defaults image (contains no ACS string) and the preserved `config-before-ether.lz` is 0 bytes — neither is a baseline. Full 20-row matrix with per-row evidence: `_work_b3567.md` §5.2. All paths abbreviated: `IGD` = `InternetGatewayDevice`, `CD` = `WANDevice.1.WANConnectionDevice`.

| Parameter | Factory value | Phase-0 baseline | Ethernet target | Rollback value | Evidence |
|---|---|---|---|---|---|
| `IGD.X_5067F0_Ext.WANSwitch.WANMode` | absent (schema default "GPON") | absent | `"ETHER"` | `"GPON"` (or absent) | PDM + schema. CONFIRMED |
| `…WANSwitch.WanAutoDetect` | 1 | 1 | 1 during deployment → 0 after success (S14) | **1** ⚠ scripts/linkdetection-GPON write 0 — deliberate choice (§8 R-MODE) | PDM + diff. CONFIRMED |
| `WANDevice.1.WANEthernetInterfaceConfig.Enable` | 1 | **absent ⚠** | 1 | baseline state = absent (restore backup; writing factory 1 ≠ baseline) | PDM vs ether-backup diff. CONFIRMED |
| `WANDevice.1.X_5067F0_GponInterafceConfig.Enable` (exact typo spelling) | absent (effective 1, STRONGLY INFERRED) | absent | 0 | absent / effective 1 | Schema OID 0xc7. CONFIRMED spelling |
| `WANDevice.1.WANCommonInterfaceConfig.WANAccessType` | absent (status param) | absent | n/a — do not write | n/a | Live value UNKNOWN; not load-bearing in any decoded path |
| `Layer3Forwarding.DefaultConnectionService` | .1 PPP | .1 PPP | .3 PPP | .1 PPP | PDM. CONFIRMED |
| `X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` | .1 PPP | .1 PPP | .3 PPP | .1 PPP | PDM. CONFIRMED |
| `…MultiLinkTypeDefaultConnectionService.DefaultConnectionService_GPON` / `_ETHER` | .1 PPP / .3 **IP** | same | _ETHER → .3 **PPP** (§4 S7); _GPON untouched | already correct (factory state) | PDM. CONFIRMED |
| `LANDevice.1.X_5067F0_IPv6LANHostConfigManagement.IPv6PDWanConnection.Interface` | .1 PPP | .1 PPP | .3 PPP (U15-conditional) | .1 PPP | PDM. CONFIRMED |
| `IGD.ManagementServer.URL` | `http://tms.airtelbroadband.in:8103` | same | unchanged (UI path); testacs only if linkdetection ran → restore | `http://tms.airtelbroadband.in:8103` | PDM + baseline + ROM. CONFIRMED |
| `IGD.ManagementServer.X_5067F0_OverIPv6` | absent | absent | 1 only as linkdetection side effect → revert | 0 / absent | linkdetection disasm. CONFIRMED |
| `CD.1.WANPPPConnection.1` (whole object; VLAN 100, ppp111, creds [REDACTED]) | present, Enable=1 | identical | **untouched** except Enable→0 park (S6) | Enable=1, rest as factory | PDM subtree. CONFIRMED |
| `CD.2.WANIPConnection.1` (VoIP, VLAN 660) | Enable=1 | identical | untouched ⚠ linkdetection ETHER switch sets 0 — another reason D is rejected | Enable=1 | PDM. CONFIRMED |
| `CD.3.WANIPConnection.1` (`Eth_Internet`, nas0_notag) | Enable=1, no Gw/Subnet/ExtIP elements | **Enable absent ⚠**; `DefaultGateway/SubnetMask/ExternalIPAddress=0.0.0.0` added (linkdetection Tx-A fingerprints) | conversion world: deleted → PPP; ADD world: kept | IP present, PPP absent; Enable per baseline = absent ⚠ | PDM + diff. CONFIRMED |
| `CD.3.WANPPPConnection.1` | absent (count 0) | absent | present, Enable=1, `3jglobal`/1480/1480/AUTO_AUTH/NAT=1/VLAN off | absent (count 0) via §8 | Schema + CGI analysis. CONFIRMED |
| `CD.4 / CD.5` profiles | factory | identical | untouched | already correct | PDM. CONFIRMED |
| Firewall DEFAULTWAN / DEFAULTWANv6 bindings | → .1 PPP / ppp111 (data) | identical | untouched | already correct | PDM. CONFIRMED |
| NAT / MSS rules | template-driven (no stored state) | — | generated for ppp131 at session up | removed via Event 207 on teardown | libbemodules. CONFIRMED |

**Must remain untouched during the entire Ethernet deployment** (any change breaks rollback or GPON): the whole CD.1 PPP object except its Enable byte; Gpon/Eth `IfName` values (`nas0`); both `_GPON` DCS keys; CD.2/CD.4/CD.5; firewall DEFAULTWAN bindings; all ManagementServer parameters except (if clobbered) URL/OverIPv6; the BrasList.

## 10. Rollback verification

Future runtime observations; none performed here.

| # | Check | Expected |
|---|---|---|
| RV-1 | WAN mode / enables [READ] | WANMode GPON (or absent=default), Gpon Enable effective 1, Eth Enable at baseline state |
| RV-2 | `/proc/fc/ctrl/wan_port_mask` | 128 (0x80) |
| RV-3 | `/proc/ni/dev_port_mapping` | port 7 (GPON) mapping |
| RV-4 | GPON PPP session | `ppp111` up with ISP address; fibre connected; discovery/auth in syslog |
| RV-5 | Default route | via ppp111; DCS v4+v6 read back as .1 PPP (§8 R-DCS) |
| RV-6 | ACS | `ManagementServer.URL` = `http://tms.airtelbroadband.in:8103`; OverIPv6 0/absent |
| RV-7 | Auto-detect | WanAutoDetect = 1 (Phase-0) — or a recorded deliberate deviation (§8) |
| RV-8 | Ethernet residue | .3 PPP count 0; conversion world: .3 IP `Eth_Internet` present again; no nas0_notag pppd in `ps` |
| RV-9 | LAN3 / Wi-Fi | clients associated, DHCP, Internet via GPON |
| RV-10 | Client Internet | end-to-end from LAN3 and Wi-Fi |

## 11. Risk register

Severity = impact × likelihood for a human-controlled deployment following §4. "Blocker" rows B-1…B-10 are the brief's ten; P4 rows are the Part-4 hunt (only evidence-rated items listed; items with no evidence either way are marked UNKNOWN with their detector).

| ID | Risk / blocker | Status | Severity | Detection | Mitigation / rollback implication |
|---|---|---|---|---|---|
| B-NEW-1 | `pppoe_srv_name` missing-newline defect corrupts generated options file when service name set (fmt @0xbd808, beConfigWANByPPPoE @0x66968) | **OPEN — CRITICAL.** Generation CONFIRMED STATIC; pppd fatality STRONGLY INFERRED | **Critical** | V-4 options-file inspection; `/tmp/pppd-info.tmp` | No config-side fix. §4 S10 hard stop; empty-service diagnostic is HYPOTHESIS only. Blocks production readiness (§13) |
| U12 | Shipped ETH edit HTML may not expose PPPoE option (zero .html in repo) | **OPEN** — operator-observable | **High** (gates preferred path) | §4 S3 look at the live page | If absent: STOP; no proven fallback (B-2) |
| B-2 | ccctest ADD commit NACK — exact rejector unknown (apply phase in cccDasHandleApply; leading hypothesis: sibling-IP coexistence) | OPEN (mechanism located; cause unproven) | Medium — only affects rejected Approach B and F-10 rollback edge | Syslog `CCC_MSG_VALIDATE_FAIL` + ccctest validation output at a diagnostic ADD | Approach B not used for deployment; rollback floor R-C does not depend on it |
| B-1 | broadband.cgi PPPoE behaviour | **RESOLVED** — all 20 questions answered CONFIRMED STATIC (§4 S4, `_work_b124.md`) | — | — | Silent-failure property drives mandatory S5 gate |
| B-3 | GPON/Ethernet coexistence | **RESOLVED** — CONFIRMED STATIC (§4 S6 shape); both-enabled runtime interaction UNKNOWN by design avoidance | Low | S5/S6 read-backs | GPON never deleted; park-only |
| B-4 | DELETE / rollback correctness | **RESOLVED with caveats** — parser+execution CONFIRMED; sweep timing UNKNOWN; DCS never auto-repaired (handled in R-DCS); safest mechanism is world-dependent (§8) | Medium | R-B count read-back gate | R-C backup restore is the guaranteed floor |
| B-5 | GPON restoration completeness | **RESOLVED** — §9 matrix; factory≠baseline differences enumerated (4 WAN-relevant diff lines) | Low | §10 RV checks | Baseline beats factory where they differ |
| B-6 | ACS side effects | **RESOLVED** — UI path immune (CONFIRMED); linkdetection values + OverIPv6 identified; Phase-0 URL known byte-exact | Low (on selected path) | V-15 / R-ACS read | Restore explicitly; never rely on linkdetection to restore |
| B-7 | Boot / reboot behaviour | **RESOLVED** — reboot CONFIRMED STATIC both directions; BE-write auto-reboot vs SET_NO_BE manual-reboot trap documented; nas0_notag rebuilt every boot | Low | S9 gates | Exactly one planned reboot per direction |
| B-8 | PPP config generation | **RESOLVED except B-NEW-1** — unit/MTU/MRU/auth/VLAN-naming/launch all CONFIRMED | (see B-NEW-1) | V-4/V-5 | — |
| B-9 | Routing/NAT/firewall GPON assumptions | **RESOLVED** — chain CONFIRMED generic; residuals U7 (route follows DCS vs ifname), U8 (exact FORWARD list), U9 (DNS propagation), U10 (fastpath) are runtime-only | Medium | V-7…V-11 | F-6 diagnosis path |
| B-10 | LAN3 / Wi-Fi preservation | **RESOLVED statically** — port 2 absent from all WAN code; bridge membership config-driven and untouched by mode switching; DHCP LAN-only. Runtime proof = V-12…V-14 | Low | §6 regression table | F-7 immediate rollback if violated |
| P4-4 | hachi watchdog falls back to literal `ppp111` if WAN ifname resolution fails → firewall repair rules could target the wrong interface | Evidenced (hachi @0x404648 / fallback @0x4027b4) | Low–Med | V-10 (`-i ppp131` in TR181FrwlForward) | Cosmetic-to-moderate: missed rule repair only; main FORWARD/NAT path unaffected |
| P4-5 | Editor/activation mismatch: ETH edit CGI contains only a bare "PPPoE" string — field-level support (service name/MTU/auth inputs) lives in broadband.cgi's handler, and the HTML form itself is absent from the repo | Evidenced | Medium (compounds U12) | S3 observation | Same gate as U12 |
| P4-6 | linkdetection rewrites IPv6 pointers (NDPPD.Enabled, IPv6PD interface → IP object) on switch | Evidenced; certain if D ever runs | Low (IPv4 deployment) / Medium if ISP delegates IPv6 (U15) | Read IPv6PD pointer at S2/S7 | Selected path never runs D; U15 handled at S7 |
| P4-7 | TR-069 (ztr69 present) could push back configuration if the ISP ACS notices the change — compounded if URL were left at testacs (it must not be) | HYPOTHESIS (no push observed in artifacts) | Low–Med likelihood, High impact | ACS URL read-backs (V-15); watch for unsolicited config changes post-deployment | Keep production ACS; S14 hardening |
| P4-8 | Default-route conflict with existing GPON route | Evidenced machinery (isDefaultGw/DCS singleton) | Low on §4 order (park S6 before DCS S7) | V-7/V-11 | §4 ordering is the mitigation |
| Refuted | Plugin mismatch (pppd↔libpppoe linkage proven), stale options accumulation (copy-overwrite each enable), PPP unit collision (IA construction), SMUX/proc absence (all nodes/modules present in rootfs: pppoe.ko, smuxdev.ko, ca-rtk.ko) | DISPROVEN as risks | — | — | — |
| UNKNOWN | Switch port isolation specifics; ONT-side VLAN reality (U13); fastpath bypass (U10); RDM post-commit callback failures beyond B-2; WANAccessType hidden dependency (no path found that reads it for Ethernet PPPoE) | UNKNOWN with detectors in `_work_b8910.md` | Unrated | V-checks / F-table | Each has a §7 diagnostic row or §6 check |

## 12. Evidence index

| Claim (short) | Artifact | SHA-256 / location | Address / location in artifact | Related report |
|---|---|---|---|---|
| broadband.cgi conversion sequence, wanIA, silent failure | `DUMPFILES/broadband.cgi` | `78eaacd575b9884778a76ead57cc895e95944cc939c465136ee3da390f3671fa` | cgiMain @0x403390; delete @0x403e34; alloc @0x403e8c; create @0x403f10; DCS block @0x404738; Save @0x4066d4; SendRecv @0x4068b8; conversion-back @0x403f70 | BROADBAND_CGI_PPPOE_ANALYSIS.md; `_work_b124.md` |
| ccctest parser semantics (ADD queue-only; DELETE form; reply printer) | `DUMPFILES/ccctest.bin` (= rootfs `usr/bin/ccctest`) | `4badd3f723df86838e20a199f08c4e844354aec605f286a3cb141f93b5d3f3bf` | ADD @0x402ca8; DELETE @0x402da8; printer @0x4017dc; help @0x403c78 | RDM_OBJECT_CREATION_ANALYSIS.md; `_work_b124.md` |
| DAS apply / NACK origin | rootfs ccc_das | (in inventory CSV) | `cccDasHandleSetIndexObject` @0x412810; `cccDasHandleApply` + callback table @0x4162a8 | `_work_b124.md` |
| RDM creation primitives + OID table | `DUMPFILES/librdm.so` | `65306765251c503d3c36fac4f93bfa348698f2ffe9ed83a646a672b57b331a1d` | OIDTable @0x294f0 (stride 280); AddIndexChildObject @0x134a0; GetAvaliableIA @0x11c20; VerifyIAValue @0x11e48; GetObjListByName @0x12324 | RDM_OBJECT_CREATION_ANALYSIS.md |
| Port mapping, eth init, L3 interface, teardown, requested link type, PPP unit/name | `DUMPFILES/libcccbe.so` (= rootfs copy, hash-verified) | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` | mapping @0x37c84; eth_Init @0x38074; createLayer3Interface @0x35348; deleteLayre3Interface @0x35f60; getLinkType @0x34334; unit @0x38264; setName @0x346d0; execPPP @0x348f4 | ETHERNET_WAN_HARDWARE.md; PPP_INTERFACE_BINDING.md; `_work_b3567.md`; `_work_b8910.md` |
| Boot gate, mode-change reboot, DCS flip, config generation (incl. B-NEW-1), MSS, DNS, disable-client | `DUMPFILES/libbemodules.so` | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` | Boot @0x50d08; doWanModeChange @0x36d3c; updateDefaultRouteByLinkType @0x6f2d8; beConfigWANByPPPoE @0x664a8 (srv_name @0x66968, fmt @0xbd808); createCfgFile @0x6a7c0; MSS @0x66f18; configDNSServers @0x11cbc; beWanDisableClient @0x6722c; wanConnectionUp @0x56d10 | ETHERNET_PPPOE_LIFECYCLE.md; `_work_b8910.md` |
| Event 206/207 dispatch | `DUMPFILES/libbeEvents.so` | `cc9d237437773f9a104ceec09f4217298543e0dc80dcd46f89e95b18c40500d1` | L3Forwarding handler @0xb370 | ROUTING_NAT_FIREWALL_ANALYSIS.md |
| linkdetection branches, ACS values, Tx-A fingerprints | `DUMPFILES/linkdetection` | `36d219bd3c86704721fe44ba5eb214dadb5ebcae9eed4b41f74e323ebf1a9f93` | switch @0x402454; GPON URL string @0x403cf0; ETHER URL string @0x404018; Tx-A Save @0x402eb8 | WAN_ACTIVATION_CALL_GRAPH.md; `_work_b3567.md` |
| Factory PDM / ROM / Phase-0 baseline | PDM XML copies; `DUMPFILES/ether-backup.lz` | PDM md5 `85b4f361…`; ether-backup decode `analysis/ether_backup_decoded.txt` | §9 matrix rows | `_work_b3567.md` §5 |
| ip-up / ip-down generic event emission | rootfs `etc/ppp/ip-up`, `ip-down` | `3fcaa848d84b5297bcbabd93dd569e7ed84f17eb50d3cb0d72b5d04c98ee4ae7` / `d5a5e2ceb638e9dcc0c3a974f0bb8f4fd869d5168b3bc128ea467e5ec347f51e` | whole files (verbatim) | ETHERNET_PPPOE_LIFECYCLE.md |
| hachi ppp111 fallback | rootfs `usr/bin/hachi` | (in inventory CSV) | fallback @0x4027b4; templates @0x404760/0x404790 | `_work_b8910.md` |
| Full artifact inventory | `research/REPOSITORY_INVENTORY.csv` | 2,601 files with SHA-256 | — | REPOSITORY_INVENTORY.md |

## 13. Final readiness verdict

## **NOT READY**

Critical static blockers remain — exactly two, both named, everything else in the brief is resolved:

1. **B-NEW-1 (firmware defect, CONFIRMED STATIC):** the generated PPPoE options file is corrupt whenever the ISP-required service name `3jglobal` is configured (`pppoe_srv_name 3jgloballinkname ppp131`). No configuration-side mitigation exists. The procedure therefore cannot be executed as a production deployment with the specified ISP profile until one of these flips it: (a) runtime evidence that this ISP's BRAS accepts an empty service name *and* a clean generated file with the name cleared (the diagnostic in §5.4), recorded back into this repo; (b) runtime evidence that pppd on this build tolerates the merged line and negotiates the correct service (considered unlikely); or (c) a firmware-side fix.
2. **U12 (UNKNOWN, trivially observable):** whether the shipped Ethernet edit page exposes the PPPoE option that triggers the proven conversion branch. If the S3 observation is negative, the preferred path is inoperable and — Approach B's rejector being unproven — no proven creation path exists at all.

**What is ready:** the complete architecture (§2), the pre-implementation checklist (§3), every proven step of the implementation procedure (§4, with the two gated steps explicitly marked), the decision tree (§5), verification (§6), diagnosis (§7), a world-dependent rollback with a backup-restore floor (§8), the factory-vs-baseline matrix (§9), and rollback verification (§10). When B-NEW-1 and U12 flip on recorded runtime evidence, this verdict becomes **STATICALLY READY, RUNTIME VALIDATION REQUIRED** without any other change to the document. **RUNTIME VALIDATED is not claimed** — no runtime evidence for the Ethernet PPPoE session exists in the repository; the only runtime evidence present is the prior GPON operation, the Phase-0 backup, and the earlier failed ADD / mode observations, each identified as such where used.

*End of document. Companion evidence: `_work_b124.md`, `_work_b3567.md`, `_work_b8910.md` (this mission); the 18 first-mission reports in the same directory.*
