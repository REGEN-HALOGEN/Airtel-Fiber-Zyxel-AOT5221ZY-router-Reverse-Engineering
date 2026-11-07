# PPP Object Analysis & Parameter Constraints

## Object Definition: `WANPPPConnection`
- **OID:** `0xc7`
- **Parent Object:** `WANConnectionDevice` (OID `0xc3`)
- **Schema Offset in `config.rdm`:** `0x3b2dc`

## Critical Parameter Mapping

| Parameter Name | Data Type | Read / Write | Verification Source |
| :--- | :--- | :---: | :--- |
| `Enable` | Boolean (`0` / `1`) | R/W | `config.rdm` / `beWanDoLayer3InterfaceAction` |
| `ConnectionType` | String (`IP_Routed`) | R/W | `config.rdm` |
| `Name` | String (Max 64) | R/W | `config.rdm` |
| `Username` | String (Max 64) | R/W | Written to `/etc/ppp/options_*` |
| `Password` | String (Max 64) | R/W | Written to `/etc/ppp/options_*` |
| `PPPoEServiceName` | String (Max 64) | R/W | Read by `beConfigWANByPPPoE` @ `0x66b3c` |
| `MaxMRUSize` | UnsignedInt | R/W | Bound to `mru %d` in pppd |
| `X_5067F0_MaxMTUSize` | UnsignedInt | R/W | Bound to `mtu %d` in pppd |
| `X_5067F0_PPPAuthenticationProtocol` | String | R/W | Evaluates `AUTO_AUTH`, `PAP`, `CHAP` |
| `NATEnabled` | Boolean (`0` / `1`) | R/W | Governs iptables masquerade insertion |
| `X_5067F0_Enable_VLANID` | Boolean (`0` / `1`) | R/W | `0` = appends `_notag`, `1` = appends `_<id>` |
| `X_5067F0_VLANID` | UnsignedInt | R/W | 802.1Q VLAN ID (0 when untagged) |
| `ConnectionStatus` | String (Read-Only) | R | Managed by `ccc_be` (`Connecting`, `Connected`) |
| `X_5067F0_IfName` | String (Internal) | R/W | Set to `"nas0_notag"` by `setWanIpPppInterfaceName` |
| `X_5067F0_InterfaceName` | String (Internal) | R/W | Set to `"ppp%d"` by `setWanIpPppInterfaceName` |

