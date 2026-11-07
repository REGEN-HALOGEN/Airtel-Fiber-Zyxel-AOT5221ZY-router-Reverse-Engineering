# Shared Library Inventory — Business Logic & Drivers

| Shared Library | Size (Bytes) | Symbols Present | Primary Exported & Internal Functions |
| :--- | :---: | :---: | :--- |
| `lib/MSTC/libbemodules.so` | 1,074,680 | Dynamic (`.dynsym`) | `constructL3WANDevName` (`0x698dc`), `beConfigWANByPPPoE` (`0x664a8`), `beWanDoLayer3InterfaceAction` (`0x6c780`), `beWanEnablePPPv4Client` (`0x66ee4`), `L3ConfigInit` (`0x4f440`). |
| `lib/MSTC/libcccbe.so` | 377,312 | Dynamic (`.dynsym`) | `libcccBeWan_eth_Init` (`0x38074`), `rtk_wan_port_mapping` (`0x37c84`), `setWanIpPppInterfaceName` (`0x346d0`), `libccc_executePPPv4Client` (`0x348f4`), `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`0x34334`). |
| `lib/librtk.so` | 2,204,184 | Full (`.symtab`) | Complete Realtek HAL: switch driver, VLAN filtering, L3/L4 hardware acceleration, port mapping. |
| `lib/MSTC/libcccrdm.so` | 446,208 | Dynamic (`.dynsym`) | `cccRdmGetObjectByOID`, `cccRdmGetObjListByOID`, `cccRdmSetParamValue`, `cccRdmSaveDatabase`. |
| `lib/MSTC/librdm.so` | 285,848 | Dynamic (`.dynsym`) | `rdmInit`, `rdmDeInit`, `rdmGetObjectByName`, `rdmGetParamValue`, `rdmSetParamValue`. |
| `lib/MSTC/libcmsg.so` | 55,664 | Dynamic (`.dynsym`) | `cmsgInit`, `cmsgCreateRequest`, `cmsgSendRecv`, `cmsgRequestSet`, `cmsgRequestSave`. |
| `lib/MSTC/libpppoe.so` | 35,864 | Dynamic (`.dynsym`) | Helper functions for PPPoE session parsing and options formatting. |

## Architectural Hierarchy
```mermaid
graph TD
    UI[Web CGI / CLI / linkdetection] -->|CMSG IPC| CCC[ccc_be daemon]
    CCC --> BEM[libbemodules.so - Business Logic]
    BEM --> CCCBE[libcccbe.so - Platform Integration]
    CCCBE --> RTK[librtk.so - Realtek HAL]
    CCCBE --> PPPD[/bin/pppd CLI / Exec]
    CCCBE --> SMUX[/bin/smuxctl CLI / Exec]
    BEM --> RDM[libcccrdm.so / librdm.so]
    RDM --> DB[(config.rdm Database)]
```

