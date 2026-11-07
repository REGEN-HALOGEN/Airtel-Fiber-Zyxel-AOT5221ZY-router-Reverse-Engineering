# RDM Parameter Inventory — Ethernet & PPPoE

## 1. Parameters under `WANSwitch`
- `WANMode` (String): `"GPON"`, `"ETHER"`.
- `WanAutoDetect` (Boolean): `0` = Disabled, `1` = Polling enabled.

## 2. Parameters under `WANEthernetInterfaceConfig`
- `Enable` (Boolean): `0` / `1`.
- `X_5067F0_IfName` (String): `"nas0"` (Base network device).
- `Status` (String): `"Up"`, `"Down"`.

## 3. Parameters under `WANConnectionDevice.i`
- `WANIPConnectionNumberOfEntries` (UnsignedInt, OID `0x44`): Count of IP connection children.
- `WANPPPConnectionNumberOfEntries` (UnsignedInt, OID `0x45`): Count of PPP connection children.

## 4. Parameters under `WANPPPConnection.i`
- `Enable` (Boolean): Activates the PPP session.
- `Name` (String): Profile display name (e.g. `Eth_PPPoE`).
- `ConnectionType` (String): `IP_Routed` / `IP_Bridged`.
- `Username` (String): PPPoE authentication username.
- `Password` (String): PPPoE authentication password.
- `PPPoEServiceName` (String): ISP Service Name (e.g. `3jglobal`).
- `MaxMRUSize` (UnsignedInt): `1480`.
- `X_5067F0_MaxMTUSize` (UnsignedInt): `1480`.
- `X_5067F0_PPPAuthenticationProtocol` (String): `AUTO_AUTH`, `PAP`, `CHAP`.
- `NATEnabled` (Boolean): `1` (enables NAT masquerading).
- `X_5067F0_Enable_VLANID` (Boolean): `0` (untagged SMUX `nas0_notag`).
- `X_5067F0_VLANID` (UnsignedInt): `0`.
- `ConnectionStatus` (String): Updated dynamically (`"Connecting"`, `"Connected"`).
- `X_5067F0_IfName` (String): Target lower device (`"nas0_notag"`).
- `X_5067F0_InterfaceName` (String): Target ppp unit (`"ppp111"`).

## 5. Parameters under `Layer3Forwarding`
- `DefaultConnectionService` (String): Full TR-098 path to the active default WAN connection object.

