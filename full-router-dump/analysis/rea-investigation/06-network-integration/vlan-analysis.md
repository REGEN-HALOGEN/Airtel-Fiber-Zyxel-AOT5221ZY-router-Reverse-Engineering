# VLAN Architecture & 802.1Q Tagging

## Interface Naming & 802.1Q Handling
- **Untagged Operation (`X_5067F0_Enable_VLANID = 0`):**
  - Function `constructL3WANDevName` selects string `"_notag"`.
  - Netdevice is named `nas0_notag`.
  - Packets exit Port 3 with standard Ethernet II untagged framing.
  - This matches our external GPON ONT requirement where VLAN tagging is terminated by the ONT or untagged by the ISP.
- **Tagged Operation (`X_5067F0_Enable_VLANID = 1`):**
  - Function `constructL3WANDevName` formats `nas0_%d` (e.g. `nas0_100` for VLAN 100).
  - SMUX driver (`smuxdev.ko`) filters and tags outbound frames with the specified 802.1Q VLAN tag.

## ISP VLAN Requirements
The ISP connection is configured untagged on the customer-facing LAN port of the ONT. Therefore, `X_5067F0_Enable_VLANID` must be configured to `0`, producing untagged interface `nas0_notag`.

