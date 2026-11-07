# STATIC AUDIT REPORT: ETHERNET PPPoE RDM INTEGRATION ARCHITECTURE

## Target Platform & Binaries
- **Device**: Airtel AOT5221ZY (Zyxel PX5311-R0)
- **SoC**: Realtek Taurus RTL9607C (AArch64, ARM Cortex-A53 quad-core)
- **OS**: Linux 5.10.138 (OpenWrt 22.03 LTS derivative, MSTC/Zyxel firmware architecture)
- **Audited Binaries**:
  - `/lib/MSTC/libbemodules.so` (SHA-256: `d9c02ff2e9b0b4119959cfcf91334ee464169542a13ee1cb6f39385312380d6f`)
  - `/lib/MSTC/libcccbe.so` (SHA-256: `90967da2011b2d075ebfcf9eb5ea0fc06e715cf4ef145fa4e67272782b3d16fc`)
  - `/usr/bin/ccc_be` (Backend Daemon)
  - `/bin/smuxctl` (Realtek SMUX Layer-2/3 control utility)
  - `/bin/pppd` (PPP Daemon v2.4.9 with `libpppoe.so` plugin)

---

## 1. Executive Summary

This static reverse-engineering audit conclusively establishes the exact, vendor-supported mechanism by which the stock MSTC/Zyxel firmware creates, configures, and activates PPPoE connections over physical Ethernet WAN (LAN4 / Port 3 / `nas0`).

Key conclusions:
1. **Full Firmware Support Confirmed**: The stock firmware contains an end-to-end, native code path specifically designed to operate PPPoE over Ethernet lower-layer interfaces (`nas0_notag` or `nas0_<vlan>`).
2. **Object Hierarchy**: PPPoE over Ethernet is represented in the RDM database under `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1`. The schema at OID `0x32` (`WANConnectionDevice`) natively supports both `WANIPConnection` (OID `0xca`) and `WANPPPConnection` (OID `0xc7`).
3. **Instance Addressing & Unit Mapping**: The firmware dynamically maps the TR-098 Instance Address (IAValue) into the PPP unit number and interface name using `libcccBeWan_getPPPPdUnitNum_wrapper()`:
   - GPON profile (`WANConnectionDevice.1.WANPPPConnection.1`): IA `1.1.1` $\to$ Unit `111` $\to$ `ppp111`.
   - Ethernet profile (`WANConnectionDevice.3.WANPPPConnection.1`): IA `1.3.1` $\to$ Unit `131` $\to$ `ppp131`.
4. **Options File Generation**: `beConfigWANByPPPoE()` copies `/etc/ppp/default_options` to `/etc/ppp/options_nas0_notag` and appends credentials, MTU/MRU, echo intervals, authentication filters, service name, and linkname.
5. **Layer-2/3 Setup**: `createLayer3Interface()` creates the untagged SMUX interface (`/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux --carrier MANUAL`), sets MTU to 1500, txqueuelen to 10, enables carrier (`carrier nas0_notag on` and `--carrier AUTO`), and brings the interface up.
6. **Execution**: `libccc_executePPPv4Client()` invokes:
   ```sh
   /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &
   ```
7. **Routing & NAT**: On link establishment, `/etc/ppp/ip-up` triggers RDM event 206 (`EVENTNOTIFY 206 string ppp131`), which updates IP parameters and directs default route and iptables masquerade to `ppp131`.

---

## 2. In-Depth Analysis of Requested Functions

### 2.1. `beConfigWANByPPPoE`
- **Location**: `libbemodules.so` @ `0x664a8` - `0x66b58` (1,712 bytes, 428 instructions)
- **Callers**:
  - `createWANPPPConnectionCfgFile()` (`libbemodules.so:0x6a8b8`)
- **Callees**:
  - `__snprintf_chk` (`0x1f1b0`), `strcmp` (`0x1e4a0`), `cccBeDoSystem` (`0x1c180`), `fopen` (`0x1d960`), `fclose` (`0x1e250`), `__fprintf_chk` (`0x1d6b0`), `fwrite` (`0x1ed70`), `random` (`0x1be50`), `libcccBeWan_getPPPPdUnitNum_wrapper` (`0x1e810`), `__syslog_chk` (`0x1cc50`).
