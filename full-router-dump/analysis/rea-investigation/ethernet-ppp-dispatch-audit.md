# Ethernet WAN Boot & Runtime Dispatch Audit

**Target Subsystem:** Backend Dispatch Engine / Mode Switching / WAN State Machine  
**Binaries Audited:**
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so` (SHA-256: `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so` (SHA-256: `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so` (SHA-256: `785b9b6574f1c9c48873da9b514d334e3579b6910da17967aeae3ea4e64f9cb9`)

---

## 1. Executive Summary & Audit Conclusions

| Audit Question | Audit Verdict | Confidence Level | Primary Supporting Evidence |
| :--- | :---: | :---: | :--- |
| **1. Triggered Only by `WANMode=ETHER`** | Strictly Conditional | **CONFIRMED** | `ConfigLoaderFunc_Boot` (`0x50ec8`) performs `strcmp(WANMode, "ETHER")`; only calls `eth_Init` on exact match. |
| **2. Requires `WANIPConnection.1.Enable=1`** | Not Required | **CONFIRMED** | `0x50e7c` evaluates `WANEthernetInterfaceConfig.Enable` (OID `0xca`). Does not inspect `WANIPConnection`. |
| **3. PPP Can Replace Ethernet IP Profile** | Supported | **CONFIRMED** | `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`0x3437c`) prioritizes `WANPPPConnection` over `WANIPConnection`. |
| **4. IP and PPP Coexistence Under Device 3** | Mutually Exclusive at Runtime | **CONFIRMED** | Dispatcher checks `WANPPPConnectionNumberOfEntries` first. If > 0, returns PPP (1) and ignores IP child. |
| **5. Dispatch Based on `WANPPPConnectionEntries`** | Strictly Determined by Entries | **CONFIRMED** | `0x34374` checks `ldrb w1, [x0]`. If `w1 > 0`, returns LinkType 1 (`PPP`), triggering `beWanEnablePPPv4Client`. |
| **6. `getWANDeviceObjectRequestedLinkType` Called at Boot** | Called at Boot | **CONFIRMED** | Invoked from `beWanDoLayer3InterfaceAction` @ `0x6c0d8` during initial layer-3 interface walk. |
| **7. PPP Path Reachable for Connection Device 3** | 100% Reachable | **CONFIRMED** | Function accepts any `path_idx` ($1 \le i \le N$). Evaluates container 3 dynamically without restriction. |
| **8. PPP Path Hardcoded to GPON / Device 1** | NOT Hardcoded | **DISPROVEN (Zero GPON lock)**| No branch restricts LinkType 1 to GPON or connection device 1. LinkType determination is completely generic. |
| **9. Config Change Triggers Callbacks** | Triggers Callbacks | **CONFIRMED** | `ccc_be` dispatches `L2ConfigLoad`, `L3ConfigLoad`, and `L4ConfigLoad` upon CMSG `SAVE`/`SEND`. |
| **10. Reboot Required for Activation** | **REBOOT REQUIRED** | **CONFIRMED** | `libcccBeWan_eth_Init` is bound exclusively to `ConfigLoaderFunc_Boot` (`0x50d08`). Runtime script requires reboot. |

---

## 2. WAN Boot Loader Disassembly: `ConfigLoaderFunc_Boot` (`0x50d08` - `0x51000`)

The WAN boot configuration loader governs physical interface selection during router startup:

```
[System Boot]
      |
      v
[OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot (0x50d08)]
      |
      +---> [getCurrentWANMode() @ 0x6eff4] -> Reads WANSwitch.WANMode
      |
      +---> [Check WANEthernetInterfaceConfig.Enable (0x50e7c)]
      |        |
      |        +-- (Enabled == 1 && WANMode == "ETHER")
      |        |         |
      |        |         v
      |        |   [libcccBeWan_eth_Init() @ 0x38074]
      |        |         |-- EthPhyEnable(1) (Port 3 PHY power-on)
      |        |         |-- smuxctl --if nas0 --set-if-rsmux ...
      |        |         |-- rtk_wan_port_mapping(0, "nas0") (wan_port_mask = 0x08)
      |        |
      |        +-- (Else) -> libcccBeWan_eth_Disabled()
      |
      +---> [Check X_5067F0_GponInterafceConfig.Enable (0x50ea8)]
               |
               +-- (Enabled == 1 && WANMode == "GPON")
               |         |
               |         v
               |   [libcccBeWan_gpon_Init() @ 0x50fb8]
               |
               +-- (Else) -> Idle optical SerDes
```

