# Failed Experiments and Contradictions

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Every contradiction found between prior reports and the artifacts, with corrections. Prior reports are preserved unmodified; corrections live here.
- **Files examined:** All prior reports under analysis/reports and full-router-dump/analysis/rea-investigation vs the binaries

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


## Failed experiments (from existing runtime evidence)
- **FE-1 — Ethernet WAN with only the IP profile:** prior live tests with ConnDev.3 holding only WANIPConnection.1 (DHCP) produced no PPPoE: link-type resolution returned IP and the backend would run DHCP, not pppd. Root cause: no WANPPPConnection under .3. (CONFIRMED FROM EXISTING RUNTIME EVIDENCE + static mechanism.)
- **FE-2 — Raw ccctest ADD of `.3.WANPPPConnection.1`:** ADD action printed success; transaction failed; PPP count stayed 0. Root cause narrowed this session to a commit/validation-phase NACK after successful ADD execution (specific rejector UNKNOWN) — full analysis in RDM_OBJECT_CREATION_ANALYSIS.md. **Do not repeat the identical bundled script.**
- **FE-3 — Correctly-spelled GPON object name:** any script using `X_5067F0_GponInterfaceConfig` fails object resolution; the schema spelling is `X_5067F0_GponInterafceConfig` (CONFIRMED STATIC, image @0x35fbc; correctly-spelled form occurs 0 times).

