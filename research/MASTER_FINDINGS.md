# Master Findings

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Consolidated, confidence-labelled findings ledger for the whole mission. This file supersedes prior 'CONFIRMED (100%)' labels where noted; prior reports are preserved unmodified.
- **Files examined:** All artifacts in the hash table; prior ledger `full-router-dump/analysis/rea-investigation/MASTER_FINDINGS.md`

## Key artifact hashes
| Artifact | Size | SHA-256 |
|---|---|---|
| DUMPFILES/broadband.cgi | 61,760 B | `78eaacd575b9884778a76ead57cc895e95944cc939c465136ee3da390f3671fa` |
| DUMPFILES/wanRemoteNode_ETH_Edit.cgi | 47,424 B | `59ee3ba6b9a946650eb9112fb0ebc2561e2e9ee5e0589ec2ada55517c4af5899` |
| DUMPFILES/wanRemoteNode_GPON_Edit.cgi | 47,416 B | `69f9a176397c742d0ee50fe07313646cf5ca27743ba1c29facf54b7c6eb148e1` |
| DUMPFILES/linkdetection | 23 KB | `36d219bd3c86704721fe44ba5eb214dadb5ebcae9eed4b41f74e323ebf1a9f93` |
| DUMPFILES/libcccbe.so | 369 KB | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` |
| DUMPFILES/libbemodules.so | 1.1 MB | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` |
| DUMPFILES/libbeEvents.so | 109 KB | `cc9d237437773f9a104ceec09f4217298543e0dc80dcd46f89e95b18c40500d1` |
| DUMPFILES/librdm.so | 280 KB | `65306765251c503d3c36fac4f93bfa348698f2ffe9ed83a646a672b57b331a1d` |
| DUMPFILES/libcccrdm.so | 436 KB | `ed2a1d6a0f70b0d0323cc8b0671d0846b2ef1f529b871104cc45eb61d4376352` |
| DUMPFILES/libcmsg.so | 55 KB | `57155a272eb9cdf9e4d62b3fee07d4f058a93ccb798d4c6503292af4b0094d70` |
| DUMPFILES/ccctest.bin | 23 KB | `4badd3f723df86838e20a199f08c4e844354aec605f286a3cb141f93b5d3f3bf` |
| DUMPFILES/ccc_be | 120 KB | `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f` |
| DUMPFILES/config.rdm (= runtime-config.rdm) | 62 KB | `fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7` |
| DUMPFILES/config_rdm_decompressed.bin | 3,145,728 B | `b1a35a37631b7dd75c1b13f6d78e6a75d6c41bb081e8c868c82330dad1dd5485` |
| rootfs lib/MSTC/libpppoe.so | — | `c6a83bc868fd2e6e0e19abbd43625a68e90e47874ea5f8d87f6437a69577e315` |
| rootfs bin/pppd | — | `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596` |
| rootfs etc/ppp/ip-up | — | `3fcaa848d84b5297bcbabd93dd569e7ed84f17eb50d3cb0d72b5d04c98ee4ae7` |
| rootfs etc/ppp/ip-down | — | `d5a5e2ceb638e9dcc0c3a974f0bb8f4fd869d5168b3bc128ea467e5ec347f51e` |
| rootfs lib/MSTC/libCmd.so | — | `fa8ecde8b14e0ff682faef8152cb5bdf446e11bc90a8a6b29f9e71dc8be3bc8c` |


## HW — hardware / port mapping
- **HW-1 CONFIRMED STATIC:** LAN4 = switch/PHY port 3, Ethernet WAN mask `0x08`; GPON = port 7, mask `0x80`. `rtk_wan_port_mapping(mode, ifname)` (libcccbe.so @0x37c84): mode 0 → `echo 3 <if> > /proc/ni/dev_port_mapping`, mask global = 0x08; mode 1 → port 7, 0x80; shared tail `echo <mask> > /proc/fc/ctrl/wan_port_mask`. Note the two writes carry different values (port index vs bitmask) — prior summaries merging them are imprecise.
- **HW-2 CONFIRMED STATIC (by omission):** LAN3 = port 2 / mask 0x04 never appears in any WAN-init function examined. Preservation is by omission, not an explicit guarantee (see ROUTING_NAT_FIREWALL_ANALYSIS.md).
- **HW-3 CONFIRMED STATIC:** Platform AArch64, kernel modules `ca-rtk.ko`/`ca-ne.ko` for Linux 5.10.138 in rootfs; SoC identity RTL9607C/Taurus is CONFIRMED FROM EXISTING RUNTIME EVIDENCE + prior DT analysis, not re-derived from DTB this session.

