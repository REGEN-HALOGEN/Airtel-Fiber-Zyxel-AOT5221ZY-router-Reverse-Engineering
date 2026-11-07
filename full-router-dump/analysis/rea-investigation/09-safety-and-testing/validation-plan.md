# Post-Activation Validation & Verification Plan

## 1. Step-by-Step Verification Checklist

Follow this systematic sequence to verify each layer of the network stack:

### Step 1: Physical Link & Hardware Port Mapping
- [ ] Connect external ONT to LAN4.
- [ ] Verify LAN4 green link LED is solid or blinking.
- [ ] Query switch port mapping:
  ```bash
  cat /proc/ni/dev_port_mapping
  # Expected output: 3 nas0
  cat /proc/fc/ctrl/wan_port_mask
  # Expected output: 8
  ```
- [ ] Verify LAN3 remains connected to `br0`:
  ```bash
  brctl show br0
  # Expected: eth2 (Port 2 / LAN3) is present in br0 port list.
  ```

### Step 2: PPPoE Session Handshake
- [ ] Verify `pppd` is running:
  ```bash
  ps | grep pppd
  # Expected: /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag
  ```
- [ ] Verify dynamic options file `/etc/ppp/options_nas0_notag`:
  ```bash
  cat /etc/ppp/options_nas0_notag
  # Expected: pppoe_srv_name 3jglobal, mtu 1480, mru 1480
  ```
- [ ] Check session interface creation:
  ```bash
  ip link show ppp111
  # Expected: ppp111 <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1480
  ```

### Step 3: IP Layer, Default Gateway & Routing
- [ ] Verify IPCP assigned address:
  ```bash
  ip addr show ppp111
  # Expected: inet <PUBLIC_OR_CGNAT_IP> peer <ISP_GATEWAY_IP>/32
  ```
- [ ] Verify default route:
  ```bash
  ip route show
  # Expected: default dev ppp111 metric 0
  ```

### Step 4: DNS Resolution & NAT Masquerade
- [ ] Verify peer DNS in `/etc/resolv.conf`:
  ```bash
  cat /etc/resolv.conf
  # Expected: nameserver <ISP_DNS_1>
  ```
- [ ] Verify iptables MASQUERADE:
  ```bash
  iptables -t nat -L POSTROUTING -v -n
  # Expected: MASQUERADE all -- * ppp111 0.0.0.0/0 0.0.0.0/0
  ```
- [ ] Verify TCP MSS clamping:
  ```bash
  iptables -L FORWARD -v -n
  # Expected: TCPMSS tcp flags:0x16/0x02 TCPMSS clamp to PMTU
  ```

### Step 5: End-to-End Connectivity Test
- [ ] Ping ISP gateway from router:
  ```bash
  ping -c 3 <ISP_GATEWAY_IP>
  ```
- [ ] Ping public IP (e.g., Google DNS `8.8.8.8`):
  ```bash
  ping -c 3 8.8.8.8
  ```
- [ ] Test DNS lookup:
  ```bash
  nslookup google.com
  ```
- [ ] Test client PC connected to LAN3 or Wi-Fi:
  - Check client internet access.
  - Run speedtest to verify Gigabit throughput and hardware NAT acceleration.

