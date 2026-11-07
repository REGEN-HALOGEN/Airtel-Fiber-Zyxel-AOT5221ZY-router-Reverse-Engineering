# REA Provider Status & Analysis Engine Diagnostics

Diagnostics obtained directly via `npx -y rea-agents@6.7.0 analyze` and `capabilities`:

| Provider ID | Provider Name | Configured | Available | Platform Support | Error Code & Diagnostic Reason |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `ghidra` | Ghidra 12.x Engine | No | No | `win32 x64` | `target_format_unsupported`: "Windows Ghidra P0 accepts native PE and explicitly selected raw 6502 targets only." Also `GHIDRA_INSTALL_DIR is not set`. |
| `hopper` | Hopper Disassembler | No | No | macOS / Linux | `unsupported_host`: "Hopper integration is not supported on win32." |
| `ida` | IDA Pro MCP Bridge | No | No | All | `not_configured`: `REA_IDA_MCP_CONFIG` is not set. |
| `kuna` | Kuna Static Analyzer | No | No | All | `not_configured`: `REA_KUNA_COMMAND` is not set. |
| `jadx` | JADX Decompiler | No | No | All | `not_configured`: `REA_JADX_MCP_JAR` is not set. |
| `rea-artifact-graph` | Safe Artifact Graph | Yes | Yes | All | Fully operational (`inspect_artifact`, `extract_artifact`). |
| `rea-dotnet-static` | Managed PE/CLI | Yes | Yes | All | Fully operational (`inspect_managed_artifact`). |
| `sqlite` | SQLite Inspector | Yes | Yes | All | Fully operational (`inspect_sqlite_database`). |
| `native-macos` | macOS Utilities | No | No | macOS | `unsupported_host`: Requires macOS. |

## Detailed Diagnostic Findings
1. **Windows Ghidra Provider Limitation:** REA's built-in Windows Ghidra P0 integration explicitly restricts target formats to Windows PE (Portable Executable) and raw 6502 code. Attempting to open an AArch64 ELF binary via REA Ghidra results in fail-closed rejection:
   ```json
   {
     "provider_id": "ghidra",
     "code": "target_format_unsupported",
     "reason": "Windows Ghidra P0 accepts native PE and explicitly selected raw 6502 targets only."
   }
   ```
2. **Firmware Extraction Providers:** REA commands `extract-firmware` and `inspect-firmware-regions` require Linux Binwalk v3.1+ or Unblob v26.6+ with `prlimit` and a `procps`-compatible `ps`. They are unavailable natively on Windows.
3. **Operational REA Tools:** REA provides CLI artifact graph inspection, safe extraction, SQLite database parsing, and client diagnostics.

