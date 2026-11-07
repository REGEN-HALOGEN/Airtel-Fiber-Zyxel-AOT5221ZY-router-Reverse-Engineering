# NAT & Hardware Acceleration Analysis

## 1. Linux Netfilter NAT Masquerading
When `WANPPPConnection.1.NATEnabled` is set to `1`:
- `ccc_be` inserts the masquerade rule into iptables table `nat`:
  ```bash
  iptables -t nat -A POSTROUTING -o ppp111 -j MASQUERADE
  ```
- All outbound LAN client traffic from `br0` (`192.168.0.0/24`) is source-NATed to the dynamic public IP assigned to `ppp111`.

## 2. Realtek Fastpath Hardware NAT (`fc_8277c.ko` / `librtk.so`)
- Realtek Taurus features hardware flow table offloading.
- Established TCP and UDP streams are programmed into switch L3/L4 hardware forwarding tables via `librtk.so` ioctl.
- Packets bypass Linux kernel netfilter, achieving line-rate Gigabit throughput with near-zero CPU load.