- **Signature**:
  ```c
  int beConfigWANByPPPoE(struct WANPPPConnection *obj, uint64_t iaValue, const char *ifname);
  ```

#### Decompiled C Pseudocode:
```c
int beConfigWANByPPPoE(struct WANPPPConnection *obj, uint64_t iaValue, const char *ifname)
{
    char options_file[256];
    char cmd[256];
    char unit_str[16];
    FILE *fp;
    const char *template_file;

    // 1. Build destination options filename: /etc/ppp/options_<ifname>
    snprintf(options_file, sizeof(options_file), "/etc/ppp/options_%s", ifname);

    // 2. Select base template file
    if (strcmp(obj->AddressingType /* +0x2c8 */, "Static") == 0 && obj->ExternalIPAddress[0] /* +0x92 */ != '\0') {
        template_file = "/etc/ppp/_options_static";
    } else {
        template_file = "/etc/ppp/default_options";
    }

    // 3. Copy base template over to destination file
    snprintf(cmd, sizeof(cmd), "cp -rf %s %s", template_file, options_file);
    cccBeDoSystem(cmd);

    // 4. Open options file in append mode
    fp = fopen(options_file, "a+");
    if (!fp) {
        syslog(LOG_ERR, "%s@%d: fopen(%s) == NULL\n", "beConfigWANByPPPoE", 0x2b4, options_file);
        return -1;
    }

    // 5. Append static IP if applicable
    if (strcmp(obj->AddressingType, "Static") == 0 && obj->ExternalIPAddress[0] != '\0') {
        fprintf(fp, "%s:\n", obj->ExternalIPAddress);
    }

    // 6. Generate and append PPP unit number
    libcccBeWan_getPPPPdUnitNum_wrapper(iaValue, unit_str, 0);
    fprintf(fp, "unit %s\n", unit_str);

    // 7. Append authentication credentials and logfile
    fprintf(fp, "user %s\n", obj->Username /* +0x324 */);
    fprintf(fp, "password %s\n", obj->Password /* +0x365 */);
    fprintf(fp, "logfile /tmp/%sLog\n", obj->X_5067F0_InterfaceName /* +0x3e7 */);

    // 8. Append link framing parameters
    fprintf(fp, "mru %d\n", obj->MaxMRUSize /* +0x18 */);
    fprintf(fp, "mtu %d\n", obj->MaxMTUSize /* +0x1a */);
    fprintf(fp, "lcp-echo-interval %d\n", obj->PPPLCPEcho /* +0x20 */);
    fprintf(fp, "lcp-echo-failure %d\n", obj->PPPLCPEchoRetry /* +0x22 */);

    // 9. Append authentication protocol filters
    if (strcmp(obj->PPPAuthenticationProtocol /* +0x649 */, "PAP") == 0) {
        fwrite("refuse-chap\n", 1, 12, fp);
        fwrite("refuse-mschap\n", 1, 14, fp);
        fwrite("refuse-mschap-v2\n", 1, 17, fp);
        fwrite("refuse-eap\n", 1, 11, fp);
    } else if (strcmp(obj->PPPAuthenticationProtocol, "CHAP") == 0) {
        fwrite("refuse-pap\n", 1, 11, fp);
        fwrite("refuse-mschap\n", 1, 14, fp);
        fwrite("refuse-mschap-v2\n", 1, 17, fp);
        fwrite("refuse-eap\n", 1, 11, fp);
    } else if (strcmp(obj->PPPAuthenticationProtocol, "MS-CHAP") == 0) {
        fwrite("refuse-pap\n", 1, 11, fp);
        fwrite("refuse-chap\n", 1, 12, fp);
        fwrite("refuse-mschap-v2\n", 1, 17, fp);
        fwrite("refuse-eap\n", 1, 11, fp);
    } // "AUTO_AUTH" writes no refuse-* options, allowing auto negotiation

    // 10. Connection trigger & persistent link options
    if (strcmp(obj->ConnectionTrigger /* +0x633 */, "OnDemand") == 0) {
        fwrite("demand\n", 1, 7, fp);
        if (obj->IdleDisconnectTime /* +0x8 */ != 0) {
            fprintf(fp, "idle %u\n", obj->IdleDisconnectTime);
        }
        // IPv6 address generation for demand
        fwrite("ipv6cp-accept-local\n", 1, 20, fp);
        fprintf(fp, "ipv6 ::%x:%x:%x:%x,::%x:%x:%x:%x\n",
                random() & 0xffff, random() & 0xffff, random() & 0xffff, random() & 0xffff,
                random() & 0xffff, random() & 0xffff, random() & 0xffff, random() & 0xffff);
    } else if (strcmp(obj->ConnectionTrigger, "AlwaysOn") == 0) {
        if (obj->IPv6Enable /* +0x43 */ != 0) {
            fwrite("+ipv6\n", 1, 6, fp);
            fwrite("ipv6cp-use-persistent\n", 1, 22, fp);
            if (obj->IPVersion /* +0x42 */ == 2) { // IPv6 only
                fwrite("noip\n", 1, 5, fp);
            }
        }
        fwrite("persist\n", 1, 8, fp);
        fwrite("passive\n", 1, 8, fp);
    }

    // 11. PPPoE Service Name
    if (obj->PPPoEServiceName[0] /* +0x532 */ != '\0') {
        fprintf(fp, "pppoe_srv_name %s\n", obj->PPPoEServiceName);
    }

    // 12. Linkname (maps to /var/run/ppp-<linkname>.pid)
    fprintf(fp, "linkname %s\n", obj->X_5067F0_InterfaceName /* +0x3e7 */);

    fclose(fp);
    return 0;
}
```

