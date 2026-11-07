# Ethernet WAN Activation Call Graph

## Complete Call Flow Diagram

```mermaid
graph TD
    subgraph Mode Control
        LD[linkdetection daemon]
        DAS[ccc_das CLI Agent]
    end

    subgraph Central Dispatcher
        BE[ccc_be daemon]
    end

    subgraph Business Logic - libbemodules.so
        L3Init[L3ConfigInit @ 0x4f440]
        BuildName[constructL3WANDevName @ 0x698dc]
        CfgPPP[beConfigWANByPPPoE @ 0x664a8]
        DoAction[beWanDoLayer3InterfaceAction @ 0x6c780]
        EnPPP[beWanEnablePPPv4Client @ 0x66ee4]
    end

    subgraph Platform Layer - libcccbe.so
        LinkType[libcccBeWan_getWANDeviceObjectRequestedLinkType @ 0x34334]
        SetName[setWanIpPppInterfaceName @ 0x346d0]
        EthInit[libcccBeWan_eth_Init @ 0x38074]
        PortMap[rtk_wan_port_mapping @ 0x37c84]
        ExecPPP[libccc_executePPPv4Client @ 0x348f4]
    end

    subgraph System Daemons & Kernel
        PPPD[/bin/pppd daemon]
        SMUX[/bin/smuxctl]
        SwitchProc[/proc/ni/dev_port_mapping & /proc/fc/ctrl/wan_port_mask]
    end

    DAS -->|CMSG IPC| BE
    LD -.->|CMSG IPC (When WanAutoDetect=1)| BE
    BE --> L3Init
    L3Init --> LinkType
    L3Init --> BuildName
    BuildName --> SetName
    L3Init --> EthInit
    EthInit --> PortMap
    EthInit --> SMUX
    PortMap --> SwitchProc
    L3Init --> CfgPPP
    L3Init --> DoAction
    DoAction --> EnPPP
    EnPPP --> ExecPPP
    ExecPPP --> PPPD
```

