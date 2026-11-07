# Web UI Configuration Workflow

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** The vendor-supported Web UI path to Ethernet PPPoE, reconstructed from broadband.cgi — what the user clicks, what the backend does, and what cannot be verified without the HTML.
- **Files examined:** DUMPFILES/broadband.cgi + edit CGIs; template HTML absent from corpus

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


## What the backend supports (CONFIRMED STATIC)
- A **Broadband list page** (broadband.cgi, `pages/network/broadband/broadband.html`) listing existing WAN connections for GPON and Ethernet, each row carrying a hidden `wanIA` (`"1,1,1"` GPON / `"1,3,1"` Ethernet — STRONGLY INFERRED values) and `wanType`.
- An **Edit page per connection** (render-only edit CGIs) whose form POSTs back to broadband.cgi with: save-flag, `RN_EncapFlag` (encap: IP/PPPoE), `RN_ModeFlag` (routed/bridged), `RN_Default_WAN_H` (make-default flag), `RN_Active_H` (Enable), `RN_Name`, `RN_UserName`, `RN_Password`, `RN_ServiceName`, `RN_PPPAuth`, `RN_ConnNail` (trigger), `RN_TimeOut`, `RN_MTU`, `RN_MRU`, VLAN fields, `RN_SelNAT`, NAT type, multicast fields.
- A **WAN-mode Restart control** on the broadband page (`RestartBtn` + `wanMode` GPON/ETHER) that flips the physical-interface Enables and `WANSwitch.WANMode` in one transaction.

## The workflow (deployment form; execution is a later human-controlled step)
1. Back up current config (existing artifacts: `ether-backup.lz`, PDM XML export) — see IMPLEMENTATION_PLAN Phase 0.
2. Broadband page → set WAN mode to **ETHER** via the Restart control (or let linkdetection auto-switch on LAN4 link-up — not recommended, see ACS hazard) → reboot.
3. Broadband page → **Edit** the Ethernet connection (`Eth_Internet`, wanIA 1,3,1) → change connection type/encap to **PPPoE**, routed mode → fill: Username/Password (user-entered only), Service name `3jglobal`, Authentication `AUTO_AUTH`, MTU 1480, MRU 1480, VLAN **disabled**, NAT enabled, Enable/Active on, set as default WAN → Save.
4. Backend effect (one transaction): old WANIPConnection.1 under .3 deleted (PortTriggering preserved), WANPPPConnection.1 created under .3, all PPP params set, DefaultConnectionService updated (if the default flag was submitted), Save + SendRecv.
5. Reboot → verify per IMPLEMENTATION_PLAN Phase 4 (object persists, ppp131 exists, route/NAT/DNS correct, LAN3/Wi-Fi intact, ACS URL restored).

## What cannot be verified from this corpus (UNKNOWN)
- Whether the shipped `broadband.html` / `wanRemoteNode_ETH_Edit.html` actually *render* the PPPoE encap option for the Ethernet row (ISP-customised UI may hide it). The templates are absent from the repo and the rootfs dump. If the option is hidden in the UI, the backend path still exists but is unreachable from the page — the fallback is the minimal ccctest plan (IMPLEMENTATION_PLAN Path B). This is the single largest open question for the Web path, and it is a *UI* question, not a backend one.
- Exact form field labels/order in the shipped firmware language pack.

## Safety notes
- The CGI never reports backend failure (result unchecked) — after Save, the workflow must re-read the connection list / RDM state rather than trusting the page.
- Password field: the CGI treats the literal `"****************"` as "unchanged" — when editing, leave the masked value only if re-using the stored GPON credentials is intended; for the ISP Ethernet account, type the real password (it is transmitted to the router's own CGI over the LAN UI session; it is never recorded in these reports).
