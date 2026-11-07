# PPPoE Interface Binding Analysis

## Core Research Question
Does the firmware hardcode the PPPoE interface to GPON, or does it dynamically bind to `nas0_notag` when configured under `WANConnectionDevice.3`?

---

## The Code-Level Binding Chain

### Step 1: Interface Name Generation
Function `constructL3WANDevName` (`libbemodules.so` @ `0x698dc`):
- Receives connection object instance pointer and base interface name.
- For `WANConnectionDevice.3`, base interface name is `nas0` (from `WANEthernetInterfaceConfig.X_5067F0_IfName`).
- Evaluates `WANPPPConnection.X_5067F0_Enable_VLANID`:
  - If VLAN disabled (`0`): concatenates `"nas0"` + `"_notag"` = `"nas0_notag"`.

### Step 2: RDM Parameter Population
Function `setWanIpPppInterfaceName` (`libcccbe.so` @ `0x346d0`):
- Takes constructed string `"nas0_notag"` and LinkType `1` (`PPP`).
- At address `0x348a8`:
  Writes `"nas0_notag"` into `WANPPPConnection->X_5067F0_IfName` (offset `0x898`).
- Allocates PPP unit (e.g. `111`) and writes `"ppp111"` to `WANPPPConnection->X_5067F0_InterfaceName` (offset `0x3e7`).

### Step 3: Daemon Execution Argument
Function `beWanDoLayer3InterfaceAction` (`libbemodules.so` @ `0x6c780`):
- Reads `X_5067F0_IfName` (`"nas0_notag"`).
- Calls `beWanEnablePPPv4Client("/bin/pppd", "nas0_notag")` (`0x66ee4`).
- Delegates to `libccc_executePPPv4Client` (`libcccbe.so` @ `0x348f4`), which formats shell command:
  ```c
  snprintf(cmd, 256, "%s file /etc/ppp/options_%s %s > /tmp/pppd-info.tmp 2>&1 &",
           "/bin/pppd", "nas0_notag", "nas0_notag");
  ```
  Trailing argument is `"nas0_notag"`.

### Step 4: Socket Binding in `libpppoe.so`
Inside `pppd`:
- `libpppoe.so::setdevname_pppoe("nas0_notag")` binds the discovery raw packet socket directly to `nas0_notag`.

**Definitive Verdict [CONFIRMED]:**
Interface binding is **100% dynamic**. There is zero hardcoded GPON dependency. When `WANPPPConnection` is created under `WANConnectionDevice.3`, the firmware seamlessly constructs `nas0_notag` and binds `pppd` directly to LAN4.

