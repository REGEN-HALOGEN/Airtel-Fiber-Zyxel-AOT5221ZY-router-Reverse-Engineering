# Unresolved Dependencies & Runtime Preconditions

## 1. Technical Dependencies

Before applying Option 3 (Clean CCC Orchestration) to the live router, the following runtime preconditions must be confirmed:

| Precondition | Description | Verification Method | Impact if Not Met |
| :--- | :--- | :--- | :--- |
| **CLI Access** | Access to `ccctest` or `ccc_das` via local SSH or serial console. | Test SSH login to `admin@192.168.0.2` with `-o HostKeyAlgorithms=+ssh-rsa`. | Cannot submit CCC configuration scripts without terminal shell. |
| **ISP VLAN Requirements** | Whether ISP 3jglobal requires 802.1Q tagged VLAN (e.g. VLAN 100, 10, or untagged) on the ONT Ethernet port. | Connect laptop directly to external ONT and test PPPoE dialer with/without VLAN. | If ISP requires tagged frames, `X_5067F0_Enable_VLANID` must be set to `1` and `X_5067F0_VLANID` set to ISP VID. |
| **ONT Bridge Configuration**| The external GPON ONT must be operating in pure Layer 2 Bridge mode. | Check ONT Web GUI / status. | If ONT is operating as a router/NAT gateway, double-NAT occurs and PPPoE discovery packets will not bridge. |
| **LAN4 Physical Integrity** | Cable between external ONT LAN port and router LAN4 must negotiate Gigabit (1000BASE-T). | Check port link LED and `cat /proc/ni/port_status`. | Degraded throughput if link negotiates at 100 Mbps or half-duplex. |

## 2. Firmware Dependencies (Resolved)
- All binary components (`pppd`, `libpppoe.so`, `libbemodules.so`, `ccc_be`) are proven present and functionally complete in the firmware rootfs.
- All kernel drivers (`ca-rtk.ko`, `ca-ne.ko`, `smuxdev.ko`, `fc_8277c.ko`) are loaded during normal boot.

