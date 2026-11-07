# Rollback Plan — return to factory GPON operation

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Deterministic restoration to the pre-change GPON state, using native DELETE and the recorded baseline.
- **Files examined:** Factory PDM XML, ether-rollback.ccc / rollback.ccc artifacts (preserved), RDM analysis

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


> Static-analysis-derived procedure for a later human-controlled session. Not executed in this mission. Baseline values (ACS URL, WANMode, DefaultConnectionService) must come from the Phase-0 record in IMPLEMENTATION_PLAN.md, not from memory.

## Rollback triggers
Session cannot be established after Phase-4 fallbacks; LAN3/Wi-Fi regression; ACS/TR-069 must be restored urgently; operator decision.

## Procedure
1. **Remove the Ethernet PPP object** (native DELETE decrements the entries count and restores factory purity — prior SAF-004 analysis, STRONGLY INFERRED): in ccctest, `DELETE InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;` as its own transaction with SAVE; SEND. (DELETE is the command documented to take an instance number.) Verify `WANPPPConnectionNumberOfEntries` under .3 reads 0. Simply setting Enable=0 is **not** a clean rollback: the entries count stays 1 and link-type resolution may keep preferring PPP for .3.
   - On the Web path, the equivalent vendor operation is editing the Ethernet connection back to IP type (broadband.cgi PPP→IP conversion, @0x403f70) — this recreates WANIPConnection.1 `Eth_Internet`; acceptable, but the ccctest DELETE + existing factory IP profile is cleaner if the IP profile still exists. Choose one; do not do both blindly — check whether ConnDev.3.WANIPConnection.1 exists first.
2. **Restore the default route pointer:** `Layer3Forwarding.DefaultConnectionService` = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1` (and the IPv6 twin if it was changed).
3. **Restore WAN mode:** `WANSwitch.WANMode` = `GPON`; `WANEthernetInterfaceConfig.Enable` = 0 (factory XML shows Enable=1 in the export — **use the Phase-0 baseline value**, exports and live state may differ); `X_5067F0_GponInterafceConfig.Enable` = baseline value. Note the vendor spelling `GponInterafceConfig` — the correctly-spelled name fails (FE-3).
4. **Restore auto-detect:** `WANSwitch.WanAutoDetect` = 1 (factory-configured value in both PDM XMLs).
5. **Restore ACS:** `ManagementServer.URL` = Phase-0 baseline (expected production `http://tms.airtelbroadband.in:8103` — confirm against baseline; linkdetection's GPON switch also restores this value, but do not rely on it).
6. **Reboot** (mandatory in both directions — the GPON OMCI/SerDes and switch mapping re-initialise at Boot; prior RTSEQ-005 analysis, STRONGLY INFERRED).
7. **Verify GPON restoration:** fibre connected; `ppp111` up with ISP address; default route via ppp111; LAN3 + Wi-Fi clients online; `/proc/fc/ctrl/wan_port_mask` = 128; dev_port_mapping port 7. Process cleanup on object deletion (`beWanDisableClient`: SIGTERM then SIGKILL to pppd, smuxctl --if-delete of nas0_notag) is backend-automatic per prior disasm — verify pppd for nas0_notag is gone (`ps | grep pppd`) rather than killing anything manually.
8. **Full-config fallback:** if individual restorations fail, restore the Phase-0 backup (`ether-backup.lz` / saved config) through the UI's backup/restore, then reboot and re-verify step 7. The preserved artifacts `ether-rollback.ccc` and `rollback.ccc` in DUMPFILES are prior rollback scripts — read them before use and reconcile every line against steps 1–5; do not execute them blind.

## What rollback does NOT require
No firmware flashing, no factory reset (a factory reset is the last resort only if the config store itself is corrupted — it would also erase the GPON credentials profile and is **not** part of this plan).

## Follow-up supersession note (2026-11-07, later session)
This plan is **superseded procedurally** by `CONCRETE_IMPLEMENTATION_CHECK_AND_ROLLBACK.md` §8/§10. Corrections to the steps above: (1) Step 1's word **"Deterministic" is withdrawn** — DELETE's parser/execution semantics are now fully audited (ccctest @0x402da8; no parent SEL; SAVE+SEND required as its own transaction), but the physical purge is mark-and-sweep with **UNKNOWN sweep timing**, so the count read-back gate is mandatory; and DELETE is only the right tool in the ADD world — in the conversion world the vendor conversion-back (broadband.cgi @0x403f70) is preferred, and doing both can create a duplicate WANIPConnection.2. (2) Step 1's claim that Enable=0 rollback is unclean because "link-type resolution may keep preferring PPP" rested on the DISPROVEN link-type reading — getLinkType returns a media type (GPON/Ethernet), not PPP/IP; the count argument stands on its own. (3) Step 3: baseline values are now known exactly — Eth Enable and Gpon Enable are both **absent** in the Phase-0 baseline export (restore the baseline state, not factory 1). (4) Step 4: WanAutoDetect=1 is confirmed as the Phase-0/factory value, but note preserved rollback.ccc and linkdetection's GPON switch both write 0 — the new document flags this as a deliberate operator choice, defaulting to baseline 1. (5) Step 6's "mandatory in both directions" is upgraded from STRONGLY INFERRED to CONFIRMED STATIC, with the BE-write auto-reboot vs SET_NO_BE manual-reboot distinction added. (6) Step 7's beWanDisableClient cleanup is confirmed (SIGTERM→sleep 2→SIGKILL, pidfile removal; smuxctl --if-delete via deleteLayre3Interface @0x35f60) with the deletion→L3-down hop STRONGLY INFERRED; add: the PPP options file is NOT deleted (inert), and DefaultConnectionService is NEVER auto-repaired — step 2 is mandatory, not bookkeeping.
