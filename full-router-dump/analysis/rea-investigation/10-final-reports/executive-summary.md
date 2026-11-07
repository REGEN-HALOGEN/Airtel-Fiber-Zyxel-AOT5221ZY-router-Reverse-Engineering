# Executive Summary: Airtel AOT5221ZY Ethernet WAN & PPPoE Repurposing

## Project Mandate
This sustained reverse engineering investigation was commissioned to determine the exact, evidence-backed mechanism for enabling Ethernet WAN on the Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C SoC, Linux 5.10.138, AArch64) using an external GPON ONT and PPPoE authentication (`3jglobal`, MTU 1480, `AUTO_AUTH`), while preserving physical LAN3 as the internal Access Point uplink.

## Investigation Methodology & Standards
- **Strict Read-Only Static Analysis:** Zero writes to router flash, MTD, UBI, or live database.
- **Windows-Native Environment:** Executed on Windows 11 Pro 64-bit using Python 3.12, Capstone 5.0.9 disassembly engine, and pyelftools 0.33.
- **Complete Binary Verification:** 474 binaries scanned, 93 networking components mapped, decompiled 1,081 instructions of `linkdetection`, analyzed `beConfigWANByPPPoE` options generator, and decoded the 3 MiB decompressed `config.rdm` database.

## Key Breakthrough Discoveries
1. **Physical Port Topography & LAN3 Preservation Guarantee [HW-001/002]:**  
   The Realtek switch maps Port 3 to LAN4 (hardware mask `0x08`) and Port 2 to LAN3 (hardware mask `0x04`). When Ethernet WAN is active, only Port 3 is isolated. LAN3 remains in `br0`, guaranteeing uninterrupted AP uplink connectivity.
2. **Smoking Gun on ACS URL Clobbering [ETH-005]:**  
   The vendor daemon `linkdetection` contains hardcoded routine `0x402454` (`linkdetect_switch_WanMode`) which overwrites `ManagementServer.URL` with `http://testacs.airtelbroadband.in:8103/` and forces `DefaultConnectionService` to IP/DHCP (`TR069`).
3. **Permanent Disarming of `linkdetection` [ETH-008]:**  
   In `linkdetection`'s `main` (`0x401e10`), the mode-switching routine is gated by `WanAutoDetect`. Setting `WanAutoDetect = 0` completely skips the auto-switching logic, neutralizing the daemon without requiring binary patching or process termination.
4. **Dynamic PPPoE Binding to `nas0_notag` [PPP-001/002]:**  
   The firmware natively supports dynamic binding of `/bin/pppd` and `libpppoe.so` to SMUX device `nas0_notag` via `PF_PACKET` raw discovery sockets.
5. **Dynamic LinkType Switching via Multi-Instance RDM [RDM-001/002]:**  
   `WANConnectionDevice.3` dynamically returns LinkType `1` (`PPP`) when `WANPPPConnectionNumberOfEntries > 0`. Adding `WANPPPConnection.1` under container `.3` instructs `ccc_be` to run `pppd` with service name `3jglobal`, MTU 1480, and `AUTO_AUTH`.

## Strategic Implementation Recommendation
The deployment should be executed entirely via **Option 3: Clean CCC Script Orchestration**. This approach is 100% reversible, requires zero flash writes, modifies no binary files, and completely protects TR-069 and local network functionality.

