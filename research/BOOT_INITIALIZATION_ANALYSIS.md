# Boot Initialization Analysis

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Boot ordering, the ConfigLoaderFunc_Boot gate, L0–L4 layer loads, linkdetection spawn, and the reboot question.
- **Files examined:** libbemodules.so, libcccbe.so, rootfs etc/init.d/ccc_init.sh (per prior reports)

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


## Sequence (CONFIRMED STATIC unless labelled)
1. `ccc_init.sh start()` (prior reports; script present in rootfs): copies `/usr/var/*` to `/var/`, links config.rdm, starts `ccc_mr & ccc_das & ccc_be &`.
2. `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot` (libbemodules @0x50d08):
   - @0x50d50 spawns linkdetection: `cccBeDoSystem("/usr/sbin/linkdetection &")`-form (format `"%s &"`).
   - Iterates WANDevice objects: OID 0xca object → Eth Enable byte; OID 0xc7 object → GPON-side byte. (Operand/return structure CONFIRMED; object naming per OIDTable — same C-11 caveat as the lifecycle report.)
   - @0x50eb8–0x50ed4: if EthEnable && `strcmp(WANMode, "ETHER")==0` → `libcccBeWan_eth_Init`.
   - Else GPON branch → `libcccBeWan_gpon_Init`; disabled branch → eth_Disabled handling.
3. `L0ConfigLoad` @0x50348 loads layers in ascending order L1 (@0x50494) → L2 (@0x5062c) → L3 (@0x50694) → L4 (@0x507e0) (prior disasm; STRONGLY INFERRED this session). Hardware init (L1-time) therefore completes before the L3 walk loads the PPP object and starts pppd.
4. Pre-reboot gatekeeper (prior disasm, STRONGLY INFERRED): on a runtime SEND committing a new PPP object, `L3ObjectChanged` @0x4ddc4 checks `checkWANDeviceObjectRequestedLinkIsUp` @0x67964; with the Ethernet PHY unmapped the link reads down and the handler exits (@0x4ee4c branch) without launching pppd — i.e. a pre-reboot commit is expected to be a safe no-op for session startup. Not re-disassembled this session.

## The reboot question
- CONFIRMED STATIC: the Boot path calls eth_Init under ETHER; linkdetection's switch only edits RDM (Save/Send) and never calls eth_Init.
- STRONGLY INFERRED: **a reboot is required** to engage port-3 remapping after changing WANMode. Prior "bound exclusively to Boot — CONFIRMED" is downgraded: `ConfigLoaderFunc_L4ObjectChanged` exists in the same module and a complete caller enumeration of the eth_Init PLT slot was not performed by any pass. Runtime check U2 settles it (change WANMode live, watch `/proc/ni/dev_port_mapping` and `/proc/fc/ctrl/wan_port_mask` before any reboot).
- Rollback symmetry (prior disasm, STRONGLY INFERRED): restoring WANMode="GPON" triggers `libcccBeWan_doWanModeChange` @0x36d3c which logs an OMD reboot reason — a reboot is likewise required to restore GPON.

## ACS side effect at boot
None at boot itself; the ACS URL clobber happens inside linkdetection's switch transactions whenever they run (see WAN_ACTIVATION_CALL_GRAPH). If WanAutoDetect remains 1, linkdetection may re-run a switch (and re-clobber) on link events — the deployment plan therefore sets WanAutoDetect=0 only *after* ETHER is established and verified, and restores the production ACS URL explicitly.
