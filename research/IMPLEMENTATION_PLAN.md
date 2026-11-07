# Implementation Plan — LAN4 Ethernet WAN + PPPoE (deployment-ready, human-controlled)

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Precise, safe deployment procedure for a later human-controlled validation session. NOT executed in this mission.
- **Files examined:** All preceding research reports

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


> **READ FIRST — limits of this plan.** This plan is built entirely from static analysis. **Static analysis does not prove a live PPPoE session.** It proves the firmware contains a complete, generic implementation path and identifies the exact objects, parameters and order of operations. Whether the session establishes against the Syrotech ONT / ISP BRAS (discovery, authentication, VLAN reality, BRAS behaviour) can only be known from the runtime observations listed per phase. Execute phases in order; do not skip the verification gates. PPPoE credentials are entered by the operator at the device UI/CLI at execution time — they appear nowhere in this plan or the repo.

## Target end state
Syrotech GPON ONT → Ethernet → AOT5221ZY LAN4 (port 3) as WAN; AOT5221ZY runs the PPPoE client on `nas0_notag`, session interface `ppp131`, NAT + routing + firewall for LAN3 + Wi-Fi (br0) clients. ISP profile: service `3jglobal`, MTU/MRU 1480, `AUTO_AUTH`, no VLAN (primary assumption — see Phase 4 fallback F2).

## Phase 0 — Backup & baseline (mandatory)
1. Export current config from the Web UI / keep the existing artifacts (`ether-backup.lz`, PDM XML) untouched; record current `WANMode`, `WanAutoDetect`, `ManagementServer.URL`, DefaultConnectionService.
2. Record baseline runtime observations: `bridge link` (LAN3 in br0), `ip link` (interfaces), `iptables -t nat -S`, current working state of LAN3 AP + Wi-Fi clients.
3. Confirm rollback media: ROLLBACK_PLAN.md + the factory GPON profile (ConnDev.1.WANPPPConnection.1) is **not** to be deleted in any path.

## Phase 1 — Choose the creation path
**Path A (preferred, vendor-supported): Web UI conversion** — broadband.cgi's IP→PPP conversion of the existing `Eth_Internet` profile (WEB_UI_CONFIGURATION_WORKFLOW.md). Use it if the ETH edit page exposes a PPPoE/connection-type option.
**Path B (fallback): minimal ccctest creation** — only if Path A's option is hidden in the shipped HTML. Path B exists to *discriminate* the commit-NACK root cause, not to repeat FE-2:
```
# Transaction 1 — creation ONLY (note: NO trailing .1, NO bundled SETs)
REQUEST;
ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection;
SAVE;
SEND;
```
Gate: PPP child count under .3 must read **1** and ccctest must print `transaction successful !!`. Capture any `validation error code: 0x…` line and syslog (`cccRdm*`, `rdmVerifyIAValue`) — that output *is* the root-cause evidence if it NACKs again. If Transaction 1 succeeds, configure in a **second** transaction (SEL the committed `.1`, then SETs with exact types: Enable boolean 1; Name string; Username string; Password string; PPPoEServiceName string `3jglobal`; X_5067F0_PPPAuthenticationProtocol string `AUTO_AUTH`; MaxMRUSize / X_5067F0_MaxMTUSize with their schema numeric types — verify type words from the schema before use, see PPP_PARAMETER_VALIDATION caution; NATEnabled boolean 1; X_5067F0_Enable_VLANID boolean 0; ConnectionType string `IP_Routed`), then SAVE; SEND. Do **not** set DefaultConnectionService in the same transaction as the ADD.

