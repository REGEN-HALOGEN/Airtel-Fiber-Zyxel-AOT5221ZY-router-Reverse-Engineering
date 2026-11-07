# RDM Object Inventory — High-Relevance Objects

| Object Path | OID | Decompressed File Offset | Instance Type | Functional Role |
| :--- | :---: | :---: | :--- | :--- |
| `InternetGatewayDevice.X_5067F0_Ext.WANSwitch` | `0xc0` | `0x227d0` | Single | WAN mode selector (`WANMode`) and auto-detect control (`WanAutoDetect`). |
| `InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig` | `0xc1` | `0x3696c` | Single | Ethernet WAN physical interface configuration and base name (`nas0`). |
| `InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig` | `0xc2` | `0x364f0` | Single | GPON optical interface control and enablement. |
| `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.i` | `0xc3` | `0x36e74` | Multi-Instance | Container for WAN profiles (1 = GPON Internet, 2 = GPON TR069, 3 = Ethernet). |
| `...WANConnectionDevice.i.WANIPConnection.i` | `0xca` | `0x370b4` | Multi-Instance | IP WAN connection (DHCP / Static); contains `Eth_Internet`. |
| `...WANConnectionDevice.i.WANPPPConnection.i` | `0xc7` | `0x3b2dc` | Multi-Instance | PPP WAN connection; supports PPPoE client terminating on `nas0_notag`. |
| `InternetGatewayDevice.Layer3Forwarding` | `0x40` | `0x27be8` | Single | Default IPv4 route pointer (`DefaultConnectionService`). |
| `InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding` | `0x41` | `0x286dd` | Single | Default IPv6 route pointer (`DefaultConnectionService`). |
| `InternetGatewayDevice.ManagementServer` | `0x50` | `0x19a00` | Single | TR-069 ACS configuration (`URL`, `Username`, `Password`). |

