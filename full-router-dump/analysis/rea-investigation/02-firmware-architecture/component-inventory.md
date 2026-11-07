# Component Inventory — Network & Management Subsystems

Total ELF files discovered in rootfs: 474. Below is the curated inventory of high-relevance components governing Ethernet WAN, PPPoE, switch management, and configuration persistence.

## 1. Network Interface & Switch Control
| Binary Path | Class / Machine | Size (Bytes) | Role & Relevance |
| :--- | :--- | :---: | :--- |
| `bin/smuxctl` | ELF64 EXEC / AArch64 | 53,616 | Realtek SMUX interface creator and filter manager (`--if-create-name`, `--set-if-rsmux`). |
| `bin/brctl` | ELF64 EXEC / AArch64 | 27,272 | Linux bridge configuration utility (`br0` management). |
| `sbin/netifd` | ELF64 EXEC / AArch64 | 206,496 | Network interface daemon managing device states and event hooks. |
| `files/linkdetection` | ELF64 EXEC / AArch64 | 22,896 | Physical link state poller (`rt_port_link_get`) and WAN mode switch daemon (`0x402454`). |

## 2. PPPoE & Point-to-Point Stack
| Binary Path | Class / Machine | Size (Bytes) | Role & Relevance |
| :--- | :--- | :---: | :--- |
| `bin/pppd` | ELF64 EXEC / AArch64 | 236,432 | Point-to-Point Protocol daemon; supports `rp-pppoe.so` socket binding. |
| `lib/MSTC/libpppoe.so` | ELF64 DYN / AArch64 | 35,864 | Vendor PPPoE utility library; session parameter formatting. |
| `lib/modules/5.10.138/pppoe.ko` | ELF64 REL / AArch64 | 23,120 | Linux PPPoE socket driver. |
| `lib/modules/5.10.138/pppox.ko` | ELF64 REL / AArch64 | 7,624 | Linux PPPoX protocol layer. |
| `lib/modules/5.10.138/ppp_generic.ko` | ELF64 REL / AArch64 | 60,648 | Core Linux PPP device layer. |
| `usr/bin/pppoe-start` | Shell script | — | Helper script for PPPoE interface invocation. |

## 3. Realtek Switch & Hardware Drivers
| Binary Path | Class / Machine | Size (Bytes) | Role & Relevance |
| :--- | :--- | :---: | :--- |
| `lib/librtk.so` | ELF64 DYN / AArch64 | 2,204,184 | Unstripped Realtek Taurus hardware HAL; L3/L4 NAT, switch table. |
| `lib/MSTC/librtk.so` | ELF64 DYN / AArch64 | 498,808 | Stripped vendor Realtek runtime library. |
| `lib/modules/5.10.138/ca-rtk.ko`| ELF64 REL / AArch64 | 392,040 | Kernel driver: Realtek Ethernet switch/MAC core. |
| `lib/modules/5.10.138/ca-ne.ko` | ELF64 REL / AArch64 | 3,975,376 | Kernel driver: Network Engine, SerDes, EPON/GPON MAC interface. |
| `lib/modules/5.10.138/fc_8277c.ko`| ELF64 REL / AArch64 | 2,088,432 | Kernel module: Flow Control / Fastpath acceleration engine. |
| `lib/modules/5.10.138/smuxdev.ko`| ELF64 REL / AArch64 | 185,944 | Kernel driver: Realtek SMUX multiplexer (`nas0_notag`). |

## 4. CCC & RDM Management Framework
| Binary Path | Class / Machine | Size (Bytes) | Role & Relevance |
| :--- | :--- | :---: | :--- |
| `usr/bin/ccc_be` | ELF64 EXEC / AArch64 | 122,064 | Central Backend daemon; dispatches CMSG messages, handles RDM events. |
| `usr/bin/ccc_das` | ELF64 EXEC / AArch64 | 112,704 | Command Agent; parses CLI/script requests to CCC backend. |
| `usr/bin/ccctest` | ELF64 EXEC / AArch64 | 22,872 | RDM database interrogation and test CLI tool. |
| `lib/MSTC/libbemodules.so` | ELF64 DYN / AArch64 | 1,074,680 | Business logic: WAN manager, options file generator, IP/PPP loaders. |
| `lib/MSTC/libcccbe.so` | ELF64 DYN / AArch64 | 377,312 | Platform layer: SMUX setup, port mapping, `pppd` invocation. |
| `lib/MSTC/libcccrdm.so` | ELF64 DYN / AArch64 | 446,208 | RDM object and parameter query/mutation engine. |
| `lib/MSTC/librdm.so` | ELF64 DYN / AArch64 | 285,848 | Core RDM binary database serializer / deserializer. |
| `lib/MSTC/libcmsg.so` | ELF64 DYN / AArch64 | 55,664 | Inter-Process Communication messaging library (socket based). |

