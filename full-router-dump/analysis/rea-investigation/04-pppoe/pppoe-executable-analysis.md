# `pppd` Executable Analysis

## Executable Metadata
- **Path:** `filesystem/rootfs/bin/pppd`
- **Class:** ELF64 AArch64 Little-Endian
- **Entry Address:** `0x4048c0`
- **Plugin Loading Mechanism:** Standard pppd plugin architecture with shared library resolution.

## Command-Line Invocations
When invoked by `ccc_be` via `libccc_executePPPv4Client` (`libcccbe.so` @ `0x348f4`), the daemon is launched as:
```bash
/bin/pppd file /etc/ppp/options_nas0_notag nas0_notag > /tmp/pppd-info.tmp 2>&1 &
```

### Argument Parsing & Device Binding
1. `file /etc/ppp/options_nas0_notag`:
   - Tells `pppd` to load and parse `/etc/ppp/options_nas0_notag`.
   - The first line in that options file is `plugin pppoe`.
   - `pppd` loads `libpppoe.so` and executes `pppoe_plugin_init()`.
2. `nas0_notag` (Trailing Positional Argument):
   - In Linux `pppd`, any non-option positional parameter is passed to the device-name hook (`setdevname_hook`).
   - `libpppoe.so` hooks this with `setdevname_pppoe()`.
   - `setdevname_pppoe("nas0_notag")` associates the PPPoE discovery socket with network interface `nas0_notag`.

