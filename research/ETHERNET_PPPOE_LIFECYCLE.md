# Ethernet PPPoE Lifecycle

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** End-to-end chain: profile → WAN mode → boot init → port mapping → nas0_notag → PPP object → config generation → pppd → discovery/auth → ppp131 → IP/DNS → route/NAT/firewall, incl. Event 206.
- **Files examined:** libbemodules.so, libcccbe.so, libbeEvents.so, rootfs etc/ppp/*, bin/pppd, libpppoe.so

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


## Chain (each link CONFIRMED STATIC unless labelled)
1. **Ethernet WAN profile** — factory `Eth_Internet` = ConnDev.3.WANIPConnection.1 (IP). Conversion (broadband.cgi) or minimal ccctest creation produces ConnDev.3.WANPPPConnection.1 with Enable=1, Username/Password [entered by user at deployment; never stored in these reports], PPPoEServiceName=`3jglobal`, MTU/MRU 1480, auth `AUTO_AUTH`, NATEnabled=1, VLAN disabled (default plan).
2. **WAN mode ETHER** — WANSwitch.WANMode="ETHER" + WANEthernetInterfaceConfig.Enable=1 (Web RESTART branch, linkdetection, or RDM edit).
3. **Boot init** — ConfigLoaderFunc_Boot @0x50d08 → eth_Init @0x38074 (see WAN_ACTIVATION_CALL_GRAPH).
4. **Port mapping** — `echo 3 nas0 > /proc/ni/dev_port_mapping`; `echo 8 > /proc/fc/ctrl/wan_port_mask`.
5. **nas0 / nas0_notag** — `createLayer3Interface` @0x35348 via smuxctl `--if-create-name`; untagged `--tags 0` ⇒ `nas0_notag`; MTU 1500 / txqueuelen 10 on the L2 device. Prior detailed claims (carrier MANUAL/AUTO sequencing, `getMatchedGPONInfo` branch) are STRONGLY INFERRED from prior disasm, not re-verified this session.
6. **Link-type resolution** — L3 walk decides PPP vs IP per connection device. Raw disasm of `libcccBeWan_getWANDeviceObjectRequestedLinkType` @0x34334 is CONFIRMED (queries OID 0xc7 object for the WANDevice IA; byte0 != 0 → return 1 = PPP; else OID 0xca byte+4 → IP encoding; null → 2), but the **naming of OIDs 0xc7/0xca at this call site is CONTRADICTED** by the OIDTable (0xc7=GponInterafceConfig, 0xca=WANEthernetInterfaceConfig) vs prior reports (PPP/IP count objects). See FAILED_EXPERIMENTS C-11 — the function's operand values and return encoding are certain; which object structs they denote needs one more targeted pass. This does not affect links 1–5 or 7–12, which are independently evidenced.
7. **Config generation** — `beConfigWANByPPPoE` @0x664a8 → `/etc/ppp/options_nas0_notag` (details in PPP_INTERFACE_BINDING / MASTER PPP-2). Template source: copies `default_options`, or `_options_static` for Static addressing. **Caveat:** in this dump `default_options` is **0 bytes** and the quoted template content lives in `_options_static` — the two files' contents look swapped vs prior descriptions; which is populated on a live unit is UNKNOWN (runtime check U3).
8. **pppd launch** — `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &` (no `-d` in this path; `-d` variants exist only in libCmd.so debug/restart templates, which use the same dual-%s substitution of X_5067F0_IfName).
9. **Discovery/auth** — pppd loads rp-pppoe plugin (rootfs `lib/pppd/2.4.7/rp-pppoe.so`; MSTC `libpppoe.so` @hash in table): `setdevname_pppoe` consumes the positional device name, resolves the interface index, opens AF_PACKET discovery (ETH_P_PPP_DISC per prior audit — STRONGLY INFERRED this session at symbol/string level). AUTO_AUTH ⇒ no refuse-* lines ⇒ PAP/CHAP negotiated freely. Service name from `pppoe_srv_name 3jglobal` in the options file.
10. **ppp131** — pppd honours `unit 131` + `linkname` (X_5067F0_InterfaceName) ⇒ interface `ppp131`, pidfile `/var/run/ppp131.pid` convention in libCmd templates. IPCP assigns IP + peer DNS (pppd `usepeerdns` in the static template; writes `/etc/ppp/resolv_%s.conf`).
11. **Event 206** — pppd runs `/etc/ppp/ip-up ppp131 nas0_notag …`; the script writes a ccctest file containing `EVENTNOTIFY 206 string ppp131;` (generic `$REALNAME`) and executes it. ccc_be Event 206 handlers (libbeEvents symbols: Route/NAT/DNS/L3Forwarding event handlers, `updateDefaultRouteByLinkType`, `eventRouteIPChange`, `configDNSServers`, `Dnsmasq_Conf_Creation`) perform route/DNS/NAT follow-up — handler bodies not re-disassembled this session: architecture CONFIRMED at symbol/string level, address-level prior detail LIKELY.
12. **Steady state** — default route via ppp131 (subject to DefaultConnectionService, see ROUTING analysis), NAT MASQUERADE on ppp131, MSS clamp via global TCPMSS rule, LAN3/Wi-Fi via br0.

## `createWANPPPConnectionCfgFile` @0x6a7c0 (libbemodules)
CONFIRMED limited role: not the options writer. Returns −1 if [obj+0x2c]==0; zeroes credential-adjacent fields; writes literal `"Disabled"` at +0x951 on one branch; dispatches through unresolved PLT helpers incl. an RDM list walk (OID 0xf5/0xf8). Exact product (likely secrets/per-connection cfg) UNKNOWN (runtime/static check U6).

## GPON-specific assumptions found
None in the PPP path code. The only GPON-shaped items are **data**: the factory DefaultConnectionService value, linkdetection's hardcoded object paths/ACS URLs, and the stored `ppp111` string in the GPON object's XML. A second format family in libbemodules @0xc1fd8 (`options_FN%d%d`, `unit %d%d`) is unresolved — not used by the main path (UNKNOWN, check U5).
