# Bridge Architecture & Port Preservation

## Bridge Configuration (`brctl`)
The router maintains Linux bridge `br0` managing internal LAN traffic and Wi-Fi access points.

### Bridge Members Under Quiescent GPON Mode:
- `eth0` (Port 0 / LAN1)
- `eth1` (Port 1 / LAN2)
- `eth2` (Port 2 / LAN3 - AP Uplink)
- `eth3` (Port 3 / LAN4)
- `wlan0` / `wlan1` (2.4 GHz / 5 GHz Wi-Fi)

### Bridge Members Under Ethernet WAN Mode:
- When `rtk_wan_port_mapping(0, "nas0")` executes:
  - Port 3 (`eth3`, mask `0x08`) is detached from switch bridge forwarding and re-mapped exclusively to `nas0`.
  - Port 2 (`eth2`, mask `0x04`) remains in `br0`.
  - Wi-Fi radios (`wlan0`, `wlan1`) remain in `br0`.
- **Conclusion:** Local AP access and wired connectivity on LAN1, LAN2, and LAN3 remain fully operational.

