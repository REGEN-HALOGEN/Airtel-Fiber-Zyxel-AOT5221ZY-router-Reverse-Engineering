# PHY & Port Mapping Control Flow

## Analysis of Switch Configuration Logic
- **Primary Source:** `files/libcccbe.so`
- **Functions:**
  - `libcccBeWan_eth_Init` (Address: `0x38074`)
  - `rtk_wan_port_mapping` (Address: `0x37c84`)

---

## 1. Ethernet WAN Initialization Sequence (`libcccBeWan_eth_Init`)

When `ccc_be` activates the Ethernet WAN interface, it executes `libcccBeWan_eth_Init()`:

```armasm
; libcccbe.so @ 0x38074
0x38074: stp x29, x30, [sp, #-0x30]!
0x38078: mov x29, sp
0x3807c: mov w0, #1
0x38080: bl  #0x10b20            ; EthPhyEnable(1)
```

1. **PHY Power-Up:**
   Invokes `EthPhyEnable(1)` to power up and configure the PHY attached to Port 3.
2. **SMUX Multiplexer Configuration:**
   Executes configuration commands against `/bin/smuxctl`:
   ```bash
   /bin/smuxctl --if nas0 --set-if-rsmux --set-if-rx-policy DROP --set-if-tx-policy CONTINUE --set-if-rxmc-policy DROP --set-if-rx-multi 1
   echo switch_on > /proc/rtk_smuxdev/hw_vlan_filter
   echo enable nas0 MC > /proc/rtk_smuxdev/hw_vlan_filter
   echo refresh nas0 > /proc/rtk_smuxdev/hw_vlan_filter
   ```
3. **Port Mapping Execution:**
   Calls `rtk_wan_port_mapping(0, "nas0")` at `0x37c84`.

---

## 2. Port Mapping Implementation (`rtk_wan_port_mapping`)

Inside `rtk_wan_port_mapping`:
```bash
# Sets Port 3 as the physical port for logical netdevice nas0
echo 3 nas0 > /proc/ni/dev_port_mapping

# Sets hardware WAN port mask to 0x08 (Port 3 only)
echo 8 > /proc/fc/ctrl/wan_port_mask
```

### Impact on Routing and LAN Bridge
- Realtek Network Interface (`ni`) assigns physical switch Port 3 to netdevice `nas0`.
- Fastpath Flow Control (`fc`) engine isolates Port 3 traffic from local LAN ports.
- LAN1 (Port 0), LAN2 (Port 1), and LAN3 (Port 2) remain assigned to `br0`.