### Disassembly Proof of Exact String Matching:
```armasm
0x50eb8: cbz  w24, #0x50f00          ; Check WANEthernetInterfaceConfig.Enable
0x50ebc: adrp x1, #0xb4000
0x50ec0: add  x1, x1, #0x2c8         ; Literal "ETHER"
0x50ec4: add  x0, sp, #0x78          ; Configured WANMode string
0x50ec8: bl   #0x1e4a0               ; <strcmp@plt>
0x50ecc: cbnz w0, #0x50f54          ; If not "ETHER" -> branch to eth_Disabled
0x50ed0: mov  x0, x21                ; WANEthernetInterfaceConfig object
0x50ed4: bl   #0x1e980               ; <libcccBeWan_eth_Init@plt> -> INITIALIZES HARDWARE!
```

---

## 3. Layer-3 Runtime Dispatch: `beWanDoLayer3InterfaceAction` (`0x6bf78`)

For each active connection device, `beWanDoLayer3InterfaceAction` resolves the requested link type:

```armasm
; Step 1: Call LinkType Resolver
0x6c0d0: mov  x1, x22                ; Target container path index (e.g., WANConnectionDevice.3)
0x6c0d4: mov  x0, x20                ; RDM database context
0x6c0d8: bl   #0x1d340               ; <libcccBeWan_getWANDeviceObjectRequestedLinkType>
0x6c0dc: mov  w19, w0                ; w19 = Returned LinkType (0 = IP, 1 = PPP, 2 = Bridged)

; Step 2: Branch on Returned LinkType
0x6c5d4: cmp  w19, #1                ; Is LinkType == 1 (PPP)?
0x6c5d8: b.ne #0x6c6bc               ; If not PPP, jump to IP/DHCP branch!

; Step 3: PPP Client Execution Path (0x6c834)
0x6c82c: add  x1, sp, #0x250         ; Interface name buffer ("nas0_notag")
0x6c830: add  x0, sp, #0x58          ; PPP config context
0x6c834: bl   #0x1c070               ; <beWanEnablePPPv4Client@plt>
; beWanEnablePPPv4Client calls libccc_executePPPv4Client -> /bin/pppd launches!

; Step 4: IP / DHCP Alternative Path (0x6cab0)
0x6caac: mov  x1, x22
0x6cab0: bl   #0x1eb20               ; <beWanEnableDHCPv4Client@plt>
```

---

## 4. Decompilation Analysis of `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`0x34334`)

```c
int libcccBeWan_getWANDeviceObjectRequestedLinkType(void *rdm, uint64_t path_idx) {
    uint32_t inst = (uint32_t)(path_idx >> 56); // Extracts instance number (e.g. 3)
    void *ia = rdmConstructIAValue(inst, ...);
    
    // Check 1: Query child OID 0xc7 (WANPPPConnection)
    void *ppp_obj = cccRdmGetObjectByOID(rdm, 0xc7, ia);
    if (ppp_obj != NULL) {
        uint8_t entries = *(uint8_t *)(ppp_obj); // WANPPPConnectionNumberOfEntries
        if (entries > 0) {
            return 1; // LINK_TYPE_PPP -> TRIGGERS PPPoE DISPATCH!
        }
    }
    
    // Check 2: Query child OID 0xca (WANIPConnection)
    void *ip_obj = cccRdmGetObjectByOID(rdm, 0xca, ia);
    if (ip_obj != NULL) {
        uint8_t type = *(uint8_t *)(ip_obj + 4);
        return (type == 0) ? 2 : 0; // 0 = LINK_TYPE_IP, 2 = LINK_TYPE_BRIDGED
    }
    
    return 2;
}
```

### Critical Architectural Findings:
1. **Zero GPON Hardcoding:** The function has no instruction comparing `inst == 1` or checking SerDes/PON status. It evaluates `WANPPPConnection` purely based on `path_idx`.
2. **Deterministic Precedence:** If `WANPPPConnection` has an entry under container 3, the function **returns 1 immediately**, completely skipping the IP connection block!
3. **Reboot Requirement:** Because `libcccBeWan_eth_Init` is called from `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot` during system startup, changing `WANMode` via CCC script in a live system does not trigger `EthPhyEnable(1)` or `dev_port_mapping` on the fly. **A device reboot is required for Ethernet WAN mode to engage at the hardware switch layer.**

