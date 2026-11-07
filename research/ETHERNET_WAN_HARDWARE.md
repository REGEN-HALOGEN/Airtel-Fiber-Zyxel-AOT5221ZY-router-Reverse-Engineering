# Ethernet WAN Hardware Initialization

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Switch/PHY init, WAN port mapping, interface creation, /proc interfaces.
- **Files examined:** DUMPFILES/libcccbe.so, DUMPFILES/linkdetection, analysis/disasm/{libcccBeWan_eth_Init,rtk_wan_port_mapping,createLayer3Interface}.txt

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


## Findings
- **CONFIRMED STATIC — `rtk_wan_port_mapping` @0x37c84 (libcccbe.so):** signature `(int mode, char *ifname)`, NULL ifname → −1. Mode 0 (Ethernet) @0x37d68: `mov w5,#3`; formats `echo %d %s > %s` → `echo 3 <ifname> > /proc/ni/dev_port_mapping`; `mov w0,#8; str w0,[global 0x6bc04]`. Mode 1 (GPON) @0x37dd8: port 7, mask 0x80. Shared tail @0x37e0c: if mask global > 0, `echo %d > /proc/fc/ctrl/wan_port_mask`. ⇒ **LAN4 = port 3 / mask 0x08; GPON = port 7 / mask 0x80.**
- **CONFIRMED STATIC — `libcccBeWan_eth_Init` @0x38074:** PLT-resolved calls this session: `EthPhyEnable(1)` @0x3808c (the `1` is an enable flag, not a port number — port attribution to port 3 comes from the final mapping call, STRONGLY INFERRED for the PHY part); `smuxctl --if %s --set-if-rsmux --set-if-rx-policy DROP --set-if-tx-policy CONTINUE --set-if-rxmc-policy DROP --set-if-rx-multi 1`; `echo switch_on > /proc/rtk_smuxdev/hw_vlan_filter`; `echo enable %s MC > …/hw_vlan_filter`; `echo refresh %s > …/hw_vlan_filter`; final `rtk_wan_port_mapping(0, name)` @0x381a0. The GPON twin `libcccBeWan_gpon_Init` @0x37e5c is near-identical with `rtk_wan_port_mapping(1, …)` plus extra rxmc drop rules.
- **CONFIRMED STATIC — `createLayer3Interface` @0x35348** is what creates the netdevices (not eth_Init): dispatches on `[obj+4]` (0=IP, 1=PPP @0x35814); `/bin/smuxctl --if-create-name %s %s --set-if-rsmux`, untagged appends `--tags 0`, tagged appends `--tags 1 --filter-vid 0x%x 1` with pop-tag/push-tag rules; `ifconfig %s mtu 1500`; `ifconfig %s txqueuelen 10`. Names are data-driven (base `nas0` + `_notag` or `_<vid>`) — no Ethernet/GPON literal.
- **CONFIRMED STATIC — link polling:** linkdetection function @0x40223c hardcodes `mov w0,#3` for the port-3 link check via `rt_port_link_get` (prior disasm, corroborated this session); GPON presence is polled via `popen("diag pon get transceiver rx-power")` searching `Rx Power: ` (prior report, STRONGLY INFERRED this session — string present, call site not re-disassembled).
- **LAN3:** port 2 / 0x04 appears in none of these functions (CONFIRMED STATIC absence). No bridge manipulation occurs in any of them.

## Boot dependence
eth_Init is called from the Boot config loader only when `WANMode=="ETHER"` and Ethernet Enable is set (see BOOT_INITIALIZATION_ANALYSIS.md). Changing WANMode at runtime therefore does not, by any code path traced, immediately remap the switch — STRONGLY INFERRED reboot requirement.

## Contradictions
Prior `activation-sequence.md` step 7 attributes PHY power, nas0_notag creation, mask write, options generation and pppd spawn all to eth_Init — DISPROVEN attribution (five separate functions); the net sequence is correct.

## Unknowns
- Whether any non-Boot caller of eth_Init exists (L4ObjectChanged path not fully enumerated) — runtime check U2.
- Exact PHY register effect of `EthPhyEnable(1)` (opaque Realtek API in librtk).