## Contradictions and corrections
| # | Prior claim | Correction (verdict) |
|---|---|---|
| C-1 | README hash table: broadband.cgi SHA-256 `6a43d922…` | DISPROVEN. Actual: `78eaacd5…` (size 61,760 B matches, hash does not). |
| C-2 | ppp-object-creation-audit / 05-rdm inventories: WANPPPConnection OID 0xc7, WANIPConnection 0xca, WANConnectionDevice 0x32, WANSwitch 0xc0, Layer3Forwarding 0x40, etc. | DISPROVEN. OIDTable ground truth: PPP.i 0xe3 / class 0xf1; IP.i 0xcd / class 0xe2; ConnDevice.i 0xcc; WANDevice.i 0xc3; 0xc7 = GponInterafceConfig; 0xca = WANEthernetInterfaceConfig; Layer3Forwarding 0x80; WANSwitch 0x4d. The audit's *conclusion* (PPP allowed under .3) is right; its OID-derived reasoning is not. MASTER_FINDINGS' own RDM-001 (0xc7/0xca as PPP/IP counts) is likewise superseded, while its LAUNCH section (0xe3) was correct. |
| C-3 | ppp-object-creation-audit hashes for librdm/libcccrdm/ccctest (`914b3017…` etc.) | DISPROVEN for the committed artifacts (actual in hash table). Only its ccc_be hash matches — that audit was written against a different dump revision. |
| C-4 | MASTER_FINDINGS AUD-001 chain: ccctest → `ccc_be 0x415860` dispatcher → AddIndexChildObject; "explicit instance → AssignIA" | DISPROVEN dispatch. 0x415860 is an internal provisioning wrapper (callers pass w3=0, OIDs 0xcd/0xd5); `cccBeHandleMessage` @0x41297c does not execute action 7 at all; the real chain runs through the libcccrdm RDM callback/resolver. The audit's librdm function addresses (0x134a0, 0x137ec) are correct. |
| C-5 | ppp-interface-binding-audit: "unit hardcoded 111 in beConfigWANByPPPoE"; "ppp111 at 0x348d4" | DISPROVEN. beConfigWANByPPPoE calls `getPPPPdUnitNum_wrapper(IA)` @0x6663c and prints `unit %s`; 111 is the computed GPON result. Also its +0x898/+0x3e7 offsets belong to a different struct than setWanIpPppInterfaceName's. Its options-name/pppd-arg conclusions remain correct. |
| C-6 | REVERSE_ENG.md: Ethernet session is `ppp111` (§525 and lifecycle chapters); §543 "ppp1 over omci_notag" parity | DISPROVEN. Formula gives ppp131 for ConnDev.3; no `omci*` L2 name exists in these binaries. The same file's §1191/§1404 ppp131 passages are correct — the file contradicts itself; ppp131 wins on disassembly. README `options_ppp131` also DISPROVEN (options file is `options_nas0_notag`). |
| C-7 | MASTER_FINDINGS AUD-004 / ppp-routing-nat-audit: ip-up emits `EVENTNOTIFY 206 string ppp111`; Event-206 handlers install route to ppp111, MASQUERADE, MSS 1440, and program fc ASIC tables | DISPROVEN as literals. ip-up (verbatim) emits `EVENTNOTIFY 206 string $REALNAME`; zero MASQUERADE strings in libbeEvents; MSS rule is the separate global addTCPMSSDefaultRule (`--clamp-mss-to-pmtu`, no literal 1440, not in beConfigWANByPPPoE); no evidence Event 206 programs fc tables. The audits' "generic" conclusion survives, their evidence does not. Their libbeEvents (`785b9b65…`) and libpppoe (`3ba88a38…`) hashes match no repo file. |
| C-8 | MASTER_FINDINGS AUD-007: Ethernet PPP = `ppp111` over nas0_notag; GPON = `ppp1` over omci_notag; "100% identical" | DISPROVEN names (ppp131 / ppp111; L2 names nas0_notag both cases per the generic construction — GPON L2 base is data-driven, `omci_notag` unverified). "100%" downgraded: architecture is shared and generic, with the C-11 open item. |
| C-9 | ethernet-ppp-dispatch-audit claim 10: eth_Init "bound exclusively to Boot — REBOOT REQUIRED, CONFIRMED" | OVER-CLAIMED. Boot binding CONFIRMED; exclusivity not audited (L4ObjectChanged exists). Downgraded to STRONGLY INFERRED. |
| C-10 | activation-sequence.md step 7: eth_Init does PHY + nas0_notag + mask + options + pppd | DISPROVEN attribution (five functions). Net sequence correct. |
| C-11 | **Unresolved internal conflict (new, this session):** `getLinkType` @0x34334 raw operands are OID 0xc7 (byte0 → PPP decision) and 0xca (byte+4 → IP decision). OIDTable + broadband.cgi usage say 0xc7/0xca are the Gpon/Ethernet *interface config* objects; prior reports say they are PPP/IP *count* objects. Both cannot be literally right. Possibilities: (a) the interface-config object structs' leading bytes serve as the queried fields (e.g. a shared object header / first params), (b) libcccbe was built against a different OID assignment than librdm's table for these two slots. The function's operands, IA construction (`rdmConstructIAValue("%d", wanDeviceInstance)`), and return encoding (1=PPP, 0/2=IP/other) are CONFIRMED; the object naming at this call site is **UNKNOWN**. Impact: low — PPP creation, naming, config generation and launch are independently proven; but any plan step that relies on "PPP count is checked first" should be treated as STRONGLY INFERRED until resolved. Resolution requires tracing cccRdmGetObjectByOID's returned struct layout for OIDs 0xc7/0xca in the SHM image. |
| C-12 | ppp-parameter-validation.md: all params "VERIFIED" vs active DB; Name LENGTH 64; VLANID range 0–4095; WANMode "factory value GPON" | PARTLY DISPROVEN. Several params are schema-image-only (0 XML occurrences); Name LENGTH is 256; VLANID MAX is 5000; WANMode appears in **neither** PDM XML (schema-only parameter; WanAutoDetect=1 is the configured one). See PPP_PARAMETER_VALIDATION.md. |
| C-13 | Prior descriptions of `/etc/ppp/default_options` content | CORRECTED: in this dump default_options is 0 bytes; the template content quoted is `_options_static`'s. Which file a live unit populates is UNKNOWN (U3). |
| C-14 | `analysis/config_rdm_decoded.xml` treated as XML | DISPROVEN: byte-identical to the decompressed binary image. Real XML exports are the PDM files. |
| C-15 | linkdetection-analysis.md | CORROBORATED, with addenda: GPON branch sets the *production* tms URL (no trailing slash) vs ETHER's testacs URL (with slash); ETHER Tx A gate `/tmp/ADD_WAN_update_181DM_done`; ETHER creates the ConnDev.3 **IP** profile only. |

## Net effect
None of the corrections overturn the central feasibility conclusion; they overturn several *mechanism* claims (dispatch chain, OID numbers, hardcoded names, MSS/NAT attribution) and two *certainty* claims (reboot exclusivity, getLinkType object naming). All deployment steps in IMPLEMENTATION_PLAN are based only on the corrected evidence.
