# Default Gateway Resolution Analysis

## Key Configuration Objects
1. `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService`:
   - Controls IPv4 default route target.
   - Default value: `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1` (GPON Internet).
   - Target unlock value: `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1` (Ethernet PPPoE).
2. `InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService`:
   - Controls IPv6 default route target.
   - Target unlock value: `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`.

## Routing Table Installation
Upon session establishment, `ccc_be` calls the kernel routing netlink interface:
```bash
ip route replace default dev ppp111
```
All outbound LAN traffic directed to the Internet is forwarded through `ppp111`.

