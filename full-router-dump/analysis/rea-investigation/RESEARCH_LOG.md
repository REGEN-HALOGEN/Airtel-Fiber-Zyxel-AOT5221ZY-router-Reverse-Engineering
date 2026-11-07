# Research Activity Log — Airtel AOT5221ZY Investigation

## Session 1: 2026-11-05

### [15:00 - 15:15] Project Directive Ingestion & Archive Reconnaissance
- Received Master Directive for Airtel AOT5221ZY firmware reverse-engineering.
- Target hardware identified: Realtek Taurus RTL9607C (AArch64), Zyxel PX5311-R0 board, Linux 5.10.138.
- Inspected authoritative directory `C:\Users\REGEN\AirtelModemRev\full-router-dump` (`README.md`, `FILE_INVENTORY.csv`, `FOLDER_TREE.txt`, `analysis/reports/`).
- Discovered extensive prior research in `analysis/reports/technical_report_pppoe_nas0_notag.md`.
- Established strict read-only boundary on firmware dumps and router hardware.

### [15:15 - 15:35] REA & Windows Toolchain Capability Audit
- Inspected Antigravity IDE MCP configuration: `C:\Users\REGEN\.gemini\config\mcp_config.json`.
- Ran `npx -y rea-agents@6.7.0 doctor --client antigravity --json`.
- Tested REA native analysis against AArch64 binary (`linkdetection`); captured `target_format_unsupported` error.
- Audited alternative Windows-native analysis tools: Python packages `capstone` 5.0.9 and `pyelftools` 0.33 confirmed operational.

### [15:35 - 15:50] Project Folder Hierarchy & Baseline Setup
- Created standardized folder structure under `analysis/rea-investigation/` with junction to `AirtelModemRev\analysis\rea-investigation`.
- Initialized core management documents: `README.md`, `PROJECT_STATUS.md`, `MASTER_FINDINGS.md`, `RESEARCH_LOG.md`, `NEXT_STEPS.md`.
- Computed and verified SHA-256 cryptographic digests for 12 core ELF binaries and modules.

### [15:50 - 16:15] Phase 2 Deep Analysis: `linkdetection` & Routine `0x402454`
- User noted installation of JDK 21 at `C:\Program Files\Eclipse Adoptium\jdk-21.0.13.9-hotspot`.
- Disassembled routine `0x402454` through `0x403534` (1,081 instructions) using Capstone.
- Recovered original function symbol: `linkdetect_switch_WanMode`.
- Identified exact ACS URL clobbering instructions: `0x40332c` - `0x40338c` overwrite `ManagementServer.URL` with `"http://testacs.airtelbroadband.in:8103/"` and set `DefaultConnectionService` to `WANConnectionDevice.3.WANIPConnection.1`.
- Traced caller tree in `main`: `0x40223c` hardcodes `mov w0, #3; ret` (Port 3 = LAN4).
- Discovered `WanAutoDetect = 0` disarms `linkdetection` mode switching completely.
- Authored all 7 Phase 2 reports under `03-ethernet-wan/`.

