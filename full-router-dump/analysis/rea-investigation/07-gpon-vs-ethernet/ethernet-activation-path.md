# Ethernet WAN Activation Path Analysis

## 1. Physical Layer & PHY Port 3 Configuration
- **Hardware Controller:** Realtek Taurus Integrated Gigabit Ethernet Switch (`ca-rtk.ko`) and external PHY transceiver.
- **Physical Interface:** Port 3 (`0x08` hardware mask) mapped to rear RJ-45 LAN4 connector.
- **PHY Enable:** Function `libcccBeWan_eth_Init()` (`libcccbe.so` @ `0x38074`) invokes `EthPhyEnable(1)` to power up and configure auto-negotiation (10/100/1000 Mbps full-duplex) on PHY port 3.
- **Switch Port Mapping:**
  ```bash
  echo 3 nas0 > /proc/ni/dev_port_mapping
  echo 8 > /proc/fc/ctrl/wan_port_mask
  ```
  This immediately isolates Port 3 from `br0` and binds its hardware ingress/egress queues to the WAN network interface `nas0`. Ports 0, 1, and 2 (LAN3 AP uplink) remain untouched in `br0`.

## 2. RDM Configuration Object Hierarchy (Ethernet WAN)
The Ethernet WAN architecture is governed by container `WANConnectionDevice.3`:
- `InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig.Enable = 1`
- `InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig.Enable = 0`
- `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3`:
  - `WANIPConnection.1`: Factory default profile (`Eth_Internet`, DHCP, TR069 service).
  - `WANPPPConnection.1`: Newly added ISP PPPoE profile (IP_Routed, Internet service, MTU 1480, `AUTO_AUTH`, `3jglobal`).

## 3. Daemon Execution & Driver Invocation
1. `ccc_be` evaluates `WANConnectionDevice.3`.
2. Function `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`libcccbe.so` @ `0x34334`) checks `WANPPPConnectionNumberOfEntries`. With entry count `1`, it returns `1` (`LINK_TYPE_PPP`).
3. `smuxctl` provisions `nas0_notag`:
   ```bash
   smuxctl add notag nas0 nas0_notag
   ip link set dev nas0_notag up
   ```
4. `beConfigWANByPPPoE` (`libbemodules.so` @ `0x664a8`) generates runtime options file `/etc/ppp/options_nas0_notag`.
5. `libccc_executePPPv4Client` launches:
   ```bash
   /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &
   ```
6. `libpppoe.so` discovers external ONT on `nas0_notag` and negotiates session with ISP BRAS.
7. Upon successful IPCP negotiation, virtual interface `ppp111` is instantiated.
8. `/etc/ppp/ip-up` notifies `ccc_be` via `EVENTNOTIFY 206 string ppp111;`.
9. `ccc_be` binds default gateway to `ppp111`, writes DNS to `/etc/resolv.conf`, and enables Fastpath hardware NAT.

