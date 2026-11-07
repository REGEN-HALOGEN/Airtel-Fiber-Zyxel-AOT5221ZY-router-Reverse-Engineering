# PPPoE Service-Name Defect and Alternative Paths — Consolidated Research Report

- **Project:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138, BusyBox 1.35) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Branch:** `research/ethernet-wan-pppoe`. **Date:** 2026-11-07 (Mission 3 consolidation).
- **Status of this document:** This is now the **single authoritative research report** for the project. It consolidates and supersedes all prior Claude-generated reports on this branch (18 Mission-1 reports, `CONCRETE_IMPLEMENTATION_CHECK_AND_ROLLBACK.md`, and all `_work_*`/`_m3_*` working files), which have been deleted in the same cleanup commit after their unique findings were transferred here. `MASTER_FINDINGS.md` remains as the short ledger and points here.
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN, or runtime access was used or attempted in any mission. No firmware was patched, modified, flashed, or deployed. Hypothetical corrections are analysed and labelled hypothetical only. No PPPoE credentials appear anywhere (presence-only, `[REDACTED]`).
- **Confidence legend:** **CONFIRMED STATIC** = decoded from the binaries/image in-repo · **CONFIRMED FROM EXISTING RUNTIME EVIDENCE** = prior user-supplied runtime logs/observations, not re-derived · **STRONGLY INFERRED** = cross-function reconstruction with one unobserved link · **HYPOTHESIS** = plausible, unproven · **UNKNOWN** = not settled statically · **DISPROVEN** = contradicted by the artifacts. Candidate-path verdicts use the Mission-3 scale: CONFIRMED STATICALLY / STRONGLY SUPPORTED / POSSIBLE BUT UNPROVEN / DISPROVEN / NOT INVESTIGATED. Nothing is labelled "working" — no runtime evidence exists.

---

## 1. Executive summary

1. **The service-name defect (B-NEW-1) is CONFIRMED at byte level** (Mission 3 independent re-verification, §4). In `libbemodules.so`, `beConfigWANByPPPoE` writes the PPPoE service name with the format string `"pppoe_srv_name %s"` (vaddr `0xbd808`) which is NUL-terminated with **no trailing newline** — the only one of the function's 32 file writes lacking `\n` — immediately before the `linkname %s\n` write. With any non-empty service name, the generated `/etc/ppp/options_nas0_notag` deterministically contains the merged line `pppoe_srv_name 3jgloballinkname ppp131`.
2. **The predicted pppd failure is now PROVEN from the bundled pppd's own code** (upgraded from inference, §6). pppd's options parser is a whitespace **token stream**, not line-based: `pppoe_srv_name` consumes exactly one argument (`3jgloballinkname` — the wrong service name), the `linkname` directive is never seen, and the stray token `ppp131` is looked up as an option, fails, produces `In file …: unrecognized option 'ppp131'`, and propagates to `main` → **`exit(2)` — before any PPPoE discovery is attempted.**
3. **No alternative service-name mechanism exists in the firmware** (§7). No `pppoe-service` option, no rp-pppoe plugin/binary, no environment variable, no separate config file, no second PPPoE client, no other RDM feed. The one mechanism that exists in pppd — passing the option on the pppd command line — is **not used** by any firmware launch format. Omitting the service name is **not** an acceptable workaround: there is no authoritative evidence the ISP accepts an empty service name for `3jglobal` (§7.9).
4. **No safe firmware-side correction can be established** (§8 of analysis in §16/§19; hypothetical-correction analysis in §11.7): `libbemodules.so` resides on `/dev/root`, a **dm-verity-protected read-only squashfs** (kernel cmdline: `root=/dev/dm-0`, verity over the UBI rootfs, dual slots). There is no runtime write path; any correction means a firmware rebuild and reflash through an update path whose operator-facing integrity route (RAS checksum/TLV vs OpenWrt sysupgrade signature) is itself not fully resolved. **No patch was created or applied.**
5. **Everything else in the architecture holds** (§11): LAN4/PHY3/mask `0x08`, `nas0_notag`, the vendor `broadband.cgi` IP→PPP conversion as the only proven PPP-object creation path, `ppp131` naming, generic routing/NAT/firewall/DNS, LAN3/Wi-Fi preservation by omission, GPON preservation with a complete restoration matrix, ACS preservation on the UI path. The six stages remain distinct: lower interface ✔ proven, RDM object ✔ proven (conversion), **valid options ✘ broken by B-NEW-1**, pppd launch ✔ proven, session ✘ (blocked by the broken options + never runtime-tested), routing/NAT ✔ proven generic.
6. **One genuinely new candidate path was found** (§§8, 10, 15): the USP/TR-369 agent **`obuspa`** imports `cmsgRequestSetIndexedObj` and carries a fully parameterised `WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d` template. It is **POSSIBLE BUT UNPROVEN** as an object-creation route — and even if it works, it does **not** cure B-NEW-1, because the created object still feeds the same defective options writer.
7. **Final verdict: NOT READY** (§20). The objective is blocked by exactly one proven firmware defect with no proven workaround, plus one operator-observable unknown (U12, whether the shipped Ethernet edit page exposes PPPoE). The exact next action is in §19.

## 2. Current project objective and exact target topology

```text
Syrotech GPON ONT
       |
       | Ethernet handoff
       v
Airtel AOT5221ZY
  LAN4 = Ethernet WAN
  PPPoE client (service name 3jglobal, MTU/MRU 1480, AUTO_AUTH)
  NAT + routing + firewall
       |
       +---- LAN3
       +---- Wi-Fi clients
```

- The Airtel router itself must establish the ISP PPPoE session through LAN4 and serve LAN3 + Wi-Fi clients.
- ISP parameters (CONFIRMED FROM EXISTING RUNTIME EVIDENCE — user-supplied): PPPoE, service name `3jglobal`, MTU 1480, MRU 1480, authentication `AUTO_AUTH`. **VLAN requirement: UNKNOWN** — the existing TP-Link router connects through the same ONT with no VLAN configured; no VLAN is invented anywhere in this report.
- The existing GPON configuration (`.1.WANPPPConnection.1`) must be preserved intact so rollback remains possible. LAN3/AP functionality must remain operational.
- Merely enabling the Ethernet PHY or obtaining an IP interface does **not** satisfy the objective; PPP session, default routing, NAT, DNS, firewall, and LAN connectivity are all required stages.

## 3. Investigation scope and tooling

- **Repository:** full clone, 2,601 files, 144,271,796 bytes; base commit `5b1dfca` (only commit on `main`). Full per-file inventory (path/type/arch/size/SHA-256) was generated in Mission 1 and is preserved as `REPOSITORY_INVENTORY.csv` on this branch (see §18 note); key artifact hashes are reproduced in §3.1.
- **Method:** ELF parsing (LIEF/pyelftools), AArch64 disassembly (Capstone 5.0.7; host `objdump` is x86-only), PLT resolution from `.rela.plt`, repo-wide string + xref scans (503 ELFs in Mission 3), RDM schema/PDM XML analysis, script/config reading. Ghidra/IDA/radare2 not installed — recorded tooling limitation.
- **Evidence discipline:** every major claim cites repo path, function, address/offset, string address/xref, and confidence. Prior-mission claims were independently re-verified where load-bearing (notably B-NEW-1, §4).

### 3.1 Key artifact hashes (SHA-256)