---

### 2.2. `createLayer3Interface`
- **Location**: `libcccbe.so` @ `0x35348` - `0x35e84` (3,096 bytes, 774 instructions)
- **Callers**:
  - `beWanDoLayer3InterfaceAction()` (`libbemodules.so:0x6c710`)
- **Callees**:
  - `__sprintf_chk` (`0x195e0`), `__snprintf_chk` (`0x198a0`), `cccBeDoSystem` (`0x197d0`), `getMatchedGPONInfo` (`0x19b80`), `__syslog_chk` (`0x1a110`).
- **Signature**:
  ```c
  int createLayer3Interface(struct Layer3InterfaceContext *ctx);
  ```

#### Decompiled C Pseudocode:
```c
int createLayer3Interface(struct Layer3InterfaceContext *ctx)
{
    char cmd[1024];

    if (!ctx) {
        syslog(LOG_ERR, "%s@%d: input error!!\n", "createLayer3Interface", 0x2bb);
        return -1;
    }

    // Check link type: 0 = IP, 1 = PPP
    if (ctx->link_type /* +0x4 */ == 1) { // LINK_TYPE_PPP
        if (!ctx->base_dev /* +0x10 */ || !ctx->virtual_dev /* +0x28 */) {
            syslog(LOG_ERR, "%s@%d: input error!!\n", "createLayer3Interface", 0x30f);
            return -1;
        }

        // 1. Create SMUX netdevice with MANUAL carrier
        snprintf(cmd, sizeof(cmd), "/bin/smuxctl --if-create-name %s %s --set-if-rsmux --carrier MANUAL",
                 ctx->base_dev /* "nas0" */, ctx->virtual_dev /* "nas0_notag" */);
        cccBeDoSystem(cmd);

        // 2. Configure VLAN tags or untagged path
        if (ctx->is_vlan /* +0x18 */ == 0) {
            // Untagged: configure MTU and txqueuelen
            snprintf(cmd, sizeof(cmd), "ifconfig %s mtu 1500", ctx->virtual_dev);
            cccBeDoSystem(cmd);
            snprintf(cmd, sizeof(cmd), "ifconfig %s txqueuelen 10", ctx->virtual_dev);
            cccBeDoSystem(cmd);
        } else {
            // Tagged: append SMUX RX and TX tagging rules
            snprintf(cmd, sizeof(cmd),
                     "/bin/smuxctl --if %s --rx --tags 1 --filter-vid 0x%x 1 --pop-tag --rule-alias %s-rx-default --rule-append",
                     ctx->virtual_dev, ctx->vlan_id /* +0x20 */, ctx->virtual_dev);
            cccBeDoSystem(cmd);

            snprintf(cmd, sizeof(cmd),
                     "/bin/smuxctl --if %s --tx --push-tag --set-vid 0x%x 1 --set-priority %d 1 --target ACCEPT --rule-alias %s-tx-default --rule-append",
                     ctx->virtual_dev, ctx->vlan_id, ctx->vlan_priority /* +0x1c */, ctx->virtual_dev);
            cccBeDoSystem(cmd);
        }

        // 3. Match GPON hardware info
        struct GponInfo gpon_info;
        memset(&gpon_info, 0, sizeof(gpon_info));
        if (getMatchedGPONInfo(ctx, &gpon_info) <= 0) {
            // Non-GPON interface (Ethernet WAN on nas0)
            if (ctx->multicast_flag /* +0x24 */ == 0) {
                // Assert carrier on the SMUX device
                snprintf(cmd, sizeof(cmd), "echo \"carrier %s on\" > /proc/rtk_smuxdev/interface", ctx->virtual_dev);
                cccBeDoSystem(cmd);

                // Set SMUX carrier detection to AUTO
                snprintf(cmd, sizeof(cmd), "/bin/smuxctl --if %s --carrier AUTO", ctx->virtual_dev);
                cccBeDoSystem(cmd);
            }
        }
        return 0;
    }

    // Link type 0 (IP connection) handling ...
    return 0;
}
```

