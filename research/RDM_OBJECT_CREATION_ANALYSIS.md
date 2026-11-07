# RDM Object Creation Analysis — the failed .3.WANPPPConnection.1 ADD

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** ccctest parser, libcmsg builders, backend dispatch, cccRdmAddIndexChildObject, rdmVerifyIAValue, commit logic; root-cause ranking.
- **Files examined:** DUMPFILES/ccctest.bin, libcmsg.so, librdm.so, libcccrdm.so, ccc_be, config_rdm_decompressed.bin, aot-current-pdm-config.xml

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


## Symptom (CONFIRMED FROM EXISTING RUNTIME EVIDENCE)
Prior live attempt: `ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1` — parser printed ADD success, transaction failed, live PPP child count under .3 remained 0. **Do not repeat that exact bundled form** (see IMPLEMENTATION_PLAN for the discriminating minimal form).

## ccctest parser (CONFIRMED STATIC)
Main loop @0x40238c: `fgets` → `strtok(line," ;")` → strcmp dispatch.
- `ADD <path>` @0x402ca8–0x402ce8: `cmsgRequestSel(req, tok, flag)` @0x402cd8 then `cmsgRequestSetIndexedObj(req, 1)` @0x402ce4. Argument passed verbatim; no dot-splitting, no instance parsing, return values ignored.
- `DELETE` identical with sub-action 0 (@0x402da8). `SAVE` @0x403278 → `cmsgRequestSave` (action 5, same request). `SEND` @0x403300 → `cmsgSendRecv(req, moduleId("ccc_das"), 60000)`.
- Vendor help (rodata): `ADD <indexed object name>` @0x403c58; DELETE is the command documented *with* an instance number @0x403c78; the vendor ADD example @0x403f90 has **no trailing instance**: `ADD InternetGatewayDevice.LANDevice.1.LANHostConfigManagement.IPInterface;` followed by SETs in the same transaction.
- libcmsg builders do zero validation: `cmsgRequestSel` @0x556c appends action 1 + verbatim path; `cmsgRequestSetIndexedObj` @0x60a8 appends action 7 + sub-action; `cmsgRequestSave` @0x5f60 appends action 5.

## Why "ADD success" + "transaction fail" is internally consistent (CONFIRMED STATIC)
Reply printer @0x4017dc reads two independent fields: header flags @+0x20 — bit 30 → `transaction fail !!` @0x40183c, bit 31 → success, bit 25 → `validation error code: 0x%08lx`; per-action — action 7 handler @0x40188c prints `ADD %s: %s` (fmt @0x404468) with success/fail from **bit 0x40000000 of that action's own reply word**. ⇒ The ADD executor reported success during action execution; a later commit/validation phase set the header NACK and rolled back. Both observations and the unchanged count follow from one mechanism.

## Backend dispatch (CONFIRMED STATIC)
- ccctest talks to module **`ccc_das`** (name resolved @0x4022ec), not directly to ccc_be.
- `cccBeHandleMessage` (ccc_be @0x41297c) directly handles only actions 2, 6, 0x10, 0x14, 0x1a. Actions 1/3/4/5/**7** fall through to the RDM module callback (libcccrdm/librdm side). After the loop, deferred BE work runs @0x412e24 if flags set, then the reply is built.
- **Correction:** the wrapper at ccc_be @0x415860 (AssignIA if w3==0 else AddIndexChildObject) is internal provisioning only — all callers pass w3=0 with OIDs 0xcd/0xd5. It is **not** the CMSG ADD dispatcher (prior audit misattribution, DISPROVEN).
- Server by-name resolver (libcccrdm @0x90f0–0x9800, STRONGLY INFERRED as the SEL/ADD path): walks dotted components; @0x9538–0x95ac explicitly strtol-parses a trailing instance and calls `cccRdmGetObjectByOID(..., flags=2)` (create-enabled) @0x95dc.

## Creation code (CONFIRMED STATIC)
- `cccRdmGetObjectByOID` (librdm @0x12ce0): template flags word [node+0x28] bit 1 SET (index-child *class*) → if flags&2, call `cccRdmAddIndexChildObject` @0x12d44 (requested instance digit **not consulted**); bit 1 CLEAR (instance object) → AssignIA path. WANPPPConnection class OID **0xf1** has flags **0x2** ⇒ always auto-allocation, never AssignIA.
- `cccRdmAddIndexChildObject` (librdm @0x134a0; libcccrdm twin @0x34184, same source): failure exits are only unknown OID, `rdmVerifyIAValue` −1, max-instances, template alloc NULL. Empty child list → `rdmSetIAValue(IA, depth, 1)` @0x137ec (instance 1 hardcoded) → `cccRdmSetObjDefault` (template memcpy, mode 2) → success tail: `cccRdmSetPreObjStatus(1)`, `cccRdmCheckIndexChildParents` @0x136e0, `cccRdmSetCBData`. **No parent-instance whitelist, no link-type check, no sibling-type check anywhere in the function.**
- `rdmVerifyIAValue` (librdm @0x11e48): checks only depth equality, non-zero bytes, per-level max. Parent IA {1,3} passes: depth 2 == class depth 2; 1 ≤ WANDevice max 4; 3 ≤ WANConnectionDevice max 8.
- `cccRdmAddObjectWithAssignIA` (librdm @0x12ab0) with its `"this index object is existed."` exit is never invoked for class 0xf1.
- Commit-phase machinery capable of a post-execution NACK exists: `cccRdmCheckObjectChg` (libcccrdm @0x2fd30) called from a status-commit walker @0x30144; `rdmInitVerifyConfig` @0x2f500; BE deferred processing. **The exact rejector was not isolated — UNKNOWN.**

## Root-cause ranking
1. **STRONGLY INFERRED — commit/validation-phase NACK + rollback after successful ADD execution.** Every static gate inside creation passes; had AddIndexChildObject returned NULL the per-action reply would have been fail, contradicting the observed success.
2. **HYPOTHESIS — a sibling action in the same SEND poisoned the transaction** (bad-typed SET, SEL of the uncommitted `.1`, or a DefaultConnectionService SET in the same transaction). ccctest accumulates all lines into one request until SEND. The original failing script is not in the repo, so the specific action is UNKNOWN. (Prior categorical claim "a SEL between ADD and SET aborts the transaction" is downgraded: the parser has no such abort; a SEL of an uncommitted instance would fail *at the server* — a poison-action candidate, not a parser rule.)
3. **DISPROVEN as hard failure — trailing `.1`:** parsed by the resolver; digit ignored on this branch; and 1 equals the auto-allocated result anyway. It remains a grammar deviation from the vendor-canonical form (`ADD …WANPPPConnection` with no instance) and the minimal retest should omit it.
4. **DISPROVEN — schema forbids PPP under .3 / parent IA validation rejects 3.**
5. **DISPROVEN — max instances (limit 8, list empty).**
6. **DISPROVEN — AssignIA "already exists".**
7. **DISPROVEN — missing SAVE as cause of count 0** (SAVE is persistence only; a committed-without-SAVE object would still appear in SHM counts until reboot).

## Verdict
`…WANConnectionDevice.3.WANPPPConnection.1` is fully schema- and code-supported. The creation executed; the transaction was NACKed at commit. Discriminating runtime step (not performed; in IMPLEMENTATION_PLAN): minimal transaction `REQUEST; ADD …WANPPPConnection; SAVE; SEND;` alone, capture the `validation error code` line and device syslog (`cccRdm*`/`rdmVerifyIAValue` log at level 3), then configure the committed object in a second transaction.
