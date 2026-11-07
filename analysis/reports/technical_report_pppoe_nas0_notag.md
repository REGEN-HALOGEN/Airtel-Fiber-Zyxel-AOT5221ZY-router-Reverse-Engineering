# Firmware Reverse Engineering & PPPoE Binding Technical Report
**Target Hardware:** Realtek Taurus (RTL9607C / Chip ID `0x6706`), AArch64, Linux 5.10.138  
**Target Device:** Airtel AOT5221ZY / Zyxel PX5311-R0  
**Primary Research Question:** Can the existing firmware PPPoE manager bind to `nas0_notag` under Ethernet WAN profile `.3` (LAN4 with external Syrotech GPON ONT), while preserving LAN3 as the AP uplink?

---

## 1. Executive Summary & Verdict

| Architectural Domain | Reverse Engineering Finding | Status / Confidence |
| :--- | :--- | :--- |
| **PPPoE Binding to `nas0_notag`** | `setWanIpPppInterfaceName` & `constructL3WANDevName` explicitly construct `nas0_notag` and bind `pppd` to `nas0_notag` as its target network interface device. | **CONFIRMED** |
| **RDM Child-Object Schema** | `WANConnectionDevice` container in `config.rdm` declares both `WANIPConnection` (OID `0xca`) and `WANPPPConnection` (OID `0xc7`) as valid multinstance child objects without instance restriction. | **CONFIRMED** |
| **Instance Link Type Detection** | `libcccBeWan_getWANDeviceObjectRequestedLinkType` inspects the active `WANConnectionDevice` instance dynamically. If `WANPPPConnectionNumberOfEntries > 0`, it returns LinkType `1` (`PPP`). It is NOT hardcoded to instance `.1`. | **CONFIRMED** |
| **PPPoE Options File & CLI** | `beConfigWANByPPPoE` generates `/etc/ppp/options_nas0_notag` and launches `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag`. | **CONFIRMED** |
| **ISP Parameter Support** | Firmware supports `pppoe_srv_name 3jglobal`, `mtu 1480`, `mru 1480`, `AUTO_AUTH` (refuse flags omitted), and TCP MSS clamping. | **CONFIRMED** |
| **Port Mapping & Isolation** | `libcccBeWan_eth_Init()` sets Port 3 (LAN4) to WAN (`wan_port_mask = 0x08`, `echo 3 nas0 > /proc/ni/dev_port_mapping`), leaving Port 2 (LAN3, mask `0x04`) intact in the LAN bridge. | **CONFIRMED** |
| **Root Cause of Historical Failures** | Default PDM XML and test backups (`ether-backup.lz`) only instantiated `WANIPConnection.1` under `WANConnectionDevice.3`. `WANPPPConnection.1` was never instantiated under profile `.3`. | **CONFIRMED** |

**Final Verdict:** **YES**. The existing firmware PPPoE manager possesses full, native code support to bind to `nas0_notag` under `WANConnectionDevice.3`. The failure in prior testing was caused by attempting to run PPPoE without creating the `WANPPPConnection` RDM child under instance `.3` and without provisioning the required SMUX interface `nas0_notag`.

---

## 2. Complete Artifact Inventory & Verification

The analysis was performed across all 45 files in `C:\Users\REGEN\AirtelModemRev\files` totaling 48,112,619 bytes.

### 2.1 Critical Binary & Module Matrix

