# In-Depth Analysis — `linkdetection` & Routine `0x402454`

## Target Metadata
- **Binary:** `files/linkdetection`
- **SHA-256:** `36d219bd3c86704721fe44ba5eb214dadb5ebcae9eed4b41f74e323ebf1a9f93`
- **Architecture:** AArch64 Little-Endian, 64-bit ELF (stripped)
- **Function Entry:** `0x402454`
- **Function Epilogue:** `0x40352c` - `0x403534`
- **Original Function Symbol:** `linkdetect_switch_WanMode` (recovered from debug string at `0x402584`)
- **Stack Allocation:** `0x360` bytes (864 bytes)

---

## 1. Function Boundaries & Calling Convention

### 1.1 Prologue
```armasm
0x402454: sub sp, sp, #0x360
0x402458: stp x29, x30, [sp]
0x40245c: mov x29, sp
0x402460: str x0, [sp, #0x18]       ; Save input argument 'mode_str'
```

### 1.2 Calling Convention & Parameters
- **Argument `x0`:** Pointer to C string indicating target WAN operating mode:
  - `"GPON"` (`0x4037b0`)
  - `"ETHER"` (`0x403868`)
  - `"DISABLE"` (`0x4038c0`)
- **Return Value `w0`:** Exit status loaded from `[sp, #0x354]` (`0` = Success, `1` = Error/Handled).

### 1.3 Epilogue
```armasm
0x403528: ldr w0, [sp, #0x354]       ; Load return value
0x40352c: ldp x29, x30, [sp]         ; Restore frame pointer and LR
0x403530: add sp, sp, #0x360         ; Tear down stack frame
0x403534: ret                        ; Return to caller
```

---

## 2. Complete Control Flow & Branching Analysis

`linkdetect_switch_WanMode` initializes RDM database access (`rdmInit("config.rdm", "config.xml")`) and connects to the CCC messaging framework via `cmsgInit("linkdetection_rtk")` and `cmsgGetModuleIdByName("ccc_das")`. It then executes three mutual-exclusion branches based on `strcmp`:

```
                 [linkdetect_switch_WanMode(x0)]
                                |
             +------------------+------------------+
             |                                     |
    strcmp(x0, "GPON") == 0               strcmp(x0, "ETHER") == 0
             |                                     |
    [GPON Reversion Path]                 [ETHER Transition Path]
             |                                     |
             |                            strcmp(x0, "DISABLE") == 0
             |                                     |
             +------------------+------------------+
                                |
                      [cmsgUnRegisterModule]
                          [rdmDeInit]
                            [ret]
```

---

## 3. The ETHER Branch (`0x402b1c` - `0x40342c`)

When `x0 == "ETHER"`, the function executes two consecutive CMSG request transactions to `ccc_be`:

### Phase 1: Verification & Creation of `WANIPConnection.1`
```armasm
0x402b24: add x2, x0, #0xb30        ; "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1"
0x402b30: bl  #0x401210             ; snprintf
0x402b44: bl  #0x401310             ; rdmGetObjectByName
```
If the IP connection object does not exist in RDM, it populates default fields:
- `Enable` = `1`
- `X_5067F0_InterfaceName` = `"nas0_notag"` (`0x402bc0`)
- `DefaultGateway` = `"0.0.0.0"`
- `X_5067F0_SERVICELIST` = `"TR069"` (`0x402c28`)
- `SubnetMask` = `"0.0.0.0"`
- `ExternalIPAddress` = `"0.0.0.0"`
- `Name` = `"Eth_Internet"` (`0x402cc4`)
- DNS instances: `.DNS.1`, `.DNS.2`, `.DNS.3`

