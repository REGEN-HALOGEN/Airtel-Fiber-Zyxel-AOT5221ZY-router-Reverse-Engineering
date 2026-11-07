# Limitations & Fallback Strategy — Windows 11 Host

## Observed Limitations & Constraints

### 1. REA Windows Ghidra P0 Architecture Restriction
- **Observed Behavior:** REA's internal Windows Ghidra provider (`ghidra`) explicitly enforces target format validation that admits only Windows PE (`portable_executable`) and raw 6502 code. When presented with an AArch64 ELF binary (`linkdetection`, `ccc_be`), it rejects the operation with `target_format_unsupported`.
- **Impact:** REA's native disassembler and decompiler MCP tools (`analyze_function`, `decompile`, `xrefs`) cannot process AArch64 ELF files directly on Windows.
- **Fallback Strategy:** Windows-native Python pipeline utilizing Capstone 5.0.9 and pyelftools 0.33. This combination provides complete, unhindered instruction-level disassembly, control flow recovery, symbol resolution, and string xref tracking.

### 2. REA Firmware Extraction Linux Prerequisite
- **Observed Behavior:** REA's `extract-firmware` and `inspect-firmware-regions` commands require Linux-specific utilities (`unblob`, Linux `binwalk`, `prlimit`, `ps`).
- **Impact:** Cannot invoke REA's automated firmware extraction on Windows.
- **Mitigation / Status:** The firmware rootfs (`filesystem/rootfs/`) and archives (`filesystem/archives/apps-filesystem.tar`) have already been fully extracted and validated with SHA-256 in the baseline archive. No further firmware carving is necessary.

### 3. Missing JDK 21+ for Standalone Ghidra
- **Observed Behavior:** The host machine has OpenJDK 1.8 (`1.8.0_442`), but lacks JDK 21+ required by modern Ghidra 11/12 distributions.
- **Status:** In accordance with non-negotiable safety rules, no third-party package managers or bulk runtimes will be installed without user instruction. Python Capstone covers all disassembly requirements without external dependencies.

### 4. Router BusyBox Utility Limitations
- **Observed Behavior:** The live router's BusyBox build is known to lack standard utilities such as `awk`, `od`, `strings`, `file`, and `hexdump`.
- **Rule:** All static inspection and extraction must be executed locally on the Windows host. Under no circumstances will live commands be executed on the router to inspect data that can be parsed statically from the firmware dump.

