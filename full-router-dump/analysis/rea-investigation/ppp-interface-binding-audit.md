# PPP Lower-Layer Interface Binding Audit

**Target Subsystem:** User-Space PPPoE Stack / Interface Resolution  
**Binaries Audited:**
- `full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so` (SHA-256: `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so` (SHA-256: `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so` (SHA-256: `3ba88a38914b4e9e03d46797a73a4b9177b9d7efae9dfcf38fbbcd7fa238f4be`)
- `full-router-dump/filesystem/rootfs/bin/pppd` (SHA-256: `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596`)

---

## 1. Executive Summary & Audit Conclusions

| Audit Question | Audit Verdict | Confidence Level | Primary Supporting Evidence |
| :--- | :---: | :---: | :--- |
| **1. Lower-Layer Interface Parameter** | Synthesized dynamically | **CONFIRMED** | Base interface `"nas0"` from `WANEthernetInterfaceConfig` + VLAN suffix. |
| **2. Exact Parameter Stored in RDM** | `X_5067F0_InterfaceName` | **CONFIRMED** | `setWanIpPppInterfaceName` (`0x348c4`) writes `"nas0_notag"` to offset `0x28` (`X_5067F0_IfName`) and `"ppp111"` to `[x19, #0x30]`. |
| **3. Interface Received by Plugin** | `nas0_notag` | **CONFIRMED** | `libccc_executePPPv4Client` (`0x3493c`) passes `nas0_notag` as trailing command-line argument to `/bin/pppd`. |
| **4. Device Binding Mechanism** | Raw `PF_PACKET` Socket | **CONFIRMED** | `libpppoe.so` (`setdevname_pppoe` @ `0x2c00`, `client_init_ses` @ `0x3408`) opens `PF_PACKET` raw socket bound to interface index. |
| **5. PPP Unit Number Generation** | Statically Derived / Fixed | **CONFIRMED** | Hardcoded to unit `111` in `beConfigWANByPPPoE` (`0x664a8`), resulting in virtual netdevice `ppp111`. |
| **6. PPP Interface Naming** | Fixed Pattern: `ppp%d` | **CONFIRMED** | `setWanIpPppInterfaceName` line `0x348d4` formats string `"ppp%d"` using unit `111` (`"ppp111"`). |
| **7. Options Filename Construction** | `/etc/ppp/options_<dev>` | **CONFIRMED** | Line `0x4aee0` formats `/etc/ppp/options_%s %s` -> `/etc/ppp/options_nas0_notag nas0_notag`. |
| **8. Interface Existence Precondition**| Must Exist Prior to `pppd` | **CONFIRMED** | `libpppoe.so` @ `0x2c00` calls `ioctl(SIOCGIFINDEX)` on device name. Fails if netdevice is missing. |

---

## 2. Complete Disassembly Trace of Interface Name Resolution

### 2.1 `setWanIpPppInterfaceName()` (`libcccbe.so` @ `0x346d0` - `0x348f0`)
This function derives both the physical lower-layer netdevice name and the virtual PPP interface name:

```armasm
0x34728: ldr  x3, [x19, #0x10]       ; Base interface pointer (e.g., "nas0")
0x34730: adrp x2, #0x4c000
0x34734: add  x2, x2, #0x160         ; Format: "%s"
0x34740: bl   #0x19820               ; <snprintf@plt> -> writes "nas0" to sp+0xc0

; Check VLAN Enable flag
0x34744: ldrb w0, [x19, #0x18]       ; VLAN Enable boolean
0x34748: cbz  w0, #0x3481c          ; If 0 (Untagged) -> branch to notag
; Tagged branch:
0x3474c: ldr  w5, [x19, #0x20]       ; VLAN ID (uint16)
0x34750: adrp x4, #0x4d000
0x34754: add  x4, x4, #0x990         ; Format: "_%d"
0x34768: bl   #0x198a0               ; <__snprintf_chk@plt> -> sp+0x40 = "_<VLANID>"
0x3476c: b    #0x3476c
; Untagged branch:
0x3481c: adrp x0, #0x4a000
0x34820: add  x0, x0, #0xea8         ; Literal "_notag"
0x34824: ldr  w1, [x0]
0x34828: str  w1, [sp, #0x40]        ; Writes "_notag" to sp+0x40

; LinkType Evaluation:
0x3476c: ldr  w20, [x19]             ; Connection LinkType (0 = IP, 1 = PPP)
0x34770: cbz  w20, #0x34838          ; If IP -> branch to IP naming
0x34774: cmp  w20, #1
0x34778: b.eq #0x348a8               ; If PPP -> branch to PPP naming

; PPP Interface Assignment Branch (0x348a8):
0x348a8: add  x6, sp, #0x40          ; Suffix ("_notag")
0x348ac: add  x5, sp, #0xc0          ; Base ("nas0")
0x348b0: adrp x4, #0x40000
0x348b4: add  x4, x4, #0xad8         ; Format: "%s%s"
0x348c4: ldr  x0, [x19, #0x28]       ; Destination: X_5067F0_IfName
0x348c8: bl   #0x198a0               ; Writes "nas0_notag" into X_5067F0_IfName!
0x348cc: ldr  w5, [x19, #0x48]       ; Unit number: 111
0x348d0: adrp x4, #0x4a000
0x348d4: add  x4, x4, #0xeb0         ; Format: "ppp%d"
0x348e4: ldr  x0, [x19, #0x30]       ; Destination: X_5067F0_InterfaceName
0x348e8: bl   #0x198a0               ; Writes "ppp111" into X_5067F0_InterfaceName!
```

---

## 3. Disassembly Trace of PPP Daemon Execution

### 3.1 `libccc_executePPPv4Client()` (`libcccbe.so` @ `0x348f4` - `0x3497c`)
```armasm
0x34938: mov  x5, x0                 ; Binary: "/bin/pppd"
0x3493c: adrp x4, #0x4a000
0x34940: add  x4, x4, #0xee0         ; Format: "%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &"
0x34944: mov  x3, #0x100
0x34950: mov  x0, x19                ; Output command buffer
0x34954: bl   #0x198a0               ; <__snprintf_chk@plt>
0x3496c: bl   #0x19ad0               ; <cccBeSystemQueue@plt> -> Executes command shell
```
- **Generated Shell Command:**
  ```bash
  /bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &
  ```

### 3.2 `libpppoe.so` Device Hook & Socket Binding
In `libpppoe.so` (`0x2c00`):
- `pppoe_plugin_init` (`0x2f98`) registers `setdevname_pppoe` (`0x2c00`) as the `setdevname_hook` inside `pppd`.
- When `pppd` parses trailing positional argument `nas0_notag`:
  1. `setdevname_pppoe` is invoked with `arg = "nas0_notag"`.
  2. Queries network interface index:
     ```c
     struct ifreq ifr;
     strncpy(ifr.ifr_name, "nas0_notag", IFNAMSIZ);
     ioctl(fd, SIOCGIFINDEX, &ifr);
     ```
  3. If interface does not exist, logs: `"bad device name: nas0_notag"` and exits with fatal code.
  4. In `client_init_ses` (`0x3408`):
     - Creates raw discovery socket: `socket(PF_PACKET, SOCK_RAW, htons(ETH_P_PPP_DISC))`.
     - Binds socket to interface index: `bind(disc_sock, &sockaddr_ll, sizeof(sockaddr_ll))`.
     - Validates Ethernet MAC broadcast capability: `if (sockaddr_ll.sll_hatype != ARPHRD_ETHER) log("Interface %s is not Ethernet!");`.
  5. In `session_connect` (`0x551c`):
     - Opens session socket: `socket(AF_PPPOX, SOCK_STREAM, PX_PROTO_OE)`.
     - Calls `connect()` transferring discovery state to Linux kernel `pppoe.ko`.

---

## 4. Options File Generation (`beConfigWANByPPPoE`)

In `libbemodules.so` @ `0x664a8`:
1. Copies base options from `/etc/ppp/default_options`.
2. Appends runtime options to `/etc/ppp/options_nas0_notag`:
   - `unit 111`
   - `linkname nas0_notag`
   - `user <ISP_USERNAME>`
   - `password <ISP_PASSWORD>`
   - `pppoe_srv_name 3jglobal` (emitted at `0x66b3c` if `PPPoEServiceName` is non-empty)
   - `mtu 1480` and `mru 1480`
   - Authentication flags: If `AUTO_AUTH`, leaves refuse flags unset, permitting open bidirectional negotiation.

