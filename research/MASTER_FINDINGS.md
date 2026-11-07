# Master Findings — Airtel AOT5221ZY LAN4 Ethernet WAN + PPPoE

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT. ISP: service name `3jglobal`, MTU/MRU 1480, `AUTO_AUTH`, VLAN UNKNOWN (none invented).
- **Authoritative report:** **[PPPOE_SERVICE_NAME_DEFECT_AND_ALTERNATIVE_PATHS.md](PPPOE_SERVICE_NAME_DEFECT_AND_ALTERNATIVE_PATHS.md)** — the consolidated single report (Mission 3, 2026-11-07). All prior Claude-generated reports on this branch were consolidated into it and deleted; this ledger no longer links to them. Full file inventory preserved as `REPOSITORY_INVENTORY.csv`.
- **Safety boundary:** STATIC ANALYSIS ONLY across all missions. No router/SSH/LAN/runtime access, no patching/flashing/deployment, no credentials recorded (presence-only, `[REDACTED]`).
- **Confidence legend:** CONFIRMED STATIC = decoded from repo binaries · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = prior user-supplied runtime data · STRONGLY INFERRED · HYPOTHESIS · UNKNOWN · DISPROVEN.
- **Tools:** Capstone 5.0.7 + LIEF + pyelftools (host objdump is x86-only); PLT from `.rela.plt`.

## ⚠ CRITICAL DEFECT — B-NEW-1 (CONFIRMED STATIC, byte level; Mission 3 re-verified)

`libbemodules.so` (sha256 `1de450de…`, both copies identical): `beConfigWANByPPPoE @0x664a8` writes the service name with format `"pppoe_srv_name %s"` @`0xbd808` — raw bytes end `…25 73 00`, **no `\n`** — the only one of the function's 32 writes without a newline, immediately before the `linkname` write (`__fprintf_chk @0x66b48` → `@0x66984`). With service name `3jglobal` the generated `/etc/ppp/options_nas0_notag` deterministically contains `pppoe_srv_name 3jgloballinkname ppp131`. **pppd fatality is PROVEN from the bundled pppd's code** (Mission 3 upgrade from inference): token-stream parser → `pppoe_srv_name` consumes `3jgloballinkname` (wrong service name; `linkname` never parsed) → stray token `ppp131` → `unrecognized option` → `exit(2)` before discovery. **No alternative service-name mechanism exists** (no rp-pppoe, no `pppoe-service`, no env/file/RDM alternate feed; the command-line mechanism exists in pppd but is used by no firmware launch format). **No safe correction can be established:** the library sits on a dm-verity read-only squashfs (`/dev/root`); correction = rebuild + reflash, integrity route unresolved, brick risk — analysis only, not attempted, not recommended. Empty service name is **not** a proven workaround (no ISP-acceptance evidence).

## Verdict

**NOT READY.** Every other stage is statically proven; the exact `3jglobal` profile is blocked by B-NEW-1 on every vendor path. **Single most useful next experiment:** the gated diagnostic in the consolidated report §19 — D1 (read-only U12 check: does the live `Eth_Internet` edit page expose PPPoE?) followed by D2 (controlled conversion with service name empty + capture of the generated options file and BRAS behaviour). If D2 fails, the project is BLOCKED pending a vendor firmware fix (defect filing = report §§4–6).

## Architecture findings (all CONFIRMED STATIC unless noted)

