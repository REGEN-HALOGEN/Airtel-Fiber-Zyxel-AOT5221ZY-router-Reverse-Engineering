# Evidence Index

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Map from every major claim to its exact evidence: file, hash, address, and where the working analysis lives.
- **Files examined:** All artifacts; this session's three working analyses (summarised inline in the reports above)

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


## Primary evidence by topic
| Claim | Evidence | Location |
|---|---|---|
| broadband.cgi hash/size; README hash wrong | sha256sum this session | REPOSITORY_INVENTORY.csv; FAILED C-1 |
| cgiMain bounds, PLT map, call counts | Capstone + .rela.plt this session | BROADBAND_CGI §Binary identity |
| OID table (0xe3 PPP.i, 0xf1 class, 0xc7 Gpon, 0xca Eth) | librdm.so OIDTable @0x294f0, stride 0x118, via cccRdmGetOffsetByOID @0x11728 | RDM_OBJECT_CREATION §3 table in working analysis; PPP_PARAMETER_VALIDATION |
| wanIA parsing | broadband.cgi @0x40397c/0x4039ec; librdm rdmConstructIAValue @0x1125c | BROADBAND_CGI |
| IP→PPP conversion sequence | @0x403dd0 SelId, @0x403e34 SetIndexedObj(0), @0x403e8c rdmGetAvaliableIAByOID (librdm @0x11c20), @0x403f10 SetIndexedObj(1), @0x403f68 path snprintf | BROADBAND_CGI |
| Save/SendRecv; result unchecked | @0x4066d4 Save; @0x4068b8 SendRecv; cmsgGetExecResult ×0 in cgiMain | BROADBAND_CGI |
| Edit CGIs render-only | 104-byte cgiMain stubs; import lists | BROADBAND_CGI |
| ccctest ADD mechanics | ccctest @0x402ca8–0x402ce8; libcmsg @0x556c/0x60a8/0x5f60 | RDM_OBJECT_CREATION |
| ADD-success vs transaction-fail independence | ccctest reply printer @0x4017dc (header bit 30 @0x40183c; per-action bit 0x40000000 @0x40188c) | RDM_OBJECT_CREATION |
| ccc_be does not execute action 7 | cccBeHandleMessage @0x41297c action loop | RDM_OBJECT_CREATION |
| Resolver parses trailing instance | libcccrdm @0x9538–0x95dc | RDM_OBJECT_CREATION |
| AddIndexChildObject gates/auto-alloc | librdm @0x134a0; instance-1 @0x137ec; rdmVerifyIAValue @0x11e48 | RDM_OBJECT_CREATION |
| Factory instances (.3 = IP only; DCS values) | aot-current-pdm-config.xml | RDM_OBJECT_CREATION §4 / PPP_PARAMETER_VALIDATION |
| Port mapping 3/0x08, 7/0x80 | libcccbe rtk_wan_port_mapping @0x37c84 (mode0 @0x37d74/@0x37d94; mode1 @0x37de4/@0x37e04; tail @0x37e14) | ETHERNET_WAN_HARDWARE |
| eth_Init composition | @0x38074; EthPhyEnable @0x3808c; mapping call @0x381a0 (PLT-resolved this session) | ETHERNET_WAN_HARDWARE |
| nas0_notag creation | createLayer3Interface @0x35348 (smuxctl @0x35468, tags @0x354c8/0x35640, mtu @0x35568) | ETHERNET_WAN_HARDWARE |
| Boot gate ETHER | ConfigLoaderFunc_Boot @0x50d08; strcmp @0x50ec8; eth_Init call @0x50ed4; linkdetection spawn @0x50d50 | BOOT_INITIALIZATION |
| linkdetection branches/ACS | @0x402454; GPON Save @0x402abc, URL @0x402a08; ETHER TxA @0x402eb8, nas0_notag @0x402bc0, gate @0x402f1c, TxB @0x4033c0, URL @0x403364; DISABLE @0x403434 | WAN_ACTIVATION_CALL_GRAPH |
| Unit formula / ppp131 | getPPPPdUnitNum_wrapper @0x38264 (ubfx @0x38290, fmt @0x4c3b8); beConfigWANByPPPoE call @0x6663c, `unit %s` @0x66640; setWanIpPppInterfaceName @0x346d0, PPP branch @0x348a8, `ppp%d` @0x4aeb0 | PPP_INTERFACE_BINDING |
| Options generation / AUTO_AUTH | beConfigWANByPPPoE @0x664a8; auth branches @0x66704, fallthrough @0x66904; service name @0x66968/0x66b3c | ETHERNET_PPPOE_LIFECYCLE |
| pppd launch | beWanEnablePPPv4Client @0x66ee4; libccc_executePPPv4Client @0x348f4, fmt @0x4aee0, cccBeSystemQueue @0x3496c | ETHERNET_PPPOE_LIFECYCLE |
| ip-up/ip-down generic 206/207 | rootfs scripts verbatim (hashes in table) | ETHERNET_PPPOE_LIFECYCLE |
| NAT generic; MSS global rule | libbemodules strings (grep counts 4/0/0); addTCPMSSDefaultRule strings | ROUTING_NAT_FIREWALL |
| Prior disasm corpus | analysis/disasm/*.txt (17 functions); rea-investigation/evidence/disassembly/*.asm; working/*_disasm.txt — spot-verified, not blindly trusted | REPOSITORY_INVENTORY |

## Working analyses produced this session
Three independent Capstone/pyelftools passes (broadband.cgi; RDM/ccctest/schema; lifecycle/routing) whose full texts are synthesised into the reports above with addresses preserved. Their headline disagreements with each other were resolved as follows: OID naming — the OIDTable reading (two passes agree) wins over the lifecycle pass's inherited labels for getLinkType operands, and the residue is logged as open contradiction C-11; getLinkType *behaviour* (operands/returns) is agreed by all passes.

## Evidence gaps (no evidence exists in the corpus)
Shipped HTML templates; the original failing ccctest script + syslog; any runtime capture of an Ethernet PPPoE session; live `/etc/ppp/default_options` content; bridge-membership captures. Each gap maps to an item in OPEN_QUESTIONS.md.