| Artifact | Size | SHA-256 |
|---|---|---|
| `DUMPFILES/broadband.cgi` | 61,760 B | `78eaacd575b9884778a76ead57cc895e95944cc939c465136ee3da390f3671fa` |
| `DUMPFILES/wanRemoteNode_ETH_Edit.cgi` | 47,424 B | `59ee3ba6b9a946650eb9112fb0ebc2561e2e9ee5e0589ec2ada55517c4af5899` |
| `DUMPFILES/wanRemoteNode_GPON_Edit.cgi` | 47,416 B | `69f9a176397c742d0ee50fe07313646cf5ca27743ba1c29facf54b7c6eb148e1` |
| `DUMPFILES/linkdetection` | 23 KB | `36d219bd3c86704721fe44ba5eb214dadb5ebcae9eed4b41f74e323ebf1a9f93` |
| `DUMPFILES/libcccbe.so` | 369 KB | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` |
| `DUMPFILES/libbemodules.so` (= rootfs copy, identical) | 1,074,680 B | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` |
| `DUMPFILES/libbeEvents.so` | 109 KB | `cc9d237437773f9a104ceec09f4217298543e0dc80dcd46f89e95b18c40500d1` |
| `DUMPFILES/librdm.so` | 280 KB | `65306765251c503d3c36fac4f93bfa348698f2ffe9ed83a646a672b57b331a1d` |
| `DUMPFILES/libcccrdm.so` | 436 KB | `ed2a1d6a0f70b0d0323cc8b0671d0846b2ef1f529b871104cc45eb61d4376352` |
| `DUMPFILES/libcmsg.so` | 55 KB | `57155a272eb9cdf9e4d62b3fee07d4f058a93ccb798d4c6503292af4b0094d70` |
| `DUMPFILES/ccctest.bin` | 23 KB | `4badd3f723df86838e20a199f08c4e844354aec605f286a3cb141f93b5d3f3bf` |
| `DUMPFILES/ccc_be` | 120 KB | `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f` |
| `DUMPFILES/config.rdm` (= runtime-config.rdm) | 62 KB | `fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7` |
| `DUMPFILES/config_rdm_decompressed.bin` | 3,145,728 B | `b1a35a37631b7dd75c1b13f6d78e6a75d6c41bb081e8c868c82330dad1dd5485` |
| rootfs `lib/MSTC/libpppoe.so` | — | `c6a83bc868fd2e6e0e19abbd43625a68e90e47874ea5f8d87f6437a69577e315` |
| rootfs `bin/pppd` | — | `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596` |
| rootfs `etc/ppp/ip-up` | — | `3fcaa848d84b5297bcbabd93dd569e7ed84f17eb50d3cb0d72b5d04c98ee4ae7` |
| rootfs `etc/ppp/ip-down` | — | `d5a5e2ceb638e9dcc0c3a974f0bb8f4fd869d5168b3bc128ea467e5ec347f51e` |
| rootfs `lib/MSTC/libCmd.so` | — | `ef06db88…` (Mission-2 correction of the `fa8ecd…` value quoted in an earlier draft) |


## 4. Service-name defect: exact disassembly evidence

**Artifact:** `libbemodules.so` (both copies — `DUMPFILES/libbemodules.so` and `full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so` — are byte-identical, sha256 `1de450de…`, ET_DYN/AArch64, no `.symtab`; function bounds from `.dynsym`, PLT resolved from `.rela.plt` and validated by decoding stubs).

### 4.1 The format string at byte level — CONFIRMED STATIC

At vaddr **`0xbd808`**, raw bytes:

```text
70 70 70 6f 65 5f 73 72 76 5f 6e 61 6d 65 20 25 73 00
"p p  p  o  e  _  s  r  v  _  n  a  m  e     %  s" NUL
```

There is **no `0x0a` (`\n`) anywhere in the string**. The 6 bytes following the NUL are `00` alignment padding — never written to the file. By contrast `"linkname %s\n"` at **`0xbd820`** ends `… 25 73 0a 00` (`%s\n` + NUL), and every sibling literal the function writes (`persist\n`, `passive\n`, `+ipv6\n`, refuse-* lines, `unit %s\n`, `mru`/`mtu` lines, etc.) is `\n`-terminated. This one string alone is not. The defect is in the format string itself, not in any write logic.

### 4.2 The defective write sequence — CONFIRMED STATIC

`beConfigWANByPPPoE` = **`0x664a8`**, size 1712, ends `0x66b58`. (Prior-mission addressing correction, recorded: the address previously quoted as "the write" — `0x66968` — is the *guard* `ldrb w0,[x20,#0x532]; cbnz w0, 0x66b34` that tests whether the service-name byte is non-zero. The write itself is below.)

- Guard @`0x66968`: service-name field (config struct +`0x532`) first byte ≠ 0 → branch to `0x66b34`.
- Setup @`0x66b34`: x0 = FILE* (x19), x2 = fmt `0xbd808`, x3 = service-name string (struct +`0x532`).
- **Write: `__fprintf_chk` @ `0x66b48`** emits exactly `pppoe_srv_name <value>` with **no newline**.
- Fall-through/branch `b 0x66970` goes **directly** into the `linkname` write: `__fprintf_chk` @ `0x66984` with fmt `"linkname %s\n"` @`0xbd820`, value = linkname string (struct +`0x3e7`, e.g. `ppp131`).

All **32 file writes** in the function were audited (13 `__fprintf_chk` + 19 `fwrite`): exactly one lacks `\n` (this one); there are **zero** `fputc`/`fputs` calls — so no branch inserts a separate `"\n"` write. Both cases reconstructed:

- Service name **empty** → the entire `pppoe_srv_name` line is skipped; file is well-formed.
- Service name **non-empty** (e.g. `3jglobal`) → file deterministically contains the merged line:
  `pppoe_srv_name 3jgloballinkname ppp131\n`
  (values are runtime data: service from struct +`0x532`, linkname from struct +`0x3e7`; the merge mechanism and byte layout are static facts).

### 4.3 Options-file naming and template — CONFIRMED STATIC

- No file in the tree contains the literal `options_nas0` — the name is built at runtime from `"/etc/ppp/options_%s"` @`0xbd598` (sole xref `0x66530`, inside `beConfigWANByPPPoE`); the suffix pieces (`nas`/`_notag`) live in `libcccbe.so`. For the Ethernet untagged profile the result is `/etc/ppp/options_nas0_notag`. The options file is named by the **L2 interface**, not by the PPP unit (prior `options_ppp131` naming: DISPROVEN).
- The generated file inherits the template content: the dump's `default_options` / `_options_static` templates are both populated (90 B / 94 B re-read verbatim in Mission 2 — incl. `plugin pppoe`, `usepeerdns`); the earlier "default_options is 0 bytes/swapped" reading is DISPROVEN for this dump.

### 4.4 Every other writer checked — CONFIRMED STATIC

Repo-wide xref scan (503 ELFs): `pppoe_srv_name` occurs as a **writer** only in `libbemodules.so` (one code xref @`0x66b3c`) and as a **parser** in `lib/MSTC/libpppoe.so` (option-table name @`0x5e9f`; the `printf("pppoe_srv_name=%s\n")` @`0x323c` in `setdevname_pppoe` is a debug print, not a file write). `pppoe-service` has **zero hits anywhere**. `rp-pppoe` occurs in **no ELF** (only the legacy shell script, §8). `PPPoEServiceName` occurs as a data-table name pointer in `broadband.cgi` (the RDM parameter name) and in XML/config dumps — never as a writer.

## 5. PPPoE options-file generation call graph

```text
…WANDevice.i ConfigLoader L3ConfigInit @0x4f440 (libbemodules)
  └─ BL @0x4f9c4 → createWANPPPConnectionCfgFile @0x6a7c0
       (Enable gate; IPv6/DNS cleanup; "Disabled" state handling;
        the libcccbe wrapper it calls @0x373a4 is a no-op stub)
       └─ BL @0x6a8b8 → beConfigWANByPPPoE @0x664a8   ← ONLY caller
            (x0 = cfg struct, x2 = filename suffix)
            ├─ builds "/etc/ppp/options_%s" from template copy
            ├─ writes unit/user/password[REDACTED]/linkname/mru/mtu,
            │   lcp-echo-*, auth refuse-* only for PAP/CHAP/MS-CHAP
            │   (AUTO_AUTH → none written), persist/passive for AlwaysOn,
            │   +ipv6 when applicable
            └─ writes "pppoe_srv_name %s" @0xbd808  ← DEFECT (§4)

Enable path:
  beWanEnablePPPv4Client @0x66ee4 → libccc_executePPPv4Client (libcccbe @0x348f4)
    → system queue: /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag
                    > /tmp/pppd-info.tmp 2>&1 &
  Interface name: setWanIpPppInterfaceName @0x346d0 (PPP branch @0x348a8),
    unit from getPPPPdUnitNum_wrapper @0x38264: snprintf("%d%d%d", IA bytes)
    → 1.1.1 = "111" (ppp111, GPON) · 1.3.1 = "131" (ppp131, Ethernet)
```

