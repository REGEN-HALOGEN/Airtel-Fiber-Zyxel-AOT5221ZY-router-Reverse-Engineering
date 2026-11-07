# `nas0_notag` Interface Analysis & SMUX Multiplexing

## Interface Hierarchy
```
[Physical Port 3 / LAN4]
            |
    [Device: nas0] (Base Realtek Network Device)
            |
    [SMUX Multiplexer: smuxdev.ko]
            |
   +--------+--------+
   |                 |
[nas0_notag]     [nas0_<vlan>] (Untagged vs 802.1Q Tagged)
```

## Function Analysis: `constructL3WANDevName`
- **Location:** `files/libbemodules.so` @ Address `0x698dc`
- **Caller:** `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L3ConfigInit` (`0x4f440`)

### Decompiled Logic:
1. Reads base name `nas0` from `InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig.X_5067F0_IfName`.
2. Inspects `X_5067F0_Enable_VLANID` on the connection object:
   - If `X_5067F0_Enable_VLANID == 0`: Appends literal `"_notag"`. Resulting interface name: `"nas0_notag"`.
   - If `X_5067F0_Enable_VLANID == 1`: Appends `_` + decimal VLAN ID (e.g. `"nas0_100"`).
3. Calls `setWanIpPppInterfaceName("nas0_notag", connection_type)` (`libcccbe.so` @ `0x346d0`):
   - When `connection_type == 1` (PPP), writes `"nas0_notag"` to `WANPPPConnection->X_5067F0_IfName`.
   - Allocates PPP unit (e.g. `ppp111`) and writes to `WANPPPConnection->X_5067F0_InterfaceName`.

## SMUX Kernel Requirements
Untagged traffic traversing `nas0_notag` requires SMUX device creation in `smuxdev.ko`:
```bash
/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux
```
Without this step, attempting to open a raw socket or AF_PACKET PPPoE discovery socket against `nas0_notag` returns `ENODEV` (No such device).