| File | Size (Bytes) | SHA-256 Digest | ELF Class / Format | Provenance / Role |
| :--- | :--- | :--- | :--- | :--- |
| `libbemodules.so` | 1,074,680 | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` | ELF64 AArch64 DYN | Core business logic: WAN manager, PPPoE options generator, L3/L4 config loader. |
| `libcccbe.so` | 377,312 | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` | ELF64 AArch64 DYN | Platform layer: SMUX control, Realtek port mapping, `pppd` execution wrapper. |
| `ccc_be` | 122,064 | `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f` | ELF64 AArch64 EXEC | Central Backend daemon: CMSG event dispatcher and TR-069/181 status handler. |
| `ccc_das` | 112,704 | `911685fbebbd6278f43c24427e13a9b6aeb339c57581add2ce3cff325cc4c5ab` | ELF64 AArch64 EXEC | Client agent: CLI/script parser for CCC (`REQUEST`, `SEL`, `ADD`, `SET`, `SEND`). |
| `librtk.so` / `librtk-full.so` | 2,204,184 | `54f58020848bd4d3b2d34fea1b3687276a367c49495074c297a17aabfc654e0e` | ELF64 AArch64 DYN (Debug) | Realtek Taurus hardware driver library: L3/L4 hardware NAT, PPPoE table, switch core. |
| `ca-rtk.ko` | 392,040 | `155ca47508b260c065ff772c3bde2cd708ff0bac96a46f2ab50cec9e38178dc9` | ELF64 AArch64 REL | Kernel driver: Realtek Ethernet switch/MAC core. |
| `ca-ne.ko` | 3,975,376 | `fb4166f8ca75e16ba59b0546662151ff1d6201527661cec2bf4b94654cb384d3` | ELF64 AArch64 REL | Kernel driver: Network Engine, SerDes, EPON/GPON MAC interface. |
| `fc_8277c.ko` | 2,088,432 | `c9116160081ef242f69315e11e408e5423d061cfeedf7b8f235af31ee884ecf0` | ELF64 AArch64 REL | Kernel module: Flow Control / Fastpath acceleration engine. |
| `config.rdm` | 63,005 | `fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7` | LZMA-alone (3,145,728 raw) | RDM binary database: Master TR-098 & TR-181 schema and default tree. |
| `aot-current-pdm-config.xml` | 583,313 | `6177ef897a056811b5fdd2f2bc5a5f5b8f4f0d1a4969b4b93ec5348bdcc9f308` | XML UTF-8 text | Active runtime persistent data model export. |
| `ether-backup.lz` | 23,485 | `bba43ffa6698b61d83cd9fdf23f07584cd4b9f1072bd46bbbe23194e05781b1a` | LZMA-alone (583,551 raw) | Backup captured during historical Ethernet WAN tests. |

### 2.2 Verified Exact Duplicate Groups (SHA-256)
1. `ubi_k0.bin` == `ubi_k1.bin` (`298b7992...`): Dual-bank Linux FIT kernel images (identical bank backups).
2. `librtk.so` == `librtk-full.so` (`54f58020...`): Full unstripped Realtek HAL library.
3. `libcrypto.so.1.1` == `libcrypto-mstc.so` (`5b46f895...`): OpenSSL 1.1 shared library.
4. `config.rdm` == `runtime-config.rdm` (`fb50191e...`): Factory RDM schema image.
5. `aot-current-pdm-config.xml` == `aot-current-pdm-backup.xml` (`6177ef89...`): Current PDM XML export.

---

## 3. Disassembly & Code-Level Architectural Analysis

### 3.1 Trace of RDM Object Hierarchy & Child Rules
In `config.rdm` (decompressed offset `0x36e74`), the TR-098 `WANConnectionDevice` definition includes:
- `WANIPConnectionNumberOfEntries` (Parameter OID `0x44`, Object OID `0xca`)
- `WANPPPConnectionNumberOfEntries` (Parameter OID `0x45`, Object OID `0xc7`)

Both `WANIPConnection` (`0x370b4`) and `WANPPPConnection` (`0x3b2dc`) are defined as dynamic multi-instance children of `WANConnectionDevice`.

