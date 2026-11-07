# Dependency Map & Execution Flow

## End-to-End Ethernet WAN & PPPoE Activation Map
The diagram below details how user configuration or link detection transitions through the firmware layers down to hardware port isolation and PPPoE daemon binding:

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Admin / CCC Script
    participant DAS as ccc_das
    participant BE as ccc_be
    participant BEM as libbemodules.so
    participant CCCBE as libcccbe.so
    participant RTK as Realtek HAL / Driver
    participant PPPD as /bin/pppd

    Admin->>DAS: Send CCC script (WANMode=ETHER, ADD WANPPPConnection)
    DAS->>BE: CMSG IPC Request (SET, ADD, SAVE)
    BE->>BEM: L3ConfigInit(instance=3)
    BEM->>CCCBE: libcccBeWan_getWANDeviceObjectRequestedLinkType(inst=3)
    Note over CCCBE: Queries OID 0xc7 (WANPPPConnectionNumberOfEntries).<br/>Returns 1 (LINK_TYPE_PPP)
    BEM->>BEM: constructL3WANDevName("nas0", VLAN=0) -> "nas0_notag"
    BEM->>CCCBE: setWanIpPppInterfaceName("nas0_notag", LinkType=1)
    CCCBE->>RTK: libcccBeWan_eth_Init()
    Note over RTK: PHY 3 enabled<br/>wan_port_mask = 0x08<br/>LAN3 (0x04) preserved in br0
    BEM->>BEM: beConfigWANByPPPoE(params)
    Note over BEM: Writes /etc/ppp/options_nas0_notag<br/>user, password, 3jglobal, mtu 1480
    BEM->>CCCBE: beWanEnablePPPv4Client("/bin/pppd", "nas0_notag")
    CCCBE->>PPPD: exec /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag
    Note over PPPD: Binds PPPoE discovery socket directly to nas0_notag
```

