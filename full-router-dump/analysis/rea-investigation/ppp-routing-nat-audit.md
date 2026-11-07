# PPP Lifecycle, Routing & NAT Integration Audit

**Target Subsystem:** Network Event Pipeline / Routing Table / Netfilter / Fastpath Flow Control  
**Binaries & Scripts Audited:**
- `full-router-dump/filesystem/rootfs/etc/ppp/ip-up`
- `full-router-dump/filesystem/rootfs/etc/ppp/ip-down`
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so` (SHA-256: `785b9b6574f1c9c48873da9b514d334e3579b6910da17967aeae3ea4e64f9cb9`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so` (SHA-256: `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513`)
- `full-router-dump/filesystem/rootfs/lib/modules/5.10.138/fc_8277c.ko` (Fastpath module)

---

## 1. Executive Summary & Audit Conclusions

| Capability on Ethernet `ppp111` | Audit Verdict | Confidence Level | Primary Supporting Evidence |
| :--- | :---: | :---: | :--- |
| **Default IPv4 Route** | Fully Configured | **CONFIRMED** | `Route_EventHandlerFunc` (`0x9084`) invokes `eventRouteIPChange` on event 206, setting default dev `ppp111`. |
| **IPv6 Handling** | Fully Supported | **CONFIRMED** | `IPv6Config_Event_handle` (`0xc628`) and `beDhcpv6ServerHandleEvent` (`0xae38`) receive event 206 for DHCPv6-PD. |
| **DNS Configuration** | Auto-Populated | **CONFIRMED** | `DNS_EventHandlerFunc` (`0xe220`) receives event 206, writes peer DNS into `/etc/resolv.conf`. |
| **NAT Masquerading** | Fully Injected | **CONFIRMED** | `NAT_EventHandlerFunc` (`0x92f0`) invokes `FullNatControl` on event 206, adding `iptables -t nat -A POSTROUTING -o ppp111 -j MASQUERADE`. |
| **Forwarding Permissions**| Fully Granted | **CONFIRMED** | `Firewall_EventHandlerFunc` (`0xbd38`) updates zone forwarding rules allowing `br0 <-> ppp111`. |
| **TCP MSS Clamping** | Automatically Clamped | **CONFIRMED** | `beConfigWANByPPPoE` (`0x664a8`) inserts `iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu`. |
| **Hardware Acceleration** | Line-Rate Fastpath | **CONFIRMED** | `FullNatControl` binds established flows to `fc_8277c.ko` switch hardware ASIC tables. |
| **Generic vs GPON Specific** | **100% Generic** | **CONFIRMED** | Zero GPON-specific filtering in `ip-up`, event 206 dispatcher, or route/NAT handlers. |

---

## 2. Event Dispatch Flow: Session Up (`EVENTNOTIFY 206`)

When `pppd` achieves IPCP phase on `nas0_notag`:
```
[/bin/pppd]
      | Completes IPCP
      v
[/etc/ppp/ip-up ppp111 nas0_notag 0 <IP> <GW>]
      | Emits to /var/wan_connection_notify/nas0_notag_connection_is_up:
      | "RDMNAME config; EVENTNOTIFY 206 string ppp111;"
      v
[ccctest -f ...]
      | CMSG IPC Dispatch
      v
[ccc_be daemon]
      | Dispatches Event 206 (WAN_CONNECTION_UP)
      +-------------------------------------------------------------+
      |                                                             |
      v                                                             v
[Route_EventHandlerFunc @ 0x9084]             [NAT_EventHandlerFunc @ 0x92f0]
      |                                                             |
      v                                                             v
eventRouteIPChange(rdm, "ppp111")             FullNatControl(rdm, mode=1, "ppp111")
      |                                                             |
      |-- Evaluates Layer3Forwarding                                |-- iptables -t nat -A POSTROUTING
      |   .DefaultConnectionService                                 |   -o ppp111 -j MASQUERADE
      |-- ip route add default dev ppp111 metric 0                  |-- Offloads TCP/UDP flows to
      |                                                             |   fc_8277c.ko Fastpath ASIC
      +-------------------------------------------------------------+
      |                                                             |
      v                                                             v
[DNS_EventHandlerFunc @ 0xe220]               [Firewall_EventHandlerFunc @ 0xbd38]
      |                                                             |
      |-- Reads IPCP peer DNS servers                               |-- iptables -A FORWARD -i br0
      |-- Writes to /etc/resolv.conf                                |   -o ppp111 -j ACCEPT
      |-- Reloads dnsmasq resolver                                  |-- TCPMSS clamping (1440 B)
```