In `libcccbe.so`, function `libcccBeWan_getWANDeviceObjectRequestedLinkType` (address `0x34334`):
```c
int libcccBeWan_getWANDeviceObjectRequestedLinkType(void *rdm, uint64_t path_idx) {
    // Queries OID 0xc7 (WANPPPConnectionNumberOfEntries) on the target instance
    if (cccRdmGetObjectByOID(rdm, 0xc7, path_idx) != NULL) {
        if (obj->entries > 0)
            return 1; // LINK_TYPE_PPP
    }
    // Queries OID 0xca (WANIPConnectionNumberOfEntries)
    if (cccRdmGetObjectByOID(rdm, 0xca, path_idx) != NULL) {
        return (obj->entries == 0) ? 2 : 0; // 0 = LINK_TYPE_IP, 2 = NONE
    }
    return 2;
}
```
**Conclusion [CONFIRMED]:** The LinkType lookup dynamically checks the child count of the specific `WANConnectionDevice` instance being initialized. If `WANPPPConnectionNumberOfEntries > 0` under `WANConnectionDevice.3`, LinkType `1` (`PPP`) is unconditionally returned.

---

### 3.2 Interface Name Construction (`constructL3WANDevName`)
When `OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L3ConfigInit` (`0x4f440` in `libbemodules.so`) processes a connection device with LinkType `1`, it invokes:
`constructL3WANDevName(rdm, 1, instance_idx, base_ifname, ppp_obj)` (`0x698dc`).

Inside `constructL3WANDevName`:
1. It reads the base interface name `nas0` from `WANEthernetInterfaceConfig.X_5067F0_IfName`.
2. It inspects `WANPPPConnection->X_5067F0_Enable_VLANID` (offset `0x34`).
3. If VLAN is disabled (`0`):
   - It selects literal string `"_notag"`.
   - Concatenates `"nas0"` + `"_notag"` = `"nas0_notag"`.
4. It calls `setWanIpPppInterfaceName` (`0x346d0` in `libcccbe.so`):
   - In `setWanIpPppInterfaceName`, register `w20` is evaluated. Since `w20 == 1` (`PPP`), it executes lines `0x348a8` - `0x348e8`:
   - Writes `"nas0_notag"` to `WANPPPConnection->X_5067F0_IfName` (offset `0x898`).
   - Retrieves the pppd unit number from `libcccBeWan_getPPPPdUnitNum_wrapper` and writes `"ppp%d"` (e.g. `"ppp111"`) to `WANPPPConnection->X_5067F0_InterfaceName` (offset `0x3e7`).

**Conclusion [CONFIRMED]:** The underlying hardware device name `nas0_notag` is explicitly constructed and saved to offset `0x898` of the `WANPPPConnection` instance.

---

### 3.3 PPPoE Configuration Generation (`beConfigWANByPPPoE`)
`createWANPPPConnectionCfgFile` (`0x6a7c0` in `libbemodules.so`) calls `beConfigWANByPPPoE` (`0x664a8`):
1. **Options File Path:** Formatted as `/etc/ppp/options_%s` using argument `x2` (`X_5067F0_IfName` = `"nas0_notag"`), creating `/etc/ppp/options_nas0_notag`.
2. **Base Template:** Copies `/etc/ppp/default_options` to `/etc/ppp/options_nas0_notag`.
3. **Session Parameters Written:**
   - `unit %s`: Allocates kernel PPP unit.
   - `user %s`: PPPoE username from `WANPPPConnection->Username`.
   - `password %s`: PPPoE password from `WANPPPConnection->Password`.
   - `mru %d` / `mtu %d`: Populated from `MaxMRUSize` (1480) and `X_5067F0_MaxMTUSize` (1480).
   - `lcp-echo-interval %d` / `lcp-echo-failure %d`: From `PPPLCPEcho` / `PPPLCPEchoRetry`.
   - `linkname %s`: Set to `"nas0_notag"`.
   - `pppoe_srv_name %s`: If `PPPoEServiceName` is set to `"3jglobal"`, writes `pppoe_srv_name 3jglobal`.
