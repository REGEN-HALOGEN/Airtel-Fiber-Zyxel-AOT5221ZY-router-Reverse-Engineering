# Next Steps & Operational Transition

## Investigation Status: 100% COMPLETE, RUNTIME-SEQUENCE VERIFIED & AUDITED

The comprehensive reverse engineering investigation, Static PPPoE Integration Audit (Tasks A through G), Final Deployment Safety Audit (ADD/SET/SAVE/SEND & Rollback), Final Runtime-Sequence Verification, AND `libCmd.so` PPPoE Session Launch Analysis are fully completed, peer-verified against firmware binaries, and documented.

---

## Authoritative Documentation Map

1. **RDM PPPoE Integration Architecture Audit (Latest Deliverable):**
   - [`full-router-dump/analysis/rea-investigation/rdm-pppoe-integration-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/rdm-pppoe-integration-audit.md)
2. **`libCmd.so` PPPoE Session Launch Analysis:**
   - [`full-router-dump/analysis/rea-investigation/libcmd-pppoe-launch-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/libcmd-pppoe-launch-audit.md)
3. **Final Runtime-Sequence Verification:**
   - [`full-router-dump/analysis/rea-investigation/runtime-sequence-verification.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/runtime-sequence-verification.md)
4. **Final Deployment Safety Audit (ADD/SET/SAVE/SEND & Rollback):**
   - [`full-router-dump/analysis/rea-investigation/final-deployment-safety-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/final-deployment-safety-audit.md)
5. **Formal Technical Conclusion & Implementation Plan:**
   - [`full-router-dump/analysis/rea-investigation/STATIC_AUDIT_CONCLUSION.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/STATIC_AUDIT_CONCLUSION.md)
6. **Master Reverse Engineering Document:**
   - [`REVERSE_ENG.md`](file:///c:/Users/REGEN/AirtelModemRev/REVERSE_ENG.md) (in root directory)
   - Synchronized alias: [`REVERSE ENG.md`](file:///c:/Users/REGEN/AirtelModemRev/REVERSE%20ENG.md)
6. **Static Audit Specialized Reports (Tasks A through G):**
   - Task A (RDM & Object Creation): [`ppp-object-creation-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/ppp-object-creation-audit.md)
   - Task B (Lower-Layer Interface Binding): [`ppp-interface-binding-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/ppp-interface-binding-audit.md)
   - Task C (Boot & Runtime Dispatch): [`ethernet-ppp-dispatch-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/ethernet-ppp-dispatch-audit.md)
   - Task D (Lifecycle, Routing, NAT & MSS): [`ppp-routing-nat-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/ppp-routing-nat-audit.md)
   - Task E (Parameter & Spelling Validation): [`ppp-parameter-validation.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/ppp-parameter-validation.md)
   - Task F (GPON vs Ethernet PPP Parity): [`gpon-vs-ethernet-ppp-comparison.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/gpon-vs-ethernet-ppp-comparison.md)
   - Task G (Script & Grammar Audit): [`deployment-script-audit.md`](file:///c:/Users/REGEN/AirtelModemRev/full-router-dump/analysis/rea-investigation/deployment-script-audit.md)

---

## Recommended Execution Flow

1. **Physical Cabling Setup:**
   - Syrotech ONT Ethernet handoff cabled to **router LAN4** (physical switch port 3, WAN mask `0x08`).
   - Existing Access Point uplink cabled to **router LAN3** (untouched, preserved in `br0`).

2. **Stage 1 (Hardware Mode & Profile Provisioning):**
   - SSH to router: `ssh admin@192.168.0.2 -o HostKeyAlgorithms=+ssh-rsa`.
   - Take backup: `ccctest -d > /tmp/backup_rdm.txt`.
   - Dispatch `stage1.cmd` (neutralizes auto-switching, sets `WANMode="ETHER"`, creates `WANPPPConnection.1` with `Enable=1`, disables GPON).
   - `checkWANDeviceObjectRequestedLinkIsUp` prevents premature `pppd` launch prior to reboot.

3. **Controlled First Reboot:**
   - Issue `/sbin/reboot`.
   - During boot: `ConfigLoaderFunc_Boot` powers up LAN4 PHY (`EthPhyEnable(1)`), configures `nas0`, and maps port 3.
   - `L3ConfigLoad` creates `nas0_notag` via `smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux` and starts `pppd`.
   - Verify `ppp111` is up: `ifconfig ppp111`, `ps | grep pppd`.

4. **Stage 2 (Default Routing Activation):**
   - Dispatch `stage2.cmd` (repoints `DefaultConnectionService` to `...WANConnectionDevice.3.WANPPPConnection.1`).
   - `editDefaultGateway` binds default route `0.0.0.0/0` to `ppp111` without restarting PPP.

5. **Rollback (If Ever Required):**
   - Dispatch `rollback.cmd` (repoints default route to GPON, deletes `WANPPPConnection.1` via `DELETE` which invokes `beWanDisableClient` with `kill -15` then `kill -9`, restores GPON profiles).
   - Issue `/sbin/reboot` to re-initialize GPON OMCI/SerDes and restore port 3 to LAN bridge.
