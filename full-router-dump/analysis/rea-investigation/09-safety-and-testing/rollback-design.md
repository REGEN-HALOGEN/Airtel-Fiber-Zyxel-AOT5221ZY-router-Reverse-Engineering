# Instant Rollback Design & Recovery Blueprint

## 1. Rollback Architecture
Because all changes are orchestrated via standard TR-098 CCC scripting in RDM without modifying the flash partitions or binary executables, rollback is **deterministic, instantaneous, and non-destructive**.

## 2. Declarative Rollback Script (`rollback_to_gpon.cmd`)
To immediately revert the router back to its factory GPON state:

```ini
# Emergency Rollback to Stock GPON Configuration
RDMNAME config;
REQUEST;

# 1. Disable Ethernet PPPoE profile
SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;
SET Enable boolean 0;

# 2. Re-enable GPON Internet & Voice profiles
SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1;
SET Enable boolean 1;

SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1;
SET Enable boolean 1;

# 3. Disable Ethernet interface, re-enable GPON interface
SEL InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig;
SET Enable boolean 0;

SEL InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig;
SET Enable boolean 1;

# 4. Restore Layer 3 Default Forwarding to GPON
SEL InternetGatewayDevice.Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1;

SEL InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1;

# 5. Restore WAN Switch Mode and Auto-Detect
SEL InternetGatewayDevice.X_5067F0_Ext.WANSwitch;
SET WANMode string GPON;
SET WanAutoDetect boolean 1;

SAVE;
SEND;
```

## 3. Rollback Execution Command
```bash
ccctest -f /tmp/rollback_to_gpon.cmd
```
Within 3–5 seconds of dispatching this script, `ccc_be` terminates `pppd` on `nas0_notag`, executes `rtk_wan_port_mapping(0, "nas0")` with port `7` (optical MAC), re-attaches Port 3 to `br0`, and restores the GPON WAN stack.

