import os

part15 = """

---

# PART 15 — STATIC PPPoE RDM INTEGRATION AUDIT (beConfigWANByPPPoE, createLayer3Interface, beWanEnablePPPv4Client, libccc_executePPPv4Client)

## 15.1 Audit Overview & Executive Findings
This audit conclusively establishes the exact, vendor-supported mechanism by which the stock MSTC/Zyxel firmware creates, configures, and activates PPPoE connections over physical Ethernet WAN (LAN4 / Port 3 / `nas0`).

- **Target Binaries**:
  - `libbemodules.so`: `beConfigWANByPPPoE` (`0x664a8`), `beWanEnablePPPv4Client` (`0x66ee4`), `constructL3WANDevName` (`0x698dc`), `createWANPPPConnectionCfgFile` (`0x6a7c0`), `beWanDoLayer3InterfaceAction` (`0x6bf78`).
  - `libcccbe.so`: `createLayer3Interface` (`0x35348`), `libccc_executePPPv4Client` (`0x348f4`), `setWanIpPppInterfaceName` (`0x346d0`), `libcccBeWan_getPPPPdUnitNum_wrapper` (`0x38264`).
- **Core Findings**:
  1. The stock firmware possesses complete, native code paths specifically designed to run PPPoE over Ethernet lower-layer interfaces (`nas0_notag` or `nas0_<vlan>`).
  2. The RDM schema for OID `0x32` (`WANConnectionDevice`) registers `WANPPPConnection` (OID `0xc7`) as a multi-instance child under any `WANConnectionDevice` instance, including `WANConnectionDevice.3`.
  3. RDM Instance Addressing maps `WANConnectionDevice.3.WANPPPConnection.1` (IA `1.3.1`) into PPP unit `131` and virtual netdevice `ppp131`.
  4. `beConfigWANByPPPoE()` copies `/etc/ppp/default_options` to `/etc/ppp/options_nas0_notag` and writes all ISP parameters (user, password, mtu, mru, echo, auth, service name).
  5. `createLayer3Interface()` creates `/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux --carrier MANUAL`, sets MTU to 1500, txqueuelen to 10, sets carrier on, and activates AUTO carrier detection.
  6. `libccc_executePPPv4Client()` queues `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`.
  7. On link establishment, `/etc/ppp/ip-up` notifies RDM via `EVENTNOTIFY 206 string ppp131;`, directing default route and NAT masquerade to `ppp131`.

---

## 15.2 Decompiled Pseudocode & Analysis of Core Functions

### 1. `beConfigWANByPPPoE` (`libbemodules.so:0x664a8`, size 1,712 bytes)
```c
int beConfigWANByPPPoE(struct WANPPPConnection *obj, uint64_t iaValue, const char *ifname)
{
    char options_file[256];
    char cmd[256];
    char unit_str[16];
    FILE *fp;
    const char *template_file;

    // 1. Build options filename: /etc/ppp/options_<ifname>
    snprintf(options_file, sizeof(options_file), "/etc/ppp/options_%s", ifname);

    // 2. Select base template file
    if (strcmp(obj->AddressingType /* +0x2c8 */, "Static") == 0 && obj->ExternalIPAddress[0] /* +0x92 */ != '\\0') {
        template_file = "/etc/ppp/_options_static";
    } else {
        template_file = "/etc/ppp/default_options";
    }

    // 3. Copy base template
    snprintf(cmd, sizeof(cmd), "cp -rf %s %s", template_file, options_file);
    cccBeDoSystem(cmd);

    // 4. Open options file
    fp = fopen(options_file, "a+");
    if (!fp) return -1;

    // 5. Static IP (if configured)
    if (strcmp(obj->AddressingType, "Static") == 0 && obj->ExternalIPAddress[0] != '\\0') {
        fprintf(fp, "%s:\\n", obj->ExternalIPAddress);
    }

    // 6. PPP unit number
    libcccBeWan_getPPPPdUnitNum_wrapper(iaValue, unit_str, 0);
    fprintf(fp, "unit %s\\n", unit_str);

    // 7. Credentials & logfile
    fprintf(fp, "user %s\\n", obj->Username /* +0x324 */);
    fprintf(fp, "password %s\\n", obj->Password /* +0x365 */);
    fprintf(fp, "logfile /tmp/%sLog\\n", obj->X_5067F0_InterfaceName /* +0x3e7 */);

    // 8. MTU / MRU & LCP Echo
    fprintf(fp, "mru %d\\n", obj->MaxMRUSize /* +0x18 */);
    fprintf(fp, "mtu %d\\n", obj->MaxMTUSize /* +0x1a */);
    fprintf(fp, "lcp-echo-interval %d\\n", obj->PPPLCPEcho /* +0x20 */);
    fprintf(fp, "lcp-echo-failure %d\\n", obj->PPPLCPEchoRetry /* +0x22 */);

    // 9. Authentication Protocol
    if (strcmp(obj->PPPAuthenticationProtocol /* +0x649 */, "PAP") == 0) {
        fwrite("refuse-chap\\n", 1, 12, fp);
        fwrite("refuse-mschap\\n", 1, 14, fp);
        fwrite("refuse-mschap-v2\\n", 1, 17, fp);
        fwrite("refuse-eap\\n", 1, 11, fp);
    } else if (strcmp(obj->PPPAuthenticationProtocol, "CHAP") == 0) {
        fwrite("refuse-pap\\n", 1, 11, fp);
        fwrite("refuse-mschap\\n", 1, 14, fp);
        fwrite("refuse-mschap-v2\\n", 1, 17, fp);
        fwrite("refuse-eap\\n", 1, 11, fp);
    } else if (strcmp(obj->PPPAuthenticationProtocol, "MS-CHAP") == 0) {
        fwrite("refuse-pap\\n", 1, 11, fp);
        fwrite("refuse-chap\\n", 1, 12, fp);
        fwrite("refuse-mschap-v2\\n", 1, 17, fp);
        fwrite("refuse-eap\\n", 1, 11, fp);
    } // "AUTO_AUTH" writes no refuse-* options, allowing auto negotiation

    // 10. Connection Trigger
    if (strcmp(obj->ConnectionTrigger /* +0x633 */, "OnDemand") == 0) {
        fwrite("demand\\n", 1, 7, fp);
        if (obj->IdleDisconnectTime != 0) fprintf(fp, "idle %u\\n", obj->IdleDisconnectTime);
        fwrite("ipv6cp-accept-local\\n", 1, 20, fp);
        fprintf(fp, "ipv6 ::%x:%x:%x:%x,::%x:%x:%x:%x\\n",
                random() & 0xffff, random() & 0xffff, random() & 0xffff, random() & 0xffff,
                random() & 0xffff, random() & 0xffff, random() & 0xffff, random() & 0xffff);
    } else if (strcmp(obj->ConnectionTrigger, "AlwaysOn") == 0) {
        if (obj->IPv6Enable /* +0x43 */ != 0) {
            fwrite("+ipv6\\n", 1, 6, fp);
            fwrite("ipv6cp-use-persistent\\n", 1, 22, fp);
            if (obj->IPVersion /* +0x42 */ == 2) fwrite("noip\\n", 1, 5, fp);
        }
        fwrite("persist\\n", 1, 8, fp);
        fwrite("passive\\n", 1, 8, fp);
    }

    // 11. PPPoE Service Name
    if (obj->PPPoEServiceName[0] /* +0x532 */ != '\\0') {
        fprintf(fp, "pppoe_srv_name %s\\n", obj->PPPoEServiceName);
    }

    // 12. Linkname
    fprintf(fp, "linkname %s\\n", obj->X_5067F0_InterfaceName /* +0x3e7 */);

    fclose(fp);
    return 0;
}
```

### 2. `createLayer3Interface` (`libcccbe.so:0x35348`, size 3,096 bytes)
```c
int createLayer3Interface(struct Layer3InterfaceContext *ctx)
{
    char cmd[1024];
    if (!ctx) return -1;

    if (ctx->link_type /* +0x4 */ == 1) { // LINK_TYPE_PPP
        if (!ctx->base_dev || !ctx->virtual_dev) return -1;

        // Create SMUX netdevice with MANUAL carrier
        snprintf(cmd, sizeof(cmd), "/bin/smuxctl --if-create-name %s %s --set-if-rsmux --carrier MANUAL",
                 ctx->base_dev /* nas0 */, ctx->virtual_dev /* nas0_notag */);
        cccBeDoSystem(cmd);

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
                     ctx->virtual_dev, ctx->vlan_id, ctx->virtual_dev);
            cccBeDoSystem(cmd);
            snprintf(cmd, sizeof(cmd),
                     "/bin/smuxctl --if %s --tx --push-tag --set-vid 0x%x 1 --set-priority %d 1 --target ACCEPT --rule-alias %s-tx-default --rule-append",
                     ctx->virtual_dev, ctx->vlan_id, ctx->vlan_priority, ctx->virtual_dev);
            cccBeDoSystem(cmd);
        }

        // Match GPON hardware info: returns 0 for Ethernet WAN (nas0)
        struct GponInfo gpon_info;
        memset(&gpon_info, 0, sizeof(gpon_info));
        if (getMatchedGPONInfo(ctx, &gpon_info) <= 0) {
            if (ctx->multicast_flag == 0) {
                // Assert carrier on SMUX device
                snprintf(cmd, sizeof(cmd), "echo \\\"carrier %s on\\\" > /proc/rtk_smuxdev/interface", ctx->virtual_dev);
                cccBeDoSystem(cmd);
                // Set SMUX carrier to AUTO
                snprintf(cmd, sizeof(cmd), "/bin/smuxctl --if %s --carrier AUTO", ctx->virtual_dev);
                cccBeDoSystem(cmd);
            }
        }
        return 0;
    }
    return 0;
}
```

### 3. `beWanEnablePPPv4Client` (`libbemodules.so:0x66ee4`) & `libccc_executePPPv4Client` (`libcccbe.so:0x348f4`)
```c
int beWanEnablePPPv4Client(void *ctx, const char *ifname)
{
    libccc_executePPPv4Client("/bin/pppd", ifname);
    beWanEnableAllMulti(ifname);
    return 0;
}

int libccc_executePPPv4Client(const char *binary, const char *ifname)
{
    char cmd[256];
    // Command template: /bin/pppd file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &
    snprintf(cmd, sizeof(cmd), "%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &",
             binary, ifname, ifname);
    cccBeSystemQueue("libccc_executePPPv4Client", cmd, 0);
    return 0;
}
```

---

## 15.3 TR-098 `WANPPPConnection` Struct Offset Map

| Offset (Hex) | Data Type | TR-098 Parameter | Firmware Function & Behavior |
|---|---|---|---|
| `+0x008` | `uint32` | `IdleDisconnectTime` | Appends `idle %u` when trigger is `OnDemand` |
| `+0x018` | `uint16` | `MaxMRUSize` | Appends `mru %d` to `/etc/ppp/options_<ifname>` |
| `+0x01a` | `uint16` | `MaxMTUSize` | Appends `mtu %d` to `/etc/ppp/options_<ifname>` |
| `+0x020` | `uint16` | `PPPLCPEcho` | Appends `lcp-echo-interval %d` |
| `+0x022` | `uint16` | `PPPLCPEchoRetry` | Appends `lcp-echo-failure %d` |
| `+0x02c` | `uint8` | `Enable` | Boolean 1=enabled, 0=disabled |
| `+0x042` | `uint8` | `IPVersion` / Mode | 1=IPv4, 2=IPv6, 3=DualStack |
| `+0x043` | `uint8` | `IPv6Enable` | Appends `+ipv6` and `ipv6cp-use-persistent` |
| `+0x092` | `char[64]` | `ExternalIPAddress` | Static IP written as `%s:\\n` if `AddressingType="Static"` |
| `+0x0c6` | `char[32]` | `Name` | Administrative interface alias (`"eth3_pppoe"`) |
| `+0x2c8` | `char[32]` | `AddressingType` | `"DHCP"` vs `"Static"` |
| `+0x324` | `char[64]` | `Username` | Appends `user %s` |
| `+0x365` | `char[64]` | `Password` | Appends `password %s` |
| `+0x3e7` | `char[32]` | `X_5067F0_InterfaceName` | Virtual PPP interface (`"ppp131"`), logfile `/tmp/%sLog`, linkname |
| `+0x532` | `char[64]` | `PPPoEServiceName` | Appends `pppoe_srv_name %s` if non-empty |
| `+0x633` | `char[32]` | `ConnectionTrigger` | `"AlwaysOn"` (`persist\npassive\n`) vs `"OnDemand"` |
| `+0x649` | `char[32]` | `PPPAuthenticationProtocol` | `"AUTO_AUTH"`, `"PAP"`, `"CHAP"`, `"MS-CHAP"` |
| `+0x898` | `char[32]` | `X_5067F0_IfName` | Lower-layer SMUX device (`"nas0_notag"`) |

---

## 15.4 Answers to the 8 Critical Investigation Questions

1. **Does `beConfigWANByPPPoE` support Ethernet PPP profiles?**
   - **YES**. Agnostic to GPON vs Ethernet; takes `ifname` as argument and generates `/etc/ppp/options_nas0_notag`.
2. **Does it require a PPP object under `WANConnectionDevice.1`, `.3`, or another parent?**
   - **Supports `WANConnectionDevice.3` natively**. The schema allows `WANPPPConnection` under any `WANConnectionDevice`. Unit derivation generates `ppp131` from IA `1.3.1`.
3. **Does it dynamically create PPP objects or only configure existing ones?**
   - Backend C code configures existing, enabled RDM objects; `ADD` in `ccctest` instantiates the object in the RDM database.
4. **Is the PPP object selected by an instance number, interface name, connection type, or another field?**
   - Selected in RDM by OID path and IAValue (`rdmConstructIAValue`), and in Layer 3 action dispatch by link type `LINK_TYPE_PPP` (1).
5. **Can the Ethernet profile `nas0_notag` be used without modifying the GPON PPP profile?**
   - **YES**. `WANConnectionDevice.1` (GPON / `ppp111`) and `WANConnectionDevice.3` (Ethernet / `ppp131`) are completely independent branches in RDM.
6. **Does the backend automatically configure default route and NAT for the new PPP connection?**
   - **YES**. On PPP establishment, `/etc/ppp/ip-up` triggers `EVENTNOTIFY 206 string ppp131;`, directing default route and iptables masquerade to `ppp131` via `Layer3Forwarding.DefaultConnectionService`.
7. **What parameters are required for service name, MTU/MRU, authentication, and VLAN?**
   - `PPPoEServiceName = "3jglobal"`, `MaxMRUSize = 1480`, `MaxMTUSize = 1480`, `PPPAuthenticationProtocol = "AUTO_AUTH"`, `ConnectionTrigger = "AlwaysOn"`, `Enable = 1`. Untagged Ethernet handoff uses default `nas0_notag` (`is_vlan = 0`).
8. **What is the exact supported backend operation for creating an Ethernet PPPoE connection?**
   - Using `ccctest`:
     ```sh
     ADD InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection;
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
     SET InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService = InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;
     SAVE;
     SEND;
     ```
"""

for fn in ['REVERSE_ENG.md', 'REVERSE ENG.md']:
    with open(fn, 'a', encoding='utf-8') as fp:
        fp.write(part15)
    print(f'Appended Part 15 to {fn}, new size: {os.path.getsize(fn)} bytes')

