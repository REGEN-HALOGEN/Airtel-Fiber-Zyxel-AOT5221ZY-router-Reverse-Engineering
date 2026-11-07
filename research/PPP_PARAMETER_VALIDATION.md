# PPP Parameter Validation

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Schema validation of every candidate PPP parameter: schema-image presence, factory-configured presence, type/limits. Credential values are never reproduced.
- **Files examined:** config_rdm_decompressed.bin (schema image), aot-current-pdm-config.xml / -backup.xml, librdm.so OIDTable

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


## Method
Two independent sources: **(S)** name present in the WANPPPConnection schema block of the decompressed RDM image (block name @0x3b2dc, class descriptor @0x3f03c); **(X)** parameter factory-configured under `WANConnectionDevice.1.WANPPPConnection.1` in the PDM XML (yields TYPE/LENGTH/MAX/MIN). A parameter can be schema-real with no configured instance anywhere (template defaults until set). This corrects the prior validation matrix, which marked everything "VERIFIED" against the active database.

## Object (CONFIRMED STATIC)
WANPPPConnection: class OID 0xf1 (template flags 0x2), instance OID 0xe3, max instances **8**, child of any WANConnectionDevice.i. Struct offsets from prior consumer analysis (libbemodules layout, STRONGLY INFERRED): Enable +0x2c, MaxMRUSize +0x18 (u16), MaxMTUSize +0x1a (u16), Username +0x324, Password +0x365, X_5067F0_InterfaceName +0x3e7, PPPoEServiceName +0x532, PPPAuthenticationProtocol +0x649, X_5067F0_IfName +0x898.

## Parameter matrix
| Parameter | S (image offset) | X (factory PPP.1) | Type / limits | Verdict |
|---|---|---|---|---|
| Enable | yes 0x3b75f | yes | boolean; factory GPON value 1; template default 0 per prior SAF-002 (STRONGLY INFERRED) — explicit SET/`Enable=1` is mandatory after a raw ADD | Schema-confirmed |
| Name | yes 0x3be6c | yes | string LENGTH **256** (prior "64" DISPROVEN) | Schema-confirmed |
| ConnectionType | yes 0x3be38 | no (only under WANIPConnection i5) | string; `"IP_Routed"` in PPP block enum/default area @0x3c9c1 (STRONGLY INFERRED) | Schema-confirmed (image only) |
| Username | yes 0x3bf80 | yes | string LENGTH 64; value present — [REDACTED] | Schema-confirmed |
| Password | yes 0x3bfb0 | yes | string LENGTH 64; value present — [REDACTED]. broadband.cgi skips Set when form value is `"****************"` (masked sentinel) | Schema-confirmed |
| PPPoEServiceName | yes 0x3c0b8 | **no — 0 occurrences in both XMLs** | string | Schema-confirmed (image only); deployment value `3jglobal` from ISP data |
| MaxMRUSize | yes 0x3b498 | no (XML occurrence is Device.PPP.Interface.1, different subtree) | numeric, consumed as `mru %d` from +0x18; exact schema type word not decoded this session | Schema-confirmed (image only) |
| X_5067F0_MaxMTUSize | yes 0x3b4c8 | **no — 0 occurrences** | numeric, consumed as `mtu %d` from +0x1a | Schema-confirmed (image only); deployment 1480 |
| X_5067F0_PPPAuthenticationProtocol | yes 0x3c160 | **no — 0 occurrences** | string; recognised values PAP/CHAP/MS-CHAP; anything else incl. `AUTO_AUTH` → no refuse-* lines | Schema-confirmed (image only) |
| NATEnabled | yes 0x3b84f | no (XML occurrences under WANIPConnection) | boolean | Schema-confirmed (image only) |
| X_5067F0_Enable_VLANID | yes 0x3b923 | no (occurrence under WANIPConnection i3) | boolean | Schema-confirmed (image only) |
| X_5067F0_VLANID | yes 0x3b540 | yes | uint16, MIN 0, MAX **5000** (prior "4095" DISPROVEN); factory GPON value 100 (data, not a requirement for Ethernet) | Schema-confirmed |
| X_5067F0_IfName | yes 0x3c7b4 | no | string; runtime-filled with the L2 device (`nas0_notag`) by setWanIpPppInterfaceName | Schema-confirmed (image only) |
| X_5067F0_InterfaceName | yes 0x3c010 | yes | string LENGTH 64; factory GPON value `ppp111` ⇒ Ethernet instance `ppp131` by the IA rule (CONFIRMED via PPP_INTERFACE_BINDING) | Schema-confirmed |

## Deployment values (from ISP data in the brief — not from firmware)
PPPoEServiceName=`3jglobal`; MaxMRUSize=1480; X_5067F0_MaxMTUSize=1480; X_5067F0_PPPAuthenticationProtocol=`AUTO_AUTH`; NATEnabled=1; Enable=1; X_5067F0_Enable_VLANID=0 (no-VLAN plan; TP-Link runtime evidence); ConnectionType=`IP_Routed` (set by broadband.cgi's tail automatically on the Web path). Username/Password: entered by the user at deployment only.

## Type-tag caution for ccctest SETs (HYPOTHESIS, relevant to root-cause Rank 2)
ccctest SET requires an explicit type token; a mismatched tag (e.g. MaxMRUSize as `string`, X_5067F0_VLANID as `uint32` instead of `uint16`) is a plausible transaction poison. Exact schema type words for the image-only numeric params were not decoded this session — the Web conversion path avoids this risk entirely because broadband.cgi uses its own typed param tables.
