# Network Daemon Interactions & Event Bus

## Daemon Interactions Matrix

| Initiator | Receiver | Transport | Event / Trigger | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| `ccc_das` | `ccc_be` | CMSG UNIX Socket | `REQUEST`, `SET`, `ADD`, `SAVE`, `SEND` | RDM transaction commit; triggers `L3ConfigInit`. |
| `ccc_be` | `pppd` | Process fork / `exec` | Interface Up Action | Spawns `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag`. |
| `pppd` | `/etc/ppp/ip-up` | Process fork | IPCP address acquired | Passes assigned IP, Gateway, and interface `ppp111`. |
| `/etc/ppp/ip-up` | `ccc_be` | `ccctest` / CMSG | `EVENTNOTIFY 206 string ppp111;` | Installs default route, updates DNS, applies NAT & MSS clamping. |
| `pppd` | `/etc/ppp/ip-down` | Process fork | Connection drop / PADT | Fires down notification. |
| `/etc/ppp/ip-down` | `ccc_be` | `ccctest` / CMSG | `EVENTNOTIFY 207 string ppp111;` | Flushes default route and clears NAT state. |