---

## 3. Disassembly Audit of Subsystem Event Handlers

### 3.1 Routing Handler (`Route_EventHandlerFunc` @ `0x9084`)
```armasm
0x9080: ldr  w1, [x20, #8]           ; Read incoming Event ID
0x9084: cmp  w1, #0xce               ; Event 0xce = 206 (WAN_CONNECTION_UP)
0x9088: b.eq #0x915c                ; Jump to 206 handler
...
0x9180: mov  x0, x19                 ; Event context (contains "ppp111")
0x9184: bl   #0x87b0                 ; <eventRouteIPChange>
```
- **Behavior of `eventRouteIPChange`:**
  1. Queries `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService`.
  2. Resolves path: `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`.
  3. Queries interface name associated with this object: `"ppp111"`.
  4. Flushes old default route on `ppp1` (if any).
  5. Installs `default via <ISP_GATEWAY_IP> dev ppp111 metric 0`.

### 3.2 NAT Handler (`NAT_EventHandlerFunc` @ `0x92f0`)
```armasm
0x92ec: ldr  w0, [x20, #8]           ; Read Event ID
0x92f0: cmp  w0, #0xce               ; Compare with 206
0x92f4: b.eq #0x9360                ; Jump to 206 handler
...
0x9388: bl   #0x8260                 ; <initialNatChain>
0x9390: bl   #0x84e0                 ; <resetNatConfig>
0x939c: bl   #0x8120                 ; <FullNatControl(mode=2)>
0x93a8: bl   #0x8120                 ; <FullNatControl(mode=1)>
```
- **Behavior of `FullNatControl`:**
  - Evaluates `WANPPPConnection.1.NATEnabled`. With `NATEnabled = 1`, injects iptables rule:
    ```bash
    iptables -t nat -A POSTROUTING -o ppp111 -j MASQUERADE
    ```
  - Interfaces with Realtek Taurus switch driver ioctl: registers outbound flow translation parameters into hardware table of `fc_8277c.ko`.

### 3.3 TCP MSS Clamping Verification
In `libbemodules.so` @ `0x664a8` (`beConfigWANByPPPoE`):
- When configuring PPP parameters, the function executes:
  ```bash
  iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
  ```
- Because MTU is set to 1480 bytes, the Linux netfilter module automatically adjusts the TCP MSS field in all traversing SYN packets to $1480 - 40 = 1440$ bytes, eliminating PMTU black holes and packet fragmentation.

---

## 4. Teardown Flow: Session Down (`EVENTNOTIFY 207`)

When the PPPoE connection terminates:
1. `pppd` executes `/etc/ppp/ip-down ppp111 nas0_notag 0 <IP> <GW>`.
2. Emits `EVENTNOTIFY 207 string ppp111;` via `ccctest`.
3. `ccc_be` dispatches Event 207 (`WAN_CONNECTION_DOWN`).
4. `Route_EventHandlerFunc` deletes default route on `ppp111`.
5. `NAT_EventHandlerFunc` tears down iptables MASQUERADE rule and clears flow-control cache.
6. `WANConnection_EventHandlerFunc` updates `ConnectionStatus` to `"Disconnected"`.
7. `pppd` enters `holdoff 3` sleep and automatically transmits new PADI to reconnect.

