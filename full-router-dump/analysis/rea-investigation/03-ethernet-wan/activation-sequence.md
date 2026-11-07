# Ethernet WAN Activation Sequence & Lifecycle

## Activation Step-by-Step Execution Sequence

```
[1. Disarm linkdetection]
    Set InternetGatewayDevice.X_5067F0_Ext.WANSwitch.WanAutoDetect = 0
            |
[2. Engage Ethernet WAN Mode]
    Set InternetGatewayDevice.X_5067F0_Ext.WANSwitch.WANMode = "ETHER"
            |
[3. Enable Ethernet Hardware Interface]
    Set InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig.Enable = 1
    Set InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig.Enable = 0
            |
[4. Deactivate Old GPON Profiles]
    Set InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.Enable = 0
    Set InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1.Enable = 0
            |
[5. Create & Enable Ethernet PPPoE Child]
    ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection
    Configure credentials, 3jglobal, MTU 1480, AUTO_AUTH, NAT=1, VLAN=0
    Set Enable = 1
            |
[6. Update Routing Service Pointers]
    Set Layer3Forwarding.DefaultConnectionService = ...WANConnectionDevice.3.WANPPPConnection.1
    Set X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService = ...WANConnectionDevice.3.WANPPPConnection.1
            |
[7. CCC Backend Execution]
    ccc_be dispatches to libcccBeWan_eth_Init():
    - Powers PHY Port 3
    - Instantiates /bin/smuxctl nas0_notag
    - Writes wan_port_mask = 0x08 (LAN4 isolated, LAN3 preserved)
    - Generates /etc/ppp/options_nas0_notag
    - Spawns /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag
```

## Lifecycle States
1. **Quiescent GPON State:** WANMode=`GPON`, `wan_port_mask = 0x80`, `br0` includes ports 0, 1, 2, 3.
2. **Transition State:** `wan_port_mask = 0x08`, PHY Port 3 detached from `br0`, mapped to `nas0`.
3. **Operational Ethernet WAN State:** PPPoE establishes session `ppp111`, receives IP from ISP BRAS, default route installed via `ppp111`, LAN3 (`br0`) operates undisturbed as local AP uplink.

