# Interface Associations & Cross-Reference Mapping

## Object Association Graph

```mermaid
erDiagram
    WANSwitch ||--|| WANEthernetInterfaceConfig : enables
    WANSwitch ||--|| X_5067F0_GponInterafceConfig : disables
    WANEthernetInterfaceConfig ||--|| WANConnectionDevice_3 : binds
    WANConnectionDevice_3 ||--|{ WANPPPConnection_1 : instantiates
    Layer3Forwarding ||--|| WANPPPConnection_1 : routes_default_to
    WANPPPConnection_1 ||--|| smuxdev_nas0_notag : attaches_lower_device
    WANPPPConnection_1 ||--|| pppd_daemon : launches
    pppd_daemon ||--|| ppp111_interface : creates_netdevice
```

## Resolution Verification
1. `WANEthernetInterfaceConfig` sets base name `nas0`.
2. `WANConnectionDevice.3` hosts `WANPPPConnection.1`.
3. `constructL3WANDevName` produces `nas0_notag`.
4. `setWanIpPppInterfaceName` links `nas0_notag` and `ppp111` into `WANPPPConnection.1`.
5. `Layer3Forwarding.DefaultConnectionService` binds default gateway to `WANPPPConnection.1`.

