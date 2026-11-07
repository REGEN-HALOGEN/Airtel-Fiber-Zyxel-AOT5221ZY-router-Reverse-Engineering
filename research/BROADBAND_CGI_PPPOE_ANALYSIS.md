# broadband.cgi PPPoE Analysis (highest priority)

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Full reconstruction of the broadband.cgi POST handler and its Ethernet PPPoE branch; wanIA semantics; PPP creation sequence; pseudocode with addresses.
- **Files examined:** DUMPFILES/broadband.cgi, wanRemoteNode_ETH_Edit.cgi, wanRemoteNode_GPON_Edit.cgi, librdm.so (OIDTable), libcmsg.so; prior working/broadband_cgiMain_disasm.txt (spot-verified)

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


## Binary identity
ELF64 AArch64 EXEC, stripped (dynsym only), entry 0x401d80, `.text 0x401d80+0x7f6c`, `.rodata 0x409d00`, template `pages/network/broadband/broadband.html`. `cgiMain` is a defined dynsym @ **0x403390, size 0x3594**, ends 0x406924. PLT (from .rela.plt): cmsgRequestSave 0x401a50, rdmGetAvaliableIAByOID 0x401a70, cmsgRequestSetIndexedObj 0x401b60, cmsgSendRecv 0x401bb0, rdmConstructIAValue 0x401bf0, cmsgRequestSet 0x401c00, cmsgRequestSel 0x401c10, cmsgRequestSelId 0x401d60. Call counts inside cgiMain (counted, not inferred from imports): Set ×83, SelId ×31, SetIndexedObj ×11, Sel ×1, Save ×2, SendRecv ×1, rdmGetAvaliableIAByOID ×2, rdmConstructIAValue ×13. **cmsgGetExecResult ×0** — the CGI never checks the backend result.

## OID resolution (independent, librdm OIDTable stride 280)
0xcd = WANIPConnection.i · 0xe3 = WANPPPConnection.i · 0xd3/0xe9 = PortTriggering (IP/PPP) · 0xd5/0xeb = DNS · 0xd8/0xee = IPv6DNS · 0x80 = Layer3Forwarding · 0x83 = X_5067F0_DefaultConnectionService child · 0x84/0x87 = IPv6 twins · 0xc7 = X_5067F0_GponInterafceConfig · 0xca = WANEthernetInterfaceConfig · 0x4d = WANSwitch. (This DISPROVES prior audits naming 0xc7 as WANPPPConnection — see FAILED_EXPERIMENTS C-2.)