---

### 2.3. `beWanEnablePPPv4Client`
- **Location**: `libbemodules.so` @ `0x66ee4` - `0x66f18` (52 bytes, 13 instructions)
- **Callers**:
  - `beWanDoLayer3InterfaceAction()` (`libbemodules.so:0x6c834`)
- **Callees**:
  - `libccc_executePPPv4Client` (`libcccbe.so:0x348f4`)
  - `beWanEnableAllMulti` (`libbemodules.so:0x66418`)

#### Disassembly & Decompiled C Pseudocode:
```c
int beWanEnablePPPv4Client(void *ctx, const char *ifname)
{
    // Execute pppd with options file
    libccc_executePPPv4Client("/bin/pppd", ifname);

    // Enable multicast reception on interface
    beWanEnableAllMulti(ifname);

    return 0;
}
```

---

### 2.4. `libccc_executePPPv4Client`
- **Location**: `libcccbe.so` @ `0x348f4` - `0x3497c` (140 bytes, 35 instructions)
- **Callers**:
  - `beWanEnablePPPv4Client()` (`libbemodules.so:0x66efc`)
  - `beWanEnablePPPv6Client()` (`libbemodules.so:0x66f34`)
- **Callees**:
  - `__snprintf_chk` (`0x198a0`)
  - `cccBeSystemQueue` (`0x19ad0`)

#### Disassembly & Decompiled C Pseudocode:
```c
int libccc_executePPPv4Client(const char *binary, const char *ifname)
{
    char cmd[256];

    // Format: "/bin/pppd file /etc/ppp/options_<ifname> <ifname> > /tmp/pppd-info.tmp 2>&1 &"
    snprintf(cmd, sizeof(cmd), "%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &",
             binary, ifname, ifname);

    // Queue system command execution to backend worker thread
    cccBeSystemQueue("libccc_executePPPv4Client", cmd, 0);

    return 0;
}
```

---

## 3. RDM Object Memory Layout & Naming Resolution

