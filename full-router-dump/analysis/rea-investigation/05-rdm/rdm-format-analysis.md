# RDM Binary Database Format Analysis

## File Metadata & Provenance
- **Raw File:** `files/config.rdm`
- **Compressed Format:** LZMA-Alone stream (Properties: `0x5d, 0x00, 0x00, 0x30, 0x00`)
- **Compressed Size:** 63,005 bytes (`SHA-256: fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7`)
- **Decompressed Size:** Exactly 3,145,728 bytes (3 MiB)
- **Engine Library:** `files/librdm.so` / `libcccrdm.so`

---

## 1. Database Header & Record Structure
Decompressed bytes `0x00` - `0x40`:
```
01 00 00 00 00 00 30 00 88 14 0b 00 ff ff 2f 00 a4 1b 02 00 ...
```
- **Version Byte:** `0x01` (RDM Version 1 schema).
- **Object Table Pointer:** Located at offset `0x78`.
- **OID Table Mapping:** Synchronized with `librdm.so::OIDTable` (`0x294f0`, size 180,320 bytes).

---

## 2. Object & Parameter Storage Architecture
The RDM database acts as the in-memory shared data model for TR-098 and TR-181 parameters:
1. **Object Node:**
   - 16-byte header: Object ID (OID), parent OID, child object flags, instance count, offset to parameter table.
   - ASCII object name (null-terminated).
2. **Parameter Node:**
   - Parameter ID / OID, type flag (String, Boolean, UnsignedInt, Int, DateTime).
   - Read/Write permission mask (Vendor, Admin, TR069 ACS).
   - Default value buffer and string offset table.
3. **Multi-Instance Child Architecture:**
   Objects defined with dynamic instance indicators (`.i.`) can be instantiated at runtime via `cccRdmAddObjectWithAssignIA` or CLI `ADD` command in `ccc_das`.

