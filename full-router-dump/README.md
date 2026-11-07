# Airtel AOT5221ZY Firmware Research Archive

Device: Airtel AOT5221ZY
Platform: Zyxel PX5311-R0
SoC: Realtek Taurus

## Directory structure

- analysis/
  - reports/         Analysis reports, hash records and verification results
  - signatures/      Reserved for extracted signature data
  - source-archives/ Original analysis archives
  - reorganization-log.csv
- configuration/     Live-router configuration exports and backups
- filesystem/
  - rootfs/          Extracted firmware root filesystem
  - archives/        Original filesystem archives
- flash/
  - physical-mtd/    Raw physical MTD partition dumps
  - ubi-volumes/     Extracted UBI firmware volumes
  - *sha256.csv      Hash manifests for flash evidence
- hardware/          Device tree binary and source
- inventory/         Flash layout and system inventory
- logs/              Future collection and analysis logs
- private-volumes/   Device-specific data, certificates and private records

## Root-level indexes

- FILE_INVENTORY.csv: File paths, sizes and modification timestamps.
- FOLDER_TREE.txt: Directory and file tree.
- README.md: Archive documentation.

## Evidence handling

1. Treat physical-mtd, ubi-volumes and private-volumes as original evidence.
2. Do not overwrite original firmware dumps.
3. Preserve SHA-256 manifests when copying or moving evidence.
4. Store extracted or modified files separately from original dumps.
5. Store live-router configuration backups in configuration/.
6. Record new collection and modification operations.
7. Never publish private-volume contents or router credentials.

## Important

The five firmware images extracted from the source archive were
verified against flash/ubi-volumes using SHA-256. Their duplicate
copies were removed. The verification manifest is retained in
analysis/reports/archive-firmware-SHA256SUMS.txt.
