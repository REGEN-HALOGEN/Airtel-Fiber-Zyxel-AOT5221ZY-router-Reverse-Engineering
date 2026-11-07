# Ethernet Profile Analysis — `Eth_Internet` vs Custom PPPoE

## 1. Existing Factory Profile `Eth_Internet`
In factory `aot-current-pdm-config.xml`, `WANConnectionDevice.3` is defined as:
```xml
<WANConnectionDevice>
    <i3>
        <WANIPConnection>
            <i1>
                <Name>Eth_Internet</Name>
                <ConnectionType>IP_Routed</ConnectionType>
                <AddressingType>DHCP</AddressingType>
                <X_5067F0_SERVICELIST>TR069</X_5067F0_SERVICELIST>
                <X_5067F0_IfName>nas0_notag</X_5067F0_IfName>
            </i1>
        </WANIPConnection>
    </i3>
</WANConnectionDevice>
```

### Analysis of Limitations
1. **AddressingType is DHCP:** Does not instantiate or run `pppd`.
2. **ServiceList is TR069:** Dedicated to TR-069 ACS management traffic, not general Internet routing.
3. **No WANPPPConnection child:** The RDM multi-instance container has 0 entries for `WANPPPConnection`, causing `libcccBeWan_getWANDeviceObjectRequestedLinkType` to return LinkType `0` (`LINK_TYPE_IP`).

---

## 2. Requirements for Ethernet WAN PPPoE Profile
To convert `WANConnectionDevice.3` into a functional ISP PPPoE connection:
1. `WANPPPConnection.1` must be added as a multi-instance child of `WANConnectionDevice.3`.
2. `WANPPPConnection.1` parameters:
   - `Enable` = `1`
   - `Name` = `Eth_PPPoE`
   - `ConnectionType` = `IP_Routed`
   - `Username` = `<ISP_USERNAME>`
   - `Password` = `<ISP_PASSWORD>`
   - `PPPoEServiceName` = `3jglobal`
   - `MaxMRUSize` = `1480`
   - `X_5067F0_MaxMTUSize` = `1480`
   - `X_5067F0_PPPAuthenticationProtocol` = `AUTO_AUTH`
   - `NATEnabled` = `1`
   - `X_5067F0_Enable_VLANID` = `0`
3. Point default route:
   `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService` = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`