## ETH — Ethernet WAN init & mode switch
- **ETH-1 CONFIRMED STATIC:** `libcccBeWan_eth_Init` @0x38074 = `EthPhyEnable(1)` + `smuxctl --if <name> --set-if-rsmux …` + hw_vlan_filter switch_on/enable/refresh + final `rtk_wan_port_mapping(0, name)`. It does **not** create `nas0`/`nas0_notag` and does not start pppd (corrects prior activation-sequence attribution).
- **ETH-2 CONFIRMED STATIC:** Boot gate — `OID_…_WANDevice_i_ConfigLoaderFunc_Boot` (libbemodules @0x50d08) spawns `/usr/sbin/linkdetection &`, and calls eth_Init only if WANEthernetInterfaceConfig Enable && `WANSwitch.WANMode == "ETHER"` (strcmp @0x50ec8).
- **ETH-3 STRONGLY INFERRED:** A reboot is required for the hardware remap after changing WANMode (Boot path proven; exclusivity vs the L4ObjectChanged path not proven — prior "exclusively Boot, CONFIRMED" is downgraded).
- **ETH-4 CONFIRMED STATIC:** `linkdetect_switch_WanMode` @0x402454 (linkdetection): GPON/ETHER/DISABLE branches; every transaction ends `cmsgRequestSave`+`cmsgSendRecv`. ETHER creates/enables only the ConnDev.3 **IP** profile (`Eth_Internet`, `X_5067F0_InterfaceName="nas0_notag"`), points DefaultConnectionService at **WANIPConnection.1**, and **clobbers ACS** `ManagementServer.URL` to `http://testacs.airtelbroadband.in:8103/` (GPON branch sets production `http://tms.airtelbroadband.in:8103`). linkdetection alone can never create a PPPoE profile.
- **ETH-5 CONFIRMED STATIC:** Factory profile `Eth_Internet` exists as `WANConnectionDevice.3.WANIPConnection.1` only; no PPP child under .3 in factory PDM XML — consistent with the runtime-observed PPP count 0.

## CGI — broadband.cgi (highest priority)
- **CGI-1 CONFIRMED STATIC:** `cgiMain` @0x403390 (size 0x3594). There is **no add-new-profile path** and no SetIndexedObj for WANConnectionDevice. The only WANPPPConnection creation is **IP→PPP type conversion of an existing connection**: delete WANIPConnection (OID 0xcd, `cmsgRequestSetIndexedObj(req,0)` @0x403e34), allocate via `rdmGetAvaliableIAByOID(rdm, 0xe3, parentIA="%d,%d")` @0x403e8c, create WANPPPConnection (OID 0xe3, `SetIndexedObj(req,1)` @0x403f10), set all PPP params, `cmsgRequestSave` @0x4066d4, single `cmsgSendRecv(...,60000)` @0x4068b8 (result never checked).
- **CGI-2 CONFIRMED STATIC:** `wanIA` is a comma-separated IA spec string (`"1,3,1"`) parsed by `rdmConstructIAValue` @0x4039ec; it identifies the *existing* connection. **No `.3` is hardcoded** — .3 comes from wanIA's 2nd component. Converting the factory Eth profile therefore creates exactly `…WANConnectionDevice.3.WANPPPConnection.1`.
- **CGI-3 CONFIRMED STATIC:** The ETH/GPON edit CGIs are render-only (104-byte cgiMain stubs; no cmsgRequestSet/SetIndexedObj/Save/SendRecv imports). All mutation is in broadband.cgi. **UNKNOWN:** whether shipped HTML exposes PPPoE for ETH — zero .html files exist in the repo/rootfs dump.
- **CGI-4 CONFIRMED STATIC:** broadband.cgi's RESTART branch is the Web UI's WAN-mode switch: sets Gpon/Eth Enable (OIDs 0xc7/0xca) by mode string and `WANSwitch.WANMode`, with Save; commit is the same single SendRecv at the end.

## RDM — object creation failure
- **RDM-1 CONFIRMED STATIC:** OID ground truth from librdm.so OIDTable (stride 0x118): WANPPPConnection class **0xf1** / instance **0xe3** (max 8), WANIPConnection class 0xe2 / instance 0xcd, WANConnectionDevice.i 0xcc (max 8), WANEthernetInterfaceConfig 0xca, WANCommonInterfaceConfig 0xc4, GponInterafceConfig 0xc7 (vendor typo is real), Layer3Forwarding 0x80, WANSwitch 0x4d.
- **RDM-2 CONFIRMED STATIC:** Every gate in `cccRdmGetObjectByOID → cccRdmAddIndexChildObject (librdm @0x134a0) → rdmVerifyIAValue (@0x11e48)` passes for parent IA {1,3}: class template flags 0x2 (bit1 → auto-allocation), empty child list → instance 1 hardcoded @0x137ec, depth/non-zero/max checks pass (WANDevice max 4, ConnDevice max 8, PPP max 8). Schema does **not** forbid PPP under .3.
- **RDM-3 STRONGLY INFERRED:** The failed ccctest ADD **executed** (per-action reply `ADD …: success` is an independent field, ccctest @0x4017dc) and the **transaction was NACKed at commit/validation** (header bit 30 → `transaction fail !!`) and rolled back — hence count stayed 0. Specific rejector UNKNOWN; leading candidate is a sibling action in the same SEND poisoning the transaction (HYPOTHESIS).
- **RDM-4 DISPROVEN:** trailing `.1` as a hard failure (server resolver strtol-parses it, libcccrdm @0x9538–0x95ac; digit ignored on the auto-allocation branch); schema forbidding .3 PPP; max-instances; AssignIA "already exists"; missing SAVE as cause of count 0.

