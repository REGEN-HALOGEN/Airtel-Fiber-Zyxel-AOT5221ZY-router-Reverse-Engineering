# _work_b124 — Blockers 1, 2, 4: independent static verification

- **Scope:** Blocker 1 (broadband.cgi 20 questions), Blocker 2 (ccctest ADD failure root cause), Blocker 4 (DELETE audit + safest rollback). STATIC ANALYSIS ONLY — no router access, no runtime claims. Every prior claim below was re-derived from the binaries in this session; where a prior claim was wrong or imprecise, the correction is stated explicitly.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe` (verified). **Analyst:** subagent session 1a18ee6c.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries in this session · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools:** Python 3.12 + Capstone 5.0.7 + pyelftools (`/tmp/revenv/bin/python`); PLT resolved from `.rela.plt` by decoding PLT stubs against GOT relocations; host objdump not used (x86-only).
- **Artifacts (SHA-256 re-verified this session, all match the prior reports' table):**
  `broadband.cgi` 78eaacd5… · `ccctest.bin` 4badd3f7… (= `rootfs/usr/bin/ccctest`, identical hash) · `librdm.so` 65306765… (= rootfs copy) · `libcccrdm.so` ed2a1d6a… (= rootfs copy) · `libcmsg.so` 57155a27… · `ccc_das` = `rootfs/usr/bin/ccc_das` · `ccc_be` 1da56bc3… · `libbemodules.so`/`libcccbe.so` from `rootfs/lib/MSTC/`.

---

# BLOCKER 1 — broadband.cgi

## 1.0 Verification of the prior claims (each re-derived)

| Prior claim | Verdict this session |
|---|---|
| `cgiMain` @0x403390, size 0x3594 | **CONFIRMED STATIC** (dynsym). `.text` 0x401d80+0x7f6c also matches. |
| `wanIA` parsed by `rdmConstructIAValue` @0x4039ec | **CONFIRMED with address refinement:** the setup instruction is at 0x4039ec (`add x0, sp, #0x4a0`); the call itself is `bl rdmConstructIAValue` @**0x4039f0**. `wanIA` form field read @0x403990 into buf sp+0x4a0, max 8 chars; `wanType` read @0x403978 into sp+0x4a8. Syslog of both values: call @0x4039e8 (block starts 0x4039c0). |
| SelId OID 0xcd + SetIndexedObj(req,0) @0x403e34 | **CONFIRMED STATIC.** SelId call @0x403dd0 (`w1=0xcd`, IA = parsed wanIA); syslog `"WanType is changed to PPP, delete %s(%llx)."` call @0x403e28; `mov w1,#0` @0x403e2c; `bl cmsgRequestSetIndexedObj` @0x403e34. Neither call's return value is tested (next instructions proceed unconditionally). |
| `rdmGetAvaliableIAByOID(0xe3)` @0x403e8c | **CONFIRMED STATIC.** Setup: parent IA built by `rdmConstructIAValue("%d,%d", b1, b2)` — format string @0x40bef8, call @0x403e74, using only the first two IA bytes of wanIA. Then `mov w1=0xe3` via [sp+0x6b8]; `bl rdmGetAvaliableIAByOID` @0x403e8c; result stored over the wanIA variable [sp+0x6a8] @0x403e90 with **no NULL/zero check** (next code loads the RDM handle and proceeds to SelId). |
| SelId(0xe3)+SetIndexedObj(req,1) @0x403f10 | **CONFIRMED STATIC.** SelId call @0x403eac; syslog `"WanType is changed, add %s(%llx)."` @0x403f04; `mov w1,#1` @0x403f08; `bl cmsgRequestSetIndexedObj` @0x403f10. Returns untested. |
| SAVE @0x4066d4 | **CONFIRMED STATIC.** `bl cmsgRequestSave` @0x4066d4 (the other Save in cgiMain is @0x40387c, RESTART branch). Return untested. |
| `cmsgSendRecv(60000)` @0x4068b8, result never checked | **CONFIRMED STATIC, with one correction of scope (see below).** `mov x2,#0xea60` (=60000) @0x4068ac; `bl cmsgSendRecv` @0x4068b8; result stored [sp+0x650] @0x4068bc and used **only** as the argument to `cmsgFree` @0x4068cc. No compare/branch on it anywhere after. |
| `cmsgGetExecResult` absent | **CORRECTED:** the *binary* imports `cmsgGetExecResult` (PLT @0x401ac0) and calls it at 5 sites — 0x40206c, 0x402290, 0x4024b0, 0x4027e4, 0x402c44 — all in unnamed helper functions **outside** `cgiMain`. Inside `cgiMain` the call count is exactly **0** (full call census below). So the precise statement is: *cgiMain never checks the exec result*; "the CGI never checks" is imprecise at whole-binary scope. The 5 external call sites do not affect the conversion path (none is reachable from cgiMain after its SendRecv; cgiMain's post-send code is cmsgFree×2, cmsgUnRegisterModule, free of the PortTriggering list, render calls @0x4068e0+, rdmDeInit, return 0). |
| Call census of cgiMain: Set ×83, SelId ×31, SetIndexedObj ×11, Sel ×1, Save ×2, SendRecv ×1, GetAvaliable ×2, ConstructIA ×13 | **CONFIRMED STATIC — exact match** on an independent census. SetIndexedObj sites: 0x403e34, 0x403f10, 0x40427c, 0x404360, 0x404fcc, 0x405124, 0x4054d0, 0x405730, 0x405c8c, 0x405de4, 0x406078 — identical list to prior report. GetAvaliable sites: 0x403e8c, 0x4042dc. Save sites: 0x40387c, 0x4066d4. SendRecv: 0x4068b8 only. |
| OIDs: 0xcd = WANIPConnection.i, 0xe3 = WANPPPConnection.i, 0x80 = Layer3Forwarding, 0x83 = its X_5067F0_DefaultConnectionService child, 0xc7 = GponInterafceConfig, 0xca = WANEthernetInterfaceConfig, 0x4d = WANSwitch, 0xd3/0xe9 PortTriggering, 0xd5/0xeb DNS, 0xd8/0xee IPv6DNS, class OIDs 0xe2/0xf1 = WANIPConnection/WANPPPConnection | **CONFIRMED STATIC — independently re-derived from `librdm.so` OIDTable** @0x294f0, stride 280: entry = {u32 OID @+0, u64 schema-image offset @+8, char protoPath[] @+16}. Read directly this session for 0x4d, 0x80, 0x83, 0x84, 0x87, 0xc3, 0xca, 0xcc, 0xd3, 0xd5, 0xd8, 0xe2, 0xe9, 0xeb, 0xee, 0xf1 — all match, including the vendor spelling `X_5067F0_GponInterafceConfig` in the 0xc7 proto path itself. |

## 1.1 The 20 questions

**(1) Exact POST field(s) selecting Ethernet PPPoE — CONFIRMED STATIC.**
There is no Ethernet-specific field and no "PPPoE" field. The conversion is generic over whichever connection `wanIA` identifies. Required field combination (disasm @0x403a94–0x403b10):
- a save-flag field equal to `"1"` — `RN_WANETHformSaveFlag` (read @0x4038f0, buf sp+0x570) or `RN_WANGPONformSaveFlag` (@0x4038d8, sp+0x588); two further flag slots (sp+0x578, sp+0x568) are compared against `"1"` (@0x40bd68) at @0x403904–0x403960; if none equals `"1"` the edit block is skipped (branch to 0x406710);
- `wanIA` = the target connection's IA string (for the factory Ethernet profile: `"1,3,1"` — see Q3);
- `RN_EncapFlag` == `"1"` (PPP) **and** `RN_ModeFlag` == `"0"` (routed) — dispatcher @0x403ad8: `strcmp(RN_EncapFlag,"1")` @0x403ae8 ≠0 → PPP→IP branch; `strcmp(RN_ModeFlag,"0")` (string @0x40be08) @0x403b04 ≠0 → PPP→IP branch; both equal → fall through to IP→PPP @0x403b10. (Entry gate @0x403a94: `strncmp(wanType, RN_EncapFlag, 7)`; if equal, conversion is suppressed unless `wanType=="1"` and `RN_ModeFlag=="1"`, jumping to the no-change edit path @0x4043c0.)
Supporting fields consumed by the same POST: `RN_UserName`, `RN_Password` (not overwritten if the submitted value is the sentinel `"****************"` @0x40c510, compared @0x405940), `RN_ServiceName`, `RN_PPPAuth`, `RN_MTU`(@0x406694→`MaxMTUSize`), `RN_Name`, `RN_Active_H` (via the table-driven parameter loop @0x40494c), `RN_Default_WAN_H`, `RN_SelNAT`, `NATTypeSetIndex`, etc.

**(2) wanIA meaning — CONFIRMED STATIC.**
Form string, max 8 chars, read @0x403990 into sp+0x4a0, logged @0x4039e8, parsed by `rdmConstructIAValue(wanIA)` (call @0x4039f0; librdm @0x1125c: strtok on `,`, strtol per token, `rdmSetIAValue` per depth). The resulting 64-bit IA value packs one byte per tree depth: byte 1 = WANDevice instance, byte 2 = WANConnectionDevice instance, byte 3 = connection instance (extraction order in cgiMain is MSB-first: `lsr #0x38` → WANDevice, next byte → WANConnectionDevice, next → connection). It identifies an **existing** connection object; it is not a request to create a new profile.

**(3) Does wanIA select .3? — CONFIRMED STATIC (mechanism) / STRONGLY INFERRED (the factory value).**
Only via its second component. **No instance number is hardcoded anywhere in cgiMain** — every object path is built with `%d` from the IA bytes (e.g. snprintf @0x403f68, format @0x40bf30). That the Ethernet profile's posted value is `"1,3,1"` is STRONGLY INFERRED: the GET/render side emits per-connection IA template variables, and the factory config (both PDM XMLs, re-checked this session) places `Eth_Internet` at `WANConnectionDevice.3.WANIPConnection.1`. The HTML that would prove what the browser posts is absent from the repo (zero `.html` files in the entire tree — re-verified).

**(4) Does it create a new WANPPPConnection? — CONFIRMED STATIC.**
Yes — as the second half of a type conversion, in the same transaction: SelId(0xe3, newIA) @0x403eac + `cmsgRequestSetIndexedObj(req, 1)` @0x403f10 queues the creation. On the server this resolves to instance creation via `cccRdmAddObjectWithAssignIA` (see Blocker 2, §2.4 — the DAS SelId/SetIndexedObj path uses the *instance* OID 0xe3 with create-enabled lookup). There is no other creation entry point in the CGI: no add-new-connection path exists.

**(5) Does it convert an existing WANIPConnection? — CONFIRMED STATIC.**
Yes; conversion is the *only* creation mechanism. IP→PPP branch @0x403b10 first reads the existing IP object (`cccRdmGetObjectByOID(rdm, 0xcd, wanIA, 1)` @0x403b20), saves its Name (obj+0x20c) and bridged state (`ConnectionType` at obj+0x92 vs `"IP_Bridged"` @0x403b48), and copies up to 12 PortTriggering entries (loop i=0..11, path format @0x40be20, `rdmGetObjectByName(...,1)` @0x403c24, 0x50-byte records) for re-creation under the new PPP object (OID 0xe9, SetIndexedObj(1) @0x406078). A PortTriggering `malloc` failure aborts the entire POST before anything is sent (syslog `"malloc fail in portTrigger_list_t"`, rdmDeInit, return 0 @0x403c98–0x403ca4).

**(6) Does it delete/disable the IP object? — CONFIRMED STATIC.**
**Deletes** (does not merely disable): SelId(0xcd, wanIA) @0x403dd0 + `cmsgRequestSetIndexedObj(req, 0)` @0x403e34, with syslog `"WanType is changed to PPP, delete %s(%llx)."` @0x403e28. Server-side this is a pre-delete mark (status 0) that is physically swept at commit (Blocker 4, §4.2). The mirror PPP→IP branch deletes the PPP object identically (SelId(0xe3) @0x404218, syslog `"WanType is changed to IP/Bridged, delete %s(%llx)."`, SetIndexedObj(0) @0x40427c).

**(7) Does it use cmsgRequestSetIndexedObj? — CONFIRMED STATIC.** Yes — 11 call sites in cgiMain (census above); the conversion uses 2 of them (delete @0x403e34, create @0x403f10), the mirror conversion 2 more (@0x40427c, @0x404360), the rest create DNS/IPv6DNS/PortTriggering children. None targets WANConnectionDevice.

**(8) Does it call rdmGetAvaliableIAByOID? — CONFIRMED STATIC.** Yes, twice in cgiMain: @0x403e8c (OID 0xe3, IP→PPP) and @0x4042dc (OID 0xcd, PPP→IP). librdm @0x11c20 re-disassembled this session: resolves the class node, requires its flags word [node+0x28] bit 1 or bit 2 set (else syslog `"OID must be indexnode or indexchild"` and return 0); walks the parent's existing children whose IA prefix matches the parent IA; candidate starts at 1 and is bumped past each existing child whose instance equals the candidate *and* whose status word has bit 3 set; empty child list → candidate 1 (@0x11e0c); finally checks candidate ≤ max-instances field [node+0x10] (else return 0) and returns parentIA with the candidate set at the child depth (`rdmSetIAValue` @0x11e20). Net semantics: **lowest free instance ≥ 1** (not max+1). **The CGI never checks the return value** — a 0 return would be stored as the IA and passed on to SelId.

**(9) Exact object path supplied — CONFIRMED STATIC.**
For creation/deletion the CGI supplies **no dotted string at all**: it selects numerically by (OID, IA) via `cmsgRequestSelId` — delete = (0xcd, {1,3,1}), create = (0xe3, {1,3,1}) for the factory case. The dotted path is built only as a *local string* for parameter values: `snprintf` @0x403f68 with format `"InternetGatewayDevice.WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d"` (@0x40bf30) from the new IA bytes → `connPath`, used as the value of the DefaultConnectionService SETs and passed to the bridge-filter helper sub_402ddc @0x40670c. (Mirror: `"...WANIPConnection.%d"` @0x40c030, snprintf @0x4043b8.)

**(10) Exact SEL/ADD/SET/SAVE/SEND sequence — CONFIRMED STATIC.**
One request object for the whole POST (`cmsgCreateRequest` @0x4036b0, module id of `ccc_das` resolved @0x4036a8). **Everything is queued locally; nothing reaches the server until the single SendRecv at the end.** Queue order for an IP→PPP conversion POST:
1. *(only if `RestartBtn=="RESTART"` and `wanMode` ∈ {GPON, ETHER})* SelId(0xc7, {1}) + Set `Enable`=(wanMode==GPON) @0x403794/0x4037b4; SelId(0xca, {1}) + Set `Enable`=(wanMode==ETHER) @0x403810/0x403830; SelId(0x4d, 0) + Set `WANMode`=wanMode @0x40384c/0x403868; Save @0x40387c. (Still not sent — falls through.)
2. SelId(0xcd, wanIA); SetIndexedObj(0) — delete IP (@0x403dd0, @0x403e34).
3. SelId(0xe3, newIA); SetIndexedObj(1) — create PPP (@0x403eac, @0x403f10).
4. Common tail (entered @0x404670 by both conversions and by pure edits): if `RN_Default_WAN_H=="1"` (read @0x404684, gate @0x404738): SelId(0x83, 0) @0x404760 + Set `DefaultConnectionService_GPON`=connPath (if the GPON save-flag is "1", @0x404798) and/or Set `DefaultConnectionService_ETHER`=connPath (if the ETH save-flag is "1", @0x4047f4); if the matching WANStatus name equals the current status string (`"XGPON"` @0x40c158 / `"Ethernet"` @0x40c180), also SelId(0x80, 0) @0x404840 + Set `DefaultConnectionService`=connPath @0x40485c. IPv6 twin (OIDs 0x87/0x84) gated on `RN_IPv6Default_WAN_H=="1"` (read @0x404a30).
5. If bridged-state changed: LAN DHCP server toggle block (@0x40486c+).
6. SelId(connOID, newIA) @0x404964 + table-driven generic SET loop @0x404970 (Enable←RN_Active_H, Name←RN_Name, VLANID, VlanMux8021p, Enable_VLANID, …); addressing/DNS child creation if missing (SelId + SetIndexedObj(1): DNS OID 0xeb @0x404fcc/0x405124 region, IPv6DNS 0xee @0x405de4); PPP block (Username←RN_UserName, Password←RN_Password unless sentinel, PPPoEServiceName←RN_ServiceName, PPPAuthenticationProtocol←RN_PPPAuth, ConnectionTrigger, IdleDisconnectTime, X_5067F0_MaxMTUSize, MaxMRUSize); PortTriggering re-adds (SelId(0xe9, childIA) + SetIndexedObj(1) @0x406078 + SETs per saved entry).
7. SelId(connOID, newIA) @0x4061f8 + NAT tail SETs (see Q13).
8. *(bridged only, @0x4065f0)* SelId + Set `X_5067F0_SERVICELIST`, `ConnectionType="IP_Bridged"`, `MaxMTUSize`←RN_MTU.
9. `cmsgRequestSave(req, mid)` @0x4066d4.
10. Bridge-filter helper `sub_402ddc(rdm, connPath, RN_ModeFlag=="1")` @0x40670c (local RDM work, not a CMSG action).
11. *(only if `RN_Release=="1"`)* reads reconnectwantype/reconnectwania; SelId(0xe3 if type "1" else 0xcd, reconnectIA) @0x406844/0x406864 + Set `X_5067F0_ReleaseStatus` @0x4068a8 — **queued after the Save action in the same request**.
12. `cmsgSendRecv(req, mid, 60000)` @0x4068b8 — the single transmission. Then cmsgFree(req), cmsgFree(reply), render, return 0.
Note: when no save-flag is "1", control jumps to 0x406710 — skipping steps 2–10 including Save — but steps 11–12 still execute (an empty or RESTART-only request is still sent).

**(11) Instance allocated — CONFIRMED STATIC (mechanism) / value for the factory case certain.**
Allocated client-side by `rdmGetAvaliableIAByOID` (Q8): lowest free instance under parent {WANDevice, WANConnectionDevice} from wanIA. Converting `"1,3,1"` with no existing PPP sibling ⇒ **instance 1**, i.e. `.3.WANPPPConnection.1`. If a PPP sibling already existed, the result would be the lowest free instance (2, 3, …), not necessarily 1. The backend re-derives/validates the instance at execution (Blocker 2, §2.4); the CGI's number is a request, not a guarantee.

**(12) Default route pointer change? — CONFIRMED STATIC.**
Conditional only (step 4 above): requires `RN_Default_WAN_H=="1"`. The CGI then sets the per-link-type marker parameters `DefaultConnectionService_GPON` / `DefaultConnectionService_ETHER` on the OID-0x83 child object, and updates the real `Layer3Forwarding.DefaultConnectionService` (OID 0x80) **only if** the corresponding WANStatus name matches the unit's current status string. A conversion POST that omits the default-WAN flag leaves the pointer untouched. IPv6 twin identical via `RN_IPv6Default_WAN_H`.

**(13) NAT enable/disable? — CONFIRMED STATIC.**
Purely RDM parameters in the NAT tail (SelId @0x4061f8 re-selects the connection): `ConnectionType="IP_Routed"` @0x406214 (string type word 0xC0000000); `NATEnabled` = `"0"` if form `RN_SelNAT=="Disabled"` else `"1"` (@0x40625c–0x406294 — set as a string-typed value); if `RN_SelNAT=="Enable"`, `X_5067F0_NATType` from `NATTypeSetIndex` ("0"→Symmetric @0x4064d0, "1"→PortReCone @0x40650c, "2"→AddrReCone @0x406548, "3"→FullCone @0x406584) and `X_5067F0_FullSetIndex` @0x4065e8; plus `X_5067F0_IGMPEnabled` (RN_Multicast), `X_5067F0_Multicast` (Proxy_version), `X_5067F0_MultiCastVLAN` (RN_MVLAN), `X_5067F0_PPPoE_PassThrough` (WAN_PPP_PASS). No iptables/system/popen exists in this binary (import census: no system/exec/popen at all).

**(14) WAN mode update? — CONFIRMED STATIC.**
Not by the conversion branch. Only the separate RESTART block (step 1 of Q10) touches WAN mode: `RestartBtn=="RESTART"` + `wanMode` ∈ {GPON, ETHER} → GponInterafceConfig.Enable, WANEthernetInterfaceConfig.Enable, WANSwitch.WANMode. A pure conversion POST leaves `WANMode` as-is — converting the Ethernet profile to PPP does **not** switch the unit into ETHER mode; that is a separate operator action.

**(15) Triggers PPP init? — CONFIRMED STATIC (CGI side) / STRONGLY INFERRED (backend timing).**
No. The CGI contains no pppd/exec/system reference and does not signal the backend synchronously; it only queues RDM operations. PPP bring-up is backend (ccc_be/libbemodules) work after the transaction commits — via the DAS apply phase's send-to-BE step and the L3 state machine — and only for an Enabled connection. The CGI cannot observe or report whether pppd ever started.

**(16) Service restart or reboot required? — CONFIRMED STATIC (CGI side); system-level question remains open (U2).**
The CGI requests neither: no reboot import is called anywhere in the binary (PLT census has no reboot/system/exec entry despite `libreboot.so` being a DT_NEEDED), and the conversion flow contains no restart action. (`RestartBtn` is only the WAN-mode form control of Q14.) Whether a WANMode change fully takes effect without a reboot is a backend/boot question — prior BOOT analysis rates "reboot required for eth_Init" STRONGLY INFERRED with the L4ObjectChanged alternative unaudited (OPEN_QUESTIONS U2); that analysis is outside this scope and was not re-derived here. For the *conversion itself* (mode unchanged), nothing in the CGI or the DAS path demands a reboot; the object change is applied by the commit machinery.

**(17) What happens if creation fails? — CONFIRMED STATIC.**
At the CGI layer: **nothing observable.** Every Sel/Set/SetIndexedObj/Save return value is ignored; `cmsgSendRecv`'s reply pointer is freed without inspection; `cmsgGetExecResult` is never called in cgiMain; cgiMain returns 0 and renders the normal page on every path. A backend NACK of the create (exactly the FE-2 failure mode) is therefore **invisible in the Web UI** — the operator cannot distinguish success from silent rollback except by re-reading the resulting configuration. The only checked failures in the whole handler are: session check, REQUEST_METHOD != POST (renders instead), rdmInit == NULL (return 0), and the PortTriggering malloc failure (aborts before sending — the one failure that *does* prevent a partial request).

**(18) Transaction rollback / partial-commit possibility — CONFIRMED STATIC (architecture) / STRONGLY INFERRED (all-or-nothing RDM state) / UNKNOWN (BE side effects).**
The whole POST is one CMSG request = one DAS transaction. Server-side, action execution only creates/marks **pre-objects** in the shared RDM image (status word: created = `cccRdmSetPreObjStatus(...,1)`, deleted = status 0); a separate apply phase (`cccDasHandleApply`, Blocker 2 §2.5) then validates each changed object through a per-class callback table and the send-to-BE step. On any apply failure it sets reply header bits 25+30 (validation-error-present + transaction-fail), logs `CCC_MSG_VALIDATE_FAIL`, runs the changelist cleanup path (@0x412f9c) and returns −1 — the pre-objects are never promoted, so **RDM state rolls back as a unit** (corroborated by the FE-2 runtime observation: ADD executed, count stayed 0). Two honest limits: (a) whether a *backend side effect* already performed for an earlier object in the same transaction (e.g. a service restart triggered via send-to-BE) is undone is **UNKNOWN** — the rollback evidence covers RDM state, not BE actions; (b) the SAVE action is queued *inside* the same request (and in the RN_Release case, actions are even queued after it) — the exact interleaving of `cccRdmSave` persistence vs the apply phase inside DAS was not fully traced, so persistence of a NACKed transaction's pre-state to flash is **UNKNOWN** (live-state rollback is the observed behaviour).

**(19) Dependence on an existing IP profile — CONFIRMED STATIC.**
Total. The conversion branch is reachable only for the connection `wanIA` identifies, reads that IP object first, deletes it, and derives the new object's parent IA and instance from it. If no WANIPConnection exists at the posted IA, `cccRdmGetObjectByOID` returns NULL and the branch degrades (name/bridged reads skipped) but still queues delete+create against the posted IA — there is no sanity check that the source object existed. There is **no** code path that creates a PPP connection under a WANConnectionDevice that has no profile being edited.

**(20) Can the normal Web UI safely create .3.WANPPPConnection.1? — mechanism CONFIRMED STATIC; "safely" qualified; HTML exposure UNKNOWN.**
Mechanism: yes — edit the existing Ethernet IP profile, submit `RN_EncapFlag="1"`, `RN_ModeFlag="0"`, the ETH save-flag `"1"` (and `RN_Default_WAN_H="1"` if the default route should move). The firmware-side handler will convert it to `.3.WANPPPConnection.1` in one transaction. Qualifications: (i) it is a **conversion, not an addition** — the Ethernet IP profile is deleted in the same transaction, so the operation is destructive if submitted unintentionally; (ii) failure is silent (Q17) — the UI will appear to accept the edit even if the backend NACKs it; (iii) whether the *shipped HTML* actually exposes the encap/mode controls on the Ethernet edit page is **UNKNOWN** — no HTML exists anywhere in the repo (verified: 0 `.html` files), and the two edit CGIs (`wanRemoteNode_ETH_Edit.cgi`, `wanRemoteNode_GPON_Edit.cgi`) are render-only stubs that merely pass `wanType`/`wanIA` through to the template. This is OPEN_QUESTIONS U12 and can only be settled by looking at the live page.

## 1.2 Reconstructed pseudocode (conversion-relevant core)

```
cgiMain(req):                                   # 0x403390
  if !session_ok or rdmInit()==NULL: return 0
  if REQUEST_METHOD != "POST": render(); return 0
  mid = cmsgGetModuleIdByName("ccc_das"); q = cmsgCreateRequest()
  if form(RestartBtn)=="RESTART" and form(wanMode) in {GPON,ETHER}:
      SelId(q,0xc7,{1}); Set(q,"Enable", wanMode==GPON)
      SelId(q,0xca,{1}); Set(q,"Enable", wanMode==ETHER)
      SelId(q,0x4d,0);   Set(q,"WANMode", wanMode)
      Save(q,mid)                               # queued only
  if none of the save-flag fields == "1": goto SEND   # 0x406710
  wanType=form(wanType); wanIA=form(wanIA)      # bufs 8 chars
  ia = rdmConstructIAValue(wanIA)               # 0x4039f0
  encap=form(RN_EncapFlag); mode=form(RN_ModeFlag)
  if strncmp(wanType,encap,7)==0 and !(wanType=="1" and mode=="1"):
      goto EDIT_ONLY                            # 0x4043c0
  if encap=="1" and mode=="0":  IP_TO_PPP:      # 0x403b10
      obj = GetObjectByOID(rdm,0xcd,ia,1); save name/bridged
      save PortTriggering[0..11] of obj         # malloc fail -> abort, send nothing
      SelId(q,0xcd,ia); SetIndexedObj(q,0)      # DELETE IP
      newIA = rdmGetAvaliableIAByOID(rdm,0xe3, ConstructIA("%d,%d",ia.b1,ia.b2))  # UNCHECKED
      SelId(q,0xe3,newIA); SetIndexedObj(q,1)   # CREATE PPP
      connPath = "IGD.WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d" % newIA
  else: PPP_TO_IP:                              # 0x403f70, exact mirror
      ... SelId(q,0xe3,ia); SetIndexedObj(q,0)  # DELETE PPP @0x40427c
      newIA = rdmGetAvaliableIAByOID(rdm,0xcd, parentIA)
      SelId(q,0xcd,newIA); SetIndexedObj(q,1)   # CREATE IP @0x404360
      connPath = "...WANIPConnection.%d"
  # common tail 0x404670: [DCS if RN_Default_WAN_H], [IPv6 DCS],
  #   generic SET loop, DNS-child creates, PPP/IP SET block,
  #   PortTrigger re-adds, NAT tail
  Save(q,mid)                                   # 0x4066d4
  sub_402ddc(rdm, connPath, mode=="1")          # bridge filter helper
  if form(RN_Release)=="1": SelId(q, 0xe3|0xcd, reconnectIA); Set(q,"X_5067F0_ReleaseStatus",...)
  reply = cmsgSendRecv(q, mid, 60000)           # 0x4068b8 — result NEVER inspected
  cmsgFree(q); cmsgFree(reply); render(); return 0
```

---

# BLOCKER 2 — the failed ccctest ADD of `.3.WANPPPConnection.1`

**Symptom (from prior runtime evidence, not re-derived):** `ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1` — the reply printed the ADD action as *success*, the transaction as *failed*, and the live PPP child count under ConnDev.3 stayed 0.

## 2.1 ccctest parser — CONFIRMED STATIC (ccctest.bin, hash-identical to rootfs ccctest)

- Main: `fopen` script file; `cmsgInit`; module id = `cmsgGetModuleIdByName("ccc_das")` @0x4022ec (stored [sp+0x6c] — **the peer is ccc_das, not ccc_be**). Delimiter string @0x404540 is `" ;\n"` (space, semicolon, newline).
- Loop @0x40238c: `__fgets_chk` one line → `strtok(line, " ;\n")` → first token dispatched by strcmp chain. `RDMNAME <name>;` (@0x40232c) builds `<name>.rdm`/`<name>.xml` and calls `rdmInit` (handle in x22; its first word is passed as the flag argument to Sel/Save). `REQUEST;` creates the request object (x23). **All commands accumulate actions into the single request object until `SEND`. Nothing is transmitted, and nothing is printed, per line.**
- `ADD <path>` handler @0x402ca8–0x402ce8 (strcmp `"ADD"` @0x404758): if no request object → fatal `"line %d: no available CMSG control block !!"` and exit. Else: `tok = strtok(NULL, delim)` @0x402cc8; `cmsgRequestSel(req, tok, flag)` @0x402cd8; `cmsgRequestSetIndexedObj(req, 1)` @0x402ce4; loop. **The path is passed verbatim — the parser does no dot-splitting, no instance parsing, no validation; both calls' return values are ignored.** There is no printf in the handler: "ADD success" cannot be a parse-time message.
- `DELETE <path>` handler @0x402da8–0x402de8: byte-for-byte the same shape with sub-action 0 (@0x402de4).
- `SAVE;` @0x403278: `cmsgRequestSave(req, flag)` @0x403298 (queues action 5).
- `SEND;` @0x4032fc: `cmsgSendRecv(req, dasModuleId, 0xea60=60000)` @0x403320; `cmsgFree(req)`; if the reply is non-NULL, the reply printer sub_4017dc is called @0x40333c; the request pointer is zeroed (a new `REQUEST;` is required for further commands).
- Vendor help text (rodata, verbatim): `ADD <indexed object name>` @0x403c58; `DELETE <an indexed object name with a specified indexed number>` @0x403c78; and the worked example @0x403f70–0x404058: `ADD InternetGatewayDevice.LANDevice.1.LANHostConfigManagement.IPInterface;` followed **directly** by `SET Enable boolean 1;` etc. — i.e. the canonical ADD form has **no trailing instance**, needs **no parent SEL**, and SETs after ADD apply to the created object with **no intervening SEL**.

## 2.2 libcmsg builders — CONFIRMED STATIC (libcmsg.so)

- `cmsgRequestSel` @0x556c: appends action word **1**, the flag word, a length byte (strlen+7), and a verbatim `memcpy` of the path @0x563c. Zero validation; returns 0, or −2 if CMSG is uninitialised.
- `cmsgRequestSelId` @0x5684 (used by the CGI): appends the by-OID/IA selection.
- `cmsgRequestSave` @0x5f60: appends action **5**. `cmsgRequestSetIndexedObj` @0x60a8: appends action **7** + sub-action word.
- ⇒ **"Parser success" is a meaningless concept here**: parsing only appends bytes to a local buffer. The first moment anything can succeed or fail is SEND.

## 2.3 The reply printer — why "ADD success" + "transaction fail" is one consistent observation — CONFIRMED STATIC

Reply printer sub_4017dc (ccctest @0x4017dc): `cmsgParseHeader` @0x4017fc, then two **independent** flag fields:
- Header word [hdr+0x20]: bit 30 (`tbnz #0x1e` @0x401808) → `puts("transaction fail !!")` @0x40183c; if bit 25 set (@0x40184c) → `printf("\nvalidation error code: 0x%08lx\n", [hdr+0x24])` @0x401850; bit 31 (@0x401810) → `puts("transaction successful !!")` @0x401868.
- Per action (`cmsgParseAction` loop @0x40194c): action type = word & 0x3fffffff; the action's own status = **bit 0x40000000 of its reply word** (x4). Type 7 dispatches on the sub-action word at [action+0x30]: ==1 → `printf("\nADD %s: %s\n", name, success|fail)` @0x402184 (fmt @0x404468); else → `"\nDELETE %s: %s\n"` @0x4018bc (fmt @0x404478). Type 5 prints `"\nSAVE: %s\n"` @0x4021d8; type 1 `"\nSEL %s: %s\n"`; type 4 `"\nSET %s: %s\n"` — all from the same per-action bit.

⇒ The ADD **executor** reported success for action 7, and a **later phase** set the header NACK. Both halves of the symptom are produced by different fields of the same reply; neither contradicts the other. (Corollary: the full ccctest output of the failed run would also have shown one SEL line per SEL action and a SAVE line — see §2.7 on missing evidence.)

## 2.4 Server execution path (ccc_das + librdm/libcccrdm) — CONFIRMED STATIC

ccc_das receives the message and executes actions **in request order**, maintaining per-transaction state `dasQ`: currentObjectOffset [+0xc0], currentOID [+0xc8], currentIA [+0xd0], rdmCB [+0xe0], plus a changelist of touched objects (appended via internal fn @0x411914 with flag words).

**SEL by name** — `cccDasHandleSel` (self-identified in syslogs @0x4160e0): finds the rdmCB matching the request; calls `rdmGetObjectByName(rdm, name, 1)` @0x4114b4.
- `rdmGetObjectByName` (librdm @0x130b4) = `cccRdmGetObjListByName` → take (OID, IA) from the list head → `cccRdmGetObjectByOID(rdm, OID, IA, flags)`.
- `cccRdmGetObjListByName` (librdm @0x12324; libcccrdm twin @0x33008) is the dotted-name walker: copies the name, `strtok` on `"."`; per token, `strtol` @0x12438 — a token whose value−1 ≤ 0xfe is an **instance component** (depth++, `rdmSetIAValue(IA, depth, value)` @0x12458, append `"i"` to the proto-name); other tokens are appended as proto text. At the end it looks up the template by proto-name (`rdmGetObjectByProtoName` @0x124a0) and returns an (OID, IA) pair — **it never creates anything**. For `...WANPPPConnection.1` it returns (OID **0xe3**, IA {1,3,1}); for `...WANPPPConnection` it returns (OID **0xf1**, IA {1,3}).
- If the object exists: dasQ := {offset=[rdmCB+0x50], OID, IA}; reply Sel **success** (w2=0) @0x4114f0.
- If not (GetObjectByOID with flags=1 returns NULL for a missing instance): dasQ.currentObjectOffset := 0, the (OID, IA) from the list are still recorded @0x411570–0x41157c, and the reply is Sel **fail** (w2=−1) @0x411588. *A SEL of a not-yet-existing instance therefore "fails" by design, while leaving exactly the state the following ADD needs.*

**SEL by ID** — `cccDasHandleSelId` @0x411610 (the CGI's path): copies OID/IA from the action into dasQ @0x411630/0x41163c; finds rdmCB; calls `cccRdmGetObjectByOID(rdm, OID, IA, 1)` @0x4116a0; sets dasQ.currentObjectOffset = found ? [rdmCB+0x50] : 0; and replies SelId **success (w2=0) unconditionally** @0x4116c0 — even when the instance does not exist yet. (Failure only if the rdmCB itself is missing @0x41167c.)

**SetIndexedObj** — `cccDasHandleSetIndexObject` @0x412810 (self-identified @0x4161c8): sub-action = first word of [action+0x30] @0x412850.
- **sub == 1 (ADD):**
  - dasQ.offset ≠ 0 (SEL resolved an existing object): `cccRdmGetObjectByOID(rdm, OID, IA, flags=1)` @0x41293c must return it and its CB offset must match, else reply fail (`"GET Object Failed !!"` / `"GET Object maybe wrong !!"` → w2=−1 @0x412cc0). On success: changelist-append with flag 0xC1000000 @0x4129a0, reply **success** @0x4129b0. (This is the "ADD of an already-existing instance" case — no creation occurs.)
  - dasQ.offset == 0 (SEL named a class or a missing instance): `cccRdmGetObjectByOID(rdm, OID, IA, flags=2)` @0x4129dc — **create-enabled**. NULL → `"Add Object Failed !!"` → reply fail @0x412cb4. Success → dasQ updated to the new object @0x412a10–0x412a20, changelist-append flag 0x40000000 @0x412a38, reply **success** @0x412a48.
- **sub == 0 (DELETE):** see Blocker 4, §4.2.
- Any other sub-action, or rdmCB missing (`"RDMCB not found !!"`): reply fail.
- The handler ends by calling `cccRdmSetIndexObject(rdm, dasQ.offset, sub)` @0x412bc8 (on the sub==0 flow; the sub==1 flows reply directly). libcccrdm `cccRdmSetIndexObject` @0x2ff3c is only a **status setter**: sub==1 → parent flags [parent+0x28] |= 8 @0x2ffe8, `cccRdmSetNodeStatus(parent,1)` @0x2fffc, `cccRdmSetPreObjStatus(obj,1)` @0x3000c; sub==0 → `cccRdmSetPreObjStatus(obj,0)` @0x30020; it returns 0 on every path.

**Creation primitives** (librdm; libcccrdm twins at +0x20ce4-ish offsets, same sizes):
- `cccRdmGetObjectByOID` @0x12ce0: template flags [node+0x28] bit 1 **set** (index-child *class*, e.g. OID 0xf1) → if caller flags &2, `cccRdmAddIndexChildObject` @0x12d44 (**the requested instance byte is never consulted on this branch**); if flags &2 clear → NULL @0x12df4. Bit 1 **clear** (instance object, e.g. OID 0xe3) → walk the parent's child list comparing IA (@0x12ea8–0x12ed0): match with status bit 3 set → return existing; list exhausted or match in a non-active slot → if caller flags &2, `cccRdmAddObjectWithAssignIA` @0x12ee4 / @0x12f88; else NULL.
- `cccRdmAddIndexChildObject` @0x134a0 (class path): failure exits are only unknown OID (@0x134c4→0x13564), `rdmVerifyIAValue` == −1 (@0x134e4→0x135c4), max-instances (@0x13658: `[parent+0x10] < candidate` → `"out of MAXNODENUMBER"` @0x13784), and template-alloc NULL. Empty child list → `rdmSetIAValue(IA, depth, 1)` @0x137ec–0x137f8 (instance **1** hardcoded) → `cccRdmSetObjDefault(...,2)` → tail: `rdmSetPreObjIA`, `cccRdmSetPreObjStatus(...,1)` @0x136a8, `cccRdmCheckIndexChildParents` @0x136e0, `cccRdmSetCBData`. Non-empty list uses the same lowest-free scan as `rdmGetAvaliableIAByOID`. **No parent-instance whitelist, no link-type check, no sibling-type check exists in the function** (complete PLT-call inventory taken).
- `cccRdmAddObjectWithAssignIA` @0x12ab0 (instance path): GetOffsetByOID; `rdmVerifyIAValue` @0x12aec (−1 → NULL); if the child list is **empty** → `cccRdmSetObjDefault` @0x12cbc → `rdmSetPreObjNext` → `rdmSetPreObjIA(new, requestedIA)` @0x12bf8 (the **exact requested IA, instance byte included** — no auto-allocation, no max scan on this path) → `cccRdmSetPreObjStatus(...,1)` @0x12c08 → `cccRdmCheckIndexChildParents` @0x12c3c → return node. If children exist, it walks them: an *active* child with equal IA (compareIAOrder @0x12bc0) → `puts("this index object is existed.")` @0x12bd0 → NULL; an inactive slot is reused.
- `rdmVerifyIAValue` @0x11e48 (spot-verified via both callers): checks depth equality, non-zero IA bytes, per-level maxima. Parent IA {1,3} and full IA {1,3,1} both pass for this schema (WANDevice max 4, WANConnectionDevice max 8, connection max 8 per OIDTable image fields).

**⇒ Both ADD spellings execute creation successfully, by different primitives:**
| | SEL resolves to | SetIndexedObj(1) calls | Primitive | Instance |
|---|---|---|---|---|
| `ADD …WANPPPConnection` (vendor form) | (0xf1 class, {1,3}), offset 0 | GetObjectByOID(0xf1, {1,3}, 2) | `cccRdmAddIndexChildObject` | auto = 1 (empty list) |
| `ADD …WANPPPConnection.1` (failed form) | (0xe3 instance, {1,3,1}), offset 0 | GetObjectByOID(0xe3, {1,3,1}, 2) | `cccRdmAddObjectWithAssignIA` | exactly 1 (requested) |

In both cases the result is a **pre-object**: present in the RDM working image with status "created, uncommitted", visible to later actions in the same transaction (subsequent SETs target it via dasQ), but not yet committed.

## 2.5 The commit/apply phase — where the NACK is produced — CONFIRMED STATIC (mechanism) / UNKNOWN (specific rejector)

After the action loop, `ccc_das` runs `cccDasHandleApply` (self-identified in its syslog @0x4131a4; body spans ~0x4131c0–0x4134b8+):
- It walks the transaction **changelist** (nodes linked via [+8]; each has object offset [+0x38], size [+0x44], flag word [+0x48] whose top bits encode the change class: 0x40000000 / 0x80000000 / 0xC0000000 cases at @0x413230/0x413244).
- Per node it calls a dispatcher @0x412ec0: the node's object-class field [obj+0x28] indexes a **function-pointer table at ccc_das 0x4162a8**; the registered per-class callback is invoked (`blr x4` @0x412f20) with arguments selected by the change class; a NULL callback returns 0. The callback's result flags are ORed back into the node flag @0x4132ac.
- Nodes whose post-callback flag has bit 0x1a set go to the **send-to-BE** step @0x4131c0 → internal fn @0x412d4c (the `cccDasLianDong` linkage handler, self-identified @0x4161e8; logs `"CCC_DAS_SEND_TO_BE"` @0x4156d8 and `"%s(): DAS object-Change conflict"` on mismatch).
- On a validation-class failure the exit @0x413120–0x413164 executes: reply header word |= **0x2000000 (bit 25)** @0x413128, error-code field zeroed @0x413134, header word |= **0x40000000 (bit 30)** @0x413140; syslog `"%s(): CCC_MSG_VALIDATE_FAIL"` (fn name `cccDasHandleApply`) @0x4131ac–0x4131b8; changelist cleanup fn @0x412f9c is called; the handler returns **−1**.

Supporting commit machinery in libcccrdm: `cccRdmSetNodeStatus` @0x300c0 (called by `cccRdmSetIndexObject`) invokes `cccRdmCheckObjectChg` @0x2fd30 at @0x30144 — a change detector (calloc + three `memcmp` of object copies), not itself a validator; `cccRdmSave` @0x2f668 is the persistence path (SysV semaphore + `system()` save scripts @0x2f780/0x2f99c + `access()` checks); `rdmInitVerifyConfig` @0x2f500 serves the separate VERIFYCONF action (`cccDasHandleVerifyConfig`, rdmInitVerifyConfig call @0x41405c in ccc_das) and boot-time config verification — it is **not** in the normal SEND path.

**What this proves:** a post-execution, pre-commit validation/apply gate exists in ccc_das, it can NACK a transaction whose every action executed successfully, it sets exactly the header bits the ccctest printer reports (25 + 30), and its failure path discards the transaction's working state (pre-objects never promoted — hence the unchanged child count). **What it does not prove:** which changelist node's callback (or the send-to-BE step) rejected this transaction, or why.

## 2.6 Token-by-token comparison: failed ccctest ADD vs the CGI sequence

| Aspect | Failed ccctest form | CGI conversion (Blocker 1) |
|---|---|---|
| Transport | `cmsgRequestSel` (by name) + `cmsgRequestSetIndexedObj(1)` queued per ADD line; executed by ccc_das at SEND | `cmsgRequestSelId` (by OID+IA) + `cmsgRequestSetIndexedObj(1)`; same server, same handlers modulo Sel/SelId entry |
| Target resolution | Name walker → (0xe3, {1,3,1}) | Numeric (0xe3, {1,3,1}) — identical dasQ state |
| Creation primitive | `cccRdmAddObjectWithAssignIA` (exact IA) | Identical (DAS SelId path also lands on OID 0xe3 + flags=2) |
| Sibling IP object | **Left in place** — after the ADD, ConnDev.3 would hold both WANIPConnection.1 and the new WANPPPConnection.1 | **Deleted first, in the same transaction** (SelId(0xcd)+SetIndexedObj(0) precedes the create in the changelist) |
| Instance source | Literal `1` from the script | `rdmGetAvaliableIAByOID` → also 1 here |
| Parameters | Whatever SETs the (missing) script bundled — vendor pattern sets them on dasQ's current object with no extra SEL | Full parameter tail (PPP block, NAT, DCS) in the same transaction |
| SAVE/SEND | Per the symptom, SAVE+SEND were issued (transaction reached the server and was NACKed there) | Save queued @0x4066d4, single SendRecv @0x4068b8 |
| Result reporting | Per-action + header bits printed by ccctest | Nothing — CGI discards the reply (Q17) |

The **only structural difference** between the failed transaction and the vendor's own conversion transaction, at the RDM level, is the continued existence of the sibling WANIPConnection.1 under the same WANConnectionDevice during apply — plus whatever additional SET/SEL/DCS actions the unknown failed script bundled.

## 2.7 Verdict

**Exact cause: NOT PROVEN.** Ranked findings:

1. **CONFIRMED STATIC — the failure was a commit/apply-phase NACK after successful ADD execution.** Every static gate inside both creation primitives passes for {1,3,1} under ConnDev.3 (schema maxima, VerifyIAValue, empty child list). Had creation itself failed, `cccDasHandleSetIndexObject` would have replied fail for action 7 and ccctest would have printed `ADD …: fail` — the opposite of the observed output. The NACK machinery is located precisely: `cccDasHandleApply` in ccc_das (header bits 25+30, `CCC_MSG_VALIDATE_FAIL`, changelist cleanup, return −1).
2. **DISPROVEN — trailing `.1` as the cause.** It is parsed by the name walker (@0x12438), routes to the instance-OID primitive, and the requested instance (1) equals both the auto-allocation result and the only possible value for an empty list. It remains a deviation from the vendor-canonical spelling, nothing more.
3. **DISPROVEN — schema/parent/max/exists blockers:** PPP under ConnDev.3 is schema-legal (OIDTable); parent IA {1,3} passes VerifyIAValue; max is 8 with an empty list; AssignIA's `"this index object is existed."` exit requires an *active* equal-IA child, and the count was 0.
4. **DISPROVEN — missing SAVE as the cause of count 0.** SAVE is persistence only (`cccRdmSave`); a committed-but-unsaved object would still appear in live counts until reboot.
5. **DISPROVEN (prior-audit claim) — "the parser aborts if a SEL follows ADD".** The parser has no such rule (handlers are two-line appenders). The server-side version of the claim (a by-name SEL of the uncommitted instance *fails*) is true but benign by design: the SEL reply is fail while dasQ is still populated (§2.4) — and a failed SEL action does **not** itself NACK the transaction (the CGI's own create relies on a not-yet-existing instance being selected). Whether a *failing sibling action* causes `cccDasHandleApply` to reject the whole changelist is precisely the unproven link.
6. **HYPOTHESIS (leading) — a sibling changelist entry failed apply.** Candidates, in order: (a) the new PPP pre-object's own per-class apply callback or its send-to-BE step rejected a PPP object coexisting with the sibling IP object under ConnDev.3 (the one state the vendor conversion never presents, because it deletes the IP object first); (b) a bundled SET with a wrong type word (the schema types are strict — e.g. MTU/MRU are numeric-typed in the schema while scripts often send them as other types); (c) a bundled DefaultConnectionService SET pointing at the not-yet-committed object; (d) a bundled SEL of `...WANPPPConnection.1` whose failure the apply phase treats as fatal. All four are consistent with the evidence; none is provable from the repo.
7. **UNVERIFIED prior claim flagged:** the older audits (`deployment-script-audit.md`, `final-deployment-safety-audit.md`) assert the failure carried `validation error code: 0x00000002` and attribute it to a post-ADD SEL. **No artifact in the repo contains that code or any captured ccctest output/syslog from the failed run** — the value appears only as an assertion in those two documents. It is treated here as HYPOTHESIS, not evidence. (In the `cccDasHandleApply` failure exit the DAS-side error-code field is in fact zeroed @0x413134; whether ccctest's parsed [hdr+0x24] would show 0, 2, or another value depends on reply construction I did not fully trace.)

**Corrections to the prior RDM report** (its conclusions survive; two mechanism details do not):
- The "server by-name resolver at libcccrdm @0x90f0–0x9800 with GetObjectByOID(flags=2) @0x95dc" is the **PDM XML loader's** walker (`cccPdmXmlTagStart`/`cccPdmXmlContent`; its error path calls `XML_GetCurrentLineNumber`). The CMSG by-name path is `cccRdmGetObjListByName` (librdm @0x12324 / libcccrdm @0x33008), which never creates. The flags=2 creation happens one step later, inside `cccDasHandleSetIndexObject`.
- "`cccRdmAddObjectWithAssignIA` is never invoked for WANPPPConnection" holds only for the class-OID (0xf1) spelling. For the actually-failed `.1` spelling, AssignIA **is** the creation primitive (via instance OID 0xe3). This strengthens, not weakens, the prior verdict: both primitives pass every static gate.
- The prior report's dispatch correction stands and is extended: action 7 is executed by **ccc_das** (`cccDasHandleSetIndexObject`), not ccc_be; ccc_be's @0x415860 wrapper remains an unrelated provisioning path (its `cccRdmDelObjectByOID` call @0x415928 is likewise internal).

**Missing evidence (exactly what would settle it):**
1. The original failed ccctest script (every line — the repo does not contain it; only later, corrected-form scripts exist in REVERSE_ENG.md and the rea-investigation audits).
2. The complete ccctest stdout of the failed run — in particular whether a `validation error code:` line was printed and its value, and the per-action lines for every bundled SEL/SET/SAVE.
3. Device syslog from the failed SEND: `cccDasHandleApply` / `CCC_MSG_VALIDATE_FAIL`, the per-object `[DAS] changelist->flag` lines, `cccDasLianDong` / `DAS object-Change conflict`, and any `cccRdm*`/`rdmVerifyIAValue` messages (the DAS logs at levels gated by the ccc log flags seen throughout the handlers).
With (1)+(3), the rejecting changelist node is directly identifiable. Without them, no static pass can distinguish hypotheses 6(a)–6(d).

**Corrected ADD:** none is recommended as a *fix*, because the cause is not proven. The minimal form in IMPLEMENTATION_PLAN Path B (`REQUEST; ADD …WANPPPConnection; SAVE; SEND;` alone) is a **diagnostic** that discriminates the hypotheses (it removes all sibling-action candidates except 6(a)); it is not a proven remedy, and if hypothesis 6(a) is the true cause it will NACK identically.

---

# BLOCKER 4 — DELETE audit: `DELETE InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;`

## 4.1 Parser behaviour — CONFIRMED STATIC

- ccctest `DELETE` handler @0x402da8: `tok = strtok(NULL, " ;\n")`; `cmsgRequestSel(req, tok, flag)` @0x402dd8; `cmsgRequestSetIndexedObj(req, 0)` @0x402de4; loop. Identical in shape to ADD; the path is passed verbatim; returns ignored; nothing printed until SEND.
- **Parent selection needed? No.** The DELETE line's own SEL carries the full dotted path (parents included). No preceding `SEL <parent>` is required by the parser, by `cccDasHandleSel`, or by `cccDasHandleSetIndexObject` — dasQ state comes entirely from this line's SEL. (A preceding SEL in the same request would in fact be *overwritten* by the DELETE's SEL.)
- **Instance parsing:** the trailing `.1` is not parsed by ccctest at all; server-side, `cccRdmGetObjListByName` strtol-parses each numeric token (@0x12438) → (OID 0xe3, IA {1,3,1}). The vendor help documents DELETE as the command that takes the instance number: `DELETE <an indexed object name with a specified indexed number>` @0x403c78 — the `.1` form is the *canonical* DELETE spelling (opposite of ADD).
- **Transactional? Yes.** DELETE is two queued actions in the same request object as everything else; it executes only at SEND, and its effect is a pre-delete mark that the same apply phase (Blocker 2, §2.5) can NACK — with the same all-or-nothing RDM rollback. A DELETE therefore cannot half-apply at the RDM level.
- **SAVE/SEND required?** SEND: yes — without it nothing executes. SAVE: required for **persistence** — without a SAVE action in the transaction, the deletion lives only in the shared RDM image and the on-flash config still contains the object, so it returns on reboot (same persistence model as ADD, §2.7 item 4). The ROLLBACK_PLAN step-1 form (DELETE as its own transaction with SAVE; SEND) matches this requirement. **Note on preserved scripts:** neither `DUMPFILES/rollback.ccc` nor `DUMPFILES/ether-rollback.ccc` uses DELETE at all (both are Enable/WANMode/DCS scripts), and `ether-rollback.ccc` contains **no SAVE** before its SEND — as preserved it would not persist its changes across a reboot. `rollback.ccc` does include SAVE. Both were re-read in full this session.

## 4.2 Backend execution and commit — CONFIRMED STATIC

`cccDasHandleSetIndexObject`, sub-action 0 (@0x412860–0x412bd8):
1. Preconditions: dasQ.currentObjectOffset ≠ 0 (@0x412864 — else reply fail @0x412cb4) **and** dasQ.currentIA ≠ 0 (@0x412870 — else syslog `"not support non-index node !!"` and reply fail). Since the preceding SEL sets offset=0 for a nonexistent instance, **DELETE of a nonexistent object fails cleanly at execution** (per-action `DELETE …: fail`), it cannot create or corrupt anything.
2. Child sweep: `cccRdmGetFullChildList` on the target (@0x412884), then for each child object: `cccRdmGetObjectByOID(..., flags=1)` and changelist/notify append with flag 0x80000000 (@0x412b40 loop) — children (DNS, PortTriggering, …) are marked for deletion together with the parent.
3. The target itself: `cccRdmGetObjectByOID(rdm, OID, IA, flags=1)` @0x412b70; notify append flag 0x80000000 @0x412bb4.
4. `cccRdmSetIndexObject(rdm, offset, 0)` @0x412bc8 → libcccrdm @0x2ff3c sub==0 arm: `cccRdmSetPreObjStatus(obj, 0)` @0x30020 — **mark only**. No unlink, no count change, no callback fires at execution time.
5. Reply success (w2=0) @0x412bd8.

Physical removal is a separate mark-and-sweep layer in libcccrdm: `cccRdmDelObject` @0x32e68 performs the actual purge (unlink via `rdmSetPreObjNext`, reset via `cccRdmSetObjDefault`, `cccRdmSetPreObjNonConfig`); `cccRdmCheckDelObject` @0x33df4 is a recursive sweeper over status-0 objects (self-calls @0x33f18/0x33f80/0x34000/0x3402c). Even the convenience APIs only mark: `cccRdmDelObjectByOID` @0x34574 = GetObjectByOID + SetPreObjStatus(0); `cccRdmDelObjectByName` @0x34530 likewise. **Not isolated:** the exact call site that runs the sweep for a DAS transaction (no direct caller of `cccRdmDelObject`/`cccRdmCheckDelObject` exists in libcccrdm's .text besides the recursion, and ccc_das imports neither) — it is driven at SAVE/verify time or via a function table; this is a genuine gap, labelled UNKNOWN (timing only — the mechanism is proven).

**Child-count decrement:** `WANPPPConnectionNumberOfEntries` under ConnDev.3 returns to 0 once the sweep unlinks the status-0 child — STRONGLY INFERRED (the count parameters in this RDM are maintained from the parent child list; the ADD side's parent bookkeeping in `cccRdmSetIndexObject`/`cccRdmSetNodeStatus`+`cccRdmCheckObjectChg` is the mirror image). The ROLLBACK_PLAN's verification step (read the count back = 0) remains the right runtime check; if the sweep has not yet run when the count is read, it may transiently still read 1 — another reason the plan's reboot step matters.

## 4.3 Side effects on a live PPP session — what tears down what

The object deletion itself only changes RDM state. Session teardown is driven by the backend object-change → Layer-3 state machine:

- **pppd termination — function CONFIRMED STATIC; trigger link STRONGLY INFERRED.** `beWanDisableClient` (libbemodules @0x6722c, size 0x364): reads the pid from `/var/wan-pid/<name>.pid` (`"cat %s/%s.pid"` popen @0x6730c–0x67340); if the connection type string contains `"ppp"` (strstr @0x67474), builds and executes via `cccBeDoSystem` @0x67464 the verbatim command `"kill -15 %d > /dev/null 2>&1 && sleep 2 && kill -9 %d > /dev/null 2>&1 &"` (@0xbdab0) — **SIGTERM, 2 s grace, SIGKILL**; then polls `/proc/<pid>/status` with a `"wait...pppd stop"` loop and removes the pid file (`removecmd("%s/%s.pid")` @0x674ec). Its only call sites are inside `beWanDoLayer3InterfaceAction` (libbemodules @0x6bf78) at @0x6c230 and @0x6cd6c; the @0x6c230 site is the link-down sequence: status `"Disconnecting"` → `libcccBeWan_stopWAN_wrapper` @0x6c220 → `beWanDisableClient` @0x6c230 → `beIfDown` @0x6c238 → `beWanConnectionNotify` @0x6c24c → … → `deleteLayre3Interface` @0x6c2a0. That a committed object deletion drives the connection through this down-path is STRONGLY INFERRED (it is the only consumer of beWanDisableClient, and object-change → L3-action is the architecture everywhere else in these libraries); the deletion→down hop itself was not traced instruction-by-instruction.
- **nas0_notag removal — CONFIRMED STATIC (function).** `deleteLayre3Interface` (libcccbe @0x35f60; vendor spelling "Layre"): resolves the L2 interface name generically (`libcccBeWan_getL2IntfName_wrapper`) and executes `"/bin/smuxctl --if-delete %s"` (fmt @0x4b728; snprintf @0x36058; `cccBeDoSystem` @0x36088). For the Ethernet PPP profile the L2 name is `nas0_notag` (established in the lifecycle analysis; the construction is interface-name-driven, not hardcoded). Called from the same down-path @0x6c2a0.
- **PPP options file — NOT deleted (CONFIRMED STATIC negative).** An exhaustive string-xref scan of libbemodules shows `/etc/ppp/options_%s` referenced only by enable/config paths (`beConfigWANByPPPoE` @0x66530, `CreatePPPByFullNAT`, `beFullNatEnablePPPv4Client`). Neither `beWanDisableClient` nor `deleteLayre3Interface` touches it. `/etc/ppp/options_nas0_notag` therefore **survives deletion as a stale file**; it is inert (only read by a pppd launched for that linkname) and is overwritten by `createWANPPPConnectionCfgFile` (libbemodules @0x6a7c0) on any future enable. Residual risk: negligible, but it means "file exists" is not evidence a profile exists.
- **Routes/NAT — CONFIRMED STATIC (mechanism).** Teardown is event-driven and interface-generic: pppd's own exit runs `/etc/ppp/ip-down` (rootfs, read verbatim this session), which writes a ccctest script containing `EVENTNOTIFY 207 string $REALNAME;` and executes it — the mirror of ip-up's Event 206 — driving the BE route/NAT handlers for that interface name. If pppd has to be SIGKILLed (after the 2 s grace), ip-down may not run, but the L3-down path independently does `beIfDown` + `smuxctl --if-delete`, and kernel routes bound to a destroyed ppp interface are dropped with it. Completeness of firewall-rule cleanup in the SIGKILL corner is STRONGLY INFERRED, not traced rule-by-rule.
- **DefaultConnectionService — NO auto-repair (CONFIRMED STATIC negative).** Nothing in the delete path, the DAS handlers, or the BE libraries rewrites `Layer3Forwarding.DefaultConnectionService` when its target disappears; libcccbe only *reads* it to determine WAN type (syslogs `"find WANPPPConnection in DefaultConnectionService"`, `"can't find wan type in layer3ForwardingPtr->DefaultConnectionService"`). **Stale-state risk #1:** if DCS still points at the deleted `.3.WANPPPConnection.1`, default-route resolution fails until DCS is repointed — rollback must repoint DCS explicitly (ROLLBACK_PLAN step 2 does). The IPv6 twin (`X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService`) is identical, and the LAN IPv6 `IPv6PDWanConnection.Interface` parameter can dangle the same way if it was ever pointed at the Ethernet object.
- **Other stale-state risks:** the surviving options file (above); `WANPPPConnectionNumberOfEntries` transiently reading 1 until the sweep runs (§4.2); linkdetection — if `WanAutoDetect` is still 1, the mode auto-detection remains active after rollback (ROLLBACK_PLAN step 4 restores it deliberately for GPON return; while experimenting it can also *re-enter* the ETHER branch and re-clobber ACS — see §4.5).

## 4.4 Can DELETE touch the GPON objects under ConnDev.1? — CONFIRMED STATIC: no (as addressed)

The entire delete flow is addressed by the exact (OID, IA) pair the SEL resolved — (0xe3, {1,3,1}) for the audited command. Child enumeration is strictly **downward** (full child list of the target). There is no wildcard, no parent cascade, no sibling iteration anywhere in `cccDasHandleSetIndexObject`, `cccRdmSetIndexObject`, or the sweep functions. A DELETE of the ConnDev.3 PPP object cannot reach `WANConnectionDevice.1.WANConnectionDevice.1.WANPPPConnection.1`. The only way to delete the GPON profile is to address it — i.e. operator error in the script path. (This is also why the preserved rollback scripts' approach — never DELETE anything, only Enable-flips — is conservative by construction.)

## 4.5 Rollback mechanisms compared — verdict

| Mechanism | What it does to the .3 PPP object | Evidence | Assessment |
|---|---|---|---|
| **A. Web UI conversion back (PPP→IP)** — broadband.cgi @0x403f70 | Deletes the PPP object **and** recreates a WANIPConnection under .3 in one vendor transaction (mirror branch verified instruction-by-instruction this session: SelId(0xe3)+SetIndexedObj(0) @0x404218/0x40427c → GetAvaliable(0xcd) @0x4042dc → SelId(0xcd)+SetIndexedObj(1) @0x4042fc/0x404360) | CONFIRMED STATIC | **Safest when the PPP object was itself created by conversion (Path A):** it is the designed inverse; the recreated IP profile lands on instance 1 (list empty after the delete) restoring `Eth_Internet` exactly. Caveats: needs the live edit page to expose the encap control (U12, UNKNOWN); silent on failure (Q17). **If the PPP object coexists with a surviving IP .1 (Path B world), conversion-back creates a duplicate `WANIPConnection.2`** (lowest-free allocation, Q8/Q11) — workable but untidy. |
| **B. ccctest DELETE (audited command)** | Marks the PPP object (and its children) pre-delete; sweep removes it; count → 0; IP .1 (if present) untouched | Execution path CONFIRMED STATIC; sweep timing UNKNOWN | **Cleanest inverse for the Path B world** (PPP added alongside IP .1): it removes exactly the added object and nothing else. It rides the same apply/commit machinery whose NACK caused FE-2 — but note the asymmetry: if this transaction NACKs, the state is unchanged (fail-safe direction), and DELETE of a long-committed object is the routine operation the vendor conversion itself performs as its first half. Must be its own REQUEST with SAVE; SEND, followed by separate transactions repointing DCS and WANMode (no auto-repair, §4.3). |
| **C. Enable=0 only** (what both preserved rollback scripts do) | Nothing — object, count, and link-type preference all remain | CONFIRMED STATIC (scripts re-read) | **Not a rollback of the object.** Acceptable as a *mode* rollback (GPON service restored via WANMode/DCS/Enable flips) but leaves `.3.WANPPPConnection.1` in the config; link-type resolution for ConnDev.3 may keep preferring PPP. ROLLBACK_PLAN already states this correctly. |
| **D. linkdetection** | **Never touches the .3 PPP object** — its string table (re-dumped this session) contains ConnDev.1 PPP, ConnDev.2 IP, ConnDev.3 **IP** paths, WANMode, both interface configs, DCS, and both ACS URLs, but no `WANConnectionDevice.3.WANPPPConnection` reference at all | CONFIRMED STATIC | Not an object rollback. Its GPON branch is a useful *mode* restorer (WANMode=GPON, enables, DCS→ConnDev.1 PPP, ACS→production `http://tms.airtelbroadband.in:8103`), and its ETHER branch creates only the .3 **IP** profile while clobbering ACS to `http://testacs.airtelbroadband.in:8103/`. Do not rely on it to remove the PPP object; do account for it re-running while WanAutoDetect=1. |
| **E. Config backup restore** (`ether-backup.lz` via UI backup/restore) | Wholesale replacement with the pre-change config (.3 = IP-only, per both PDM XMLs re-checked this session) | CONFIRMED STATIC (artifacts exist; XML contents verified) | Strongest deterministic fallback if A/B fail or state is uncertain — restores *everything* (ACS, DCS, WANMode) in one step, at the cost of discarding any unrelated config changes made since the backup. Follow with reboot + GPON verification. |
| **F. Factory reset** | Restores ROM defaults (.3 IP-only in the romfile image) | CONFIRMED STATIC for the .3 shape; credential loss STRONGLY INFERRED | **Last resort only.** The GPON PPP profile's provisioned credentials live in the operator config, not the ROM default image; a reset forfeits them and requires re-provisioning. Not part of any recommended path — ROLLBACK_PLAN's exclusion is correct. |

**Blocker 4 verdict:** The audited DELETE is **proven at the execution level** (parser → DAS handler → mark) and **proven in mechanism at the commit level** (same apply machinery as ADD; physical sweep functions identified), with one timing gap (the sweep's exact trigger). It is the correct rollback primitive **for the Path B world**, paired with explicit DCS + WANMode restoration in separate transactions and a SAVE in its own transaction. For the **Path A world** (PPP created by Web UI conversion), the vendor conversion-back (A) is safer because it atomically restores `Eth_Internet`. Mechanism E is the fallback if either NACKs repeatedly. DELETE cannot touch the GPON profile as addressed (§4.4).

---

# Consolidated list of what remains unprovable statically

1. **Blocker 2 exact rejector** — which changelist node/callback (or send-to-BE step) NACKed FE-2, and why. Needs the original script + full ccctest output (validation code line) + device syslog (`cccDasHandleApply`, `CCC_MSG_VALIDATE_FAIL`, changelist flag lines). (§2.7)
2. Whether a failing *sibling action* (vs a failing apply callback) is what turns an executed transaction into a header NACK — the apply loop's numeric return-class semantics (the ≤5 classes at ccc_das @0x413100) and the per-class callback table at 0x4162a8 were located but not fully decoded for OID 0xe3/0xf1.
3. **Blocker 1/2 persistence corner:** exact interleaving of `cccRdmSave` vs `cccDasHandleApply` inside a DAS transaction — whether a NACKed transaction can leave pre-objects in the on-flash config (live-state rollback is observed; flash-state is not).
4. **Blocker 4 sweep timing:** the call site that runs `cccRdmDelObject`/`cccRdmCheckDelObject` for a DAS transaction (functions proven; trigger not found in libcccrdm/ccc_das .text).
5. **Blocker 4 BE hop:** object-deletion → `beWanDoLayer3InterfaceAction` down-path is STRONGLY INFERRED, not traced end-to-end; SIGKILL-corner firewall cleanup likewise.
6. **Blocker 1 Q20:** whether the shipped Ethernet edit HTML exposes the PPPoE encap option (no HTML in repo; U12) — a live-page observation, not a static question.
7. **Blocker 1 Q16 (system level):** whether a WANMode switch completes without reboot (U2) — outside this scope; prior rating STRONGLY INFERRED stands unrevised.
8. The `validation error code: 0x00000002` asserted by two older audits is **uncorroborated by any artifact** and should not be quoted as evidence.