## Q&A against the brief §7 (all CONFIRMED STATIC unless labelled)
1. **How an Ethernet submission is identified:** there is no Ethernet-specific code path. The POST is generic: session check → `rdmInit` → if not POST, GET render (showForm emits per-connection template vars `ETHWanIA`/`GPONWanIA` as `"%d,%d,%d"`). The edit runs only if a save-flag form field (`RN_WANGPONformSaveFlag`/`RN_WANETHformSaveFlag`, …) equals `"1"` (@0x403880–0x403964).
2. **wanIA:** form string (max 8 chars, buf sp+0x4a0 @0x40397c), logged @0x4039c0, parsed @0x4039ec by `rdmConstructIAValue(wanIA)` (librdm @0x1125c: strtok on `,`, strtol per token, rdmSetIAValue per depth). It is the IA spec of an **existing** connection: WANDevice, WANConnectionDevice, connection instance.
3. **Does wanIA select .3?** Only in the sense that the posted value's 2nd component does. **No instance number is hardcoded in cgiMain**; every path is `%d`-built from wanIA bytes. For the factory Eth profile the posted value would be `"1,3,1"` (STRONGLY INFERRED — showForm emits the IA of each existing connection; the HTML itself is absent).
4. **Create or edit a PPP object?** Creates — by conversion (see sequence). There is no pure-edit of a non-existent PPP and no add-new-connection entry point.
5. **cmsgRequestSetIndexedObj invoked?** Yes — 11 sites in cgiMain, enumerated below.
6. **rdmGetAvaliableIAByOID invoked?** Yes — @0x403e8c (IP→PPP) and @0x4042dc (PPP→IP). librdm @0x11c20: walks the parent's existing children, bumps a candidate from 1 past taken instances, checks schema max; returns 0 on failure — **return value is never checked by the CGI**.
7. **Exact object path for PPP creation:** built @0x403f68 as `InternetGatewayDevice.WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d` from the new IA bytes.
8. **Instance allocation:** computed in the CGI's librdm view via rdmGetAvaliableIAByOID(parentIA = first two wanIA components, `"%d,%d"` @0x403e74). Converting `"1,3,1"` with no PPP sibling ⇒ parent {1,3} + instance 1 ⇒ **`.3.WANPPPConnection.1`** (tie-break first-free vs max+1 not fully modelled — STRONGLY INFERRED; either rule yields 1 here).
9. **Exact CMSG sequence:** one request object for the whole POST (`cmsgCreateRequest`, module id of `ccc_das`); all Sel/Set/SetIndexedObj/Save operations are *queued*; `cmsgRequestSave(req, mid)` @0x4066d4; bridge-filter helper sub_402ddc; optional RN_Release block; **single `cmsgSendRecv(req, mid, 60000)` @0x4068b8 at the very end**; cmsgFree×2; render; return 0.
10. **Existing IP object deleted or disabled?** Deleted: SelId(0xcd, wanIA) @0x403dd0, syslog `"WanType is changed to PPP, delete %s"` @0x403e28, `SetIndexedObj(req, 0)` @0x403e34. Its PortTriggering entries (≤12) are first copied to a malloc'd list (malloc failure aborts the whole POST, nothing sent) and re-added under the new PPP object (OID 0xe9, SetIndexedObj(1) @0x406078).
11. **WAN mode changed?** Only in the separate RESTART branch (@0x4036b8–0x40387c): form `RestartBtn=="RESTART"` + `wanMode` ∈ {GPON, ETHER} → SelId 0xc7 Set Enable=(mode==GPON); SelId 0xca Set Enable=(mode==ETHER); SelId 0x4d Set WANMode=mode; Save @0x40387c. The conversion branch does not touch WAN mode.
12. **Default route pointer updated?** Conditionally: only if form `RN_Default_WAN_H=="1"` (@0x404738): SelId 0x83 + Set `DefaultConnectionService_GPON` or `DefaultConnectionService_ETHER` = connPath (these are *parameter names* on the OID-0x83 child, not objects); if either marker matches the current WANStatus name, SelId 0x80 + Set `DefaultConnectionService` = connPath @0x40485c. IPv6 twin via 0x87/0x84 gated on `RN_IPv6Default_WAN_H=="1"`.
13. **NAT/firewall:** purely via RDM params in the common tail (@0x4061e0–0x4065f0): `ConnectionType="IP_Routed"` @0x406214, NATEnabled from form RN_SelNAT, X_5067F0_NATType (Symmetric/PortReCone/AddrReCone/FullCone), IGMP/multicast params, PPPoE_PassThrough. No iptables/system/popen exists in this binary.
14. **PPP init immediate or deferred?** Deferred by construction: the CGI only queues operations; pppd startup is ccc_be's business after commit (and, per the boot-gating evidence, effectively after reboot — see BOOT analysis). No exec/system/pppd strings in broadband.cgi.
15. **Errors:** essentially unhandled — Sel/Set/SetIndexedObj/Save/SendRecv returns never tested, cmsgGetExecResult never called, cgiMain returns 0 on all paths. Checked failures only: rdmInit NULL, session, REQUEST_METHOD, PortTriggering malloc. A backend NACK of the ADD would be invisible in this CGI (directly relevant to the ccctest failure mode — the Web path would not report it either).
16. **Can the normal Web UI Add workflow create `.3.WANPPPConnection.1`?** There is no "Add" — but **YES via Edit/convert**: edit the existing Eth IP profile, set requested encap `RN_EncapFlag="1"` (PPP) and `RN_ModeFlag="0"` (routed), save-flag `"1"`. Whether the shipped HTML *exposes* those options for ETH is UNKNOWN (no HTML in the corpus).

