# WAN Object Analysis & Schema Hierarchy

## Profile Container Mapping (`WANConnectionDevice.i`)

```
WANDevice.1
   │
   ├── X_5067F0_GponInterafceConfig (GPON Optical Control)
   ├── WANEthernetInterfaceConfig   (Ethernet Switch Port 3 Control, ifname: nas0)
   │
   ├── WANConnectionDevice.1        (Factory GPON Internet Profile)
   │     └── WANPPPConnection.1     (Active in default GPON mode)
   │
   ├── WANConnectionDevice.2        (Factory GPON TR069 Profile)
   │     └── WANIPConnection.1      (IP/DHCP management profile)
   │
   └── WANConnectionDevice.3        (Factory Ethernet Hardware Profile)
         ├── WANIPConnection.1      (Factory 'Eth_Internet' - Inactive/DHCP)
         └── WANPPPConnection.1     (Target Custom Unlock Profile - PPPoE)
```

## Multi-Instance Dynamic Instantiation
`config.rdm` explicitly defines both `WANIPConnection` and `WANPPPConnection` as valid children of `WANConnectionDevice` without instance index or medium restrictions. When `ADD WANPPPConnection` is delivered to `WANConnectionDevice.3`, the RDM manager allocates a new node and increments `WANPPPConnectionNumberOfEntries` from `0` to `1`.

