# Ethernet Hardware Architecture & Switch Topography

## Target Platform
- **SoC:** Realtek Taurus RTL9607C (AArch64)
- **Ethernet Switch Core:** Integrated 5-port Realtek Gigabit Switch (`ca-rtk.ko`)
- **SerDes / Optical Core:** Integrated EPON/GPON MAC + SerDes (`ca-ne.ko`)
- **Fastpath Acceleration:** Realtek Flow Control Engine (`fc_8277c.ko`)

## Physical Port Allocation
The Realtek Taurus switch core exposes 8 internal port indices (bits 0 through 7):

| Port Index | Port Mask | Physical Connector | Linux Interface (Default) | Role in GPON Mode | Role in Ethernet WAN Mode |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `0x01` | LAN1 | `eth0` / `br0` | Local LAN Port | Local LAN Port (Untouched) |
| **1** | `0x02` | LAN2 | `eth1` / `br0` | Local LAN Port | Local LAN Port (Untouched) |
| **2** | `0x04` | LAN3 | `eth2` / `br0` | Local LAN Port (AP Uplink) | **Local LAN Port (AP Uplink - PRESERVED)** |
| **3** | `0x08` | LAN4 | `eth3` -> `nas0` | Local LAN Port | **Dedicated Ethernet WAN Port** |
| **4** | `0x10` | Internal CPU | `cpu0` | Management MII Bus | Management MII Bus |
| **5** | `0x20` | Internal | Reserved | Unused | Unused |
| **6** | `0x40` | Internal | Reserved | Unused | Unused |
| **7** | `0x80` | PON MAC | `pon0` -> `nas0` | Active WAN Port | Inactive / SerDes Idle |

## Key Findings
1. **Port 2 Isolation Guarantee [CONFIRMED]:** Port 2 (LAN3, hardware mask `0x04`) is physically and logically distinct from Port 3 (LAN4, hardware mask `0x08`). When WAN port mask `0x08` is engaged, Port 2 remains bridged in `br0`.
2. **SerDes Unchanged [CONFIRMED]:** Ethernet WAN operation on PHY Port 3 requires no modification to optical SerDes registers or PON calibration data.