## Type-conversion dispatch (branch conditions, CONFIRMED STATIC)
```
0x403a94 strncmp(wanType, RN_EncapFlag, 7)
  !=0 → 0x403ad8 dispatcher;  ==0 → if wanType!="1" or RN_ModeFlag!="1" → no-change @0x4043c0, else dispatcher
0x403ad8: if RN_EncapFlag!="1" → PPP→IP @0x403f70; if RN_ModeFlag!="0" → PPP→IP; else fallthrough IP→PPP @0x403b10
```
(wanType = current type code, "1"=PPP; RN_EncapFlag = requested encap, vendor-syslog-labelled "appliedWanType" — a source mislabel; RN_ModeFlag: "1"=bridged, "0"=routed. Semantics STRONGLY INFERRED from all uses.)

## IP→PPP sequence (CONFIRMED STATIC)
```
0x403b10 obj=cccRdmGetObjectByOID(rdm,0xcd,wanIA,1); if ConnectionType=="IP_Bridged" set bridged flags; save name string
  loop i=0..11: save PortTriggering of old IP conn (path …WANIPConnection.%d.X_5067F0_NAT.PortTriggering.%d)
0x403dd0 SelId(req,0xcd,wanIA); 0x403e34 SetIndexedObj(req,0)            ; DELETE IP
0x403e74 parentIA=rdmConstructIAValue("%d,%d",b1,b2)
0x403e8c newIA=rdmGetAvaliableIAByOID(rdm,0xe3,parentIA)                 ; overwrites wanIA var, unchecked
0x403eac SelId(req,0xe3,newIA);  0x403f10 SetIndexedObj(req,1)           ; CREATE PPP
0x403f68 connPath=snprintf("…WANDevice.%d.WANConnectionDevice.%d.WANPPPConnection.%d", newIA)
  → common tail: DCS update (conditional), LAN DHCP toggle if bridged changed,
    generic loop (Enable←RN_Active_H, Name←RN_Name, VLANID, VlanMux8021p, Enable_VLANID),
    PPP block (Username←RN_UserName, Password←RN_Password unless "****************", PPPoEServiceName←RN_ServiceName,
      PPPAuthenticationProtocol←RN_PPPAuth, ConnectionTrigger, IdleDisconnectTime, X_5067F0_MaxMTUSize←RN_MTU,
      MaxMRUSize←RN_MRU, addressing/DNS child ADD if missing (0xeb), IPv6DNS (0xee), PortTrigger re-add (0xe9)),
    NAT tail, Save @0x4066d4, SendRecv @0x4068b8
```
Mirror PPP→IP conversion @0x403f70–0x4043bc verified identically (delete 0xe3 @0x40427c, create 0xcd @0x404360).

## All 11 SetIndexedObj sites in cgiMain
0x403e34 (0, del IP) · 0x403f10 (1, **create PPP**) · 0x40427c (0, del PPP) · 0x404360 (1, create IP) · 0x404fcc, 0x405124, 0x4054d0, 0x405c8c (1, DNS child creates) · 0x405de4 (1, IPv6DNS) · 0x405730 (1, PortTrigger re-add IP) · 0x406078 (1, PortTrigger re-add PPP). **None targets WANConnectionDevice.**

## ETH/GPON edit CGIs
Both render-only: 104-byte cgiMain stubs (ETH @0x403150, GPON @0x403450), template paths `…/wanRemoteNode_ETH_Edit.html` / `…_GPON_Edit.html`, no mutation imports at all. ETH imports `getWANDeviceObjectRequestedLinkType`, GPON does not; GPON carries ATM QoS strings, ETH carries MLG_MTU/MRU_ETH_Error strings. Both read wanType/wanIA and write `/tmp/WANPageEditFlag`.

## Reconstructed pseudocode
See §10 of the working analysis reproduced in EVIDENCE_INDEX (findings_broadband §10): session → rdmInit → POST gate → optional RESTART WAN-mode block → save-flag gate → wanIA parse → conversion dispatch → conditional DCS → param blocks → NAT tail → Save → SendRecv (unchecked) → render → return 0.

## Contradictions
README §5 workflow CONFIRMED in substance with 4 corrections (parent IA is "%d,%d" not full wanIA; Enable comes from form RN_Active_H, not hardcoded 1; Save/SendRecv are at the very end, not per-step; ".3" comes from wanIA, not code). README's broadband.cgi hash DISPROVEN (see FAILED_EXPERIMENTS C-1). Prior claim "PPPoE creation impossible via Web GUI" PARTLY CONTRADICTED — no *new-profile* creation exists, but conversion creates the PPP object.
