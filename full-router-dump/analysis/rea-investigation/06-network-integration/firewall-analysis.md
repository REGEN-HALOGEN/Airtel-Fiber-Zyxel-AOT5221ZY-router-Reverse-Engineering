# Firewall & TCP MSS Clamping Analysis

## 1. TCP MSS Clamping [NET-002]
Because PPPoE adds 8 bytes of encapsulation overhead to standard Ethernet frames, MTU is 1480 bytes. To prevent path MTU fragmentation issues on outbound TCP connections:
- In `libbemodules.so` @ `0x664a8`, the configuration generator inserts:
  ```bash
  iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
  ```
- This dynamically rewrites the Maximum Segment Size on all TCP SYN packets traversing the WAN.

## 2. Firewall Zones & Forwarding
- `br0` belongs to LAN zone (ACCEPT).
- `ppp111` is assigned to WAN zone (DROP unsolicited inbound, ACCEPT established/related).
- Forwarding rule:
  ```bash
  iptables -A FORWARD -i br0 -o ppp111 -j ACCEPT
  iptables -A FORWARD -i ppp111 -o br0 -m state --state RELATED,ESTABLISHED -j ACCEPT
  ```

