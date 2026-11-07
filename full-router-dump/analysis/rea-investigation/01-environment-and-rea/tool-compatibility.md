# Tool Compatibility Matrix — Windows 11 Native

This matrix documents the operational status of all analysis tools evaluated for this firmware reverse-engineering investigation.

| Tool / Technology | Host Environment | Compatibility | Target Scope | Operational Verification & Evidence |
| :--- | :--- | :---: | :--- | :--- |
| **Python 3.12 `capstone`** | Windows 11 Native | **VERIFIED** | AArch64 disassembly, branch analysis, instruction decoding | Tested with Capstone 5.0.9 (`CS_ARCH_ARM64`). Successfully disassembled subroutine `0x402454` in `linkdetection`. |
| **Python 3.12 `pyelftools`** | Windows 11 Native | **VERIFIED** | ELF headers, sections, dynamic symbols (`.dynsym`), relocations | Tested with pyelftools 0.33. Successfully extracted dynamic symbols from `linkdetection` and `libbemodules.so`. |
| **REA CLI (`rea-agents`)** | Windows 11 Native | **PARTIAL** | Artifact graph inspection, JavaScript/Web, SQLite, client checks | Tested v6.7.0. `doctor` and `capabilities` operational. Native AArch64 ELF analysis rejected. |
| **Binwalk (Python)** | Windows 11 Native | **PARTIAL** | Firmware signature scanning | Python `binwalk` 2.1.0 installed. Signature scans verified in `analysis/reports/binwalk-signatures.txt`. Recursive extraction requires Linux. |
| **Ghidra (Standalone)** | Windows 11 Native | **INCOMPATIBLE** | Decompilation, AArch64 analysis | Host currently has OpenJDK 1.8. Ghidra 12 requires JDK 21+. Not configured in PATH. |
| **REA Ghidra Provider** | Windows 11 Native | **INCOMPATIBLE** | Native binary decompilation | Hardcoded format filter: accepts PE and raw 6502 only. Explicitly rejects ELF. |
| **Unblob** | Linux Only | **UNAVAILABLE** | UBI/SquashFS recursive extraction | Unblob requires Linux kernel features, `prlimit`, and Linux utilities. |
| **Native Python RDM Parser** | Windows 11 Native | **VERIFIED** | TR-098/TR-181 RDM binary decompression & XML parsing | Operational scripts (`analysis/check_rdm_records.py`, `analysis/inspect_rdm_schema.py`) decode `config.rdm`. |

## AArch64 ELF Analysis Route on Windows
The verified, reliable, high-fidelity reverse-engineering pipeline for AArch64 ELF binaries on this Windows 11 machine is:
1. **Structural & Symbol Parsing:** `pyelftools` to extract ELF headers, section offsets, dynamic symbol tables (`.dynsym`), symbol strings (`.dynstr`), and relocations (`.rela.plt`, `.rela.dyn`).
2. **Instruction Disassembly & Control Flow:** `capstone` 5.0.9 in 64-bit ARM mode (`CS_ARCH_ARM64, CS_MODE_ARM`) to recover basic blocks, register dependencies, branch targets, and call sites.
3. **Symbol & PLT Resolution:** Automated cross-referencing between `.rela.plt` offsets and dynamic symbol indices to resolve external library function calls (`cmsg*`, `rt_port_link_get`, `rdm*`).
4. **Data & String Cross-Referencing:** Virtual address mapping between `.rodata` string pointers loaded into registers (`adrp`, `add`) and string literals.

