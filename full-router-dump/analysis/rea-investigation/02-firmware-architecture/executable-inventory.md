# Executable Inventory — High-Relevance Binaries

Detailed analysis of the four primary executables controlling WAN mode switching, daemon execution, and IPC.

| Executable | Architecture | Stripped | Entry Address | Imported Symbols | Key Functionality |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `files/linkdetection` | ELF64 AArch64 | Yes | `0x401480` | 52 dynsym | Physical link poller (`rt_port_link_get`); mode switch logic at `0x402454`; CMSG IPC sender. |
| `usr/bin/ccc_be` | ELF64 AArch64 | Yes | `0x401db0` | 239 dynsym | Central backend dispatcher; loads `libbemodules.so` and `libcccbe.so`; coordinates network actions. |
| `usr/bin/ccc_das` | ELF64 AArch64 | Yes | `0x401bc0` | 184 dynsym | CCC command agent; parses scripts containing `REQUEST`, `SEL`, `ADD`, `SET`, `SEND`. |
| `bin/pppd` | ELF64 AArch64 | Yes | `0x402500` | 310 dynsym | Linux PPPoE client daemon; supports option file loading and direct interface binding. |

## Dynamic Symbol Import Analysis for `linkdetection`
Extracted dynamic symbols confirm the precise operational boundaries of `linkdetection`:
- **Hardware Link Query:** `rt_port_link_get` (queries Realtek PHY link state for specified port index).
- **CMSG IPC Requests:** `cmsgCreateRequest`, `cmsgRequestSel`, `cmsgRequestSet`, `cmsgRequestSave`, `cmsgSendRecv`, `cmsgRequestEventNotify`.
- **RDM Direct Queries:** `rdmInit`, `rdmGetObjectByName`, `cccRdmGetObjectByOID`, `cccRdmGetObjListByOID`.
- **System Commands:** `system`, `popen`, `pclose` (invokes shell utilities for network/route configuration).
- **LED Notification:** `ledctl_event`.