- **HW:** LAN4 = PHY port 3, mask `0x08`; GPON port 7 / `0x80`; LAN3 = port 2 (absent from all WAN code — preservation by omission). `rtk_wan_port_mapping` @`0x37c84` (libcccbe).
- **Init:** `libcccBeWan_eth_Init` @`0x38074` (PHY + rsmux + vlan filter + mapping; does NOT create nas0); `createLayer3Interface` @`0x35348` creates `nas0_notag`; boot gate @`0x50d08` requires Eth Enable && `WANMode=="ETHER"`; **reboot required both directions** (Boot-only init; BE WANMode writes force `WAN_MODE_CHANGE_REBOOT` @`0x36d3c`).
- **Object creation:** the ONLY proven path is `broadband.cgi` (`cgiMain` @`0x403390`) **IP→PPP conversion** of an existing profile: `wanIA="1,3,1"` names the existing connection (no `.3` hardcoded); delete IP (OID `0xcd`, @`0x403e34`) → alloc PPP (`rdmGetAvaliableIAByOID(0xe3)` @`0x403e8c`, return unchecked) → create (OID `0xe3`, @`0x403f10`) → params → Save @`0x4066d4` → single `cmsgSendRecv` @`0x4068b8`, **result never checked** (failure invisible; read-back mandatory). Conversion-back @`0x403f70` is the rollback hinge. Edit CGIs are render-only stubs. UI path never touches ManagementServer (ACS-immune). U12 (HTML exposes PPPoE for ETH?) UNKNOWN — zero .html in repo.
- **Failed ccctest ADD:** parser "success" = queue-only; NACK issued in `cccDasHandleApply` (callback table @`0x4162a8`, tag `CCC_MSG_VALIDATE_FAIL`); exact rejecting callback UNKNOWN (needs original script + syslog). Schema permits `.3` PPP (class `0xf1`/inst `0xe3`, max 8, auto-alloc @librdm `0x134a0`). Leading hypothesis: sibling-IP coexistence (vendor deletes IP first).
- **PPP lifecycle:** unit = `snprintf("%d%d%d", IA)` (@`0x38264`) → **1.3.1 = ppp131**, 1.1.1 = ppp111; no unit literals anywhere. Options file = `options_nas0_notag` (L2-named), sole writer `beConfigWANByPPPoE` (sole caller `createWANPPPConnectionCfgFile @0x6a7c0`). Launch: `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag &` (@`0x348f4`). AUTO_AUTH → no refuse-* lines. ip-up/ip-down generic (`EVENTNOTIFY 206/207 string $REALNAME`).
- **Routing/NAT/firewall/DNS:** generic, interface-name driven. NAT `MASQUERADE -o %s` (libbemodules only); MSS = global `--clamp-mss-to-pmtu` (1480→1440, no literal); FORWARD lives in hachi's TR181Frwl watchdog + config reload @`0xbcb8`; DNS via `usepeerdns` → `resolv_%s.conf` → `configDNSServers`. DCS hazard: `updateDefaultRouteByLinkType` @`0x6f2d8` rewrites live DCS from per-mode keys; factory `_ETHER` key = `.3` **IP** — all 4 DCS pointers must be set to `.3` PPP **after** object commit. Only `ppp111` literal in the system: hachi ifname fallback @`0x4027b4` (hachi also relaunches pppd on the same vendor options file).
- **Coexistence:** `.3` PPP + `.1` GPON PPP intact = CONFIRMED; safe shape `.3` enabled / `.1` parked Enable=0, **never delete `.1`** (5 factory references). `getWANDeviceObjectRequestedLinkType` @`0x34334` returns a **media** type (prior "1=PPP" DISPROVEN).
- **ACS:** Phase-0 URL KNOWN byte-exact: `http://tms.airtelbroadband.in:8103` (no slash). `linkdetection` ETHER branch clobbers to `http://testacs.airtelbroadband.in:8103/` (with slash) + `OverIPv6`=1, creates only the `.3` IP profile, disables VoIP CD.2 — **rejected as a route**. GPON branch sets the production URL.
- **DELETE audit:** own transaction, SAVE+SEND required, mark-and-sweep (sweep timing UNKNOWN; count read-back is the only proof), DCS never auto-repaired, options file never deleted, cannot touch `.1`. Rollback is world-dependent (conversion-back vs DELETE); backup restore is the floor. User script `ether-rollback.ccc` is defective (no SAVE/DELETE/ACS) — preserved unmodified as evidence.
- **Restoration matrix:** full factory-vs-Phase-0-vs-target-vs-rollback table in consolidated report §14.3 (traps: WanAutoDetect rollback = 1 not 0; Eth Enable baseline = absent ≠ factory 1; `.3` IP baseline bears linkdetection fingerprints; `_ETHER` key factory = `.3` IP).

## Candidate paths (summary; full table in report §15)

| Candidate | Verdict |
|---|---|
| P1 Vendor UI conversion (A/C — provably the same path) | STRONGLY SUPPORTED (creation route) — blocked at options stage by B-NEW-1 |
| P2 Minimal ccctest ADD | POSSIBLE BUT UNPROVEN (diagnostic only) |
| P3 USP/`obuspa` creation (NEW, Mission 3) | POSSIBLE BUT UNPROVEN — does not cure B-NEW-1 |
| P7 Out-of-band pppd launch | POSSIBLE BUT UNPROVEN — only route that can present `3jglobal` correctly; integration/persistence undemonstrated |
| P8 Empty service name on P1 | POSSIBLE BUT UNPROVEN — diagnostic hypothesis, NOT a workaround |
| P9 Hypothetical firmware byte fix | POSSIBLE BUT UNPROVEN (hypothetical; dm-verity/reflash; not recommended) |
| P4 linkdetection route · P5 FullNAT PPP · P6 legacy create_connection/rp-pppoe · P10 "GPON writer reuse" | DISPROVEN |

## Disproven (selection)

Ethernet = `ppp111`; hardcoded unit 111; NAT `-o ppp111` literal; ip-up `ppp111` literal; MSS literal 1440; schema forbids `.3` PPP; trailing `.1` broke the ADD; correctly-spelled `GponInterfaceConfig`; `rp-pppoe.so` present; a second options generator for the WAN profile; prior audits' OID tables and several hashes (see report §17).

## Open (report §18)

U12 (gate), U13 VLAN, U1 rejector, U3/U4/U7–U11/U15/U16 runtime observations; USP exposure (B-M3-1); update-integrity route. Closed across missions: U2, U5, U6 (mostly), U14.

*History: Mission 1 (inventory + 18 reports, commits `c5bc074`/`308822c`), Mission 2 (CONCRETE_IMPLEMENTATION_CHECK_AND_ROLLBACK, `7adb3e5`), Mission 3 (this consolidation + cleanup). Git history is preserved; superseded documents live in history, not the working tree.*