## Phase 2 — WAN mode ETHER (order matters)
1. Ensure the PPP object exists and is Enabled (Phase 1 gate passed).
2. Set WAN mode to ETHER by **one** of: Web UI Restart control (broadband page), or an RDM transaction setting `WANSwitch.WANMode` string `ETHER` + `WANEthernetInterfaceConfig.Enable` boolean 1 (object OID 0xca; use the correctly-spelled path `InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig`). Avoid relying on linkdetection auto-switch (it also creates the IP profile and clobbers ACS — if it has already run, that is acceptable; note the ACS state).
3. Set `Layer3Forwarding.DefaultConnectionService` (separate transaction) to `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`. (On Path A this is done by the CGI if the default-WAN flag was submitted — verify, don't assume.)
4. **ACS repair:** read `InternetGatewayDevice.ManagementServer.URL`; if it equals `http://testacs.airtelbroadband.in:8103/`, restore `http://tms.airtelbroadband.in:8103`. (Verify the production value from the pre-change baseline recorded in Phase 0 — do not trust this plan over your baseline.)
5. Do **not** yet set WanAutoDetect=0 (linkdetection must not fight the transition, but disabling it before ETHER is proven removes the GPON fall-back detection; Phase 5 revisits this).

## Phase 3 — Reboot and hardware verification
1. Connect the Syrotech ONT Ethernet to **LAN4**; keep the LAN3 AP and a Wi-Fi client attached for regression checks. Reboot the AOT5221ZY.
2. Runtime observations (the proof for criteria 1–3): `/proc/ni/dev_port_mapping` shows port 3 → nas0; `/proc/fc/ctrl/wan_port_mask` = 8; `ip link` shows `nas0` and `nas0_notag`; syslog shows eth init / smuxctl activity. If the mask is still 128/GPON, stop — WANMode/Enable gate failed; re-check Phase 2 values in RDM.

## Phase 4 — Session verification (the proof static analysis cannot give)
1. `ip link` / pidfile: **`ppp131`** exists (not ppp111). Generated file `/etc/ppp/options_nas0_notag` contains `unit 131`, `linkname`, `pppoe_srv_name 3jglobal`, `mtu 1480`, `mru 1480`. `/tmp/pppd-info.tmp` and syslog show discovery reaching PADR and authentication succeeding (AUTO_AUTH ⇒ PAP or CHAP as offered by the BRAS).
2. `ip addr show ppp131` has the ISP address; `ip route` default via ppp131; `/etc/resolv.conf` / dnsmasq contain peer DNS; `iptables -t nat -S` shows MASQUERADE `-o ppp131`; `iptables -S FORWARD` shows the clamp + forwarding state.
3. End-to-end: LAN3 client and Wi-Fi client both reach the Internet; LAN3 still in br0 (`bridge link`); Wi-Fi associated.
4. **Fallbacks if the session does not establish:**
   - F1 (no PADI response): confirm ONT link on LAN4, confirm nas0_notag carrier; re-check that the TP-Link still connects on the same ONT port (isolates ONT/BRAS vs AOT config).
   - F2 (VLAN): the no-VLAN assumption comes from the TP-Link's config, not from the ISP contract. If discovery times out with everything else correct, try the tagged variant once: `X_5067F0_Enable_VLANID` boolean 1 + `X_5067F0_VLANID` uint16 = the ISP VLAN **only if the operator has an authoritative value** (do not guess-scan VLAN IDs); expect `nas0_<vid>` and `options_nas0_<vid>`, interface still ppp131. Revert if no PADR.
   - F3 (auth failure): re-enter credentials at the UI (masked-sentinel trap: `"****************"` means *unchanged* in broadband.cgi); confirm service name spelling `3jglobal`; try explicit `PAP` then `CHAP` only if AUTO_AUTH negotiation is shown failing in syslog.
   - F4 (session up, no LAN Internet): check DefaultConnectionService (U7 test), NAT rule presence, and whether Event 206 fired (`/var/wan_connection_notify/nas0_notag_connection_is_up` exists).

## Phase 5 — Hardening after success
1. Set `WANSwitch.WanAutoDetect` boolean 0 **only after** ETHER PPPoE is verified, so linkdetection cannot flip the unit back or re-clobber ACS on a transient GPON-side signal. Record that this disables automatic GPON fall-back (rollback restores it).
2. Re-verify ManagementServer.URL is the production baseline value.
3. Export the working config as the new known-good backup; label it distinctly from the factory/GPON backups.
4. Log all Phase 3–4 observations back into the repo (new runtime-evidence report) — they convert this plan's STRONGLY INFERRED items into CONFIRMED FROM RUNTIME EVIDENCE.

## Stop conditions
Brick-risk actions are out of scope throughout: no firmware flashing, no bootloader work, no GPON/SerDes changes, no deletion of the GPON PPP profile. Any phase whose gate fails twice → stop and execute ROLLBACK_PLAN.md.
