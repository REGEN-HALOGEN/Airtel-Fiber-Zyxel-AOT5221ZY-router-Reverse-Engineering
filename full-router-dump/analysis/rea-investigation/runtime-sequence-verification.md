# Final Runtime-Sequence Verification — Ethernet PPPoE Lifecycle Audit

**Target System:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C SoC, Linux 5.10.138, AArch64)  
**Binary Artifacts Audited:**
- `full-router-dump/filesystem/rootfs/usr/bin/ccc_be` (CMSG transaction commit loop @ `0x411d38` - `0x411da8`, factory Ethernet WAN setup @ `0x414b54`, delete handler @ `0x4158f8`, module loader @ `0x411780`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbe.so` (`cccBeRegConfigObj` @ `0x1140`, `cccBeSystemQueue` @ `0x22dc`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so` (`beModuleInit_WAN` @ `0x434cc`, `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L0ConfigLoad` @ `0x50348`, `..._Boot` @ `0x50d08`, `..._L1ConfigLoad` @ `0x4f144`, `..._L3ObjectChanged` @ `0x4ddc4`, `checkWANDeviceObjectRequestedLinkIsUp` @ `0x67964`, `beWanDoLayer3InterfaceAction` @ `0x6bf78`, `beWanDisableClient` @ `0x6722c`, `layer3ForwardingHandleFunc` @ `0x397e4`, `beL2BrChangeDefaultWAN` @ `0x4cc58`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so` (`libcccBeWan_eth_Init` @ `0x38074`, `libcccBeWan_doWanModeChange` @ `0x36d3c`, `createLayer3Interface` @ `0x35348`, `libccc_executePPPv4Client` @ `0x348f4`, `libcccBeWan_getWANDeviceObjectRequestedLinkType` @ `0x34334`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so` (`pppoe_plugin_init` @ `0x2f98`, `setdevname_pppoe` @ `0x2c00`, `client_init_ses` @ `0x3408`, `get_sockaddr_ll` @ `0x4d10`, `session_connect` @ `0x551c`, `poe_fatal` @ `0x4958`, `poe_die` @ `0x48dc`)
- `full-router-dump/filesystem/rootfs/bin/pppd` (Option parsing & execution lifecycle)
- `full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so` (`cccRdmDelObjectByOID` @ `0x13890`, `cccRdmAddIndexChildObject` @ `0x134a0`)

---

## 1. Stage 1 Callback & Pre-Reboot Lifecycle

### 1.1 Synchronous Invocation Trace of `SEND` in `ccc_be`
When `ccctest` transmits the Stage 1 payload via `cmsgSendRecv(60000)`, `ccc_be` processes the transaction through `cmsgParseAction`:
1. **Mutation Phase (`0x411dc4` - `0x411e80`):**
   - Applies Opcode 1 (`SEL`), Opcode 7 (`ADD`), and Opcode 2 (`SET`).
   - Appends Opcode 6 (`SAVE`), invoking `rdmSave()` which persists the new RDM tree to flash (`/var/config.rdm`).
2. **Transaction Commit Phase (`0x411d38` - `0x411da8`):**
   ```armasm
   0x00411d38: ldr  x0, [x20, #0x70]     ; Fetch mutated event list handle
   0x00411d3c: ldr  w26, [x0, #4]        ; Number of changed objects
   0x00411d84: ldr  x0, [x20, #0x70]     ; Loop over mutated objects
   0x00411d90: ldr  w0, [x0, #8]         ; Fetch Event ID / OID
   0x00411d94: bl   #0x410b80            ; <cccBeGetEventById>
   0x00411d9c: ldr  x19, [x0, #0x18]     ; Registered callback chain
   0x00411d58: ldr  x2, [x19, #0x20]     ; Function pointer to callback
   0x00411d70: blr  x2                   ; Synchronously invoke backend apply callback!
   ```
   Committing `...WANConnectionDevice.3.WANPPPConnection` synchronously calls `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L3ObjectChanged` (`libbemodules.so` @ `0x4ddc4`).

### 1.2 Does Stage 1 Launch `pppd` Before Reboot? (No — Disproven by Disassembly)
Inspection of `L3ObjectChanged` reveals an immediate hardware gatekeeper:
```armasm
; Inside OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L3ObjectChanged:
0x0004def0: ldr  x0, [x0, #0xcf0]        ; Pointer to glb_status_tb (0xe6cf0)
0x0004def4: ldr  w2, [x0, #4]            ; Active WAN device index
0x0004def8: ldr  x1, [x19, #8]           ; Connection Device Instance (3)
0x0004defc: mov  x0, x20                 ; RDM handle
0x0004df00: bl   #0x1e5c0                ; <checkWANDeviceObjectRequestedLinkIsUp>
0x0004df04: cbz  w0, #0x4ee4c            ; IF LINK NOT UP -> BRANCH DIRECTLY TO RETURN!
```

Disassembly of `checkWANDeviceObjectRequestedLinkIsUp` (`libbemodules.so` @ `0x67964`):
```armasm
0x00067964: adrp x3, #0xe6000
0x00067968: ldr  x3, [x3, #0xcf0]        ; Load glb_status_tb
0x0006796c: ldrb w3, [x3]                ; Byte 0: Physical link status
0x00067970: cmp  w3, #1                  ; Is physical link up?
0x00067974: b.ne #0x679c0                ; If NOT UP -> return 0!
...
0x000679c0: mov  w3, #0
0x000679c4: mov  w0, w3                  ; Return false (0)
0x000679c8: ret
```
- **Finding:** Before reboot, the router is running in GPON mode. Physical switch port 3 is not initialized as an Ethernet WAN port, and `glb_status_tb[0]` is `0`.
- **Result:** `checkWANDeviceObjectRequestedLinkIsUp` returns `0`. `L3ObjectChanged` takes branch `cbz w0, #0x4ee4c` straight to function exit.
- **Conclusion:** `beWanDoLayer3InterfaceAction` is **NEVER** invoked prior to reboot. Consequently, `pppd` is **NOT** launched before reboot during Stage 1.

### 1.3 What Happens If `pppd` Were Forced Without `nas0_notag`?
To prove failure behavior unconditionally, we trace what happens if `libccc_executePPPv4Client` were executed while `nas0_notag` does not exist:
1. `libccc_executePPPv4Client` (`libcccbe.so` @ `0x348f4`) constructs:
   `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`
   via `__snprintf_chk` (`0x34954`) and enqueues it to `cccBeSystemQueue` (`0x3496c`).
2. `/bin/pppd` dynamically loads `libpppoe.so` and executes `client_init_ses` (`0x3408`):
   ```armasm
   0x000034c0: mov  x0, x23                 ; Device name string: "nas0_notag"
   0x000034c4: bl   #0x2750                 ; <get_sockaddr_ll@plt> (0x4d10)
   0x000034c8: mov  w20, w0                 ; Result of get_sockaddr_ll
   ```
3. In `get_sockaddr_ll` (`0x4d10`):
   ```armasm
   0x00004d44: mov  x0, x22                 ; struct ifreq
   0x00004d48: bl   #0x2820                 ; strncpy(ifr.ifr_name, "nas0_notag", 16)
   0x00004d54: mov  x1, #0x8933             ; SIOCGIFINDEX
   0x00004d58: ldr  w0, [x0]                ; Socket fd
   0x00004d5c: bl   #0x28a0                 ; <ioctl@plt>
   0x00004d60: tbz  w0, #0x1f, #0x4d98      ; If non-negative -> success
   0x00004d64: mov  w0, #0                  ; On ENODEV (-1) -> return 0 (failure)
   0x00004d74: ret
   ```
4. Back in `client_init_ses` (`0x3408`):
   ```armasm
   0x00003504: tbz  w20, #0x1f, #0x3518     ; Check get_sockaddr_ll status
   0x00003508: adrp x0, #0x6000
   0x00003510: add  x0, x0, #0xf6           ; "bad device name: %s"
   0x00003514: bl   #0x2500                 ; <error@plt>
   ...
   0x00003528: bl   #0x2530                 ; <bind@plt> fails (bind to PF_PACKET failed)
   ...
   0x00003560: bl   #0x2780                 ; <poe_fatal> (Failed to create PPPoE socket)
   ```
5. `poe_fatal` (`libpppoe.so` @ `0x4958`) prints the error to syslog and stderr, and calls `poe_die(1)` (`0x49c8`), which invokes `exit(1)`.
6. **Failure State & Retry Analysis:**
   - `pppd` terminates immediately with exit code 1.
   - Zero retry loops exist in `pppd` or `libpppoe.so` when the netdevice does not exist.
   - `pppd` imports only `rdmInit`, `rdmDeInit`, and `cccRdmGetObjectByOID` from RDM; it **never writes** to RDM.
   - No failure status (e.g., `ERROR_NO_CARRIER`) is recorded into `config.rdm`.
   - Error output is redirected to `/tmp/pppd-info.tmp`.

---

## 2. Boot Ordering & `nas0_notag` Creation

### 2.1 The Exact Boot Registration and Invocation Hierarchy
In `libbemodules.so`, module initialization `beModuleInit_WAN` (`0x434cc`) registers the WAN configuration descriptor `WAN_RegConfigStruct` (`0x115668`) via `cccBeRegConfigObj` (`libbe.so` @ `0x1140`).

During boot, `ccc_be` invokes the registered configuration loader `WANConfig_ConfigLoaderFunc` (`0x510bc`), which calls `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L0ConfigLoad` (`0x50348`).

Disassembly of `L0ConfigLoad` (`0x50348` - `0x50850`) reveals the strict linear boot sequence:
```armasm
; Step 1: Physical Layer 1 Config Load
0x00050494: bl   #0x1d230   ; <OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L1ConfigLoad>

; Step 2: Evaluate WAN Mode Transition
0x000505a8: bl   #0x1cf20   ; <libcccBeWan_doWanModeChange>

; Step 3: Layer 2 Connection Device Config Load
0x0005062c: bl   #0x1e690   ; <OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L2ConfigLoad>

; Step 4: Layer 3 Protocol Interface Config Load (PPP / IP)
0x00050694: bl   #0x1df00   ; <OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L3ConfigLoad>

; Step 5: Layer 4 Services Config Load (NAT / Routing)
0x000507e0: bl   #0x1cb70   ; <OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L4ConfigLoad>
```

### 2.2 Proof: `libcccBeWan_eth_Init()` Finishes Before Layer 3 Processes PPP
`libcccBeWan_eth_Init()` is called during Layer 1 hardware initialization by `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot` (`libbemodules.so` @ `0x50d08`):
```armasm
; In ConfigLoaderFunc_Boot:
0x00050d90: bl   #0x1e660   ; <getCurrentWANMode> -> returns "ETHER"
...
0x00050e6c: mov  w1, #0xca  ; OID 0xca = WANEthernetInterfaceConfig
0x00050e70: bl   #0x1de40   ; <cccRdmGetObjectByOID>
0x00050e7c: ldrb w0, [x0, #4]; Check Enable byte
...
0x00050ec8: bl   #0x1e4a0   ; strcmp(wan_mode, "ETHER")
0x00050ecc: cbnz w0, #0x50f54
0x00050ed0: mov  x0, x21    ; WANEthernetInterfaceConfig handle
0x00050ed4: bl   #0x1e980   ; <libcccBeWan_eth_Init> (libcccbe.so @ 0x38074)
```
Inside `libcccBeWan_eth_Init()` (`0x38074`):
1. `0x38090`: `bl <EthPhyEnable(1)>` — powers up physical port 3 (LAN4).
2. `0x38108`: `bl <cccBeDoSystem>` — runs:
   `/bin/smuxctl --if nas0 --set-if-rsmux --set-if-rx-policy DROP --set-if-tx-policy CONTINUE --set-if-rxmc-policy DROP --set-if-rx-multi 1`
3. `0x3813c`: `bl <cccBeDoSystem>` — runs `echo switch_on > /proc/rtk_smuxdev/hw_vlan_filter`.
4. `0x3816c`: `bl <cccBeDoSystem>` — runs `echo enable nas0 MC > /proc/rtk_smuxdev/hw_vlan_filter`.
5. `0x3819c`: `bl <cccBeDoSystem>` — runs `echo refresh nas0 > /proc/rtk_smuxdev/hw_vlan_filter`.
6. `0x381a8`: `bl <rtk_wan_port_mapping(0, "nas0")>` — maps hardware switch port 3 to netdevice `nas0`.

**Architectural Order:** Because `ConfigLoaderFunc_Boot` and `L1ConfigLoad` execute at the start of `L0ConfigLoad` (`0x50494`), `libcccBeWan_eth_Init()` completely finishes hardware initialization, PHY power-on, and switch port binding **before** `L0ConfigLoad` advances to `L3ConfigLoad` (`0x50694`).

### 2.3 Where and How `nas0_notag` Is Actually Created
Static disassembly disproves the common assumption that `rtk_wan_port_mapping` creates `nas0_notag`.
`rtk_wan_port_mapping(0, "nas0")` only configures the Taurus hardware switch ASIC to steer port 3 ingress/egress to the base driver `nas0`.

The netdevice `nas0_notag` is created dynamically by `createLayer3Interface` (`libcccbe.so` @ `0x35348`), called from `beWanDoLayer3InterfaceAction` (`libbemodules.so` @ `0x6c558`):
```armasm
; In createLayer3Interface (0x35348):
0x0003544c: ldr  x5, [x19, #0x10]       ; Base device: "nas0"
0x00035454: ldr  x6, [x19, #0x28]       ; Target virtual device: "nas0_notag"
0x00035470: adrp x3, #0x4b000
0x00035474: add  x3, x3, #0x88          ; Format: "%s --if-create-name %s %s --set-if-rsmux"
0x00035484: bl   #0x195e0               ; <__sprintf_chk>
; Command constructed: "/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux"
0x000354a0: bl   #0x197d0               ; <cccBeDoSystem> (creates nas0_notag in kernel!)
```
Once `createLayer3Interface` returns, `beWanDoLayer3InterfaceAction` proceeds to `0x6c834` (`beWanEnablePPPv4Client`), writing `/etc/ppp/options_nas0_notag` and launching `pppd`. `nas0_notag` is already live in `/proc/net/dev`.

---

## 3. Second-Stage Behavior (`DefaultConnectionService`)

### 3.1 Callback Trace for `Layer3Forwarding`
When Stage 2 executes:
```ini
SEL InternetGatewayDevice.Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;
SAVE;
SEND;
```
`ccc_be` commits the modification and invokes `layer3ForwardingHandleFunc` (`libbemodules.so` @ `0x397e4`):
```armasm
0x0003981c: mov  x1, x20                ; New DefaultConnectionService string
0x00039820: mov  x0, x19                ; RDM context
0x00039824: bl   #0x1bf50                ; <editDefaultGateway>
0x00039828: mov  w0, #0
0x00039834: ret
```
Simultaneously, `beL2BrChangeDefaultWAN` (`0x4cc58`) resolves the object name via `rdmGetObjectByName` (`0x4ccc4`), extracts the interface name (`ppp111`), and updates the internal default bridge routing table entry.

### 3.2 Does Changing `DefaultConnectionService` Restart PPP? (No)
- Neither `layer3ForwardingHandleFunc` nor `editDefaultGateway` nor `beL2BrChangeDefaultWAN` invokes `beWanDoLayer3InterfaceAction()` or `beWanDisableClient()`.
- Zero signals (`SIGTERM` / `SIGKILL`) are sent to `pppd`.
- `editDefaultGateway` executes purely routing operations: updating the kernel default route (`ip route replace default dev ppp111`) and default DNS forwarding in `dnsmasq`.
- **PPP Process State:** The `pppd` daemon continues running uninterrupted.

### 3.3 Can Stage 2 Safely Run After the First Reboot? (Yes — Recommended Flow)
Running Stage 2 **after** the first reboot is the optimal deployment strategy:
1. Stage 1 configures the hardware mode, adds the PPP object, and persists to flash.
2. The router is rebooted.
3. During boot, hardware port 3 powers up, `nas0` is mapped, `nas0_notag` is instantiated, and `pppd` establishes session `ppp111`.
4. The administrator verifies via SSH:
   - `cat /proc/net/dev | grep nas0` (both `nas0` and `nas0_notag` exist).
   - `ps | grep pppd` (`pppd` is active).
   - `ifconfig ppp111` (ISP IPv4 address assigned).
5. Stage 2 is dispatched: `DefaultConnectionService` updates the default route to `ppp111` with zero packet disruption and zero dangling route hazards.

---

## 4. Rollback Deletion Trace & GPON Restoration

### 4.1 Trace of the Native `DELETE` Operation
When rolling back, the script executes:
`DELETE InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;`

1. **`ccctest` Parsing (`0x402da8`):**
   Calls `cmsgRequestSel` with the full instance path, followed by `cmsgRequestSetIndexedObj(req, 0)` (Flag = 0: `DELETE`).
2. **`ccc_be` Server Handling (`0x4158f8`):**
   Calls `cccRdmDelObjectByOID` (`librdm.so` @ `0x13890`).
3. **`librdm.so` Deletion (`0x13890`):**
   ```armasm
   0x000138a4: bl   <cccRdmGetObjectByOID>
   0x000138b8: bl   <cccRdmSetPreObjStatus> (Status = 0: DELETED)
   ```
   Decrements `WANPPPConnectionNumberOfEntries` back from `1` to `0`, exactly restoring the factory baseline.
4. **Backend Apply on Deletion:**
   When the delete transaction commits, `beWanDoLayer3InterfaceAction` is called with `w23 = 0` (`action = STOP`):
   ```armasm
   0x0006c7d0: cbz  w23, #0x6c920           ; Action == STOP
   0x0006c230: bl   #0x1cf70                ; <beWanDisableClient>
   ```
   Inside `beWanDisableClient` (`libbemodules.so` @ `0x6722c`):
   - Queries `pppd` process ID via `popen` (`0x67340`).
   - Parses PID with `strtol` (`0x673ec`).
   - Executes through `cccBeDoSystem` (`0x67464`):
     `kill -15 <pid> > /dev/null 2>&1 && sleep 2 && kill -9 <pid> > /dev/null 2>&1 &`
   - Spawns `/bin/smuxctl --if-delete nas0_notag`, destroying the virtual SMUX netdevice.

### 4.2 Is a Second Reboot Required for Rollback? (Yes — Mandatory)
Returning to GPON mode requires:
1. Repointing `DefaultConnectionService` back to `...WANConnectionDevice.1.WANPPPConnection.1`.
2. Deleting `...WANConnectionDevice.3.WANPPPConnection.1`.
3. Enabling GPON interface (`X_5067F0_GponInterafceConfig.Enable = 1`).
4. Setting `WANSwitch.WANMode = "GPON"` and `WanAutoDetect = 1`.
5. Saving to `/var/config.rdm`.

**Why a second reboot is mandatory:**
- In `libcccbe.so` (`0x36d3c`), `libcccBeWan_doWanModeChange` detects `WANMode` changing from `"ETHER"` to `"GPON"` and triggers an immediate forced reboot (`write_omd_reboot_log` @ `0x36dc4`).
- Physical GPON initialization (`libcccBeWan_gpon_Init` @ `0x50fb8`) runs **strictly during system boot** (`ConfigLoaderFunc_Boot`).
- The Taurus switch port 3 cannot be unmapped from WAN mode back to LAN bridge mode without a full driver re-initialization during reboot.

---

## 5. Evidence Classification Ledger

| Item / Behavior | Verification Level | Exact Binary Address / Evidence Reference | Proven Fact vs Inference |
| :--- | :--- | :--- | :--- |
| **`ADD` Selection Context** | **Proven Static Fact** | `ccctest` @ `0x402cd8` (`cmsgRequestSel`) | Target object context remains active for all subsequent `SET` commands. |
| **Schema Default `Enable=0`** | **Proven Static Fact** | `librdm.so` @ `0x134a0`, template offset `0x3b761` | New instance created disabled; explicit `SET Enable boolean 1;` is mandatory. |
| **Pre-Reboot `pppd` Gate** | **Proven Static Fact** | `libbemodules.so` @ `0x4df00` (`checkWANDeviceObjectRequestedLinkIsUp`) | Physical link down blocks `beWanDoLayer3InterfaceAction`; `pppd` does not start before reboot. |
| **Missing Netdevice Exit** | **Proven Static Fact** | `libpppoe.so` @ `0x4d5c` (`SIOCGIFINDEX`), `0x3560` (`poe_fatal`) | `ioctl` fails -> `client_init_ses` calls `poe_die(1)`. No retry loop, no RDM corruption. |
| **Boot Call Sequence** | **Proven Static Fact** | `libbemodules.so` @ `0x50348` (`L0ConfigLoad`), `0x50494` -> `0x50694` | L1 (PHY/Switch mapping) strictly completes before L3 (PPP) processes. |
| **`nas0_notag` Creation Path** | **Proven Static Fact** | `libcccbe.so` @ `0x35470` (`createLayer3Interface`), `libbemodules.so` @ `0x6c558` | Instantiated via `/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux`. |
| **Stage 2 Routing Update** | **Proven Static Fact** | `libbemodules.so` @ `0x39824` (`editDefaultGateway`), `0x4cc58` (`beL2BrChangeDefaultWAN`) | Routing and bridge update only; does not restart `pppd`. |
| **Graceful PPP Termination** | **Proven Static Fact** | `libbemodules.so` @ `0x67434` (`beWanDisableClient`) | Formats `kill -15 %d ... sleep 2 ... kill -9 %d` on deletion. |
| **GPON Reboot Requirement** | **Proven Static Fact** | `libcccbe.so` @ `0x36dc0` (`libcccBeWan_doWanModeChange`), `0x50fb8` | Switching `WANMode` back to GPON requires reboot to initialize OMCI/SerDes. |
| **ISP VLAN Requirements** | **Runtime-Only Unknown** | Cannot be proven statically | ISP may require untagged traffic or specific 802.1Q VLAN (e.g., VLAN 100). |
| **Physical Optical Linkup** | **Runtime-Only Unknown** | Cannot be proven statically | Syrotech ONT Ethernet link negotiation with RTL9607C PHY port 3. |

---

## 6. Authoritative Multi-Stage Execution Timeline

```
================================================================================
                           STAGE 1: HARDWARE & PROFILE PROVISIONING
================================================================================
1. Dispatch stage1.cmd via ccctest:
   - WanAutoDetect=0, WANMode="ETHER"
   - WANEthernetInterfaceConfig.Enable=1
   - X_5067F0_GponInterafceConfig.Enable=0
   - Disable GPON Connection Devices 1 & 2
   - ADD WANPPPConnection under ConnectionDevice 3
   - SET Enable=1, Name="Eth_PPPoE", ConnectionType="IP_Routed", MTU/MRU=1480, Auth=AUTO_AUTH
   - SAVE; SEND;
2. ccc_be persists config to /var/config.rdm.
3. L3ObjectChanged evaluates checkWANDeviceObjectRequestedLinkIsUp (returns 0).
4. No pppd process launched yet. System state completely stable.

================================================================================
                                FIRST REBOOT
================================================================================
5. Operator issues `/sbin/reboot`.
6. Taurus SoC reboots into Linux 5.10.138.
7. ccc_be initializes and calls ConfigLoaderFunc_Boot (0x50d08):
   - EthPhyEnable(1) powers on LAN4 PHY.
   - smuxctl configures nas0.
   - rtk_wan_port_mapping(0, "nas0") binds switch port 3 to nas0.
8. L0ConfigLoad walks hierarchy to L3ConfigLoad (0x50694):
   - beWanDoLayer3InterfaceAction calls createLayer3Interface (0x35348).
   - smuxctl --if-create-name nas0 nas0_notag creates virtual interface.
   - beWanEnablePPPv4Client writes /etc/ppp/options_nas0_notag and spawns pppd.
9. pppd initializes via libpppoe.so:
   - get_sockaddr_ll finds nas0_notag.
   - PADI packet transmitted out LAN4 to Syrotech ONT.
   - PPPoE session establishes; kernel creates netdevice `ppp111`.

================================================================================
                        VERIFICATION & STAGE 2 ACTIVATION
================================================================================
10. Operator inspects live router via SSH:
    - Verify `ifconfig nas0_notag`
    - Verify `ifconfig ppp111` has valid ISP IP
    - Verify `ps | grep pppd`
11. Dispatch stage2.cmd via ccctest:
    - Layer3Forwarding.DefaultConnectionService = WANPPPConnection.1
    - X_5067F0_IPv6Layer3Forwarding.DefaultConnectionService = WANPPPConnection.1
    - SAVE; SEND;
12. layer3ForwardingHandleFunc invokes editDefaultGateway:
    - Default route 0.0.0.0/0 repointed to ppp111.
    - Router LAN clients now route internet traffic through Syrotech ONT.

================================================================================
                           DETERMINISTIC ROLLBACK FLOW
================================================================================
13. If rollback needed, dispatch rollback.cmd via ccctest:
    - Layer3Forwarding.DefaultConnectionService restored to GPON
    - DELETE ...WANConnectionDevice.3.WANPPPConnection.1;
    - GPON Connection Devices 1 & 2 Enable=1
    - X_5067F0_GponInterafceConfig.Enable=1
    - WANSwitch.WANMode="GPON", WanAutoDetect=1
    - SAVE; SEND;
14. ccc_be executes cccRdmDelObjectByOID:
    - beWanDisableClient sends SIGTERM (-15) then SIGKILL (-9) to pppd.
    - WANPPPConnectionNumberOfEntries decremented back to 0.
    - nas0_notag destroyed via smuxctl.
15. Operator executes `/sbin/reboot`:
    - Switch port 3 restored to internal LAN bridge.
    - GPON SerDes and OMCI stack re-initialized.
    - Router restored 100% to stock factory condition.
```

