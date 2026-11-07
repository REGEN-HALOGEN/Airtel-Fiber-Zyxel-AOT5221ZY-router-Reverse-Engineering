# Missing Integration & Firmware Gap Analysis

## 1. What is Missing in Factory Default State
1. **Instantiated Ethernet PPPoE Profile:**
   - Under `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3`, the factory default RDM database only contains `WANIPConnection.1` (`Eth_Internet`, DHCP, TR069).
   - There is no pre-existing `WANPPPConnection.1` under container `.3`.
   - *Impact:* Attempting to run Ethernet WAN without creating `WANPPPConnection.1` results in `ccc_be` launching `udhcpc` instead of `pppd`.

2. **Web GUI WAN Configuration Controls:**
   - The Airtel-branded Web GUI (`/usr/local/www/`) hides or restricts the WAN management page, preventing users from creating new WAN profiles or selecting `nas0_notag` as a PPPoE interface.
   - *Impact:* Configuration must be applied via CLI using `ccc_das` or direct RDM injection, not the Web GUI.

3. **Vendor Automatic Switching Safety:**
   - The built-in auto-switching routine in `linkdetection` (`0x402454`) was designed for factory automated provisioning, not residential multi-ISP failover.
   - *Impact:* It clobbers the ACS URL to `testacs.airtelbroadband.in:8103`. Auto-switching MUST be permanently disabled via `WanAutoDetect = 0`.

## 2. What is NOT Missing (Proven Existing)
- The Linux kernel drivers (`ca-rtk.ko`, `smuxdev.ko`, `fc_8277c.ko`, `pppoe.ko`).
- The user-space daemons (`pppd`, `smuxctl`, `ccc_be`, `ccc_das`).
- The back-end handler logic (`libbemodules.so`, `libcccbe.so`, `librdm.so`).
- The multi-instance TR-098 schema supporting `WANPPPConnection` under any `WANConnectionDevice` instance.

**Engineering Verdict:** There are zero binary or kernel gaps. The "missing integration" is strictly configuration state in the RDM database, which is 100% addressable via standard CCC scripting.

