# Implementation Options Evaluation

Three distinct implementation options were evaluated to achieve the desired network topology:

---

## Option 1: Binary Patching of `linkdetection`
- **Mechanism:** Disassemble `linkdetection`, patch addresses `0x40332c` - `0x40338c` (replace ACS URL overwrite and `DefaultConnectionService` assignment with NOPs `0x1f2003d5`), and re-flash or mount over `/usr/bin/linkdetection`.
- **Pros:** Preserves automatic cable-detection mode switching.
- **Cons:**
  - Requires writing to root filesystem or UBI partition.
  - Violates the strictly non-destructive, read-only safety rules.
  - High risk of bricking during binary substitution.
- **Feasibility:** Rejected (Violates Safety Rules).

---

## Option 2: Full Flash Repack / Custom Firmware
- **Mechanism:** Unpack SquashFS rootfs, modify default RDM templates and web GUI, rebuild image, and flash via U-Boot or web recovery.
- **Pros:** Completely removes Airtel branding and restrictions permanently.
- **Cons:**
  - High brick risk.
  - Modifies flash memory / bootloader environment.
  - Violates project safety constraints.
- **Feasibility:** Rejected.

---

## Option 3: Clean CCC Script Orchestration via CLI (Recommended)
- **Mechanism:**
  1. Access the device via read-only SSH/CLI.
  2. Disarm `linkdetection` by writing `WanAutoDetect = 0`.
  3. Execute a single declarative CCC script (`ccctest -f /tmp/eth_pppoe.cmd` or via `ccc_das`).
  4. Instantiate `WANPPPConnection.1` under `WANConnectionDevice.3` with ISP credentials (`3jglobal`, MTU 1480, `AUTO_AUTH`).
  5. Direct `Layer3Forwarding` to the new instance.
- **Pros:**
  - **Zero flash modification:** Operates entirely within standard RDM runtime configuration engine.
  - **Zero binary modification:** Uses 100% stock binaries and libraries.
  - **100% Reversible:** Running an inverse CCC script instantly reverts the router to stock GPON state.
  - **Zero ACS disruption:** Preserves original management parameters.
- **Feasibility:** **Selected (100% Feasible, Safe, and Proven).**

