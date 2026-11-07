# Firmware Layout & Partition Architecture

## Storage Architecture & Flash Layout
The Airtel AOT5221ZY / Zyxel PX5311-R0 utilizes SPI NAND flash managed via UBI (Unsorted Block Images) with a dual-bank failover topology.

### Partition & Volume Structure
| Flash Component | Physical MTD Offset | Type / Format | Function & Content |
| :--- | :--- | :--- | :--- |
| **Bootloader** | `mtd0` | Raw Binary | Realtek Bootloader / ARM Trusted Firmware |
| **Env / Configuration** | `mtd1` - `mtd3` | Raw Binary / U-Boot Env | Bootloader parameters, dual-boot slot pointers |
| **Kernel Bank 0 (`ubi_k0.bin`)** | UBI Volume | FIT (Flattened Image Tree) | Linux Kernel 5.10.138 + Device Tree (Slot 0) |
| **Kernel Bank 1 (`ubi_k1.bin`)** | UBI Volume | FIT (Flattened Image Tree) | Backup identical Linux Kernel FIT (Slot 1) |
| **Rootfs Bank 0** | UBI Volume | SquashFS (LZMA) | Extracted active root filesystem (`filesystem/rootfs/`) |
| **Rootfs Bank 1** | UBI Volume | SquashFS (LZMA) | Redundant secondary rootfs |
| **Private Data** | UBI Volume | JFFS2 / Raw | Device identity, MAC addresses, SSL certs |

## Filesystem Directory Organization (`filesystem/rootfs/`)
- `/bin`: BusyBox applets, `pppd`, `smuxctl`, `brctl`, `board_detect`.
- `/sbin`: Network lifecycle daemons (`netifd`, `udhcpc`, `hotplug2`).
- `/usr/bin`: Management tools (`ccc_be`, `ccc_das`, `ccctest`, `pppoe-start`, `wan_event_notify.sh`).
- `/lib/MSTC`: Core vendor libraries (`libbemodules.so`, `libcccbe.so`, `libcccrdm.so`, `librtk.so`, `librdm.so`, `libpppoe.so`).
- `/lib/modules/5.10.138`: Kernel modules (`ca-rtk.ko`, `ca-ne.ko`, `fc_8277c.ko`, `smuxdev.ko`, `pppoe.ko`, `ppp_generic.ko`).
- `/etc/ppp`: PPP configuration templates (`default_options`, `_options_static`, `pap-secrets`, `chap-secrets`, `ip-up`, `ip-down`).
- `/usr/var/default-rdm`: Master TR-098/TR-181 data model database (`config.rdm`).

