# Activity Log — REA Investigation

## 2026-11-05
- **15:00:** Began Phase 0 initialization following Master Project Directive.
- **15:05:** Audited `full-router-dump` archive hierarchy, verified `README.md`, `FILE_INVENTORY.csv`, `FOLDER_TREE.txt`.
- **15:10:** Audited prior research reports in `analysis/reports/technical_report_pppoe_nas0_notag.md`.
- **15:15:** Executed REA diagnostics (`rea doctor`, `rea setup --dry-run`).
- **15:20:** Verified Antigravity MCP server configuration in `C:\Users\REGEN\.gemini\config\mcp_config.json`.
- **15:25:** Tested REA native analysis on AArch64 ELF (`linkdetection`); captured `target_format_unsupported` error.
- **15:30:** Verified Windows-native Python disassembler (`capstone` 5.0.9) and ELF parser (`pyelftools` 0.33).
- **15:35:** Verified Capstone disassembly of `linkdetection` routine `0x402454`.
- **15:40:** Created `analysis/rea-investigation/` directory hierarchy with junction to `AirtelModemRev\analysis\rea-investigation`.
- **15:45:** Generated baseline and environment reports across `00-project-baseline/` and `01-environment-and-rea/`.
- **15:50:** Computed authoritative SHA-256 digests for key ELF binaries and modules.
- **16:00:** Verified user installation of JDK 21 at `C:\Program Files\Eclipse Adoptium\jdk-21.0.13.9-hotspot`.
- **16:05:** Authored Python disassembly script `working/scripts/disasm_linkdetection.py`; dumped 1,081 annotated instructions of `0x402454` to `evidence/disassembly/linkdetection_0x402454.asm`.
- **16:10:** Recovered symbol `linkdetect_switch_WanMode`; resolved all PLT call targets (`cmsg*`, `rdm*`, `rt_port_link_get`).
- **16:15:** Traced ACS URL clobbering to `http://testacs.airtelbroadband.in:8103/` in ETHER branch (`0x403364`).
- **16:20:** Discovered hardcoded PHY Port 3 (`mov w0, #3` at `0x40223c`) and optical power polling via `diag pon get transceiver rx-power` (`0x402244`).
- **16:25:** Proved that `WanAutoDetect = 0` completely neutralizes `linkdetection` mode switching.
- **16:30:** Authored all 7 Phase 2 reports under `03-ethernet-wan/`.
