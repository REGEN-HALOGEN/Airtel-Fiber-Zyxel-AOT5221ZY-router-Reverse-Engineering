# PPP Interface Binding — ppp131 vs ppp111

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** The unit/interface-name derivation, with the complete disassembly evidence and every hardcoded name found.
- **Files examined:** libcccbe.so (getPPPPdUnitNum_wrapper @0x38264, setWanIpPppInterfaceName @0x346d0, libccc_executePPPv4Client @0x348f4), libbemodules.so (beConfigWANByPPPoE @0x664a8), libCmd.so

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


## Verdict
**CONFIRMED STATIC: `WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1` → `ppp131`; GPON `1.1.1` → `ppp111`. One generic mechanism; neither name is hardcoded anywhere.** `grep -a ppp111|ppp131` over all binaries = 0 hits; `ppp111` exists only as data in the stored GPON config XML.

## Step 1 — unit string from IA (string concatenation, not arithmetic)
`libcccBeWan_getPPPPdUnitNum_wrapper` (libcccbe @0x38264, fresh disassembly this session):
```
0x38290 ubfx x7, x0, #0x28, #8     ; IA byte 5 = WANPPPConnection instance
0x38294 ubfx x6, x0, #0x30, #8     ; IA byte 6 = WANConnectionDevice instance
0x38298 lsr  x5, x0, #0x38         ; IA byte 7 = WANDevice instance
0x3829c format @0x4c3b8 = "%d%d%d" → snprintf(tmp, "%d%d%d", wanDev, connDev, pppInst)
0x382b8 strtol(tmp,10) → *intOut (if non-NULL); 0x38334 snprintf("%s") → strOut (if non-NULL)
```
⇒ IA 1.3.1 → `"131"`; IA 1.1.1 → `"111"`. (For an instance ≥ 10 concatenation ≠ arithmetic — e.g. 1.10.1 → `"1101"` — immaterial here.)

## Step 2 — interface name + L2 name
`setWanIpPppInterfaceName` (libcccbe @0x346d0), PPP branch @0x348a8:
```
0x348a8 snprintf(dst, 0x20, "%s%s", base, suffix)        ; L2 name: base + suffix
0x348cc ldr w5, [x19,#0x48]                              ; unit integer
0x348d0 format @0x4aeb0 = "ppp%d" → InterfaceName = "ppp<unit>"
```
Suffix: VLAN-enable byte [obj+0x18]==0 → literal `"_notag"` @0x3481c; else `"_%d"` % VLAN ID @0x3474c. LinkType [obj+0]: 0 → IP branch (both fields = base+suffix), 1 → PPP branch, other → error/0.
Prior struct-offset claims (+0x898 X_5067F0_IfName / +0x3e7 X_5067F0_InterfaceName) belong to the libbemodules object layout, not this function's small struct — the *values* it produces are as above (correction to ppp-interface-binding-audit §2.1).

## Caller side
`beConfigWANByPPPoE` @0x66628–0x66640: calls the wrapper with the object's IA (str-out = stack buf) and `fprintf(fp, "unit %s", buf)` (fmt @0xbd650) — pppd receives **`unit 131` as text** and creates ppp131 itself. Options file is named by the **L2** name: `/etc/ppp/options_nas0_notag` — prior `options_ppp131` (README) is DISPROVEN.

## Every hardcoded PPP-related name found
- Formats: `"%d%d%d"` (@0x4c3b8), `"ppp%d"` (@0x4aeb0), `"unit %s"`, `"/etc/ppp/options_%s"`, `"%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &"` (@0x4aee0, libccc_executePPPv4Client — both %s = X_5067F0_IfName).
- libCmd.so templates: `/bin/pppd [ -d ] file /etc/ppp/options_%s %s`, kill/restart via `ppp%s.pid` (%s = unit string) and `%s.pid` (%s = full ifname) — two conventions, both generic (prior libcmd audit, corroborated).
- Literals: `nas0`, `nas0_100` (VLAN example), `nas0_notag` (as data/default in ccc_be). **No** `ppp111`, `ppp131`, `omci*`, `veip*` literals in the PPP path (`veip` occurs once in libbemodules, context unresolved).
- Unresolved second family (libbemodules @0xc1fd8): `options_FN%d%d`, `unit %d%d`, `ppp%d%d.pid` — containing function not xref-resolved; not used by the main path. UNKNOWN (check U5).
