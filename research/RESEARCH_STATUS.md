# Research Status

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Overall mission status against the 11 completion criteria in §16 of the brief.
- **Files examined:** `research/*` (this set), `DUMPFILES/*`, `analysis/*`, `full-router-dump/analysis/rea-investigation/*`

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


## Verdict in one paragraph
The static implementation path for LAN4 Ethernet WAN + PPPoE is **established end-to-end at code level**, with one genuine blocker isolated and one preferred workaround proven at code level: (1) the firmware's own Web backend (`broadband.cgi`) contains a complete IP→PPP **type-conversion** path that creates `WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1` — this is the vendor-supported route; (2) the previously failed raw `ccctest ADD` did **not** fail in the object-creation code — the ADD action executed and the **transaction was NACKed at commit/validation and rolled back** (specific rejector UNKNOWN statically). PPP interface binding is definitively `ppp131` for the Ethernet object (generic IA-derived formula, no hardcoding). Routing/NAT/firewall/DNS/MSS code is generic and interface-name driven.

## Completion criteria (§16 of brief)
| # | Criterion | Status |
|---|---|---|
| 1 | Physical LAN4 port mapping | CONFIRMED STATIC — port 3, mask 0x08 (`rtk_wan_port_mapping` @0x37c84) |
| 2 | Ethernet WAN initialization | CONFIRMED STATIC — `libcccBeWan_eth_Init` @0x38074, boot-gated on `WANMode=="ETHER"` + Eth Enable |
| 3 | `nas0_notag` creation | CONFIRMED STATIC — `createLayer3Interface` @0x35348, smuxctl `--if-create-name`, tags 0 untagged |
| 4 | Valid PPPoE object creation under .3 | CONFIRMED STATIC for the broadband.cgi conversion path; raw ccctest ADD root cause narrowed to commit-phase NACK (rejector UNKNOWN) |
| 5 | PPP configuration generation | CONFIRMED STATIC — `beConfigWANByPPPoE` @0x664a8 → `/etc/ppp/options_nas0_notag` |
| 6 | PPP interface mapping | CONFIRMED STATIC — IA 1.3.1 → unit `"131"` → `ppp131` |
| 7 | PPP daemon launch | CONFIRMED STATIC — `libccc_executePPPv4Client` @0x348f4 → `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag &` |
| 8 | PPPoE discovery/auth support | CONFIRMED STATIC — rp-pppoe plugin (`libpppoe.so`), AUTO_AUTH = no refuse-* lines |
| 9 | Default route integration | STRONGLY INFERRED — generic, follows `Layer3Forwarding.DefaultConnectionService`; runtime check U7 |
| 10 | NAT + firewall integration | CONFIRMED STATIC (NAT templates generic `NAT_POSTROUTING -o %s`); firewall FORWARD pair UNKNOWN as literal string |
| 11 | LAN3 + Wi-Fi preservation | STRONGLY INFERRED — port 2 / mask 0x04 never touched by WAN code (preservation by omission); runtime check U11 |

## What static analysis does NOT prove
A live PPPoE session (PADI/PADR, LCP, auth, IPCP) against the Syrotech ONT / ISP BRAS, the VLAN requirement, the exact commit-phase rejector for the raw ADD, and post-change bridge membership. Each unproven step lists its required runtime observation in `OPEN_QUESTIONS.md`.

## Contradictions corrected this session
See `FAILED_EXPERIMENTS_AND_CONTRADICTIONS.md` — 12 items, including wrong OID tables in prior audits (WANPPPConnection.i is OID 0xe3, class 0xf1 — not 0xc7), a wrong broadband.cgi SHA-256 in the README, the "unit hardcoded 111" claim (DISPROVEN), and `ppp111`-for-Ethernet passages (DISPROVEN; correct is `ppp131`).

## Remaining blockers
1. Exact commit-phase rejector of the failed ccctest transaction — needs the original failing script + device syslog (not in repo).
2. No HTML templates exist in the repo/rootfs dump — whether the shipped Web UI *exposes* the PPPoE encap option for the ETH profile cannot be verified from this corpus (the backend supports it).
3. `getLinkType` OID-operand naming conflict (see `FAILED_EXPERIMENTS_AND_CONTRADICTIONS.md` C-11).

## External corroboration (§12 of brief — corroboration only, never proof for this firmware)
Searches performed 2026-11-07 (browser search):
- **Zyxel PX5311-T0 official product page** — https://www.zyxel.com/service-provider/emea/en/products/fiber-oltsonts/gpon/hgus/px5311-t0 — confirms the PX5311 family: GPON VoIP IAD, 4× GbE LAN, Wi-Fi 6 AX3000, TR-069/OMCI, "Zyxel OPAL firmware" trunk shared across CPEs. Note the public variant is **-T0**; the Airtel unit is **PX5311-R0** (ISP variant) — no public R0 page/firmware was found. Confidence: MEDIUM for family identity, LOW for any R0-specific behaviour.
- **RTL9607C platform:** multiple OEM ONU datasheets (e.g. Chima SDN7758 series, HDV HUR4002XR) describe RTL9607C-based HGUs with multi-WAN, PPPoE/DHCP/Static WAN, hardware NAT, port binding — consistent with the feature set in this firmware, but those products run a different (Realtek Luna, MIPS) SDK stack; several datasheets describe the SoC as MIPS, whereas every binary in this repo is AArch64 — for *this* unit the binaries win; external SoC descriptions are treated as LOW confidence and possibly a different silicon revision/SDK. No public source was found for `nas0_notag`, `ppp131`, MSTC RDM/CMSG internals, or a Zyxel OPAL GPL release for this model — those points rest solely on the in-repo static evidence.
- **hack-gpon / RTL960x community material** (e.g. https://deepwiki.com/hack-gpon/hack-gpon.github.io) documents Realtek Luna-SDK ONTs (`flash get/set`, `diag`) — a different management model from this unit's TR-098 RDM/CMSG; useful only as platform-family context. Confidence: LOW.