**Other options-file generators — exhaustive result:** exactly one other generator exists, for a **different** file: `CreatePPPByFullNAT @0x91d30` writes `/etc/ppp/options_FN%d%d` (same cp+fopen pattern, all format strings `\n`-terminated, **never** emits `pppoe_srv_name` or `linkname`); its launcher `beFullNatEnablePPPv4Client @0x92200` only starts pppd against that file. It is the FullNAT slave-pppd side-feature with no WAN default-route/DCS integration — not an alternative WAN path. Everything else touching options files is a consumer/launcher: libcccbe's launch template, `libCmd.so`'s five pppd launch/kill templates, `hachi`'s restart (reuses the *same* `options_%s` file), pppd itself, and `libpppoe.so` reading `/etc/ppp/options.%s` (dot form).

## 6. pppd option parsing and service-name behavior

**Artifacts:** rootfs `bin/pppd` (sha256 `c94df022…`), rootfs `lib/MSTC/libpppoe.so` (sha256 `c6a83bc8…`).

### 6.1 `pppoe_srv_name` is a plugin option — CONFIRMED STATIC

- The string `pppoe_srv_name` occurs **0 times** in `bin/pppd` — it is not a core option.
- `libpppoe.so` option table @`0x18220`, registered by `pppoe_plugin_init` @`0x2f98` via pppd's `add_options`: entry @`0x18268` = name `pppoe_srv_name`, type 5 (`o_string`), description "PPPoE service name", target address = `&pppoe_srv_name` (ABS64 relocation @`0x18278` → the `char*` global @`0x18508`), flags/limits 0. pppd's `process_option` therefore does `pppoe_srv_name = strdup(value)` with **no length cap**. Sibling options: `device name` (o_wild → `setdevname_pppoe` @`0x2c00`), `pppoe_ac_name`, `pppoe_hostuniq`, `pppoe_retransmit`.
- Loading is hard-wired: pppd lists `libpppoe.so` in `DT_NEEDED`, imports `pppoe_plugin_init`, and has **no dlopen**. The core `plugin` option handler @`0x414d30` strcmp's its argument against `"pppoe"` (@`0x414db4`, direct call) after a pppd-2.4.7 version check. There is no plugin directory (`lib/pppd/2.4.7/` does not exist in the dump).
- The variable is consumed in `setdevname_pppoe` (@`0x2e64`, discovery filter tags) and session setup (@`0x322c`, debug log `pppoe_srv_name=%s`).

### 6.2 What the merged line does in THIS parser — PROVEN FROM CODE

This upgrades the prior STRONGLY INFERRED fatality to **proven from the binary's own control flow** (still not a runtime observation — none exists):

