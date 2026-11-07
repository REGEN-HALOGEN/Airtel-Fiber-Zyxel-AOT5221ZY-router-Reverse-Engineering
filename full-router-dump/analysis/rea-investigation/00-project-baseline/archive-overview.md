# Archive Overview — Airtel AOT5221ZY

## Archive Identity & Scope
- **Archive Path:** `C:\Users\REGEN\AirtelModemRev\full-router-dump`
- **Total Files Indexed:** 1,849 entries catalogued in `FILE_INVENTORY.csv` (280,849 bytes)
- **Hierarchy Representation:** Documented in `FOLDER_TREE.txt` (96,659 bytes)
- **Primary Firmware Sources:** Dual-bank UBI flash volumes (`ubi_k0.bin`, `ubi_k1.bin`), physical MTD partition dumps, and root filesystem extraction (`filesystem/rootfs`).

## Folder Structure Summary
| Directory | Role & Evidence Class | Preservation Policy |
| :--- | :--- | :--- |
| `analysis/` | Derived reports, reorganization logs, signatures, and previous report outputs | Read-only baseline; extended via `analysis/rea-investigation/` |
| `configuration/` | Live-router exports, backups (`.xml`, `.rdm`, `.lz`) | Immutable original backups |
| `filesystem/rootfs/` | Extracted root filesystem of the active firmware | Authoritative static reverse-engineering target |
| `filesystem/archives/` | Original filesystem compressed archives (`apps-filesystem.tar`) | Immutable source archive |
| `flash/physical-mtd/` | Raw NAND MTD partition images (bootloader, environment, config, kernel) | Immutable physical evidence |
| `flash/ubi-volumes/` | Extracted UBI volumes | Immutable flash evidence |
| `hardware/` | Device tree binary (`.dtb`) and decompiled source (`.dts`) | Hardware memory & register mapping reference |
| `inventory/` | Flash layout manifests, slot comparisons, partition offsets | System architectural reference |
| `private-volumes/` | Device serial numbers, MAC addresses, private keys, certificates | Strictly protected; confidential; never logged |

## Archive Integrity Check
All five original firmware images extracted from the source archive were cryptographically verified using SHA-256 against `flash/ubi-volumes`. The manifest is retained in `analysis/reports/archive-firmware-SHA256SUMS.txt`.

