# Routing Architecture & Default Gateway Management

## Routing Architecture
The router operates standard Linux kernel routing tables augmented by Realtek Fastpath Flow Control (`fc_8277c.ko`) hardware L3/L4 NAT offloading.

### Default Route Propagation Flow
```
[PPPoE Session (ppp111)]
            | IPCP Ack
            v
[/etc/ppp/ip-up]
            | EVENTNOTIFY 206
            v
[ccc_be daemon]
            | Evaluates DefaultConnectionService
            v
[Linux Routing Table]
            | ip route add default via <ISP_GW> dev ppp111
            v
[Realtek Fastpath NAT]
```

## Policy Routing & Metric Selection
- The default route is keyed to `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService`.
- When set to `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`, `ccc_be` binds the default route (`0.0.0.0/0`) with metric 0 to `ppp111`.
- If GPON was previously active, the previous default route on `ppp1` is flushed.

