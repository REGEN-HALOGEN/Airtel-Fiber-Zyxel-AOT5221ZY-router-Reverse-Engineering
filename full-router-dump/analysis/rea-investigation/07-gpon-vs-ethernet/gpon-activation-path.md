# GPON WAN Activation Path Analysis

## 1. Physical Layer & Optical MAC Initialization
- **Hardware Controller:** Realtek Taurus Optical MAC Engine controlled by kernel module `ca-ne.ko` (Network Engine driver).
- **Physical Interface:** Port 7 (`0x80` hardware mask).
- **Transceiver Monitoring:** Polled via `diag pon get transceiver rx-power` or `ioctl` to optical transceiver I2C bus.
- **Link State Signaling:** When optical sync (O5 state) is achieved, `ca-ne.ko` triggers link state up event on netdevice `nas0`.

## 2. RDM Configuration Object Hierarchy (GPON)
Under factory Airtel configuration, the GPON WAN stack is mapped to container `WANConnectionDevice.1`:
- `InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig.Enable = 1`
- `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1`:
  - `WANPPPConnection.1`: Internet data traffic (PPPoE, tagged VLAN 100 or untagged depending on OLT profile).
- `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2`:
  - `WANIPConnection.1`: Voice/VoIP or TR-069 management traffic (DHCP, tagged VLAN).

## 3. Daemon Execution & Driver Invocation
1. `ccc_be` reads `WANMode = "GPON"`.
2. Hardware port mapping sets Port 7 as WAN:
   ```bash
   echo 7 nas0 > /proc/ni/dev_port_mapping
   echo 80 > /proc/fc/ctrl/wan_port_mask
   ```
3. `smuxctl` creates sub-interfaces on `nas0` (e.g. `nas0_100` for 802.1Q tagged traffic or `nas0_notag`).
4. `libccc_executePPPv4Client` launches `/bin/pppd file /etc/ppp/options_nas0_100 nas0_100`.
5. Upon PADS session completion, `ppp1` interface is instantiated.
6. `/etc/ppp/ip-up` notifies `ccc_be` via `EVENTNOTIFY 206 string ppp1;`.
7. `ccc_be` binds default gateway to `ppp1` and configures NAT masquerading.

