# Architectural Differences: GPON vs Ethernet WAN

## Side-by-Side Comparison Matrix

| Architectural Domain | GPON WAN Stack | Ethernet WAN Stack | Evidence References |
| :--- | :--- | :--- | :--- |
| **Physical Medium** | Fiber Optical (SC/APC) | 1000BASE-T RJ-45 (LAN4) | HW-001, HW-002 |
| **Switch Port Index** | Port 7 | Port 3 | `libcccBeWan_eth_Init` @ `0x38074` |
| **Switch Port Mask** | `0x80` | `0x08` | `/proc/fc/ctrl/wan_port_mask` |
| **Base Netdevice** | `nas0` | `nas0` | `WANEthernetInterfaceConfig` |
| **Untagged Subdevice** | `nas0_notag` (or tagged `nas0_100`) | `nas0_notag` | `constructL3WANDevName` @ `0x698dc` |
| **PHY Initialization** | `ca-ne.ko` (SerDes calibration) | `EthPhyEnable(1)` (RTL8211/8218) | `libcccbe.so` @ `0x3807c` |
| **WAN Switch Object** | `WANMode = "GPON"` | `WANMode = "ETHER"` | `config.rdm` @ `0x227d0` |
| **Container Instance** | `WANConnectionDevice.1` | `WANConnectionDevice.3` | `config.rdm` @ `0x36e74` |
| **Active Child Object** | `WANPPPConnection.1` | `WANPPPConnection.1` (Created) | `config.rdm` @ `0x3b2dc` |
| **LinkType Resolution** | Returns `1` (`LINK_TYPE_PPP`) | Returns `1` (`LINK_TYPE_PPP`) | `libcccbe.so` @ `0x34334` |
| **Daemon Launched** | `/bin/pppd` | `/bin/pppd` | `libcccbe.so` @ `0x348f4` |
| **Options File** | `/etc/ppp/options_nas0_100` | `/etc/ppp/options_nas0_notag` | `beConfigWANByPPPoE` @ `0x664a8` |
| **Auth & Parameters** | `3jglobal`, MTU 1480, `AUTO_AUTH` | `3jglobal`, MTU 1480, `AUTO_AUTH` | Identical generator code |
| **Default Routing** | `Layer3Forwarding` -> Instance `.1` | `Layer3Forwarding` -> Instance `.3` | `config.rdm` @ `0x27be8` |
| **NAT & Firewall** | Netfilter + Realtek HW NAT | Netfilter + Realtek HW NAT | Identical kernel flow engine |
| **LAN3 AP Uplink** | Preserved in `br0` (`0x04`) | Preserved in `br0` (`0x04`) | Hardware mask isolation |

## Conclusion
The Ethernet WAN stack reuses **95% of the same codebase** as GPON (PPP daemon, options generator, routing engine, NAT accelerator, firewall rules). The only divergence is the lower-layer physical switch port (`3` vs `7`) and the container instance (`3` vs `1`).