1. **Tokenization:** `getword` @`0x415250` is a pure whitespace **token stream** across the whole file (handles `#` comments, `\` escapes, `"` quotes). The newline flag it sets is **never tested** by `options_from_file` @`0x415bc0`. Line boundaries do not exist for this parser.
2. `pppoe_srv_name` takes **exactly one argument** (`n_arguments` logic @`0x414354`; its flags lack bit `0x200` for multi-arg) → it consumes `3jgloballinkname` as the service name. **Wrong service name — independently fatal to the ISP requirement**, regardless of what follows. The `linkname` directive is never parsed (linkname/link binding is lost).
3. Next token `ppp131` is looked up as an option name → not found (NULL) → `option_error("In file %s: unrecognized option '%s'")` (format @`0x429c3c`, call @`0x415d5c`).
4. `options_from_file` returns 0 → the `file` option handler @`0x415f00` propagates failure through `process_option` (@`0x415a58` → `0x4156ec`) → `parse_args` @`0x415ad8` returns 0 (@`0x415bb0`) → `main` @`0x403be0` executes `mov w0,#2` → **`exit(2)`**.
5. Result: pppd dies during option parsing, **before PPPoE discovery (PADI) is ever sent**. It is not a warning on any code path in this build.

**Consequence:** with service name `3jglobal` set, the vendor-generated configuration cannot establish a session — two independent reasons (wrong service value; fatal stray token). With the service name left empty the file is well-formed but the profile no longer carries the ISP-required service name (see §7.9).


## 7. All alternative service-name mechanisms investigated

Full-rootfs hunt (binaries, libraries, scripts, configs, kernel modules). **Result: NONE FOUND in every category.**

1. **rp-pppoe suite option (`pppoe-service` / `-S`):** zero hits for `pppoe-service` in any file; no standalone `pppoe` client binary exists in the rootfs.
2. **rp-pppoe plugin:** no `rp-pppoe.so` and no `lib/pppd/2.4.7/` directory in the dump (this corrects a prior-mission aside that implied one). It would be unloadable anyway — this pppd has no dlopen and hard-wires `libpppoe.so`. The only stale reference is the legacy script `usr/bin/create_connection` line 126 (`/sbin/pppd file $2 plugin rp-pppoe.so nic-…`): dead path (no `/sbin/pppd`, no `/etc/sysconfig`, the plugin name is rejected by the hard-wired handler, and it sets no service name).
3. **`usr/bin/pppoe-start`:** present but **0 bytes** — a placeholder, not a mechanism.
4. **Environment variables:** neither `pppd` nor `libpppoe.so` imports `getenv`. No env-based service-name channel exists.
5. **Separate configuration files:** no `/etc/ppp/peers/` directory, no `pppoe.conf`; `etc/ppp/` contains only the two options templates plus auth/secret and up/down scripts — none contains a service name or a place to put one that the generated-file flow would read.
6. **Other PPPoE clients:** no accel-ppp, no pppoe-server/relay, no second client implementation of any kind.
7. **Kernel path:** `pppoe.ko` (with pppox/ppp_generic) is present, but contains no service-name strings or module parameters — the kernel channel is driven exclusively by the pppd plugin above.
8. **Command-line service name:** the *mechanism* exists inside pppd (command-line tokens go through the same option machinery and a `pppoe_srv_name <value>` argument placed after plugin registration would be honoured) — but **no firmware launch path uses it**. Every launch format in the firmware is exactly `pppd [-d] file /etc/ppp/options_%s %s` (libcccbe, libbemodules, libCmd templates; §5). There is no supported vendor surface that adds arguments. Classed **POSSIBLE BUT UNPROVEN** as a hypothetical (it would require invoking pppd outside the vendor lifecycle — see §10/§15, candidate P7).
9. **RDM side:** `PPPoEServiceName` is the **only** source feeding the writer — the format string @`0xbd808` has exactly one xref (@`0x66b3c`, in `beConfigWANByPPPoE`), the string exists in no other firmware binary, and nothing downstream overrides the value. No RDM parameter feeds `pppoe_ac_name` either (`ACNAME=` strings in the tree belong to an unrelated reporting helper; `pppoe_ac_name` is written by nothing).
10. **Omitting the service name — explicitly NOT a workaround:** an empty `PPPoEServiceName` produces a well-formed options file (§4.2), but the ISP profile specifies service name `3jglobal`, and **no authoritative evidence** (ISP provisioning data, BRAS behaviour record, or successful-session log) establishes that this BRAS accepts an empty/unspecified service name. Per the mission rule, it is recorded as an **unproven diagnostic hypothesis**, not a solution (§19, step D1).

## 8. All alternative PPPoE configuration paths discovered

1. **Vendor conversion (broadband.cgi)** — the only proven object-creation + configuration path; still ends in the defective writer. Detailed in §9.
2. **USP/TR-369 agent `obuspa` — NEW candidate (POSSIBLE BUT UNPROVEN).** The rootfs USP agent imports `cmsgRequestSetIndexedObj` and contains a fully parameterised template `WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d`. Statically, this is a second management surface capable in principle of indexed PPP object creation (bypassing the ccctest ADD failure mode). Unproven: whether the USP data-model mapping actually exposes WANPPPConnection creation to an operator-reachable controller, whether the same DAS apply-phase validation (Blocker 2, §9.3) would reject it, and whether any USP controller/credentials exist on the unit. **It does not cure B-NEW-1** — any object it creates still feeds `beConfigWANByPPPoE`.
3. **FullNAT PPP generator** (`CreatePPPByFullNAT @0x91d30` / `beFullNatEnablePPPv4Client @0x92200`) — writes a genuinely different, well-formed options file (`options_FN%d%d`, no service-name line at all) but it is a slave-PPP feature with no WAN DCS/default-route/NAT-zone integration and no service-name support. Not a WAN path (§5).
4. **Legacy `usr/bin/create_connection` script — DISPROVEN as viable:** no caller anywhere in the tree; its ifcfg directory `/etc/sysconfig/network-scripts/wan-multi/` does not exist; it requires `rp-pppoe.so`, which does not exist; it sets no service name.
5. **Watchdog/manager restarts** (`hachi`, libCmd templates) — all relaunch pppd against the **same** generated `options_%s` file. They are lifecycle consumers, not configuration paths, and inherit the defect verbatim.
6. **GPON vs Ethernet generator sharing — CONFIRMED:** both use the *same* `beConfigWANByPPPoE` (the defect is profile-agnostic; it is invisible on factory GPON only because of how that profile's options happen to be exercised in prior use — the merged-line generation occurs for **any** connection whose service name is non-empty). There is no Ethernet-specific or GPON-specific alternate writer to switch to.

## 9. Vendor CGI and RDM object creation findings

### 9.1 broadband.cgi — the conversion (CONFIRMED STATIC, all 20 Mission-2 questions answered)

- `cgiMain` @`0x403390` (61,760 B binary, sha256 `78eaacd5…`). There is **no Add-new-profile path** and no `SetIndexedObj` for WANConnectionDevice anywhere in the binary.
- **Trigger:** form save flag + `RN_EncapFlag`=="1" + `RN_ModeFlag`=="0" for the connection named by the form (dispatch @`0x403ad8`).
- **`wanIA`** is a comma-separated IA spec string (e.g. `"1,3,1"`) parsed by `rdmConstructIAValue` (call site @`0x4039f0`); it identifies the **existing** connection. No `.3` is hardcoded — `.3` is wanIA's second component. Converting the factory `Eth_Internet` profile therefore creates exactly `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`.
- **Sequence:** save PortTriggering → SelId(OID `0xcd`) + `cmsgRequestSetIndexedObj(req,0)` @`0x403e34` (**delete the IP object**) → `rdmGetAvaliableIAByOID(rdm, 0xe3, parentIA="%d,%d")` @`0x403e8c` (allocate lowest-free PPP instance; **return value never checked**) → SelId(`0xe3`) + `SetIndexedObj(req,1)` @`0x403f10` (**create the PPP object**) → set all PPP parameters (Username, Password [REDACTED], PPPoEServiceName, authentication, MTU, MRU, NAT tail) → conditional DefaultConnectionService update (only if the default-WAN flag was submitted) → `cmsgRequestSave` @`0x4066d4` → single `cmsgSendRecv(60000)` @`0x4068b8`.
- **Failure is invisible:** the transaction result is never checked in `cgiMain` (`cmsgGetExecResult` is called 0× in `cgiMain` — whole-binary correction: it *is* called at 5 sites in other helpers). A failed conversion looks identical to a successful one in the UI; a read-back verification step is mandatory.
- The conversion changes **no** WAN mode, triggers **no** pppd action, and requires **no** reboot itself. PPP→IP conversion-back is verified at @`0x403f70` (the rollback hinge, §14).
- The handler has **total dependence on the existing IP profile** — there is nothing to convert if `.3.WANIPConnection.1` does not exist.
- The ETH/GPON edit CGIs are render-only (104-byte `cgiMain` stubs; no mutation imports). All mutation lives in `broadband.cgi`. Its RESTART branch is the Web UI's WAN-mode switch (sets Gpon/Eth Enable OIDs `0xc7`/`0xca` + `WANSwitch.WANMode`, with Save).
- **UNKNOWN (U12):** whether the shipped HTML edit page exposes the PPPoE encapsulation option for Ethernet — zero `.html` files exist anywhere in the repo/rootfs dump. Operator-observable in seconds on the live UI; gates the preferred path.

### 9.2 RDM schema ground truth (CONFIRMED STATIC, librdm.so OIDTable, stride 0x118)

| Object | Class OID | Instance OID | Max |
|---|---|---|---|
| WANPPPConnection | `0xf1` | `0xe3` | 8 |
| WANIPConnection | `0xe2` | `0xcd` | 8 |
| WANConnectionDevice.i | — | `0xcc` | 8 |
| WANEthernetInterfaceConfig | — | `0xca` | — |
| X_5067F0_GponInterafceConfig *(vendor typo, exact spelling)* | — | `0xc7` | — |
| WANCommonInterfaceConfig | — | `0xc4` | — |
| Layer3Forwarding | — | `0x80` | — |
| X_5067F0_Ext.WANSwitch | — | `0x4d` | — |

Class template flags `0x2` → instance auto-allocation via `cccRdmAddIndexChildObject` (librdm @`0x134a0`, instance 1 hardcoded @`0x137ec` for an empty child list); `rdmVerifyIAValue` @`0x11e48` checks only depth/non-zero/max. **The schema does not forbid PPP under `.3`.** PPP parameter validation (schema): all 14 parameters confirmed; corrections recorded — `Name` LENGTH 256 (not 64), `VLANID` MAX 5000 (not 4095), `WANMode` appears in neither PDM XML (schema-only), 8 PPP parameters are schema-image-only with no factory-configured instance (incl. `PPPoEServiceName`, `MaxMTUSize`, `PPPAuthenticationProtocol`, `NATEnabled`).

### 9.3 The failed direct ccctest ADD (Blocker 2) — mechanism located, exact rejector UNKNOWN

- The parser's "success" is queue-only: `ccctest` (@`0x402ca8`) passes the path verbatim to `cmsgRequestSel` + `cmsgRequestSetIndexedObj(req,1)`; `libcmsg` performs zero validation. Its reply printer (@`0x4017dc`) proves the per-action verdict (bit `0x40000000` → `ADD…: success`) is independent of the header verdict (bit 30 → `transaction fail !!`).
- The `.1` spelling resolves server-side via `cccRdmGetObjListByName` (librdm @`0x12324`) → `cccDasHandleSetIndexObject` (ccc_das @`0x412810`) → `cccRdmAddObjectWithAssignIA`; the NACK is issued in **`cccDasHandleApply`** (callback table @`0x4162a8`, log tag `CCC_MSG_VALIDATE_FAIL`).
- Leading hypothesis (UNPROVEN): a sibling action bundled in the same SEND — plausibly the coexisting `.3` IP object, which the vendor conversion deletes *first* — poisoned the apply phase. No corrected ADD is recommended; an ADD-alone transaction is diagnostic-only. The exact rejecting callback requires the original failed script + full stdout + device syslog grepping `CCC_MSG_VALIDATE_FAIL` — none of which exists in the repo. (The older audits' "validation error code 0x00000002" appears in **no** artifact — uncorroborated, do not quote. DISPROVEN as causes: trailing `.1`, schema forbidding `.3`, max-instances, AssignIA, missing SAVE.)
- Comparison with the vendor sequence is instructive: the CGI **deletes IP first, then creates PPP, in one transaction, and never checks the result** — the failed CLI attempts did neither the delete-first ordering nor (evidently) a clean single-purpose transaction.

## 10. Alternative Ethernet WAN implementation architectures

1. **A/C — Vendor UI conversion (same path, one execution).** Approaches A (Web UI) and C (profile conversion) from Mission 2 are **provably the same firmware path**: the UI is the conversion's only caller. Create `.3.WANPPPConnection.1` by converting `Eth_Internet`, park `.1` (Enable=0, never delete), correct the DCS pointers (§11.5), set WANMode=ETHER via the UI RESTART branch (not `linkdetection`), one reboot. Blocked only by B-NEW-1 (options stage) and U12 (UI exposure gate).
2. **USP/TR-369 object creation (obuspa)** — §8.2. An object-creation alternative only; configuration generation is unchanged and defective.
3. **Manual/out-of-band pppd launch with a hand-built options file** — the firmware *contains* all components (pppd, plugin, kernel modules, `nas0_notag`), and pppd would accept a correct options file (including a command-line service name, §7.8). But no vendor lifecycle (RDM enable path, Event 206 wiring as configured, watchdog, persistence across reboot) is demonstrated for an out-of-band launch, and the mission rule forbids recommending manually created configuration unless integration is demonstrated. Classed **POSSIBLE BUT UNPROVEN**, listed for completeness — not a supported path.
4. **FullNAT PPP** — different feature, no WAN integration (§8.3). DISPROVEN for this objective.
5. **Native `linkdetection` ETHER switch as the activation route — rejected:** it creates/enables only the `.3` **IP** profile, points DCS at `WANIPConnection.1`, disables the VoIP connection device `.2`, rewrites IPv6 pointers to the IP object, and **clobbers the ACS URL** to `http://testacs.airtelbroadband.in:8103/` (with trailing slash) plus `ManagementServer.X_5067F0_OverIPv6`=1. It can never create a PPPoE profile. (Its GPON branch sets the production `http://tms.airtelbroadband.in:8103`, no slash.)


## 11. Full PPPoE lifecycle and integration analysis

Mission-3 recheck of all 18 integration items: **16 hold, 1 corrected/completed (FORWARD), 1 holds with the standing B-NEW-1 blocker (pppd launch + options)**. The six stages are kept distinct — proving one never proves the next.

| # | Stage / item | Verdict | Evidence |
|---|---|---|---|
| 1 | LAN4 = PHY port 3, WAN mask `0x08` (GPON port 7 / `0x80`) | CONFIRMED STATIC | `rtk_wan_port_mapping` (libcccbe @`0x37c84`): two distinct writes — port index → `/proc/ni/dev_port_mapping`, bitmask → `/proc/fc/ctrl/wan_port_mask`. Prior summaries merging the two values are imprecise. |
| 2 | `nas0` / `nas0_notag` creation | CONFIRMED STATIC | `createLayer3Interface` @`0x35348` (`smuxctl … --tags 0` for untagged); `libcccBeWan_eth_Init` does **not** create it. Tagged variant `nas0_<vid>` exists if a VLAN were ever proven required. |
| 3 | Ethernet WAN init | CONFIRMED STATIC | `libcccBeWan_eth_Init` @`0x38074` = EthPhyEnable(1) + `smuxctl` rsmux + hw_vlan_filter + `rtk_wan_port_mapping(0,…)`. No pppd involvement. |
| 4 | WAN-mode boot callback | CONFIRMED STATIC | Boot gate @`0x50d08` (libbemodules): eth_Init only if Eth Enable && `WANSwitch.WANMode=="ETHER"` (strcmp @`0x50ec8`); spawns `linkdetection &`. **Reboot required both directions:** init functions have exactly one call site (Boot); BE WANMode writes force `WAN_MODE_CHANGE_REBOOT` via `doWanModeChange` @`0x36d3c`; SET_NO_BE writes silently require a manual reboot. `nas0_notag` is rebuilt every boot. |
| 5 | PPP object creation + parameter validation | CONFIRMED STATIC (conversion only) | §9. Direct ADD blocked at DAS apply (rejector UNKNOWN, §9.3). |
| 6 | PPP interface naming | CONFIRMED STATIC | Generic `snprintf("%d%d%d", IA)` formula → `ppp131` for 1.3.1, `ppp111` for 1.1.1. **No `ppp111`/`ppp131` literal exists in any binary** (the one `ppp111` fallback is hachi's, item 15). |
| 7 | pppd launch + generated options | Launch CONFIRMED STATIC; **options BROKEN (B-NEW-1)** | §5 call graph; §4 defect; §6 fatality. MTU/MRU serialization (struct +`0x1a`/ +`0x18`), AUTO_AUTH → zero refuse-* lines, service-name serialization defective. |
| 8 | Link up/down events | CONFIRMED STATIC | `/etc/ppp/ip-up` verbatim generic: `EVENTNOTIFY 206 string $REALNAME` via a ccctest script file; ip-down emits 207; IPv6 twins 213/214. All route/NAT/DNS/MSS work is delegated to ccc_be Event 206/207 handlers. |
| 9 | IPv4/IPv6 DCS pointers | CONFIRMED STATIC + hazard | `Layer3Forwarding.DefaultConnectionService` + IPv6 twin + per-mode keys (OID `0x83`) + IPv6PD interface pointer. **Hazard:** `updateDefaultRouteByLinkType` @`0x6f2d8` rewrites the live DCS from per-mode keys on mode flips — and the factory `_ETHER` key points at the `.3` **IP** object. All four pointers must be set to the `.3` PPP object **after** the PPP object is committed, never before. |
| 10 | Default route installation | CONFIRMED STATIC (mechanism); primacy UNKNOWN (U7) | Route handler @`0x56d10`, `isDefaultGw`/DCS-gated. Whether the runtime route follows DCS or the Event-206 interface name is a runtime observation (U7). |
| 11 | NAT / MASQUERADE | CONFIRMED STATIC | Generic templates in libbemodules only: `iptables -t nat -A NAT_POSTROUTING -o %s -j MASQUERADE` (+ `-s %s/24`, SNAT variants). Zero MASQUERADE strings in libbeEvents. Prior literal `-o ppp111` claim DISPROVEN. |
| 12 | Firewall FORWARD | CORRECTED/COMPLETED in Mission 3 | The previously "missing" FORWARD pair lives in **hachi's watchdog** operating over the TR181Frwl chains plus the config-driven reload @`0xbcb8`. Interface-name driven. Exact ppp131 rule list remains a runtime check (U8). |
| 13 | DNS propagation | CONFIRMED STATIC (mechanism); runtime = U9 | `usepeerdns` (template) → `resolv_%s.conf` → `configDNSServers` handles both IP and PPP branches; inherits the DCS hazard (item 9). |
| 14 | MSS clamping | CONFIRMED STATIC | Global pair `addTCPMSSDefaultRule`/`delTCPMSSDefaultRule`: `iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu` (+ip6tables); called from `beConfigWANByPPPoE` @`0x66f18` area. No literal 1440 — effective MSS follows MTU (1480 → 1440). Call timing = U10. |
| 15 | `hachi` watchdog | CONFIRMED STATIC + new detail | Falls back to literal `ppp111` **only if** WAN ifname resolution returns nothing (@`0x4027b4`; rule context @`0x404648`). Mission-3 addition: hachi also **re-launches pppd against the same `options_%s` file** — it is a lifecycle consumer of the defective file, not a bypass. Risk: Low–Med (missed firewall-rule repair on the wrong interface only). |
| 16 | Teardown / rollback mechanics | CONFIRMED STATIC with caveats | pppd teardown: SIGTERM → 2 s → SIGKILL @`0x6722c`; `nas0_notag` removed via `smuxctl` delete @`0x35f60` on interface teardown; **the options file is never deleted** (inert residue). DELETE semantics: §14. |
| 17 | LAN3 / Wi-Fi preservation | CONFIRMED STATIC (by omission) | §13. |
| 18 | GPON + ACS preservation | CONFIRMED STATIC | §14. |

### 11.7 Hypothetical firmware-side corrections — ANALYSIS ONLY (nothing patched, nothing deployed)

| Candidate correction | Location | Sharing / side effects | Integrity & storage | Reboot survival | Rollback | Assessment |
|---|---|---|---|---|---|---|
| Single-byte change: append `\n` — **not actually a single byte**: the format string is NUL-terminated in a packed string table; inserting a byte shifts subsequent strings unless a free byte exists. The 6 bytes after the NUL are alignment padding before the next string, so an in-place change of the NUL at `0xbd808+19` to `0x0a` plus a new NUL one byte later is *arithmetically* possible within padding. | `libbemodules.so`, fmt @`0xbd808` | The string has exactly **one** xref (the defective write) — no other code path shares it, so the change would affect only PPPoE options generation. | **Blocking:** the library lives at `/lib/MSTC/` on `/dev/root` — **read-only squashfs under dm-verity** (cmdline `root=/dev/dm-0`, verity over UBI volume `ubi_r0`; dual slots r0/r1 byte-identical). The system's only overlay covers `/etc` (upper on ubifs `/config`); `/lib` is not overlaid. There is **no runtime write path** to the file. | A change could only persist via a rebuilt firmware image flashed through the update path. | Rollback = reflash the stock image (if obtainable/accepted). | **HYPOTHETICAL — NOT ESTABLISHED AS SAFE.** Update-path integrity: the RAS path (`fwupgrade.sh` → `fw_utils.sh` → `check_chksum_0.0.1`) enforces model check (101), magic (102), per-image header **checksum** (100) and TLV `isVerify`; an OpenWrt sysupgrade/usign signature path coexists behind `REQUIRE_IMAGE_SIGNATURE`. Which route is operator-facing is UNKNOWN; a checksum-only route might accept a rebuilt image, a signature route would reject it, and a failed flash risks bricking the unit. **This report does not recommend attempting it.** |
| Replacing `libbemodules.so` wholesale on a writable overlay | n/a | Same library serves all WAN types — collateral risk to GPON/IP paths. | No overlay covers `/lib` (see above). | No. | n/a | **Not possible on the stock layout** (static evidence). |
| Diverting generation (e.g. making the service name arrive via a different writer) | n/a | No other writer exists (§§4.4, 7, 8). | — | — | — | **DISPROVEN as an existing mechanism.** |

**Plain statement:** no safe correction path can be established from static evidence. The defect is real, narrow, and — on this firmware layout — not correctable without a vendor firmware change or a full reflash whose acceptance and safety cannot be proven here.

## 12. Routing, NAT, firewall and DNS implications

- **Default route:** installed by the Event-206 route handler following the DCS machinery (item 9/10). The single most error-prone step of any deployment is DCS correctness: four pointers (IPv4 DCS, IPv6 DCS, `_ETHER` per-mode key, IPv6PD interface) must name the `.3` **PPP** object, set only after the object exists, because `updateDefaultRouteByLinkType` will otherwise rewrite the live DCS back to the `.3` IP object on a mode flip.
- **NAT:** generic `-o %s MASQUERADE` — interface-name driven, works for `ppp131` by construction. No GPON-specific NAT assumption exists anywhere (prior `-o ppp111` literal: DISPROVEN).
- **Firewall:** FORWARD handling is config-driven (TR181Frwl chains) + hachi watchdog repair (§11 item 12); the only `ppp111` literal in the entire system is hachi's ifname-resolution fallback — a repair-path cosmetic risk, not a session blocker.
- **DNS:** `usepeerdns` + per-interface `resolv_%s.conf` + `configDNSServers` (IP and PPP branches) — generic; runtime propagation to LAN clients is U9.
- **MSS:** global PMTU clamp (§11 item 14); MTU 1480 ⇒ effective MSS 1440 automatically.
- **IPv6:** pointers and NDPPD/IPv6PD machinery point at connection objects generically; whether the ISP delegates IPv6 over this PPPoE is UNKNOWN (U15) and out of scope for the IPv4 objective.
- **Fastpath:** the only proven hardware-flow coupling is the `wan_port_mask` at init; fastpath offload behaviour for established `ppp131` flows is UNKNOWN (U10) — a performance question, not a correctness blocker on static evidence.
- **Hardcoded-assumption sweep (Mission 3 re-run):** `ppp131` — zero literals anywhere. `ppp111` — exactly one literal (hachi fallback). `nas0_100` / GPON-specific connection paths — none found in the PPP/routing/NAT handlers; L2 naming is data-driven (`nas0_notag` untagged, `nas0_<vid>` tagged).

## 13. LAN3/Wi-Fi preservation analysis

- **CONFIRMED STATIC (by omission):** LAN3 = port 2 / mask `0x04` appears in **no** WAN-init, mode-switch, PPP, routing, or firewall function examined across three missions. The WAN mask write touches only the WAN port bit (`0x08` Ethernet / `0x80` GPON).
- Bridge membership is configuration-driven (LAN bridge config), and no mode-switching or conversion code path modifies bridge membership, LAN DHCP, or LAN addressing. Wi-Fi AP interfaces are members of the same LAN bridge by the same configuration, untouched by all WAN code examined.
- Preservation is therefore **by omission, not by an explicit guarantee** — the honest classification. The runtime regression checks (bridge membership before/after, DHCP lease, client association, LAN→Internet via the new WAN) are enumerated in the consolidated procedure retained in §19/§14 summaries and remain runtime obligations (U11).
- The one mode-switch actor that *does* damage unrelated profiles is `linkdetection` (disables VoIP ConnDev.2, §10.5) — another reason it is rejected as the activation route; it still does not touch LAN3/Wi-Fi.

## 14. GPON preservation and rollback implications

### 14.1 Coexistence — CONFIRMED STATIC

`.3.WANPPPConnection.1` can exist while `.1.WANPPPConnection.1` (GPON) remains intact: an ADD/conversion under `.3` touches only `.3`'s child counts. Safe shape: **`.3` PPP enabled, `.1` PPP parked at Enable=0, never deleted** — five factory references point at the `.1` PPP object. Both-enabled simultaneously is a vendor-never-shipped state: UNKNOWN, avoided by design. `getWANDeviceObjectRequestedLinkType` (libcccbe @`0x34334`) returns a **media** type (Gpon Enable OID `0xc7` ≠ 0 → GPON wins; else Eth Enable `0xca` ≠ 0 → Ethernet; else other) — the prior "return 1 = PPP" reading is DISPROVEN (U14/C-11 closed).

### 14.2 DELETE audit (ccctest `DELETE …WANConnectionDevice.3.WANPPPConnection.1;`)

- Parser: canonical form includes the `.1` instance; no parent SEL required; DELETE must be its own transaction with **SAVE + SEND both required**.
- Execution: **mark-and-sweep** purge — the object is marked, the actual purge timing is **UNKNOWN**; a child-count read-back to 0 is the only acceptable proof of completion.
- **DCS is never auto-repaired** — if DCS pointed at the deleted object it must be restored manually (mandatory rollback step).
- The PPP options file is **never deleted** (inert residue, §11 item 16). pppd for the deleted object is terminated by the normal disable/teardown path (§11 item 16) — but only in the audited sequence; deletion alone is not a session-teardown guarantee.
- DELETE under `.3` **cannot touch `.1`** (CONFIRMED STATIC — addressing is downward-only from the named parent).
- **World-dependence:** rollback differs by creation world — conversion world ⇒ vendor **conversion-back** (@`0x403f70`) is the safest mechanism; ADD world ⇒ the audited DELETE. Mixing worlds creates `WANIPConnection.2` artefacts. Config-backup restore is the guaranteed floor in both worlds.
- The preserved user script `ether-rollback.ccc` is **defective**: it contains no SAVE, deletes no `.3` PPP object, and restores no ACS value. Do not rely on it as-is. (It is user-provided evidence and is preserved unmodified.)

### 14.3 Factory vs Phase-0 baseline restoration matrix (consolidated)

Sources: factory PDM XML = backup copy = ROM decode (byte-identical); Phase-0 live baseline = `ether-backup.lz` decode. `IGD` = `InternetGatewayDevice`, `CD` = `WANDevice.1.WANConnectionDevice`. **Baseline beats factory where they differ.**

| Parameter | Factory | Phase-0 baseline | Ethernet target | Rollback value |
|---|---|---|---|---|
| `IGD.X_5067F0_Ext.WANSwitch.WANMode` | absent (schema default "GPON") | absent | `"ETHER"` | `"GPON"` / absent |
| `…WANSwitch.WanAutoDetect` | 1 | 1 | 1 during deployment → 0 after success | **1** ⚠ (scripts/linkdetection write 0 — deliberate-choice trap) |
| `WANDevice.1.WANEthernetInterfaceConfig.Enable` | 1 | **absent ⚠** | 1 | baseline state (absent) — writing factory 1 ≠ baseline |
| `WANDevice.1.X_5067F0_GponInterafceConfig.Enable` (exact typo spelling) | absent (effective 1, STRONGLY INFERRED) | absent | 0 | absent / effective 1 |
| `WANDevice.1.WANCommonInterfaceConfig.WANAccessType` | absent (status param) | absent | do not write | n/a (live value UNKNOWN; not load-bearing in any decoded path) |
| `Layer3Forwarding.DefaultConnectionService` | .1 PPP | .1 PPP | .3 PPP | .1 PPP |
| `X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` | .1 PPP | .1 PPP | .3 PPP | .1 PPP |
| `…DefaultConnectionService_GPON` / `_ETHER` keys | .1 PPP / .3 **IP** | same | _ETHER → .3 **PPP**; _GPON untouched | factory state (already correct) |
| `…IPv6PDWanConnection.Interface` | .1 PPP | .1 PPP | .3 PPP (U15-conditional) | .1 PPP |
| `IGD.ManagementServer.URL` | `http://tms.airtelbroadband.in:8103` | same | **unchanged** (UI path); testacs only if linkdetection ran → restore | `http://tms.airtelbroadband.in:8103` (no trailing slash) |
| `IGD.ManagementServer.X_5067F0_OverIPv6` | absent | absent | 1 only as linkdetection side effect → revert | 0 / absent |
| `CD.1.WANPPPConnection.1` (VLAN 100, ppp111, creds [REDACTED]) | present, Enable=1 | identical | untouched except Enable→0 park | Enable=1, rest as factory |
| `CD.2.WANIPConnection.1` (VoIP, VLAN 660) | Enable=1 | identical | untouched ⚠ (linkdetection ETHER sets 0 — rejected path) | Enable=1 |
| `CD.3.WANIPConnection.1` (`Eth_Internet`, nas0_notag) | Enable=1 | **Enable absent ⚠** + `0.0.0.0` Gw/Subnet/ExtIP elements (linkdetection Tx-A fingerprints) | conversion world: deleted → PPP; ADD world: kept | IP present, PPP absent, Enable per baseline |
| `CD.3.WANPPPConnection.1` | absent (count 0) | absent | present, Enable=1, `3jglobal`/1480/1480/AUTO_AUTH/NAT=1/VLAN off | absent (count 0) |
| `CD.4` / `CD.5` profiles | factory | identical | untouched | already correct |
| Firewall DEFAULTWAN / DEFAULTWANv6 bindings | → .1 PPP / ppp111 | identical | untouched | already correct |

**Must remain untouched during any Ethernet deployment:** the whole `CD.1` PPP object except its Enable byte; Gpon/Eth `IfName` values; both `_GPON` DCS keys; `CD.2`/`CD.4`/`CD.5`; firewall DEFAULTWAN bindings; all ManagementServer parameters (except repairing URL/OverIPv6 if linkdetection clobbered them); the BrasList.

### 14.4 ACS/TR-069 — closed

Phase-0 ACS URL is **known byte-exact**: `http://tms.airtelbroadband.in:8103` (no trailing slash; factory PDM + ether-backup + ROM agree). `linkdetection`'s ETHER branch writes `http://testacs.airtelbroadband.in:8103/` (**with** slash) + `OverIPv6`=1; its GPON branch writes the production URL. **`broadband.cgi` never touches ManagementServer** — the UI/conversion path is ACS-immune (CONFIRMED STATIC). TR-069 (ztr69) push-back after a legitimate change is a HYPOTHESIS-level risk with no artifact evidence; keeping the production ACS URL is the mitigation.


## 15. Candidate implementation paths comparison table

| Candidate | Firmware evidence | PPPoE service-name compatibility | RDM requirements | Routing/NAT integration | Risks | Verdict |
|---|---|---|---|---|---|---|
| **P1 — Vendor UI conversion (A/C)**: convert `Eth_Internet` (.3 IP) → PPPoE via broadband.cgi, park .1, fix DCS, WANMode=ETHER via UI RESTART, reboot | cgiMain @0x403390 full sequence decoded (§9.1); only proven creation path | **✘ Broken** — converted object feeds defective writer; `3jglobal` produces merged line → pppd exit(2) (§§4, 6) | Conversion only; no ADD needed; DCS ×4 set after commit | Full vendor integration (Event 206, NAT, DNS, MSS) — CONFIRMED generic | U12 (UI may not expose PPPoE for ETH); silent CGI failure (mandatory read-back) | **STRONGLY SUPPORTED** as the object-creation route; **blocked at the options stage by B-NEW-1** |
| **P2 — Minimal ccctest ADD** (.3 PPP, no `.1`, no bundled SETs) | Parser + DAS chain decoded (§9.3); schema permits | ✘ Broken — same writer | Direct ADD; exact apply-phase rejector UNKNOWN | Same vendor integration *if* object commits | Prior identical-family attempt NACKed in `cccDasHandleApply`; cause unproven | **POSSIBLE BUT UNPROVEN** (diagnostic-only; not a deployment path) |
| **P3 — USP/TR-369 (obuspa) object creation** + vendor enable flow | obuspa imports `cmsgRequestSetIndexedObj`; template `WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d` (Mission 3, §8.2) | ✘ Broken — same writer | USP data-model create instead of CGI/CLI | Same vendor integration *if* object commits and enables normally | USP exposure/controller/credentials UNKNOWN; may hit the same DAS validation as P2 | **POSSIBLE BUT UNPROVEN** (new; creation-stage alternative only) |
| **P4 — linkdetection ETHER switch** as activation/creation route | linkdetection @0x402454 fully decoded | ✘ — creates no PPP at all | Creates .3 **IP** only | Points DCS at the IP object (wrong for PPPoE) | Clobbers ACS to testacs + OverIPv6=1; disables VoIP CD.2; rewrites IPv6 pointers | **DISPROVEN** for this objective (retained only as evidence of mode machinery) |
| **P5 — FullNAT PPP generator** (`options_FN%d%d`) | CreatePPPByFullNAT @0x91d30 decoded (§5) | ✘ — never emits a service name at all | FullNAT feature objects, not WAN profile | No DCS/default-route/WAN-NAT integration | Wrong feature (slave PPP) | **DISPROVEN** for this objective |
| **P6 — Legacy `create_connection` / rp-pppoe script path** | Script present at usr/bin/create_connection line 126 | ✘ — sets no service name; requires nonexistent `rp-pppoe.so` | ifcfg files in a directory that does not exist | None | No caller; dead on this firmware | **DISPROVEN** |
| **P7 — Out-of-band pppd launch** (hand-built options file or command-line `pppoe_srv_name 3jglobal`, bypassing the vendor generator) | All components exist (pppd, libpppoe.so, pppoe.ko, nas0_notag); pppd option machinery would accept it (§7.8) | **✔ Compatible in principle** — the only candidate that can present `3jglobal` correctly | None (bypasses RDM) — which is also its defect: no RDM state, no vendor enable lifecycle | **Not demonstrated**: Event 206 fires from ip-up regardless of launcher, but persistence across reboot, watchdog interaction, DCS/route primacy (U7), and disable/teardown ownership are all unproven | Unsupported by any vendor surface; lost on reboot (options regenerated / process not relaunched by vendor paths — hachi relaunches only the vendor file); mission rule: no recommended manual path without demonstrated integration | **POSSIBLE BUT UNPROVEN** |
| **P8 — Empty service name** on P1 (leave `PPPoEServiceName` unset) | Writer skips the line; file well-formed (§4.2) | **? Unknown** — no authoritative evidence the BRAS accepts empty for the `3jglobal` profile | Same as P1 | Same as P1 | If the BRAS requires the service name, discovery/auth fails with no local error pointing at the cause | **POSSIBLE BUT UNPROVEN** (diagnostic hypothesis only — explicitly **not** a workaround, §7.10) |
| **P9 — Hypothetical firmware correction** (format-string byte fix via rebuild/reflash) | Defect location byte-exact (§4); string has a single xref; padding space exists arithmetically (§11.7) | ✔ Would be compatible if correctly applied | None | Full vendor integration (it *is* the vendor path, repaired) | dm-verity read-only rootfs; reflash required; update-route integrity (checksum vs signature) unresolved; brick risk; **analysis only — not attempted, not recommended on this evidence** | **POSSIBLE BUT UNPROVEN** (hypothetical) |
| **P10 — GPON PPPoE writer reuse for Ethernet** ("use the working GPON path") | Both profiles share the *same* `beConfigWANByPPPoE` (§8.6) | ✘ — identical defect | n/a | n/a | Premise false: there is no second writer | **DISPROVEN** |

**Reading of the table:** every vendor-supported path (P1–P3) converges on the same defective writer; the only candidates that can present `3jglobal` correctly (P7, P9) are unproven/unsupported or hypothetical. That is the whole blocker, stated once.

## 16. Newly discovered blockers

- **B-NEW-1 (CRITICAL, pre-existing from Mission 2, re-verified + escalated in Mission 3):** service-name format defect (§4) with pppd fatality now **proven from pppd's code** (§6.2). No config-side mitigation exists (file regenerated per enable; sole writer; sole RDM source). Blocks every vendor path.
- **B-M3-1 (new, informational):** `obuspa` (USP) attack/usage surface is unmapped — it is simultaneously the only new creation candidate (P3) and an unexamined management plane. No blocker to P1, but P3 cannot be evaluated further without a dedicated USP data-model pass.
- **B-M3-2 (new, minor):** `hachi` is not merely a firewall watchdog — it can **relaunch pppd against the vendor options file**. Any future out-of-band experiment (P7) must account for hachi restarting the *defective* vendor file's session attempts and for two pppd instances contending for the same unit/linkname. LOW–MED.
- **B-M3-3 (new, clarification of scope):** firmware-correction feasibility is bounded by **dm-verity + dual-slot UBI layout** (§11.7) — even the update path's operator-facing integrity route is unresolved (RAS checksum/TLV vs sysupgrade signature). This converts "small patch" intuition into "reflash project with brick risk" — recorded so it is not re-litigated.
- No other new blockers: the 18-item integration recheck found no third deployment blocker (§11).

## 17. Disproven approaches and why they fail

1. **Direct ccctest ADD as previously attempted** — NACKed at DAS apply (§9.3); parser "success" was queue-only.
2. **`linkdetection` as the Ethernet-PPPoE activator** — creates IP only, clobbers ACS, disables VoIP CD.2 (§10.5).
3. **"Ethernet session is ppp111"** (prior REVERSE_ENG passages) — formula gives `ppp131` for ConnDev.3; the same file contradicts itself elsewhere; disassembly wins (C-6).
4. **Hardcoded unit 111 / `-o ppp111` NAT / ip-up `ppp111` literal / MSS literal 1440** — all DISPROVEN as literals (C-5, C-7; §11 items 11/14; §12).
5. **rp-pppoe plugin / `pppoe-start` / `create_connection`** — absent, empty, or dead (§§7, 8).
6. **FullNAT PPP as a WAN path** — wrong feature, no routing integration (§8.3).
7. **A second/generated-elsewhere options file for the WAN profile** — no second generator exists (§5).
8. **Schema forbids `.3` PPP / trailing `.1` broke the ADD / missing SAVE caused count 0** — all DISPROVEN (§9.2–9.3).
9. **`getLinkType` returns "1 = PPP"** — it returns a media type (§14.1).
10. **Correctly-spelled `X_5067F0_GponInterfaceConfig`** — fails resolution; the vendor spelling is `…GponInterafceConfig` (sic), CONFIRMED.
11. **Old rollback script `ether-rollback.ccc`** — defective (no SAVE, no .3 PPP deletion, no ACS restore) (§14.2). Preserved as user evidence; not a mechanism.
12. **Prior OID tables / audit hashes in pre-mission audits** — superseded by OIDTable ground truth and the §3.1 hash table (C-1…C-15, Mission-1 ledger, transferred here in substance: wrong broadband.cgi hash in README; `ccc_be 0x415860` misattributed as ADD dispatcher; `analysis/config_rdm_decoded.xml` is not XML; REVERSE_ENG self-contradiction on ppp131).

## 18. Remaining unknowns

Runtime observations (each with its settling observation — none performed; static analysis cannot substitute):

| ID | Unknown | Settles by |
|---|---|---|
| U1 (narrowed) | Exact DAS apply-phase rejecting callback for the failed ADD | Original failed script + full ccctest stdout + device syslog grepping `CCC_MSG_VALIDATE_FAIL` |
| U3 (reframed, low-risk) | Live `/etc/ppp/default_options` contents vs dump templates | `cat` both files on a running unit; inspect a generated `options_nas0_notag` |
| U4 | pppd honours `unit 131` text → creates `ppp131` | `ip link`, `/var/run/ppp131.pid`, `/tmp/pppd-info.tmp` after a successful enable |
| U7 | Event-206 route follows DCS vs event ifname | Bring ppp131 up with DCS deliberately mispointed; observe `ip route` |
| U8 | Exact FORWARD rule list installed for ppp131 | `iptables -S FORWARD; iptables -t nat -S` with session up |
| U9 | Peer DNS reaches resolv.conf/dnsmasq for ppp131 | Inspect resolv.conf + dnsmasq config after IPCP |
| U10 | MSS call timing; fastpath offload of ppp131 flows | `iptables -S FORWARD \| grep TCPMSS` at boot vs up; flow counters under load |
| U11 | LAN3 stays in the LAN bridge through activation | `bridge link` before/after captures |
| **U12** | **Shipped ETH edit HTML exposes PPPoE option?** | **Operator opens the live Eth_Internet edit page — seconds (gates P1)** |
| U13 | ISP VLAN actually required on this ONT path? | Authoritative ISP provisioning data, or the untagged attempt's outcome |
| U15 | IPv6 delegation behaviour of the Ethernet PPPoE profile | After v4 success: check IPv6 PD/RA state |
| U16 | Default values of schema-image-only PPP params in a freshly created object | Read back the full object after a successful creation |

Static unknowns: DAS sweep timing after DELETE (§14.2); SAVE-vs-apply flash persistence on a NACKed transaction; Gpon Enable schema-default byte in isolation (inferred 1); live `WANAccessType` value; CWMP reaction to URL changes; which firmware-update integrity route is operator-facing (§11.7); USP data-model exposure (§16 B-M3-1).

*Repository-cleanup note:* the full 2,601-file inventory (`REPOSITORY_INVENTORY.csv`, Mission-1 generated) is **preserved on this branch for user review** rather than deleted — it is the reproducibility audit trail for every hash cited here; its summary document was superseded by §3.1 and deleted. All other Mission-1/2 reports and working files were deleted in this consolidation after transfer of their unique findings into this report and `MASTER_FINDINGS.md`. No pre-mission file, firmware artifact, user script/log/backup, or source file was deleted or modified.

## 19. Safest technically supported next steps

Ordered; each step is gated by the previous one's evidence. **No step involves patching, flashing, or unsupported commands.**

- **D1 (operator, minutes, zero-risk, read-only):** Open the live Web UI edit page for `Eth_Internet` and record whether a PPPoE encapsulation option with service-name/MTU/MRU/auth fields is exposed → settles **U12**, the gate for P1. Also read back (read-only) the current `.3` object counts, DCS values, `ManagementServer.URL`, and `WanAutoDetect` against the §14.3 matrix.
- **D2 (operator, controlled, diagnostic — the single most useful experiment):** In a maintenance window with the §14 rollback floor (config backup) in place, perform the P1 conversion **with the service name left empty** and enable the profile, then capture: (a) `cat /etc/ppp/options_nas0_notag` (expected: well-formed, no srv_name line — verifies the generation model end-to-end), (b) whether a session establishes (tests the P8 hypothesis against the real BRAS), (c) `/tmp/pppd-info.tmp` and syslog. If the BRAS accepts an empty service name and the session + routing/NAT verify, P8 becomes evidence-backed and the project flips to *statically ready, runtime validated for the session stage* for that configuration. If it rejects, B-NEW-1 is confirmed as an absolute blocker for the exact ISP profile and D3 is the only remaining route. Rollback per §14 (conversion-back + DCS restore + backup floor).
- **D3 (vendor channel, parallel):** Report B-NEW-1 to Airtel/Zyxel as a firmware defect with the byte-level evidence in §4 (format string @`0xbd808` in `libbemodules.so`, single xref, merged-line consequence, pppd exit(2) chain in §6). A vendor firmware fix is the only route that makes the *exact* `3jglobal` profile work through supported paths if D2 fails.
- **D4 (static, optional):** Dedicated USP/`obuspa` data-model pass to grade P3 properly (exposure, controller requirements, DAS interaction) — worth doing only if D2 fails and D3 stalls, since P3 does not cure B-NEW-1.
- **Explicitly not recommended:** repeating the failed ccctest ADD (§9.3); invoking `linkdetection` (§10.5); any firmware patching/flashing experiment (§11.7); presenting the empty-service-name configuration as a solution before D2 evidence exists (§7.10).

## 20. Final readiness verdict

## **NOT READY**

- The firmware **statically supports every stage** of the target topology except one: it generates a **corrupt PPPoE options file whenever the ISP-required service name `3jglobal` is configured** (B-NEW-1, byte-level CONFIRMED, §4), and the bundled pppd **provably exits with code 2** on that file before discovery (§6). No alternative service-name mechanism, no second options generator, and no safe correction path exist in the firmware (§§7, 8, 11.7).
- The verdict is **NOT READY rather than BLOCKED** because two live, low-cost actions can change it without any firmware change: the U12 observation (D1) and the empty-service-name diagnostic against the real BRAS (D2). If D2 produces a working session, the deployment route P1+P8 is evidence-backed end-to-end except the remaining runtime checks (U4, U7–U11). If D2 fails, the project becomes **BLOCKED** pending a vendor firmware fix (D3) — and this report's §§4–6 are the defect filing.
- **RUNTIME VALIDATED is not claimed for any part of this project.** No PPPoE session, on any profile, has been established as part of this research.

*End of consolidated report. Ledger: `MASTER_FINDINGS.md` (this directory). Inventory: `REPOSITORY_INVENTORY.csv` (preserved, §18).*