## PPP — lifecycle & binding
- **PPP-1 CONFIRMED STATIC:** Unit = decimal **string concatenation** of IA bytes: `libcccBeWan_getPPPPdUnitNum_wrapper` @0x38264, `snprintf("%d%d%d")` (fmt @0x4c3b8) → `beConfigWANByPPPoE` @0x6663c writes `unit %s` into the options file. Interface name: `setWanIpPppInterfaceName` @0x346d0, PPP branch @0x348a8, `snprintf("ppp%d", unit)` (fmt @0x4aeb0). **1.1.1 → ppp111 (GPON); 1.3.1 → ppp131 (Ethernet). No ppp111/ppp131 literal exists in any binary.**
- **PPP-2 CONFIRMED STATIC:** `beConfigWANByPPPoE` @0x664a8 writes `/etc/ppp/options_nas0_notag` (named by L2 interface, **not** options_ppp131): unit, user, password [REDACTED], linkname, `mru`=[obj+0x18], `mtu`=[obj+0x1a], lcp-echo-*, auth refuse-* only for PAP/CHAP/MS-CHAP (**AUTO_AUTH → none**), persist/passive for AlwaysOn, `pppoe_srv_name` if service name non-empty.
- **PPP-3 CONFIRMED STATIC:** Launch: `beWanEnablePPPv4Client` @0x66ee4 → `libccc_executePPPv4Client` @0x348f4 → `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &` (via cccBeSystemQueue). Positional device arg is consumed by rp-pppoe plugin `libpppoe.so` (`setdevname_pppoe`); no GPON/omci literal in pppd or the plugin.
- **PPP-4 CONFIRMED STATIC:** `/etc/ppp/ip-up` is verbatim generic: writes `EVENTNOTIFY 206 string $REALNAME;` via a ccctest script file; ip-down emits 207. Neither script does route/NAT/DNS/MSS work — all delegated to ccc_be Event 206/207 handlers. Prior "ip-up emits EVENTNOTIFY 206 string ppp111" is DISPROVEN as a literal (it emits whatever pppd passes as $1 — ppp131 in the Ethernet case).

## NET — routing / NAT / firewall
- **NET-1 CONFIRMED STATIC:** NAT templates are generic in libbemodules: `iptables -t nat -A NAT_POSTROUTING -o %s -j MASQUERADE` (+ `-s %s/24`, SNAT variants). Zero MASQUERADE strings in libbeEvents/libcccbe. Prior literal `-o ppp111` claim DISPROVEN.
- **NET-2 CONFIRMED STATIC:** MSS clamp is the dedicated global pair `addTCPMSSDefaultRule`/`delTCPMSSDefaultRule`: `iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu` (+ip6tables). No literal 1440; effective MSS follows MTU (1480→1440). Not inside beConfigWANByPPPoE. Call timing UNKNOWN.
- **NET-3 STRONGLY INFERRED:** Default route follows `Layer3Forwarding.DefaultConnectionService` (an RDM string; factory value = GPON PPP path; vendor per-mode keys `DefaultConnectionService_GPON`/`_ETHER` exist on OID 0x83). Event 206 handlers (libbeEvents: Route/NAT/DNS/L3Forwarding handler symbols) are interface-name driven with no GPON literal. Runtime check U7 decides whether the route follows DCS or the event ifname.
- **NET-4 UNKNOWN:** Fastpath offload of established ppp131 flows (only proven fc coupling is `wan_port_mask` at init); the exact FORWARD accept pair as a literal string (not found — may be concatenated or generic WAN-zone code).

## ISP profile (from brief, not from binaries)
Service name `3jglobal`, MTU/MRU 1480, `AUTO_AUTH` — CONFIRMED FROM EXISTING RUNTIME EVIDENCE (user-supplied ISP data). VLAN requirement: **UNKNOWN** — the existing TP-Link connects with no VLAN configured (runtime evidence), and the firmware's untagged path (`nas0_notag`) is fully implemented; tagged path (`nas0_<vid>`) also exists if needed.
