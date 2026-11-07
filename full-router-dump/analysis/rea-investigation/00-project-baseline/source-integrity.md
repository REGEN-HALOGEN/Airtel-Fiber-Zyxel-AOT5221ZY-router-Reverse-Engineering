# Source Integrity Verification & Preservation Rules

## Integrity Verification Policy
1. **Flash & Filesystem Immutability:**
   - Raw partition dumps in `flash/physical-mtd/` and extracted UBI volumes in `flash/ubi-volumes/` are marked read-only.
   - All duplicate files removed during previous reorganization were validated against SHA-256 manifests stored in `analysis/reports/archive-firmware-SHA256SUMS.txt`.
   - Extracted root filesystem files in `filesystem/rootfs/` must never be directly modified or overwritten.

2. **Analysis Separation:**
   - All derived scripts, intermediate dumps, disassembly listings, and reports are isolated exclusively under `analysis/rea-investigation/` and its subdirectories (`evidence/`, `working/`, `logs/`).
   - No temporary files may be created inside `filesystem/rootfs/` or `flash/`.

3. **Confidentiality & Secret Redaction:**
   - In accordance with non-negotiable safety rules, files in `private-volumes/` contain device identities, certificates, and MAC data. These are excluded from report output.
   - ISP credentials (PPPoE usernames/passwords) must remain strictly redacted in all analysis reports.

4. **Cryptographic Baseline Signatures:**
   - All critical binaries cataloged in `evidence-inventory.md` possess verified SHA-256 digests. Any newly extracted binary or derivative will have its digest recorded immediately into `evidence/hashes/`.

