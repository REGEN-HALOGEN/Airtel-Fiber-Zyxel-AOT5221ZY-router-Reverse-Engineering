# Open Questions

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Every item static analysis could not settle, with the exact runtime observation (or extra static pass) that would settle it. None of these were guessed at in the reports.
- **Files examined:** —

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


| # | Question | Why it matters | Required observation / pass |
|---|---|---|---|
| U1 | Does the minimal ccctest ADD (no trailing .1, no bundled SETs) commit? What is the exact commit-phase rejector of FE-2? | Decides Path B viability and closes the root-cause | Run IMPLEMENTATION_PLAN Path B Transaction 1; capture ccctest `validation error code` output + device syslog (`cccRdm*`/`rdmVerifyIAValue`, level 3) |
| U2 | Is eth_Init reachable without reboot (L4ObjectChanged)? | Decides whether Phase 3 reboot is truly mandatory | Change WANMode to ETHER live; watch `/proc/ni/dev_port_mapping` + `/proc/fc/ctrl/wan_port_mask` + syslog before any reboot |
| U3 | Live contents of `/etc/ppp/default_options` vs `_options_static` (dump copies look swapped/empty) | The generated options file inherits the template (plugin, usepeerdns, holdoff) | `cat` both on a running unit; inspect generated `options_nas0_notag` for `unit 131`, srv_name, mtu/mru |
| U4 | Does pppd honour `unit 131` text and create ppp131? | Criterion 6/7 proof | `ip link`, `/var/run/ppp131.pid`, `/tmp/pppd-info.tmp` after enable |
| U5 | Which function uses the `options_FN%d%d` / `unit %d%d` family (libbemodules @0xc1fd8)? | Exclude a competing PPP path | Static: adrp/add xref scan for VA 0xc1ff0 in libbemodules .text |
| U6 | Exact product of `createWANPPPConnectionCfgFile` @0x6a7c0 | Completeness of lifecycle | Static PLT resolution of its 5 helpers; runtime: diff /etc/ppp + secrets files before/after enable |
| U7 | Does the Event-206 route follow DefaultConnectionService or the event ifname? | Decides whether DCS correctness is load-bearing at runtime | Bring ppp131 up with DCS deliberately pointing at the GPON object; observe `ip route` |
| U8 | Exact FORWARD/firewall rules installed for ppp131 | Criterion 10 proof | `iptables -S FORWARD; iptables -t nat -S` with session up |
| U9 | Does peer DNS reach resolv.conf/dnsmasq for ppp131? | LAN client DNS | `cat /etc/resolv.conf` + dnsmasq conf after IPCP |
| U10 | MSS rule call timing; fastpath offload of ppp131 flows | Performance/correctness colour | `iptables -S FORWARD \| grep TCPMSS` at boot vs up; fc flow counters under load |
| U11 | Does LAN3 stay in br0 through activation? | Criterion 11 proof | `bridge link` before/after (Phase 0 vs Phase 4 captures) |
| U12 | Does the shipped ETH edit HTML expose the PPPoE encap option? | Decides Path A vs Path B | Human observation of the live Web UI edit page for Eth_Internet (cannot be answered from this repo) |
| U13 | Is a VLAN actually required by the ISP on this ONT path? | No-VLAN is inferred from the TP-Link's config only | Phase-4 fallback F2 outcome; or authoritative ISP provisioning data |
| U14 | getLinkType OID-operand naming (C-11): what structs do OIDs 0xc7/0xca denote at libcccbe @0x34334? | Removes the last mechanism-level ambiguity in link-type resolution | Static: trace cccRdmGetObjectByOID return layout for 0xc7/0xca in the SHM image; compare leading bytes with the interface-config templates |
| U15 | IPv6 behaviour of the Ethernet PPPoE profile (NDPPD/IPv6PD point at the IP object after linkdetection's switch) | Only if the ISP delegates IPv6 over this PPPoE | Runtime: after v4 success, check IPv6 PD/RA state; if absent and required, retarget IPv6PDWanConnection.Interface to the PPP object in a separate transaction |
| U16 | Default *values* of the schema-image-only PPP parameters in a freshly created object (beyond Enable=0) | Predicts Path B SET list completeness | After a successful minimal ADD (U1), read back the full .1 object before configuring it |

## Follow-up mission updates (2026-11-07, later session)
- **U14 CLOSED:** getLinkType @0x34334 operands are OIDs 0xc7/0xca = Gpon/Eth interface-config Enables; return is a media link type (1=GPON, 0=Ethernet, 2=other). C-11 resolved.
- **U5 CLOSED:** `options_FN%d%d` / `unit %d%d` family belongs to `CreatePPPByFullNAT` @0x91d30 / `beFullNatEnablePPPv4Client` @0x92200 (libbemodules) — FullNAT slave-pppd feature, not the main path.
- **U6 MOSTLY CLOSED:** createWANPPPConnectionCfgFile @0x6a7c0 decoded as orchestrator (Enable gate, IPv6/DNS cleanup, "Disabled" state string); the libcccbe wrapper it calls @0x373a4 is a no-op stub.
- **U3 REFRAMED:** dump copies of default_options/_options_static are both populated (90 B dynamic incl. `plugin pppoe`/`usepeerdns`); prior "0 bytes/swapped" reading DISPROVEN for this dump. Live-unit contents still a runtime read, now low-risk.
- **U2 CLOSED (as CONFIRMED STATIC):** eth_Init is Boot-only; WANMode BE writes force reboot (`WAN_MODE_CHANGE_REBOOT`), SET_NO_BE writes require a manual reboot.
- **NEW B-NEW-1 (CRITICAL, supersedes U1 in importance):** `pppoe_srv_name %s` format @0xbd808 lacks a trailing newline → merged `pppoe_srv_name 3jgloballinkname ppp131` line in generated options. Runtime observations that would settle severity: `cat /etc/ppp/options_nas0_notag` after first enable + `/tmp/pppd-info.tmp` content + whether the BRAS accepts an empty service name (diagnostic in CONCRETE_IMPLEMENTATION_CHECK_AND_ROLLBACK.md §5.4).
- **U1 narrowed:** the NACK is issued by `cccDasHandleApply` (ccc_das, callback table @0x4162a8); needed evidence unchanged (original script + full stdout + syslog), now with the exact log tag to grep: `CCC_MSG_VALIDATE_FAIL`.
- U4, U7–U13, U15, U16 remain open as runtime observations; U12 remains the gate for the preferred path (see CONCRETE_IMPLEMENTATION_CHECK_AND_ROLLBACK.md §§4–5).
