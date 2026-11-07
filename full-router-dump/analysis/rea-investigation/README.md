# Airtel AOT5221ZY REA Reverse Engineering Investigation

## Project Overview
- **Target Device:** Airtel AOT5221ZY (Zyxel PX5311-R0)
- **SoC Platform:** Realtek Taurus (RTL9607C / Chip ID `0x6706`), AArch64 Little-Endian
- **Operating System:** Linux 5.10.138
- **Primary Objective:** Reverse-engineer firmware to determine exact mechanism for enabling Ethernet WAN on LAN4 (PHY port 3, SMUX interface `nas0_notag`) with PPPoE client terminating on external GPON ONT, while preserving LAN3 as the local AP uplink.

## Investigation Directory Structure
```
analysis/rea-investigation/
├── README.md                           # This document
├── PROJECT_STATUS.md                   # Current status, milestones, phase tracking
├── MASTER_FINDINGS.md                  # Comprehensive findings ledger with stable IDs
├── RESEARCH_LOG.md                     # Chronological research activity and decisions
├── NEXT_STEPS.md                       # Ordered tasks, dependencies, and priorities
│
├── 00-project-baseline/                # Baseline archive integrity and prior findings
├── 01-environment-and-rea/             # Windows 11 host, REA, and tool compatibility
├── 02-firmware-architecture/           # Component inventory, daemons, shared libraries
├── 03-ethernet-wan/                    # Ethernet WAN switch, linkdetection, nas0_notag
├── 04-pppoe/                           # PPPoE daemon, options generation, binding
├── 05-rdm/                             # RDM database format, schema, TR-098 objects
├── 06-network-integration/             # Routing, NAT, firewall, DNS, bridging
├── 07-gpon-vs-ethernet/                # Comparative matrix: GPON stack vs Ethernet stack
├── 08-implementation-research/         # Minimal viable unlock options and trade-offs
├── 09-safety-and-testing/              # Risk register, backup requirements, rollback design
├── 10-final-reports/                   # Consolidations, executive summary, conclusion
│
├── evidence/                           # Verified tool outputs, hashes, disasm, decomp
├── working/                            # Scripts, intermediate extractions, scratchpads
└── logs/                               # Activity log, tool execution log, file operation log
```

## Non-Negotiable Operational Rules
1. **Strictly Read-Only:** No flash writes, no MTD/UBI modification, no live RDM writes, no speculative configuration changes on the live router.
2. **Windows 11 Native:** No WSL, no Linux VMs, no Docker. Analysis tools must be Windows-native (PowerShell 7, Python 3.12 with Capstone/pyelftools, REA CLI).
3. **Evidence-Backed Findings:** Every technical claim must specify source file, SHA-256 hash, function address, instruction offset, tool used, and confidence level.
4. **Credential Protection:** Never log, print, or commit ISP PPPoE credentials or private router certificates.

