# `libpppoe.so` Library Analysis

## Target Metadata
- **Path:** `filesystem/rootfs/lib/MSTC/libpppoe.so`
- **Class:** ELF64 AArch64 Shared Object (`ET_DYN`)
- **Key Functions:**
  - `pppoe_plugin_init` (Address: `0x2f98`)
  - `setdevname_pppoe` (Address: `0x2c00`)
  - `send_disc`
  - `session_connect`
  - `session_disconnect`

## 1. Plugin Initialization (`pppoe_plugin_init`)
At `0x2f98`, `pppoe_plugin_init` is called by `pppd`. It performs:
1. Verifies kernel PPP subsystem availability via `ppp_available()`.
2. Registers custom PPPoE command-line and options file options via `add_options()`.
3. Hooks device resolution by replacing `setdevname_hook` with `setdevname_pppoe`.
4. Logs debug confirmation string:
   ```
   "PPPoE Plugin Initialized"
   ```

## 2. Device Binding (`setdevname_pppoe`)
At `0x2c00`, `setdevname_pppoe` receives the device name pointer (`"nas0_notag"`):
1. Allocates discovery socket via `socket(PF_PACKET, SOCK_RAW, htons(ETH_P_PPP_DISC))`.
2. Resolves interface index of `nas0_notag` via `ioctl(SIOCGIFINDEX)`.
3. Binds the raw packet socket to `nas0_notag` using `sockaddr_ll`.
4. Saves global reference `devnam = "nas0_notag"`.

## 3. Discovery Protocol Engine (`send_disc`)
During link establishment:
1. Formats PADI (PPPoE Active Discovery Initiation) broadcast packet (`FF:FF:FF:FF:FF:FF`).
2. Appends Service-Name tag:
   If `pppoe_srv_name` is set (e.g. `"3jglobal"`), it injects TLV tag `0x0101` (`TAG_SVC_NAME`) with string `"3jglobal"`.
3. Sends PADI out `nas0_notag`.
4. Awaits PADO from external ONT / ISP BRAS.
5. Emits PADR (Request) and parses PADS (Session Confirmation) containing 16-bit Session ID.
6. Transfers session to kernel driver `pppoe.ko` via `connect()` on `AF_PPPOX` socket.