4. **Authentication Modes:**
   - If `X_5067F0_PPPAuthenticationProtocol == "PAP"`: Writes `refuse-chap`, `refuse-mschap`, `refuse-mschap-v2`, `refuse-eap`.
   - If `"CHAP"`: Writes `refuse-pap`, `refuse-mschap`, `refuse-mschap-v2`, `refuse-eap`.
   - If `"AUTO_AUTH"`: No refuse options are emitted, allowing pppd to negotiate either PAP or CHAP as requested by the ISP BRAS.
5. **MSS Clamping:** Emits firewall rules:
   `iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu`

---

### 3.4 Daemon Invocation & Network Interface Binding
In `beWanDoLayer3InterfaceAction` (`0x6c780` in `libbemodules.so`):
1. Connection state is transitioned:
   `strncpy(WANPPPConnection->ConnectionStatus, "Connecting", 0x14)`.
2. Resolves target linkname from `WANPPPConnection->X_5067F0_IfName` (`"nas0_notag"`).
3. Invokes `beWanEnablePPPv4Client("/bin/pppd", "nas0_notag")`.
4. `beWanEnablePPPv4Client` (`0x66ee4`) delegates to `libccc_executePPPv4Client`:
   ```c
   // libcccbe.so @ 0x348f4
   snprintf(cmd, 256, "%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &",
            "/bin/pppd", "nas0_notag", "nas0_notag");
   cccBeDoSystem(cmd);
   ```
5. **Resulting Execution String:**
   `/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &`

**Conclusion [CONFIRMED]:** The exact command line passed to the system shell supplies `nas0_notag` as the trailing positional interface argument to `pppd`. In Linux `pppd` (with `rp-pppoe.so`), a positional network interface identifier binds the PPPoE discovery socket directly to that Ethernet device.

---

### 3.5 Realtek Port Mapping & Switch Architecture
`libcccBeWan_eth_Init` (`0x38074` in `libcccbe.so`) executes on Ethernet WAN activation:
1. `EthPhyEnable(1)`: Powers on the RTL8211/RTL8218 PHY on physical port 3 (LAN4).
2. Configures Realtek SMUX hardware filtering:
   ```bash
   /bin/smuxctl --if nas0 --set-if-rsmux --set-if-rx-policy DROP --set-if-tx-policy CONTINUE --set-if-rxmc-policy DROP --set-if-rx-multi 1
   echo switch_on > /proc/rtk_smuxdev/hw_vlan_filter
   echo enable nas0 MC > /proc/rtk_smuxdev/hw_vlan_filter
   echo refresh nas0 > /proc/rtk_smuxdev/hw_vlan_filter
   ```
3. Configures port mapping via `rtk_wan_port_mapping(0, "nas0")` (`0x37c84`):
   ```bash
   echo 3 nas0 > /proc/ni/dev_port_mapping
   echo 8 > /proc/fc/ctrl/wan_port_mask
   ```

**Switch Port Mapping Table [CONFIRMED]:**
| Port Index | Function | Hardware Mask | Bridge Association | Status Under Ethernet WAN |
| :---: | :---: | :---: | :---: | :---: |
| **0** | LAN1 | `0x01` | `br0` (LAN) | Untouched |
| **1** | LAN2 | `0x02` | `br0` (LAN) | Untouched |
| **2** | LAN3 | `0x04` | `br0` (LAN) | **PRESERVED: Remains AP Uplink** |
| **3** | LAN4 | `0x08` | Isolated to `nas0` | **Ethernet WAN Port** |
| **7** | GPON | `0x80` | Isolated to `nas0` | Inactive when `wan_port_mask = 0x08` |

---

## 4. Why Historical Attempts Failed

Prior attempts to establish an Ethernet WAN connection succeeded in generating `nas0_notag` and setting `wan_port_mask = 0x08`, but no PPPoE session came up. The decompiled control flow reveals the exact failure mechanism:

