# Proposed Implementation & Operational Runbook

## 1. Prerequisites & Physical Cabling
1. Connect Ethernet patch cable from external GPON ONT (LAN port) to **router LAN4**.
2. Connect local Access Point / PC to **router LAN3** (or connect via Wi-Fi).
3. Connect management PC to LAN1 or LAN2 (or Wi-Fi).

## 2. Pre-Flight Backup Runbook (CLI)
Log into the router via SSH (`admin@192.168.0.2`):
```bash
# Capture full RDM state dump
ccctest -d > /tmp/backup_rdm.txt

# Capture network state
cat /proc/ni/dev_port_mapping > /tmp/backup_port_mapping.txt
cat /proc/fc/ctrl/wan_port_mask > /tmp/backup_wan_mask.txt
```

## 3. Deployment Runbook (`apply_eth_pppoe.cmd`)
Create `/tmp/apply_eth_pppoe.cmd` on the router:

```ini
RDMNAME config;
REQUEST;

# Step 1: Disarm linkdetection auto-switching
SEL InternetGatewayDevice.X_5067F0_Ext.WANSwitch;
SET WanAutoDetect boolean 0;
SET WANMode string ETHER;

# Step 2: Enable Ethernet hardware interface, disable GPON interface
SEL InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig;
SET Enable boolean 1;

SEL InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig;
SET Enable boolean 0;

# Step 3: Disable existing GPON profiles
SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1;
SET Enable boolean 0;

SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1;
SET Enable boolean 0;

# Step 4: Instantiate and configure Ethernet PPPoE profile under instance 3
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

# Step 5: Direct Layer 3 default forwarding to Ethernet PPPoE
SEL InternetGatewayDevice.Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

SEL InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

SAVE;
SEND;
```

Execute the script:
```bash
ccctest -f /tmp/apply_eth_pppoe.cmd
```

## 4. Verification Commands
```bash
# 1. Verify port 3 mapped to nas0
cat /proc/ni/dev_port_mapping

# 2. Verify pppd running
ps | grep pppd

# 3. Verify interface ppp111 created and IP assigned
ip addr show ppp111

# 4. Verify default route
ip route show

# 5. Test internet connectivity
ping -c 3 8.8.8.8
```

## 5. Instant Emergency Rollback Runbook (`rollback_to_gpon.cmd`)
If rollback is required:
```bash
ccctest -f /tmp/rollback_to_gpon.cmd
```
The router immediately restores GPON mode and re-attaches LAN4 to `br0`.

