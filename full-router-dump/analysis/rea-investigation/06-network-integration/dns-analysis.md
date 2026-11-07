# DNS Propagation & Resolver Architecture

## Mechanism
1. **Dynamic Acquisition:** `default_options` includes `usepeerdns`. When negotiating IPCP, `pppd` receives Primary and Secondary DNS server IP addresses from the ISP BRAS.
2. **System Propagation:**
   - `/etc/ppp/ip-up` exports DNS environment variables (`$DNS1`, `$DNS2`).
   - `ccc_be` receives `EVENTNOTIFY 206` and writes DNS records to `/etc/resolv.conf`:
     ```
     nameserver <ISP_DNS_1>
     nameserver <ISP_DNS_2>
     ```
   - Local DNS caching forwarder (dnsmasq) reads `/etc/resolv.conf` and forwards local LAN DNS queries from clients on `br0` to the ISP servers.