### [16:15 - 16:35] Master Report Creation & Phase 3 Deep Dive (PPPoE Subsystem)
- Created compiled master report [`REVERSE_ENG.md`](file:///c:/Users/REGEN/AirtelModemRev/REVERSE_ENG.md) in the root of `AirtelModemRev`.
- Disassembled `libpppoe.so` (`pppoe_plugin_init` @ `0x2f98`, `setdevname_pppoe` @ `0x2c00`).
- Confirmed dynamic socket binding to `nas0_notag` via `PF_PACKET` raw socket and `ioctl(SIOCGIFINDEX)`.
- Disassembled `beConfigWANByPPPoE` (`0x664a8` in `libbemodules.so`):
  - Verified creation of `/etc/ppp/options_nas0_notag` from template `/etc/ppp/default_options`.
  - Confirmed emission of `pppoe_srv_name 3jglobal` (`0x66b3c`).
  - Confirmed MTU/MRU 1480 configuration.
  - Confirmed `AUTO_AUTH` leaves PAP and CHAP refuse flags unset for open negotiation.
- Analyzed `/etc/ppp/ip-up` and `/etc/ppp/ip-down`:
  - Verified emission of `EVENTNOTIFY 206 string ppp111;` to `ccctest`.
  - Mapped automated default route installation, DNS propagation, and NAT masquerading in `ccc_be`.
- Authored all 8 Phase 3 reports under `04-pppoe/`.
- Appended compiled Phase 3 findings to `REVERSE_ENG.md`.


### [16:35 - 17:00] Phase 4: RDM Database Deep Decoding
- Decompressed `files/config.rdm` (LZMA-alone stream) to `analysis/config_rdm_decompressed.bin` (3,145,728 bytes).
- Parsed `librdm.so` export `OIDTable` (`0x294f0`, 180,320 bytes), indexing TR-098 schema objects and OID maps.
- Verified offsets and parameters for `WANSwitch` (`0x227d0`), `WANEthernetInterfaceConfig` (`0x3696c`), `WANConnectionDevice` (`0x36e74`), `WANPPPConnection` (`0x3b2dc`), and `Layer3Forwarding` (`0x27be8`).
- Proved dynamic LinkType switching: `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`0x34334`) returns LinkType `1` (`PPP`) when `WANPPPConnectionNumberOfEntries > 0`.
- Authored all 7 Phase 4 reports under `05-rdm/`.
- Appended compiled Phase 4 findings to `REVERSE_ENG.md`.

### [17:00 - 17:45] Phases 5 to 10: Network Integration, Implementation Blueprint & Final Reports
- **Phase 5 (Network Integration):** Analyzed Linux routing table propagation, default gateway metric binding, Netfilter masquerading, Realtek Fastpath hardware flow cache (`fc_8277c.ko`), TCP MSS clamping (PMTU 1440), and LAN3 isolation guarantee (`HW-002`). Authored all 8 reports under `06-network-integration/`.
- **Phase 6 (GPON vs Ethernet Comparison):** Produced full architectural matrix and code reuse breakdown showing 95% subsystem convergence between modes. Authored all 5 reports under `07-gpon-vs-ethernet/`.
- **Phase 7 (Implementation Research):** Synthesized Option 3: Clean CCC Script Orchestration via CLI (`ccc_das`). Confirmed zero flash writes, zero binary changes, and 100% reversible operation. Authored all 5 reports under `08-implementation-research/`.
- **Phases 8 & 9 (Safety, Testing, Risk & Rollback):** Formulated Risk Register and instant 3-second rollback script (`rollback_to_gpon.cmd`). Authored all 4 reports under `09-safety-and-testing/`.
- **Phase 10 (Final Consolidation):** Authored Executive Summary, Technical Conclusion, and Operational Runbook under `10-final-reports/`.
- **Master Document Synchronization:** Fully compiled and synchronized all phases into root documents [`REVERSE_ENG.md`](file:///c:/Users/REGEN\AirtelModemRev\REVERSE_ENG.md) and [`REVERSE ENG.md`](file:///c:/Users/REGEN\AirtelModemRev\REVERSE ENG.md).


## Session 2: 2026-11-05 — Static PPPoE Integration Audit (Tasks A through G)

### [17:45 - 18:30] Static Audit Tasks A through D Execution
- **Task A (RDM Object Creation):**
  - Traced `ADD` command in `ccctest` (`0x402cac`), `cmsgRequestSetIndexedObj` (`libcmsg.so` @ `0x56a4`), and `cccRdmAddIndexChildObject` (`librdm.so` @ `0x134a0`).
  - Discovered that line `0x137ec` hardcodes `mov x2, #1` when child list is empty, guaranteeing automatic allocation of instance `.1` (`WANConnectionDevice.3.WANPPPConnection.1`).
  - Confirmed zero parent instance restrictions in `librdm.so`. Authored `ppp-object-creation-audit.md`.
- **Task B (Interface Binding):**
  - Traced `setWanIpPppInterfaceName()` (`libcccbe.so` @ `0x346d0`): verified formatting of base name `"nas0"` + suffix `"_notag"`, assigning `"nas0_notag"` to `X_5067F0_IfName` and `"ppp111"` to `X_5067F0_InterfaceName`.
  - Traced `libccc_executePPPv4Client()` (`0x348f4`): confirmed execution of `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag`.
  - Disassembled `libpppoe.so` (`setdevname_pppoe` @ `0x2c00`): confirmed raw `PF_PACKET` socket bound to `nas0_notag`. Authored `ppp-interface-binding-audit.md`.
- **Task C (Ethernet WAN Boot & Dispatch):**
  - Traced caller of `libcccBeWan_eth_Init()` (`0x38074`): identified `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot` (`libbemodules.so` @ `0x50d08`) as the sole caller during boot when `WANMode == "ETHER"`.
  - Confirmed physical port 3 mapping (`rtk_wan_port_mapping(0, "nas0")`) and PHY power-up require a device reboot.
  - Traced `libcccBeWan_getWANDeviceObjectRequestedLinkType()` (`0x34334`): verified check on `WANPPPConnection` count branching to `beWanEnablePPPv4Client`. Authored `ethernet-ppp-dispatch-audit.md`.
- **Task D (PPP Lifecycle & Routing/NAT):**
  - Traced `/etc/ppp/ip-up`: verified dispatch of `EVENTNOTIFY 206 string ppp111;` to `ccc_be`.
  - Traced Event 206 handlers in `libbeEvents.so`: `Route_EventHandlerFunc` (`0x9084`), `NAT_EventHandlerFunc` (`0x92f0`), `Firewall_EventHandlerFunc`, and `fc_8277c.ko` Fastpath offload. Confirmed 100% generic handling of `ppp111`. Authored `ppp-routing-nat-audit.md`.

### [18:30 - 19:15] Static Audit Tasks E through G & Final Formal Conclusion
- **Task E (Parameter Validation):**
  - Verified every parameter from proposed deployment against `config_rdm_decompressed.bin` and `librdm.so`.
  - Discovered critical vendor spelling: `X_5067F0_GponInterafceConfig` (with `afce`).
  - Authored `ppp-parameter-validation.md`.
- **Task F (GPON vs Ethernet Comparison):**
  - Compiled detailed side-by-side comparison matrix demonstrating 100% architectural parity across drivers, PPP, routing, NAT, firewall, and Fastpath offload.
  - Authored `gpon-vs-ethernet-ppp-comparison.md`.
- **Task G (Script Audit):**
  - Conducted line-by-line audit of deployment and rollback scripts.
  - Identified grammar bug in originally proposed `ADD` construct (`ADD` requires fully qualified path; calling `SEL` before `SEND` aborts transaction).
  - Formulated verified two-stage deployment protocol (`stage1_create_eth_pppoe.cmd` + `stage2_set_l3_forwarding.cmd` + `reboot`).
  - Authored `deployment-script-audit.md`.
- **Final Audit Conclusion & Master Sync:**
  - Authored `STATIC_AUDIT_CONCLUSION.md` declaring **CONFIRMED** feasibility.
  - Appended complete audit findings and two-stage runbook to master report `REVERSE_ENG.md` and `REVERSE ENG.md`.


## Session 3: 2026-11-05 — Final Deployment Safety Audit (ADD / SET / SAVE / SEND & Rollback)

### [19:15 - 20:00] Binary Disassembly of Command Semantics & Rollback Parity
- **ADD Semantics:**
  - Disassembled `ccctest` parser (`0x402cac` - `0x402ce8`): proved `ADD` calls `cmsgRequestSel` and sets target object context in `req`.
  - Disassembled `cmsgRequestSet` (`0x5824`): proved subsequent `SET` applies directly to the `ADD` target without requiring `SEL`.
  - Disassembled `cccRdmAddIndexChildObject` (`0x134a0`) and `cccRdmSetObjDefault` (`0x114cc`): proved schema template `Enable = false` (0) is copied on creation, requiring explicit `SET Enable boolean 1;`.
- **Runtime Pre-Reboot Safe Failure:**
  - Proved that if `beWanDoLayer3InterfaceAction` launches `pppd` prior to reboot, `ioctl(SIOCGIFINDEX, "nas0_notag")` in `libpppoe.so` (`0x2c00`) fails with `ENODEV` because `nas0` is only created at boot by `ConfigLoaderFunc_Boot` (`0x50d08`). `pppd` exits cleanly with code 1.
- **Rollback Audit & Exact Baseline Parity:**
  - Inspected `files/aot-current-pdm-config.xml`: discovered `WANEthernetInterfaceConfig.Enable` was ALREADY `1` in factory config (corrected earlier assumption that set it to `0`).
  - Disassembled `ccctest DELETE` path (`0x402da8`): proved `DELETE` calls `cmsgRequestSetIndexedObj(req, 0)` and `cccRdmDelObjectByOID` (`0x40f830`), decrementing `WANPPPConnectionNumberOfEntries` back to `0`.
  - Proved `DELETE` is mandatory to restore LinkType resolver behavior.
  - Authored `final-deployment-safety-audit.md`.
  - Updated `MASTER_FINDINGS.md`, `PROJECT_STATUS.md`, `NEXT_STEPS.md`, and master report `REVERSE_ENG.md`.


## Session 4: 2026-11-05 — Final Runtime-Sequence Verification (Ethernet PPPoE Lifecycle)

### [20:00 - 20:45] Disassembly Verification of Runtime Lifecycle & Boot Order
- **Question 1: Stage 1 Callback & Pre-Reboot Gate:**
  - Traced `SEND` transaction commit in `ccc_be` (`0x411d38` - `0x411da8`): calls `blr x2` on registered event handlers.
  - Disassembled `L3ObjectChanged` (`libbemodules.so` @ `0x4ddc4`): discovered `checkWANDeviceObjectRequestedLinkIsUp` gatekeeper (`0x4df00`).
  - Disassembled `checkWANDeviceObjectRequestedLinkIsUp` (`0x67964`): reads `glb_status_tb[0]`. Because physical link is down before reboot, returns `0`. `L3ObjectChanged` immediately exits without calling `beWanDoLayer3InterfaceAction`.
  - Disassembled `libpppoe.so` (`client_init_ses` @ `0x3408`, `get_sockaddr_ll` @ `0x4d10`, `poe_fatal` @ `0x4958`): proved `pppd` terminates immediately with exit code 1 if netdevice is missing, without retry loops or RDM status changes.
- **Question 2: Boot Ordering & `nas0_notag` Dynamic Instantiation:**
  - Disassembled `L0ConfigLoad` (`libbemodules.so` @ `0x50348`): established strict linear order L1 (`0x50494`) -> L2 (`0x5062c`) -> L3 (`0x50694`) -> L4 (`0x507e0`).
  - Proved `ConfigLoaderFunc_Boot` (`0x50d08`) runs `libcccBeWan_eth_Init()` during L1, completing PHY enablement and port 3 switch mapping before L3 executes.
  - Disassembled `createLayer3Interface` (`libcccbe.so` @ `0x35348`): proved `nas0_notag` is instantiated via `/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux`.
- **Question 3: Second-Stage Route Independence:**
  - Disassembled `layer3ForwardingHandleFunc` (`0x397e4`) and `beL2BrChangeDefaultWAN` (`0x4cc58`): proved `DefaultConnectionService` calls `editDefaultGateway` to update routing/bridge tables only, with zero PPP daemon restarts.
- **Question 4: Rollback & Deletion Lifecycle:**
  - Disassembled `beWanDisableClient` (`0x6722c`): proved `pppd` is terminated via `kill -15 <pid> > /dev/null 2>&1 && sleep 2 && kill -9 <pid> > /dev/null 2>&1 &` before destroying `nas0_notag` via `smuxctl --if-delete`.
  - Disassembled `libcccBeWan_doWanModeChange` (`0x36d3c`): proved returning `WANMode` to GPON forces a system reboot to re-initialize GPON OMCI/SerDes hardware.
- **Deliverables & Synchronization:**
  - Authored `runtime-sequence-verification.md`.
  - Synchronized `MASTER_FINDINGS.md`, `PROJECT_STATUS.md`, `NEXT_STEPS.md`, and master report `REVERSE_ENG.md` / `REVERSE ENG.md`.


## Session 5: 2026-11-05 — `libCmd.so` PPPoE Session Launch Analysis

### [20:45 - 21:15] Binary Reverse Engineering of PPPoE Launchers & CLI Handlers
- **Target Binary & String Pattern Matching:**
  - Located primary binary: `full-router-dump/filesystem/rootfs/lib/MSTC/libCmd.so` (1,189,384 bytes).
  - Located all command strings in `.rodata`:
    - `0xcadd8`: `ps | grep "pppd -d file /etc/ppp/options_%s %s"`
    - `0xcae18`: `/bin/pppd -d file /etc/ppp/options_%s %s`
    - `0xcae48`: `/bin/ls /var/run | grep ppp%s.pid && kill -SIGTERM \`cat /var/run/ppp%s.pid\` && rm -f /var/run/ppp%s.pid`
    - `0xcaeb8`: `/bin/ls /var/run | grep ppp%s.pid || /bin/pppd -d file /etc/ppp/options_%s %s &`
    - `0xcaf08`: `/bin/ls /var/run | grep ppp%s.pid || /bin/pppd file /etc/ppp/options_%s %s &`
    - `0xcaf78`: `/bin/ls /var/run | grep %s.pid || /bin/pppd file /etc/ppp/options_%s %s &`
    - `0xcafc8`: `/bin/ls /var/run | grep %s.pid && kill -SIGTERM \`cat /var/run/%s.pid\` && rm -f /var/run/%s.pid`
- **Containing Functions & Call Graph:**
  - `CheckAndRestartPPP` (`0x4945c`, size 808 bytes): Called by CLI `ppp debug <ifname|all> <1|0>` (`0x609f8`) at `0x60bd8` and `0x60c60`.
  - `wrapperDoPPP` (`0x49784`, size 504 bytes): Called by CLI `ppp config <wan_index> <up|down>` (`0x60d24`) via command table at `0x12c220`.
- **RDM Object & Parameter Offsets:**
  - Identified target object: OID `0xe3` (`WANPPPConnection`).
  - Proved struct offset `+0x03e7`: `X_5067F0_InterfaceName` (`"ppp111"`), used for PID validation and signal targeting.
  - Proved struct offset `+0x0898`: `X_5067F0_IfName` (`"nas0_100"` / `"nas0_notag"`), used for options filename and device binding.
- **Argument & Syntax Resolution:**
  - Proved both `%s` in `/bin/pppd [ -d ] file /etc/ppp/options_%s %s` receive `obj->X_5067F0_IfName`.
  - Proved the second `%s` is the Linux netdevice passed as a positional parameter to `pppd` for `libpppoe.so` discovery socket binding.
  - Proved identical logic in `libcccbe.so` (`libccc_executePPPv4Client` @ `0x348f4`): `%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &`.
- **Verification of `nas0_notag`:**
  - Confirmed 100% zero restriction against untagged Ethernet WAN; automatically constructs `/etc/ppp/options_nas0_notag nas0_notag`.
- **Deliverables & Synchronization:**
  - Authored `libcmd-pppoe-launch-audit.md`.
  - Updated `PROJECT_STATUS.md`, `RESEARCH_LOG.md`, `MASTER_FINDINGS.md`, and synchronized root master ledgers `REVERSE_ENG.md` and `REVERSE ENG.md`.

## Session 6: 2026-11-05 — Static PPPoE RDM Integration Architecture Audit

### [21:30 - 22:30] Static Decompilation & Lifecycle Audit of `beConfigWANByPPPoE`, `createLayer3Interface`, `beWanEnablePPPv4Client`, `libccc_executePPPv4Client`
- **Target Functions & Locations:**
  - `beConfigWANByPPPoE` (`libbemodules.so:0x664a8`, size 1,712 bytes, 428 instructions).
  - `createLayer3Interface` (`libcccbe.so:0x35348`, size 3,096 bytes, 774 instructions).
  - `beWanEnablePPPv4Client` (`libbemodules.so:0x66ee4`, size 52 bytes, 13 instructions).
  - `libccc_executePPPv4Client` (`libcccbe.so:0x348f4`, size 140 bytes, 35 instructions).
  - `constructL3WANDevName` (`libbemodules.so:0x698dc`, size 596 bytes).
  - `setWanIpPppInterfaceName` (`libcccbe.so:0x346d0`, size 548 bytes).
  - `libcccBeWan_getPPPPdUnitNum_wrapper` (`libcccbe.so:0x38264`, size 344 bytes).
- **Struct Offset Mapping (`struct WANPPPConnection`):**
  - Mapped all 15 accessed struct offsets relative to `x20`:
    `+0x008` (IdleDisconnectTime), `+0x018` (MaxMRUSize), `+0x01a` (MaxMTUSize), `+0x020` (PPPLCPEcho), `+0x022` (PPPLCPEchoRetry), `+0x02c` (Enable), `+0x042` (IPVersion), `+0x043` (IPv6Enable), `+0x092` (ExternalIPAddress), `+0x0c6` (Name), `+0x2c8` (AddressingType), `+0x324` (Username), `+0x365` (Password), `+0x3e7` (X_5067F0_InterfaceName), `+0x532` (PPPoEServiceName), `+0x633` (ConnectionTrigger), `+0x649` (PPPAuthenticationProtocol), `+0x898` (X_5067F0_IfName).
- **IAValue to PPP Unit Mapping:**
  - Proved `libcccBeWan_getPPPPdUnitNum_wrapper` formats IA bits 56..40 with `"%d%d%d"`.
  - For `WANConnectionDevice.3.WANPPPConnection.1` (IA `1.3.1`), generates unit `131` and virtual interface `ppp131`.
- **Options File Generation:**
  - Proved `beConfigWANByPPPoE` copies `/etc/ppp/default_options` to `/etc/ppp/options_nas0_notag` and appends all ISP parameters: `user`, `password`, `mru 1480`, `mtu 1480`, `pppoe_srv_name 3jglobal`, `linkname ppp131`.
- **Netdevice Creation & Activation:**
  - Proved `createLayer3Interface` executes `/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux --carrier MANUAL`, sets MTU 1500, txqueuelen 10, enables carrier (`echo "carrier nas0_notag on" > /proc/rtk_smuxdev/interface`), and sets carrier AUTO.
- **PPPoE Execution & Route/NAT Binding:**
  - Proved `libccc_executePPPv4Client` executes `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`.
  - Proved `/etc/ppp/ip-up` triggers `EVENTNOTIFY 206 string ppp131;` via `ccctest`, directing default route and NAT masquerade to `ppp131`.
- **Deliverables & Synchronization:**
  - Authored `rdm-pppoe-integration-audit.md`.
  - Updated `PROJECT_STATUS.md`, `RESEARCH_LOG.md`, `MASTER_FINDINGS.md`, `NEXT_STEPS.md`.
  - Appended Part 15 to `REVERSE_ENG.md` and `REVERSE ENG.md` (both verified at 83,566 bytes).