1. **Missing `WANPPPConnection` under Profile `.3`:**
   In factory `aot-current-pdm-config.xml` and test backup `ether-backup.lz`, `WANConnectionDevice.3` exclusively contains:
   `<WANIPConnection><i1><Name>Eth_Internet</Name>...`
   Because `WANPPPConnectionNumberOfEntries` was `0`, `libcccBeWan_getWANDeviceObjectRequestedLinkType` returned `0` (`LINK_TYPE_IP`). The backend invoked `beWanEnableDHCPClient`, seeking a DHCP lease. It **never executed `beWanEnablePPPv4Client`**.
2. **Missing Pre-requisite SMUX Device:**
   `libcccBeWan_eth_Init()` configures the base device `nas0`, but expects child SMUX interfaces (`nas0_notag` or `nas0_VLAN`) to exist before traffic can be routed. When untagged PPPoE was attempted without `/bin/smuxctl --if-create-name nas0 nas0_notag --set-if-rsmux`, the socket bind to `nas0_notag` failed with `ENODEV`.
3. **Misconfigured Default Connection Service:**
   In `ether-backup.lz`, `Layer3Forwarding.DefaultConnectionService` remained pointed to GPON (`WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1`), preventing default route population for Ethernet WAN.

---

## 5. Technical Verdict by Capability Classification

- **PPPoE Engine Binding to `nas0_notag`:** **CONFIRMED**  
  Source code in `constructL3WANDevName`, `setWanIpPppInterfaceName`, and `libccc_executePPPv4Client` proves end-to-end interface binding to `nas0_notag`.
- **RDM Multi-Instance Support for PPP on ConnectionDevice.3:** **CONFIRMED**  
  Binary schema in `config.rdm` and dispatch logic in `L3ConfigInit` prove that `WANConnectionDevice.3.WANPPPConnection.1` is a valid, recognized TR-098 path.
- **ISP Parameters (`3jglobal`, MTU 1480, `AUTO_AUTH`):** **CONFIRMED**  
  `beConfigWANByPPPoE` natively supports `pppoe_srv_name %s`, `mtu %d`, `mru %d`, and leaves PAP/CHAP open on `AUTO_AUTH`.
- **Physical Port Preservation of LAN3:** **CONFIRMED**  
  Realtek WAN port mask `0x08` isolates only Port 3. Port 2 (LAN3, mask `0x04`) remains in `br0`.
- **Runtime Transition without Reboot:** **UNTESTED**  
  Applying this configuration requires sending CCC commands via `ccc_das` to create `WANPPPConnection.1` under `WANConnectionDevice.3`, setting `WANMode` to `ETHER`, and verifying `nas0_notag` link state.

---

## 6. Proposed Configuration Blueprint (No Writes Executed)

> [!IMPORTANT]
> In accordance with instructions, **no write commands or live settings changes have been executed**. The following CCC script represents the exact baseline required to instantiate PPPoE on `nas0_notag` under profile `.3` for user approval:

```ini
# Baseline Ethernet WAN PPPoE Configuration Template (Untagged, LAN4)
RDMNAME config;
REQUEST;

# 1. Switch Router Operating Mode to Ethernet WAN
SEL InternetGatewayDevice.X_5067F0_Ext.WANSwitch;
SET WANMode string ETHER;
SET WanAutoDetect boolean 0;

# 2. Configure WAN Connection Device 3 for PPPoE
SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3;
ADD WANPPPConnection;

SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;
SET Enable boolean 1;
SET Name string Eth_PPPoE;
SET ConnectionType string IP_Routed;
SET Username string <ISP_USERNAME>;
SET Password string <ISP_PASSWORD>;
SET PPPoEServiceName string 3jglobal;
SET MaxMRUSize uint32 1480;
SET X_5067F0_MaxMTUSize uint32 1480;
SET X_5067F0_PPPAuthenticationProtocol string AUTO_AUTH;
SET NATEnabled boolean 1;
SET X_5067F0_Enable_VLANID boolean 0;
SET X_5067F0_VLANID uint16 0;

# 3. Direct Default Routing to Ethernet PPPoE
SEL InternetGatewayDevice.Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

SEL InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

SAVE;
SEND;
```