### Phase 2: WAN Mode Mutation & ACS URL Clobbering
In the second transaction (`0x403000` - `0x4033e0`), it commits the following changes via CMSG IPC:
1. `InternetGatewayDevice.X_5067F0_Ext.WANSwitch.WANMode` = `"ETHER"` (`0x403008`)
2. `InternetGatewayDevice.X_5067F0_Ext.WANSwitch.WanAutoDetect` = `0`
3. `InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig.Enable` = `0`
4. `InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig.Enable` = `1`
5. `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.Enable` = `0` (Disables GPON PPPoE)
6. `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1.Enable` = `0`
7. `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1.Enable` = `1` (Enables IP/DHCP Profile)
8. `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService` = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1`
9. `InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService` = `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANIPConnection.1`

### 3.1 The ACS URL Side Effect [CONFIRMED]
At addresses `0x40332c` - `0x40338c`:
```armasm
0x40332c: add x2, x0, #0xcc8        ; "InternetGatewayDevice.ManagementServer"
0x403338: bl  #0x401210             ; snprintf
0x403358: bl  #0x401350             ; cmsgRequestSel
0x403364: add x2, x0, #0x18         ; "http://testacs.airtelbroadband.in:8103/"
0x403370: bl  #0x401210             ; snprintf
0x403384: add x1, x0, #0xd18        ; "URL"
0x40338c: bl  #0x401190             ; cmsgRequestSetNoBE
```
**Conclusion:** `linkdetection` unconditionally overwrites the router's ACS URL with Airtel's lab test URL (`http://testacs.airtelbroadband.in:8103/`).

---

## 4. Hardware Interaction & Polling Loop

Static analysis of the callers to `0x402454` revealed:
1. **PHY Port 3 Hardcoding:**
   Function `0x40223c` consists of two instructions:
   ```armasm
   0x40223c: mov w0, #3
   0x402240: ret
   ```
   This hardcodes PHY Port 3 (LAN4) as the Ethernet WAN port.
2. **PHY Link Polling (`0x402404`):**
   Calls `rt_port_link_get(3, &link_status)`. If link is UP (`1`), increments consecutive tick counter `[sp, #0x180]`.
3. **Transition Trigger:**
   When Port 3 link remains UP for 6 consecutive cycles (`cmp w0, #6` at `0x401ec0`), it automatically calls `linkdetect_switch_WanMode("ETHER")`.
4. **GPON Polling (`0x402244`):**
   Executes `diag pon get transceiver rx-power` via `popen`. If `"Rx Power: "` is found, calls `linkdetect_switch_WanMode("GPON")`.

---

## 5. Architectural Discovery: Disarming `linkdetection`

Analysis of `main` at `0x401a08` - `0x401ad8` revealed how `linkdetection` decides whether to run auto-switching:
```armasm
0x401a10: add x1, x0, #0x750        ; "InternetGatewayDevice.X_5067F0_Ext.WANSwitch"
0x401a18: bl  #0x401310             ; rdmGetObjectByName
0x401ac8: ldr x0, [sp, #0x168]
0x401acc: ldrb w0, [x0]             ; Offset 0x0 = WanAutoDetect boolean
0x401ad0: cmp w0, #1
0x401ad4: b.ne #0x401ae0            ; If not 1, do not enable auto-detect flag
...
0x401e0c: cmp w0, #1                ; Checks [sp, #0x184] (auto-detect flag)
0x401e10: b.ne #0x401b7c            ; SKIPS ALL AUTO-SWITCHING LOGIC!
```

**CRITICAL FINDING [CONFIRMED]:**
If `InternetGatewayDevice.X_5067F0_Ext.WANSwitch.WanAutoDetect` is configured to `0`:
1. `linkdetection` skips all mode transition logic.
2. It NEVER calls `linkdetect_switch_WanMode("ETHER")` or `linkdetect_switch_WanMode("GPON")`.
3. It NEVER mutates `DefaultConnectionService` to `WANIPConnection.1`.
4. It NEVER clobbers the ACS URL to `http://testacs.airtelbroadband.in:8103/`.
5. It safely coexists as a passive link-state monitor for front-panel LEDs (`isEthLinkStateChage`).

