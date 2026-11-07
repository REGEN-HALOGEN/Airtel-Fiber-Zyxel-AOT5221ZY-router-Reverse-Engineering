# WAN Activation Call Graph

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Boot-time and mode-switch call graphs for Ethernet WAN activation, incl. linkdetection @0x402454 branch analysis.
- **Files examined:** DUMPFILES/linkdetection, libbemodules.so, libcccbe.so; prior analysis/disasm + rea-investigation/03-ethernet-wan

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


## Boot graph (CONFIRMED STATIC unless labelled)
```
etc/init.d/ccc_init.sh: ccc_mr & ccc_das & ccc_be &
└─ OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot (libbemodules @0x50d08)
   ├─ @0x50d50: cccBeDoSystem("/usr/sbin/linkdetection &")        ; auto-switch daemon spawned
   ├─ reads WANEthernetInterfaceConfig.Enable, GponInterafceConfig.Enable, WANSwitch.WANMode
   ├─ if EthEnable && WANMode=="ETHER" (strcmp @0x50ec8) → libcccBeWan_eth_Init @0x38074
   │    └─ EthPhyEnable(1); smuxctl rsmux; hw_vlan_filter on/enable/refresh; rtk_wan_port_mapping(0,"nas0")
   │         └─ echo 3 nas0 > /proc/ni/dev_port_mapping ; echo 8 > /proc/fc/ctrl/wan_port_mask
   └─ else GPON branch → libcccBeWan_gpon_Init @0x37e5c (symmetric, mapping mode 1)
└─ L0ConfigLoad @0x50348 → L1 → L2 → L3ConfigLoad → L3ConfigInit (libbemodules @0x4f440)
   └─ beWanDoLayer3InterfaceAction → link-type resolution → (PPP) constructL3WANDevName @0x698dc
        → setWanIpPppInterfaceName @0x346d0 → createLayer3Interface @0x35348 (nas0_notag)
        → beConfigWANByPPPoE @0x664a8 (options file) → beWanEnablePPPv4Client @0x66ee4
        → libccc_executePPPv4Client @0x348f4 → /bin/pppd … nas0_notag &
```
Layer ordering L1 (hardware) before L3 (PPP) is CONFIRMED STATIC from prior disasm of L0ConfigLoad @0x50348, corroborated by symbol/log strings this session (STRONGLY INFERRED for the exact sub-ordering inside L3ConfigInit).

## linkdetection `linkdetect_switch_WanMode` @0x402454 (CONFIRMED STATIC, fresh PLT/string scan)
Prologue frame 0x360; arg ∈ {"GPON" @0x4039b8, "ETHER" @0x403d70, "DISABLE" @0x404040}; `rdmInit("config.xml","config.rdm")`, `cmsgInit("linkdetection_rtk")`, module = `cmsgGetModuleIdByName("ccc_das")`. **Every transaction ends `cmsgRequestSave` + `cmsgSendRecv`** (CMSG SAVE+SEND), then cmsgFree×2, unregister, rdmDeInit.

- **GPON branch** (strcmp @0x4025c8; Save @0x402abc): one transaction setting WANMode="GPON", WanAutoDetect, Gpon Enable, Eth Enable, ConnDev.1 PPP Enable, ConnDev.2 IP Enable, ConnDev.3 IP Enable, NDPPD.Enabled, IPv6PD interface → ConnDev.1 PPP, Layer3Forwarding.DefaultConnectionService → ConnDev.1.WANPPPConnection.1 (and IPv6 twin), **ManagementServer.URL = `http://tms.airtelbroadband.in:8103`** (@0x402a08), OverIPv6, DeviceRecognition.Enable.
- **ETHER branch** (strcmp @0x402b10): Tx A (Save @0x402eb8) — if `WANConnectionDevice.3.WANIPConnection.1` is missing, create it via SetIndexedObj with Name="Eth_Internet", X_5067F0_InterfaceName="nas0_notag" (@0x402bc0), gateway/subnet/IP "0.0.0.0", SERVICELIST="TR069", RIPVersion="N/A", VLAN/IGMP/DualStack flags, DNS.1–.3 children. Gate: `access("/tmp/ADD_WAN_update_181DM_done", …)` @0x402f1c. Tx B (Save @0x4033c0) — WANMode="ETHER", Gpon/Eth Enables, ConnDev.1 PPP / ConnDev.2 IP / ConnDev.3 IP Enables, NDPPD, IPv6PD → ConnDev.3 **IP**, DefaultConnectionService → ConnDev.3 **WANIPConnection.1** (v4+v6), **ManagementServer.URL = `http://testacs.airtelbroadband.in:8103/`** (@0x403364), OverIPv6.
- **DISABLE branch** (strcmp @0x403434; Save @0x4034c4): only WanAutoDetect.
- **Auto-detect disarm:** at startup linkdetection reads WANSwitch; if `WanAutoDetect == 0` it branches over all switching checks (prior analysis @0x401a08–0x401e10; STRONGLY INFERRED this session).

## Required vs side effects (for Ethernet PPPoE)
| Change | Class |
|---|---|
| WANMode="ETHER"; WANEthernetInterfaceConfig.Enable=1 | **Strictly required** (Boot gate) |
| WANPPPConnection child under ConnDev.3, Enable=1 | **Strictly required** — linkdetection never creates it |
| DefaultConnectionService → ConnDev.3.WANPPPConnection.1 | **Strictly required** — linkdetection points it at the IP object; must be overwritten |
| Gpon Enable=0; disabling ConnDev.1 PPP / ConnDev.2 IP; enabling ConnDev.3 IP | Stock transition, not required by any traced gate (PPP presence takes link-type priority — but see C-11 caveat in FAILED_EXPERIMENTS) |
| NDPPD / IPv6PD retargeting | IPv6-only relevance |
| ManagementServer.URL → testacs (ETHER) | **Pure side effect / hazard** — restores to production only on GPON switch; plan must restore it manually |
| Eth_Internet IP profile creation; `/tmp/ADD_WAN_update_181DM_done` gate | Vendor transition machinery; the IP profile is however the **substrate for the broadband.cgi conversion path** |

## Forwarding changes
linkdetection itself performs no forwarding/hardware writes — it only mutates RDM via CMSG (CONFIRMED STATIC). Forwarding effects occur in ccc_be when the committed config is loaded (Boot/L3 walk) and on Event 206.
