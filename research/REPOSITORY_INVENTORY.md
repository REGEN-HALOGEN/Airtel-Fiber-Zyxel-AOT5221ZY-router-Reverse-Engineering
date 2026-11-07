# Repository Inventory

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Full inventory of the cloned repository. Machine-readable per-file inventory (path, type, arch, size, SHA-256 for all 2,601 files) is committed alongside as `REPOSITORY_INVENTORY.csv`.
- **Files examined:** Entire repo at commit 5b1dfca

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


## Summary (CONFIRMED STATIC, generated this session)
- Files (excluding .git): **2,601**; total bytes **144,271,796** (~162 MB on disk incl. .git).
- Single commit on main: `5b1dfca feat: initial commit of Airtel AOT5221ZY / Zyxel PX5311-R0 reverse engineering project`.
- Format counts (top): ASCII text 1,305 · empty 364 · ELF64 shared objects 266 · POSIX shell scripts 178 · Python scripts 161 · ELF64 executables 115 · ELF64 relocatable (.ko etc.) 109 · ELF64 PIE executables 13 · XML 4 · LZMA 4 · Device Tree Blobs 3.
- Top-level layout: `README.md`, `REVERSE ENG.md` (= `REVERSE_ENG.md`, duplicate), `DUMPFILES/` (45 curated artifacts, 47 MB), `analysis/` (prior Python analysis scripts, disasm text, reports), `full-router-dump/` (rootfs tree, flash, rea-investigation report tree with ~200 working scripts).

## Key artifact classes
- **Firmware binaries (DUMPFILES/):** broadband.cgi, wanRemoteNode_ETH_Edit.cgi, wanRemoteNode_GPON_Edit.cgi, linkdetection, ccc_be, ccc_das, ccctest.bin, diag, led_ctrl, ledctl_agent; libraries libcccbe, libcccrdm, librdm, librdmcommon, libcmsg, libbe, libbeEvents, libbemodules, librtk(-full), libwebutil, libx2rrdm, libledctl, libcrypto(-mstc); kernel modules ca-rtk.ko, ca-ne.ko, ca-rtk-epon-drv.ko, fc_8277c.ko; images ubi_k0.bin = ubi_k1.bin (duplicate SHA-256).
- **RDM/config:** config.rdm = runtime-config.rdm (identical, LZMA), config_rdm_decompressed.bin (3,145,728 B), aot-current-pdm-config.xml = aot-current-pdm-backup.xml (identical), aot-current-romfile, ether-backup.lz, ether-rollback.ccc, rollback.ccc. **Correction:** `analysis/config_rdm_decoded.xml` is NOT XML — it is byte-identical to the decompressed binary image.
- **Rootfs:** `full-router-dump/filesystem/rootfs/` — full tree incl. `etc/ppp/{ip-up,ip-down,default_options,_options_static,…}`, `lib/MSTC/*`, `bin/pppd`, `lib/pppd/2.4.7/rp-pppoe.so` (= libpppoe.so in MSTC path per prior audit; hash in table), init scripts. Rootfs copies of the DUMPFILES binaries are hash-identical to the DUMPFILES copies (CONFIRMED STATIC for ccctest, ccc_be, librdm, libcccrdm, libcmsg, libcccbe, libbemodules, libbeEvents).
- **Prior disassembly:** `analysis/disasm/*.txt` (17 functions), `full-router-dump/analysis/rea-investigation/evidence/disassembly/*.asm`, `working/*_disasm.txt` — spot-verified against fresh Capstone disassembly this session (broadband cgiMain bounds and call sites match).
- **Prior reports:** `analysis/reports/` (inventory-summary, technical_report_pppoe_nas0_notag), `full-router-dump/analysis/rea-investigation/` (MASTER_FINDINGS, ~15 audit files, 00–10 section trees). Read in full for the sections relevant to §§5–11 of the brief; critical claims independently re-verified — see FAILED_EXPERIMENTS_AND_CONTRADICTIONS.md.
- **Missing artifacts (precise):** (a) **all HTML templates** referenced by the CGIs (`pages/network/broadband/*.html`) — absent from repo and rootfs dump; (b) the original failing ccctest script and its syslog — absent; (c) Ghidra/IDA project files — absent (prior work was Capstone-script based).

## Duplicates / integrity notes
Exact duplicate groups confirmed by SHA-256 include ubi_k0/ubi_k1, librtk/librtk-full, the two PDM XMLs, config.rdm/runtime-config.rdm. Several prior reports cite hashes that do **not** match the committed artifacts (broadband.cgi in README; librdm/libcccrdm/ccctest in ppp-object-creation-audit; libbeEvents/libpppoe in ppp-routing-nat-audit) — treat those reports' hash tables as stale, conclusions re-baselined in this research set.
