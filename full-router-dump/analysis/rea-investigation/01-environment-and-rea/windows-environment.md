# Windows 11 Operating Environment

## Host Specifications
- **Operating System:** Windows 11 Pro 64-bit (`win32 x64`)
- **Shell:** PowerShell 7.6.9 (`pwsh`)
- **Active Workspace:** `C:\Users\REGEN\AirtelModemRev`
- **Authoritative Archive:** `C:\Users\REGEN\AirtelModemRev\full-router-dump`
- **IDE:** Google Antigravity IDE (Antigravity Agent Mode)

## Installed Language Runtimes
| Runtime | Executable Path / Command | Version | Role in Project | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Node.js** | `C:\Program Files\nodejs\node.exe` | `v26.12.1` | REA agent execution, MCP server lifecycle | Operational |
| **npm** | `C:\Program Files\nodejs\npm.cmd` | `11.20.0` | Package manager, npx cache runner | Operational |
| **Python** | `python.exe` | `3.12.10` | Binary parsing, Capstone disassembly, RDM decoding | Operational |
| **PowerShell** | `pwsh.exe` | `7.6.9` | Primary automation shell, file management | Operational |
| **Java** | `java.exe` | `1.8.0_442` (Temurin) | Legacy runtime (Ghidra 12 requires JDK 21+) | Incompatible with Ghidra |

## Non-Negotiable Environment Constraints
- **NO WSL / Linux Containers:** No Windows Subsystem for Linux, Linux VMs, or Docker containers are permitted.
- **Strictly Windows-Native:** All execution scripts and analysis tools must run directly under native Windows 11 win32/x64 environment.