Static analysis of `constructL3WANDevName()` (`libbemodules.so:0x698dc`), `setWanIpPppInterfaceName()` (`libcccbe.so:0x346d0`), and `libcccBeWan_getPPPPdUnitNum_wrapper()` (`libcccbe.so:0x38264`) reveals the exact memory structure and naming mechanics for TR-098 `WANPPPConnection`:

### 3.1. Structure Offset Map (`struct WANPPPConnection`)

| Offset (Hex) | Data Type | TR-098 Parameter Name | Usage in Firmware |
|---|---|---|---|
| `+0x008` | `uint32` | `IdleDisconnectTime` | Written to `idle %u` when trigger is `OnDemand` |
| `+0x018` | `uint16` | `MaxMRUSize` | Written to `mru %d` in options file |
| `+0x01a` | `uint16` | `MaxMTUSize` | Written to `mtu %d` in options file |
| `+0x020` | `uint16` | `PPPLCPEcho` | Written to `lcp-echo-interval %d` |
| `+0x022` | `uint16` | `PPPLCPEchoRetry` | Written to `lcp-echo-failure %d` |
| `+0x02c` | `uint8` | `Enable` | Boolean: 1 enables interface, 0 disables |
| `+0x042` | `uint8` | `IPVersion` / `AddressingType` | 1=IPv4, 2=IPv6, 3=DualStack |
| `+0x043` | `uint8` | `IPv6Enable` | Appends `+ipv6` and `ipv6cp-use-persistent` |
| `+0x092` | `char[64]` | `ExternalIPAddress` | Static IP address (when `AddressingType="Static"`) |
| `+0x0c6` | `char[32]` | `Name` | Administrative interface alias (e.g. `"eth3_pppoe"`) |
| `+0x2c8` | `char[32]` | `AddressingType` | `"DHCP"` vs `"Static"` |
| `+0x324` | `char[64]` | `Username` | Written to `user %s` |
| `+0x365` | `char[64]` | `Password` | Written to `password %s` |
| `+0x3e7` | `char[32]` | `X_5067F0_InterfaceName` | Virtual PPP interface name (e.g. `"ppp131"`) |
| `+0x532` | `char[64]` | `PPPoEServiceName` | Written to `pppoe_srv_name %s` |
| `+0x633` | `char[32]` | `ConnectionTrigger` | `"AlwaysOn"` (`persist\npassive`) vs `"OnDemand"` |
| `+0x649` | `char[32]` | `PPPAuthenticationProtocol` | `"AUTO_AUTH"`, `"PAP"`, `"CHAP"`, `"MS-CHAP"` |
| `+0x898` | `char[32]` | `X_5067F0_IfName` | Lower-layer SMUX device name (`"nas0_notag"`) |

### 3.2. Instance Address (IAValue) to Interface Name Mapping
The function `libcccBeWan_getPPPPdUnitNum_wrapper()` extracts 3 bytes from the 64-bit RDM Instance Address:
```c
uint8_t wan_dev = (iaValue >> 56) & 0xff;   // Byte 7: WANDevice instance (1)
uint8_t conn_dev = (iaValue >> 48) & 0xff;  // Byte 6: WANConnectionDevice instance (1 or 3)
uint8_t ppp_inst = (iaValue >> 40) & 0xff;  // Byte 5: WANPPPConnection instance (1)
snprintf(unit_str, sizeof(unit_str), "%d%d%d", wan_dev, conn_dev, ppp_inst);
```

- When configured under `WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1` (GPON):
  - `wan_dev = 1`, `conn_dev = 1`, `ppp_inst = 1` $\to$ Unit `"111"` $\to$ `ppp111`.
- When configured under `WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1` (Ethernet):
  - `wan_dev = 1`, `conn_dev = 3`, `ppp_inst = 1` $\to$ Unit `"131"` $\to$ `ppp131`.

Function `setWanIpPppInterfaceName()` then writes:
- `obj->X_5067F0_IfName` (`+0x898`) = `"nas0_notag"` (derived from base `"nas0"` + `"_notag"`).
- `obj->X_5067F0_InterfaceName` (`+0x3e7`) = `"ppp131"` (formatted as `"ppp%d"` with unit `131`).

