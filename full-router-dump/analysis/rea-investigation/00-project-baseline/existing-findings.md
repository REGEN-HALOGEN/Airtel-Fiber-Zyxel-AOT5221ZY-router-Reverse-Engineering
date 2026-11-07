# Existing Findings Audit — Prior Research Baseline

## Context & Provenance
Prior research conducted in `analysis/reports/technical_report_pppoe_nas0_notag.md` established critical technical facts regarding the AOT5221ZY / Zyxel PX5311-R0 architecture. These findings serve as the starting baseline for this REA investigation and have been re-verified against binary artifacts.

## Summary of Inherited Baseline Findings

### 1. Platform & Kernel
- **SoC:** Realtek Taurus (RTL9607C / Chip ID `0x6706`), dual-core ARM Cortex-A53 (AArch64).
- **Kernel:** Linux 5.10.138 with vendor Realtek drivers (`ca-rtk.ko`, `ca-ne.ko`, `fc_8277c.ko`, `smuxdev.ko`).
- **Endianness:** Little-endian 64-bit ELF.

### 2. Physical Switch & Port Mapping
- Switch core manages physical ports 0 through 7.
- **Port 0:** LAN1 (mask `0x01`), in `br0`.
- **Port 1:** LAN2 (mask `0x02`), in `br0`.
- **Port 2:** LAN3 (mask `0x04`), in `br0` (Local AP uplink).
- **Port 3:** LAN4 (mask `0x08`), converted to WAN interface `nas0` on Ethernet transition.
- **Port 7:** GPON (mask `0x80`), internal optical MAC.
- **Isolation Guarantee:** Isolating Port 3 (`wan_port_mask = 0x08`) leaves Port 2 (`0x04`) unaffected in `br0`.

### 3. PPPoE & Interface Binding
- Interface name construction function `constructL3WANDevName` (`libbemodules.so` @ `0x698dc`) dynamically constructs `nas0_notag` when VLAN is disabled.
- Function `setWanIpPppInterfaceName` (`libcccbe.so` @ `0x346d0`) writes `nas0_notag` to `WANPPPConnection->X_5067F0_IfName` (offset `0x898`).
- Function `beConfigWANByPPPoE` (`libbemodules.so` @ `0x664a8`) generates `/etc/ppp/options_nas0_notag`.
- Function `libccc_executePPPv4Client` (`libcccbe.so` @ `0x348f4`) executes:
  `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`
- Positional argument `nas0_notag` binds `pppd`'s PPPoE socket directly to `nas0_notag`.

### 4. RDM Child Multi-Instance Logic
- `WANConnectionDevice` (OID `0x36e74`) defines `WANIPConnectionNumberOfEntries` (OID `0x44`) and `WANPPPConnectionNumberOfEntries` (OID `0x45`).
- `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`libcccbe.so` @ `0x34334`) returns LinkType `1` (`LINK_TYPE_PPP`) dynamically if `WANPPPConnectionNumberOfEntries > 0`.
- **Root Cause of Past Failures:** Historical Ethernet test exports (`ether-backup.lz`, `aot-current-pdm-config.xml`) only instantiated `WANIPConnection.1` under `WANConnectionDevice.3`. `WANPPPConnection.1` was never instantiated under `.3`.

### 5. Mode Switching Binary (`linkdetection`)
- A standalone binary `linkdetection` contains mode transition function at `0x402454`.
- It monitors port status via `rt_port_link_get` and invokes CMSG IPC to command `ccc_be`.
- Has known side-effect altering ACS URL on Ethernet switch; requires full static analysis before any activation can be safely attempted.

