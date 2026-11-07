# Airtel AOT5221ZY (Zyxel PX5311-R0) Reverse Engineering

[![SoC: Realtek RTL9607C](https://img.shields.io/badge/SoC-Realtek_RTL9607C-blue.svg)](https://www.realtek.com/)
[![Arch: AArch64](https://img.shields.io/badge/Arch-AArch64_Cortex--A53-orange.svg)]()
[![Kernel: Linux 5.10.138](https://img.shields.io/badge/Kernel-Linux_5.10.138-green.svg)]()
[![Protocol: PPPoE over Ethernet](https://img.shields.io/badge/WAN-PPPoE_over_LAN4-purple.svg)]()
[![Methodology: 100% Read-Only](https://img.shields.io/badge/Audit-Strictly_Read--Only-red.svg)]()

> **Master Repository for Deep Reverse-Engineering the Airtel AOT5221ZY Wi-Fi 6 GPON ONT Router (Zyxel PX5311-R0 OEM, Realtek Taurus Platform) to Enable Native Ethernet WAN and ISP PPPoE.**

---

## 📋 Table of Contents

- [Overview & Mission](#-overview--mission)
- [Target Hardware & Platform](#-target-hardware--platform)
- [Executive Summary of Discoveries](#-executive-summary-of-discoveries)
- [Repository Structure](#-repository-structure)
- [Deep Dive: Subsystem Analysis](#-deep-dive-subsystem-analysis)
  - [1. Switch Port Mapping & Hardware Masks](#1-switch-port-mapping--hardware-masks)
  - [2. Virtual Network Layer (`nas0_notag`)](#2-virtual-network-layer-nas0_notag)
  - [3. Backend WAN Configuration Stack](#3-backend-wan-configuration-stack)
  - [4. RDM Database & CMSG IPC Mechanics](#4-rdm-database--cmsg-ipc-mechanics)
  - [5. Web Interface Backend (`broadband.cgi`)](#5-web-interface-backend-broadbandcgi)
- [Cryptographic Proofs & Evidence Verification](#-cryptographic-proofs--evidence-verification)
- [Windows-Native Analysis Environment](#-windows-native-analysis-environment)
- [Safety Protocol & Project Roadmap](#-safety-protocol--next-steps)

---

## 🎯 Overview & Mission

The **Airtel AOT5221ZY** is a high-performance Wi-Fi 6 (802.11ax) dual-band residential gateway manufactured by **Zyxel (PX5311-R0)** on the **Realtek Taurus (RTL9607C)** platform. The stock firmware provided by Bharti Airtel is configured to route WAN traffic exclusively across the integrated GPON optical interface (`nas0_0` over SerDes / optical transceiver, Port Mask `0x80`).

### Objective
Enable **Ethernet WAN** operation through physical **LAN4** (Switch Port 3, Port Mask `0x08`) using an external upstream GPON ONT (Syrotech) as an Ethernet handoff, establishing a native **PPPoE** connection to the local ISP (`3jglobal`, MTU 1492), while keeping the factory Wi-Fi 6 wireless access point and LAN switching configurations 100% intact.

### Rule of Operation
Strictly evidence-backed, **zero-guesswork**, read-only firmware reverse engineering. No speculative flashing, no blind NVRAM writes, no firmware patching without verified disassembly proof.

---

## 🔬 Target Hardware & Platform

| Parameter | Specification |
| :--- | :--- |
| **Device Model** | Airtel AOT5221ZY |
| **OEM Base Model** | Zyxel PX5311-R0 |
| **System-on-Chip (SoC)** | Realtek Taurus RTL9607C (Chip ID `0x6706`) |
| **CPU Architecture** | Dual-Core ARM Cortex-A53 (AArch64 Little-Endian) |
| **Operating System** | Embedded Linux 5.10.138 (OpenWrt 22.03-derived hybrid) |
| **Kernel Modules** | `ca-rtk.ko` (Switch/MAC), `ca-ne.ko` (Network Engine/SerDes), `fc_8277c.ko` (Fastpath Flow Control) |
| **Configuration Engine** | Zyxel / MSTC CCC (`ccc_be`, `ccc_das`, `libcmsg.so`, `libcccrdm.so`, `librdm.so`) |
| **Storage Structure** | SPI NAND Flash, UBI Volumes, SquashFS + UBIFS |

---

## ⚡ Executive Summary of Discoveries

Through systematic static reverse engineering across 16 major audit phases:

1. **Hardware Ethernet WAN Port Confirmed**: Switch port 3 (physical LAN4) is the platform's hardware Ethernet WAN port. In GPON mode, its port mask bit (`0x08`) is part of the LAN bridge. In Ethernet WAN mode, `rtk_wan_port_mapping(0, "nas0")` removes port 3 from LAN and maps it to `nas0`.
2. **Interface Demultiplexing**: The Realtek SMUX subsystem creates `nas0_notag` for untagged traffic and `nas0_<vlan>` for 802.1Q tagged traffic.
3. **PPPoE Launcher Compatibility**: The stock `/bin/pppd` and `libCmd.so` templates natively support launching PPPoE sessions over `nas0_notag` via `/etc/ppp/options_<ifname>`.
4. **Data Model (RDM) Schema**: The router's configuration database uses standard TR-098 / TR-181 OIDs. GPON lives under `WANDevice.1.WANConnectionDevice.1`, while Ethernet WAN lives under `WANDevice.1.WANConnectionDevice.3`.
5. **Backend Transaction Flow**: Switching WAN mode from IP to PPPoE in the stock firmware requires an atomic CMSG transaction: deleting the existing `WANIPConnection` (`OID 0xcd`), allocating a new IA via `rdmGetAvaliableIAByOID` (`OID 0xe3`), creating `WANPPPConnection`, populating credentials, and executing `cmsgRequestSave` followed by `cmsgRequestSend`.

---

## 📁 Repository Structure

```
AirtelModemRev/
├── README.md                                  # Primary repository overview and technical synthesis
├── .gitignore                                 # Git rules (filters raw flash dumps, private certs, temp files)
├── REVERSE_ENG.md                             # Authoritative 16-phase reverse engineering chronicle
├── REVERSE ENG.md                             # Synchronized mirror of the master report
│
├── analysis/                                  # High-level disassembly scripts, symbols, and decoded configs
│   ├── check_rdm_records.py                   # RDM database parser
│   ├── config_rdm_decoded.xml                 # Decoded factory RDM XML schema
│   ├── disasm.py                              # AArch64 Capstone disassembly utility
│   ├── dynsym_*.txt                           # Dynamic symbol tables of core daemons/libraries
│   ├── disasm/                                # Disassembly listings of key firmware functions
│   │   ├── beConfigWANByPPPoE.txt             # Disassembly of libbemodules WAN PPPoE builder
│   │   ├── beWanDoLayer3InterfaceAction_PPP.txt
│   │   ├── beWanEnablePPPv4Client.txt         # Disassembly of PPPv4 client activation
│   │   ├── constructL3WANDevName.txt          # Disassembly of Layer 3 device naming
│   │   ├── createWANPPPConnectionCfgFile.txt  # Disassembly of PPP options file generator
│   │   ├── libcccBeWan_eth_Init.txt           # Disassembly of Ethernet WAN port initializer
│   │   ├── rtk_wan_port_mapping.txt           # Disassembly of Realtek switch port mapping
│   │   └── setWanIpPppInterfaceName.txt       # Disassembly of PPP interface naming
│   └── reports/                               # High-level inventory and architecture summaries
│
├── DUMPFILES/                                 # Isolated target binaries, kernel modules, and test scripts
│   ├── broadband.cgi                          # Web WAN configuration backend binary
│   ├── ca-rtk.ko, ca-ne.ko, fc_8277c.ko       # Realtek hardware switch & network engine drivers
│   ├── ccc_be, ccc_das, ccctest.bin           # CCC management daemon, agent, and test CLI
│   ├── libbemodules.so, libcccbe.so           # Central WAN management backend shared objects
│   ├── libcmsg.so, libcccrdm.so, librdm.so    # CMSG IPC and RDM database access libraries
│   ├── aot-current-pdm-config.xml             # Exported PDM configuration backup
│   └── config.rdm                             # Factory default RDM database
│
└── full-router-dump/                          # Complete firmware research repository
    ├── FILE_INVENTORY.csv                     # Exhaustive file manifest with sizes and timestamps
    ├── FOLDER_TREE.txt                        # Complete directory layout tree
    ├── README.md                              # Evidence handling protocols and storage guide
    │
    ├── analysis/
    │   ├── rea-investigation/                 # Systematic investigation directories (Phases 00 to 10)
    │   │   ├── 00-project-baseline/           # Baseline hardware and firmware audit
    │   │   ├── 01-environment-and-rea/        # Windows-native toolchain validation
    │   │   ├── 02-firmware-architecture/      # Boot, kernel, and process architecture
    │   │   ├── 03-ethernet-wan/               # Physical LAN4 switch mapping audit
    │   │   ├── 04-pppoe/                      # Native pppd and options file generator
    │   │   ├── 05-rdm/                        # RDM database schema & record layout
    │   │   ├── 06-network-integration/        # Layer 3 forwarders, routing, and NAT
    │   │   ├── 07-gpon-vs-ethernet/           # GPON vs. Ethernet WAN execution differences
    │   │   ├── 08-implementation-research/    # CMSG transaction mechanics
    │   │   ├── 09-safety-and-testing/         # Rollback triggers and survival criteria
    │   │   ├── 10-final-reports/              # Architectural sign-offs
    │   │   ├── PROJECT_STATUS.md              # Milestone tracking ledger
    │   │   ├── RESEARCH_LOG.md                # Chronological research session logs
    │   │   ├── MASTER_FINDINGS.md             # Canonical technical finding records (FINDING-001..RDM-004)
    │   │   ├── NEXT_STEPS.md                  # Prioritized action plan
    │   │   └── working/                       # Decompilation scripts and assembly dumps
    │   │       ├── broadband_cgiMain_disasm.txt
    │   │       └── scripts/                   # Specialized Python analysis utilities
    │   └── reports/                           # Hash manifests, slot diffs, and binwalk signatures
    │
    ├── filesystem/
    │   ├── rootfs/                            # Complete extracted Linux 5.10 AArch64 root filesystem
    │   └── rootfs-symlinks.json               # Symbolic link reconstruction manifest
    │
    ├── flash/                                 # Cryptographic manifests for raw flash partitions
    │   ├── physical-mtd-sha256.csv            # SHA-256 manifest of raw physical MTD partitions
    │   └── ubi-volumes-sha256.csv             # SHA-256 manifest of raw UBI volumes
    │
    ├── hardware/                              # Device tree artifacts
    │   ├── device-tree.dtb                    # Compiled Device Tree Blob
    │   └── router-device-tree.dts             # Decompiled Device Tree Source
    │
    ├── inventory/                             # System memory and flash partition layout documentation
    └── private-volumes/                       # Hash manifests for private volumes
        └── private-volumes-sha256.csv         # Cryptographic record for private identity blocks
```

---

## 🔍 Deep Dive: Subsystem Analysis

### 1. Switch Port Mapping & Hardware Masks
- **Binary:** `/lib/MSTC/libcccbe.so` (`libcccBeWan_eth_Init` at `0x37c84`).
- **Driver:** `/lib/modules/5.10.138/ca-rtk.ko`.
- **Operation:**
  Calls `rtk_wan_port_mapping(0, "nas0")`, which invokes IOCTL commands on the Realtek switch driver.
  - Port 0: LAN1 (Mask `0x01`)
  - Port 1: LAN2 (Mask `0x02`)
  - Port 2: LAN3 (Mask `0x04`)
  - **Port 3: LAN4 (Mask `0x08`)** &larr; **Physical Ethernet WAN Target**
  - Port 7: GPON Optical SerDes (Mask `0x80`)

### 2. Virtual Network Layer (`nas0_notag`)
- **Binary:** `/bin/smuxctl`.
- Realtek SMUX handles tagged/untagged packet steering.
- The Ethernet WAN lower-layer interface is initialized as `nas0`.
- For untagged PPPoE handoffs (standard Indian fiber ISP handoff via external ONT), `smuxctl` registers `nas0_notag`.
- PPPoE options generator binds `pppd` to `nas0_notag`.

### 3. Backend WAN Configuration Stack
- **Daemon:** `ccc_be` (CCC Backend Engine).
- **Core WAN Module:** `libbemodules.so`.
- **Functions:**
  - `beConfigWANByPPPoE` (`0x664a8`): Formulates options files (`/etc/ppp/options_ppp131`), binds interface names, parses MTU/MRU, and configures authentication protocol.
  - `createWANPPPConnectionCfgFile` (`0x6a7c0`): Writes configuration parameters to disk.
  - `beWanEnablePPPv4Client` (`0x66ee4`): Triggers client activation.
  - `beWanDoLayer3InterfaceAction` (`0x6bf78`): Configures default route, NAT, and firewall rules upon link acquisition.

### 4. RDM Database & CMSG IPC Mechanics
- Configuration is not stored in plain flat files; it is governed by the **RDM (Relational Data Model)** database.
- Inter-process communication uses **CMSG (Configuration Message Service)** via UNIX domain sockets:
  - `cmsgCreateRequest()`: Initiates a transaction.
  - `cmsgRequestSelId()`: Selects target OID and Instance Address (IA).
  - `cmsgRequestSetIndexedObj()`: Deletes (`0`) or creates (`1`) child objects.
  - `cmsgRequestSet()`: Applies parameter updates.
  - `cmsgRequestSave()`: Writes persistent state to `/data/config.rdm`.
  - `cmsgSendRecv()`: Commits transaction to `ccc_be` and triggers backend callbacks.

### 5. Web Interface Backend (`broadband.cgi`)
- **Binary:** `/www/cgi-bin/broadband.cgi` (61,760 bytes AArch64 ELF).
- **Endpoint:** Handles POST requests from the Broadband WAN configuration web GUI.
- **Conversion Workflow:**
  When switching from Ethernet DHCP (`WANIPConnection`) to Ethernet PPPoE (`WANPPPConnection`):
  1. Identifies existing child `WANIPConnection` under `WANConnectionDevice.3` (OID `0xcd`).
  2. Preserves existing port triggering entries in a temporary linked list.
  3. Executes `cmsgRequestSetIndexedObj(req, 0)` &rarr; **Deletes old WANIPConnection**.
  4. Calls `rdmGetAvaliableIAByOID(rdmCB, 0xe3, parentIA)` &rarr; **Dynamically allocates new WANPPPConnection instance**.
  5. Executes `cmsgRequestSetIndexedObj(req, 1)` &rarr; **Creates new WANPPPConnection**.
  6. Sets `Username`, `Password`, `PPPoEServiceName`, `MaxMTUSize`, `NATEnabled`, `Enable=1`.
  7. Commits via `cmsgRequestSave` and `cmsgSendRecv`.

---

## 🔒 Cryptographic Proofs & Evidence Verification

Every firmware binary analyzed in this project is verified against SHA-256 digests computed directly from source dumps:

| Target File | Extracted Size | SHA-256 Digest |
| :--- | :---: | :--- |
| `broadband.cgi` | 61,760 B | `6a43d922bb0db5dfd3fdf21187d995c613ca9c3629f1d044bb71f021ee53b062` |
| `libbemodules.so` | 1,074,680 B | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` |
| `libcccbe.so` | 377,312 B | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` |
| `ccc_be` | 122,064 B | `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f` |
| `ccc_das` | 112,704 B | `911685fbebbd6278f43c24427e13a9b6aeb339c57581add2ce3cff325cc4c5ab` |
| `pppd` | 236,432 B | `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596` |
| `smuxctl` | 53,616 B | `3b97d99f84f242f4774906116e84073570029efa1066381a004e9e0ab5e50638` |
| `librtk.so` | 2,204,184 B | `54f58020848bd4d3b2d34fea1b3687276a367c49495074c297a17aabfc654e0e` |
| `ca-rtk.ko` | 392,040 B | `155ca47508b260c065ff772c3bde2cd708ff0bac96a46f2ab50cec9e38178dc9` |
| `ca-ne.ko` | 3,975,376 B | `fb4166f8ca75e16ba59b0546662151ff1d6201527661cec2bf4b94654cb384d3` |
| `fc_8277c.ko` | 2,088,432 B | `c9116160081ef242f69315e11e408e5423d061cfeedf7b8f235af31ee884ecf0` |
| `config.rdm` | 63,005 B | `fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7` |

---

## 💻 Windows-Native Analysis Environment

All reverse engineering was performed on **Windows 11 Pro 64-bit** without virtual machines, WSL, or Linux hosts:

- **Scripting & Automation**: PowerShell 7 & Python 3.12.10
- **Disassembly Engine**: [Capstone Engine 5.0.9](https://www.capstone-engine.org/) (`CS_ARCH_ARM64`, `CS_MODE_LITTLE_ENDIAN`)
- **ELF Parsing**: [pyelftools 0.33](https://github.com/eliben/pyelftools)
- **Binary Analysis Framework**: NSA Ghidra 11.x for Windows (JDK 21)
- **Symbol Resolution**: Custom AST and basic-block branch tracers implemented in Python.

---

## 🛡️ Safety Protocol & Next Steps

### Safety Guarantees
1. **Read-Only Verification**: All findings derived purely from disassembling unpacked binaries.
2. **Crash-Safe Operations**: No flash memory partitions (`/dev/mtd*`) or UBI volumes will ever be directly written or modified via raw block access.
3. **Rollback Assurance**: Configuration changes will strictly use vendor-supported CMSG/RDM transactions, allowing complete rollback to the factory backup (`ether-backup.lz` / `rollback.ccc`).

### Current Status & Milestones
- [x] Phase 0–14: Hardware port mapping, SMUX untagged interface creation, pppd launcher mechanics, and RDM schema verified.
- [x] Phase 15: Static PPPoE RDM Integration Architecture Audit signed off.
- [ ] Phase 16: Complete `broadband.cgi` web backend POST handler parameter mapping.
- [ ] Phase 17: Live read-only verification of active RDM instances via serial / SSH.
- [ ] Phase 18: Deployment execution of Ethernet WAN PPPoE unlock.

---

## 📄 License & Attribution

This repository is maintained for educational, interoperability, and reverse-engineering research purposes under fair-use provisions for device repurposing and electronic waste reduction. All trademarks, binary names, and firmware components belong to their respective owners (Bharti Airtel Ltd., Zyxel Communications Corp., Realtek Semiconductor Corp.).