---

## 4. Answers to the 8 Critical Questions

### Question 1: Does `beConfigWANByPPPoE` support Ethernet PPP profiles?
**Answer**: YES, 100% conclusively.
`beConfigWANByPPPoE` takes the underlying interface name as an explicit string argument (`const char *ifname`). It builds the options file `/etc/ppp/options_<ifname>` and populates standard PPP options. It contains zero GPON-specific hardware dependencies and operates identically whether called for a GPON interface (`veip0.1`) or an Ethernet SMUX interface (`nas0_notag`).

### Question 2: Does it require a PPP object under `WANConnectionDevice.1`, `.3`, or another parent?
**Answer**: It fully supports `WANConnectionDevice.3` (Ethernet WAN) as well as `WANConnectionDevice.1` (GPON).
The schema for OID `0x32` (`WANConnectionDevice`) registers `WANPPPConnection` (OID `0xc7`) as a valid multi-instance child object for all `WANConnectionDevice` containers.
The unit generator `libcccBeWan_getPPPPdUnitNum_wrapper()` dynamically maps `WANConnectionDevice.3` to PPP unit `131` and virtual interface `ppp131`.

### Question 3: Does it dynamically create PPP objects or only configure existing ones?
**Answer**: In the RDM database, the user/management engine dynamically creates the object using `ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection;`.
At the backend C level, `beConfigWANByPPPoE` and `createWANPPPConnectionCfgFile` do not create RDM nodes; they query existing, enabled RDM objects from the active database and configure the kernel network stack, SMUX devices, options files, and `pppd` daemons accordingly.

### Question 4: Is the PPP object selected by an instance number, interface name, connection type, or another field?
**Answer**: Selection occurs via:
1. In RDM / IPC: TR-098 OID path (`WANConnectionDevice.3.WANPPPConnection.1`) and 64-bit IAValue (`rdmConstructIAValue`).
2. In Layer-3 Action Dispatch: `libcccBeWan_getWANDeviceObjectRequestedLinkType()` checks if the object is `LINK_TYPE_PPP` (1).
3. The lower-layer SMUX device is resolved to `X_5067F0_IfName` (`"nas0_notag"`).
4. The virtual PPP interface is resolved to `X_5067F0_InterfaceName` (`"ppp131"`).

### Question 5: Can the Ethernet profile `nas0_notag` be used without modifying the GPON PPP profile?
**Answer**: YES.
`WANConnectionDevice.1` (GPON) and `WANConnectionDevice.3` (Ethernet) are completely independent branches in the RDM tree.
- `WANConnectionDevice.1.WANPPPConnection.1` retains its own options file (`/etc/ppp/options_veip0.1`) and unit (`ppp111`).
- `WANConnectionDevice.3.WANPPPConnection.1` creates its own independent options file (`/etc/ppp/options_nas0_notag`) and unit (`ppp131`).
The GPON profile does not need to be altered or deleted. To direct traffic out of Ethernet WAN, only `Layer3Forwarding.DefaultConnectionService` needs to point to `WANConnectionDevice.3.WANPPPConnection.1`.

### Question 6: Does the backend automatically configure default route and NAT for the new PPP connection?
**Answer**: YES.
1. Options file contains `plugin pppoe` and `noipdefault` (copied from `/etc/ppp/default_options`).
2. When PPPoE negotiation completes and IPCP establishes, `pppd` invokes `/etc/ppp/ip-up`.
3. `/etc/ppp/ip-up` generates `/var/wan_connection_notify/nas0_notag_connection_is_up` and invokes `ccctest` with `EVENTNOTIFY 206 string ppp131;`.
4. Event 206 in `ccc_be` reads assigned IP/Gateway/DNS, populates RDM, sets `ConnectionStatus = "Connected"`, installs the default route via `ppp131`, and adds iptables NAT masquerade rules for LAN egress.

