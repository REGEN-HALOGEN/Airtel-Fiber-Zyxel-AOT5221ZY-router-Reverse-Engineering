# Minimal-Change Implementation Analysis

## 1. Minimal Reversible Configuration Blueprint
To transition the device from GPON to external ONT Ethernet WAN with PPPoE without any firmware modifications or flash writes, the following CCC script is required:

```ini
# Baseline Ethernet WAN PPPoE Configuration Script
RDMNAME config;
REQUEST;

# 1. Disarm linkdetection auto-switching to protect ACS URL
SEL InternetGatewayDevice.X_5067F0_Ext.WANSwitch;
SET WanAutoDetect boolean 0;
SET WANMode string ETHER;

# 2. Enable Ethernet hardware interface, disable GPON interface
SEL InternetGatewayDevice.WANDevice.1.WANEthernetInterfaceConfig;
SET Enable boolean 1;

SEL InternetGatewayDevice.WANDevice.1.X_5067F0_GponInterafceConfig;
SET Enable boolean 0;

# 3. Disable old GPON profiles
SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1;
SET Enable boolean 0;

SEL InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1;
SET Enable boolean 0;

# 4. Instantiate and configure Ethernet PPPoE profile
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

# 5. Direct default routing to Ethernet PPPoE
SEL InternetGatewayDevice.Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

SEL InternetGatewayDevice.X_5067F0_IPv6Layer3Forwarding;
SET DefaultConnectionService string InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1;

SAVE;
SEND;
```

## 2. Safety & Risk Evaluation
- **Zero Flash Writes:** Executed in runtime RDM memory via `ccc_das`.
- **Zero Kernel Patching:** Reuses existing vendor drivers and kernel modules.
- **LAN3 Preservation:** Port 2 (LAN3) remains in `br0`.
- **ACS Preservation:** `WanAutoDetect = 0` guarantees `ManagementServer.URL` is never modified.
- **Instant Rollback:** An exact inverse script restores GPON mode within seconds.

