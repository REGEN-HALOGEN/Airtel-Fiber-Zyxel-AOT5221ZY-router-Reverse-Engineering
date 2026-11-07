# Daemon Inventory — System & Network Processes

| Daemon | Binary Path | Supervision / Startup Method | IPC / Control Mechanism | Role in WAN Lifecycle |
| :--- | :--- | :--- | :--- | :--- |
| `ccc_be` | `/usr/bin/ccc_be` | `inittab` / init script | CMSG UNIX domain socket | Central configuration manager; executes WAN state transitions. |
| `linkdetection` | `/bin/linkdetection` | Background daemon / `inittab` | Polls Realtek PHY; sends CMSG | Monitors WAN physical cable insert/remove; triggers mode transitions. |
| `netifd` | `/sbin/netifd` | `procd` / init script | `ubus` / event socket | OpenWrt interface manager; handles interface up/down events. |
| `pppd` | `/bin/pppd` | Forked by `ccc_be` (`libccc_executePPPv4Client`) | CLI arguments, `/etc/ppp/options_*` | Runs PPPoE discovery, authentication, IPCP/IPV6CP negotiation. |
| `udhcpc` | `/sbin/udhcpc` | Forked by `ccc_be` (`beWanEnableDHCPClient`) | CLI arguments | DHCP client for IP WAN connections (e.g. `Eth_Internet`). |
| `ledctl_agent` | `/bin/ledctl_agent` | Init script | UNIX domain socket / CMSG | Controls front-panel RGB LEDs based on link status. |