### Question 7: What parameters are required for service name, MTU/MRU, authentication, and VLAN?
**Answer**:
- **Service Name**: Parameter `PPPoEServiceName` (string at offset `+0x532`). Value `"3jglobal"`. Written to options file as `pppoe_srv_name 3jglobal`.
- **MRU**: Parameter `MaxMRUSize` (uint16 at offset `+0x18`). Value `1480`. Written to options file as `mru 1480`.
- **MTU**: Parameter `MaxMTUSize` (uint16 at offset `+0x1a`). Value `1480`. Written to options file as `mtu 1480`.
- **Authentication**: Parameter `PPPAuthenticationProtocol` (string at offset `+0x649`). Value `"AUTO_AUTH"`. Skips all `refuse-*` lines, allowing automatic negotiation.
- **Username / Password**: Parameters `Username` (`+0x324`) and `Password` (`+0x365`).
- **Connection Trigger**: Parameter `ConnectionTrigger` (`+0x633`). Value `"AlwaysOn"`. Generates `persist` and `passive`.
- **VLAN**: If ISP handoff is untagged (native Ethernet), the default lower layer `nas0_notag` is used (`is_vlan = 0`). If ISP requires a VLAN (e.g. VLAN 100), setting `X_5067F0_VlanId = 100` instructs `createLayer3Interface()` to create `nas0_100` and append SMUX tag/pop rules.

### Question 8: What is the exact supported backend operation for creating an Ethernet PPPoE connection?
**Answer**: The exact, vendor-supported sequence using `ccctest` / RDM command stream is:
```sh
# 1. Instantiate the WANPPPConnection child object under Ethernet container WANConnectionDevice.3
ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection;

# 2. Configure connection parameters on the newly selected object
SET Enable = 1;
SET ConnectionType = IP_Routed;
SET Name = eth3_pppoe;
SET Username = <isp_username>;
SET Password = <isp_password>;
SET PPPoEServiceName = 3jglobal;
SET MaxMRUSize = 1480;
SET MaxMTUSize = 1480;
SET PPPAuthenticationProtocol = AUTO_AUTH;
SET ConnectionTrigger = AlwaysOn;
SET NATEnabled = 1;

# 3. Direct default gateway forwarding to the Ethernet PPP connection
SET InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService = InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

# 4. Save to persistent storage and send transaction commit to backend
SAVE;
SEND;
```

---

## 5. Verification Matrix

| Verification Item | Target Address / Symbol | Evidence Status | Firmware Mechanism |
|---|---|---|---|
| Options file generation | `libbemodules.so:0x664a8` (`beConfigWANByPPPoE`) | Verified | Formats `/etc/ppp/options_%s` using interface name argument |
| SMUX netdevice creation | `libcccbe.so:0x35348` (`createLayer3Interface`) | Verified | `/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux --carrier MANUAL` |
| SMUX carrier activation | `libcccbe.so:0x35de0` (`createLayer3Interface`) | Verified | `echo "carrier nas0_notag on" > /proc/rtk_smuxdev/interface` & `--carrier AUTO` |
| Interface MTU & txqueuelen | `libcccbe.so:0x35884` (`createLayer3Interface`) | Verified | `ifconfig nas0_notag mtu 1500`, `ifconfig nas0_notag txqueuelen 10` |
| pppd process launch | `libcccbe.so:0x348f4` (`libccc_executePPPv4Client`) | Verified | `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &` |
| PPP Unit derivation | `libcccbe.so:0x38264` (`libcccBeWan_getPPPPdUnitNum_wrapper`) | Verified | IA bits 56..40 $\to$ `"%d%d%d"` $\to$ Unit `131` $\to$ `ppp131` |
| Connection UP event | `/etc/ppp/ip-up` | Verified | Triggers `EVENTNOTIFY 206 string ppp131` via `ccctest` |
| Default route & NAT | `ccc_be` Event 206 Dispatch | Verified | Directs default route & NAT masquerade to `Layer3Forwarding.DefaultConnectionService` |

