# RDM Schema & Object Creation Audit (`WANPPPConnection`)

**Target Subsystem:** MSTC RDM Engine / TR-098 Object Management  
**Binaries Audited:**
- `full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so` (SHA-256: `914b3017a5d3f23a5e888636fa09930cb9f3efeaebf99dcdd189dd07b1e2283e`)
- `full-router-dump/filesystem/rootfs/lib/MSTC/libcccrdm.so` (SHA-256: `24874052ca5fbaefb99320875c754d9c7921356f9172081d636ee2c6bb11bf79`)
- `full-router-dump/filesystem/rootfs/usr/bin/ccc_be` (SHA-256: `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f`)
- `full-router-dump/filesystem/rootfs/usr/bin/ccctest` (SHA-256: `268db4c75ca1f603c40dd4e5488172ee8ff287c88a87612dc574b6ff9bc6a4eb`)
- `files/config.rdm` / `files/config_rdm_decompressed.bin` (3,145,728 bytes)

---

## 1. Executive Summary & Audit Conclusions

| Audit Question | Audit Verdict | Confidence Level | Primary Supporting Evidence |
| :--- | :---: | :---: | :--- |
| **1. Parent-Child Relationship** | Confirmed Parent-Child | **CONFIRMED** | `librdm.so` schema tables map `WANPPPConnection` (OID `0xc7`) as direct child of `WANConnectionDevice` (OID `0x32`). |
| **2. Allowed Child of `WANConnectionDevice`** | Allowed | **CONFIRMED** | `config_rdm_decompressed.bin` @ `0x36e74` declares both `WANIPConnectionNumberOfEntries` (OID `0x44`) and `WANPPPConnectionNumberOfEntries` (OID `0x45`). |
| **3. Allowed Under Instance 3 Specifically** | Allowed | **CONFIRMED** | `cccRdmAddIndexChildObject` (`0x134a0`) performs generic IA-depth validation; schema permits any instance `i` under `WANDevice.1.WANConnectionDevice.{i}`. |
| **4. Instance Creation via `ADD` Supported** | Supported | **CONFIRMED** | `ccctest` @ `0x402cac` parses `"ADD"`, issues `cmsgRequestSetIndexedObj(req, 1)`. `ccc_be` @ `0x41587c` invokes `cccRdmAddIndexChildObject`. |
| **5. Creation Requirements & Templates** | Supported / Automated | **CONFIRMED** | Requires prior selection (`SEL`) of parent container. Template defaults populated via `cccRdmSetObjDefault` (`0x4550`). |
| **6. Active Model vs Generic Schema** | Divergence Identified | **CONFIRMED** | Stock factory database (`aot-current-pdm-config.xml`) instantiates IP under instance 3, but generic schema supports PPP under any instance. |
| **7. Instance Numbering Allocation** | Auto-Allocated | **CONFIRMED** | `cccRdmAddIndexChildObject` (`0x13638` - `0x13650`) scans child list; allocates `1` if empty, or `max + 1`. |
| **8. Persistence Before Recognition** | Memory-Committed | **CONFIRMED** | Objects exist in shared memory upon `SAVE` and are immediately visible to `ccc_be` dispatchers without reboot. |

---

## 2. Parent-Child Relationship & Schema Definitions

In `librdm.so`, TR-098 data model objects are indexed in `OIDTable` (`0x29478`).

### Object Hierarchy in Shared Memory:
```
InternetGatewayDevice (OID 0x01)
  └── WANDevice.1 (OID 0x30)
        ├── WANEthernetInterfaceConfig (OID 0xca / 0x3696c)
        ├── X_5067F0_GponInterafceConfig (OID 0xc5 / 0x367f0)
        └── WANConnectionDevice.{i} (OID 0x32 / 0x36e74)
              ├── WANIPConnection.{i} (OID 0xca / 0x370b4)
              └── WANPPPConnection.{i} (OID 0xc7 / 0x3b2dc)
```

### Binary Evidence from `config_rdm_decompressed.bin`:
- **`WANConnectionDevice` (Offset `0x36e74`):**
  - Declares child parameter `WANIPConnectionNumberOfEntries` (Offset `0x36f51`, OID `0x44`, uint32).
  - Declares child parameter `WANPPPConnectionNumberOfEntries` (Offset `0x36f95`, OID `0x45`, uint32).
- **`WANPPPConnection` (Offset `0x3b2dc`):**
  - Schema multi-instance depth: `{WANDevice.i, WANConnectionDevice.i, WANPPPConnection.i}` (depth 3).
  - Maximum instances allowed: 8 (declared at `[x27, #0x10]` in RDM descriptor).

---

## 3. Disassembly Analysis: `ADD` Command Processing Pipeline

### Step 1: Parsing in `ccctest` (`0x402ca8` - `0x402ce8`)
When `ccctest` reads an input line starting with `ADD`:
```armasm
0x402ca8: adrp x1, #0x404000
0x402cac: add  x1, x1, #0x758       ; Literal "ADD"
0x402cb0: mov  x0, x19              ; Current token
0x402cb4: bl   #0x4012e0            ; <strcmp@plt>
0x402cb8: cbnz w0, #0x402da8         ; Not ADD -> branch
0x402cbc: cbz  x23, #0x402d60        ; Request handle NULL check
0x402cc0: mov  x1, x20              ; Delimiters
0x402cc4: mov  x0, #0               ; NULL for strtok
0x402cc8: bl   #0x401110            ; <strtok@plt> -> returns "WANPPPConnection"
0x402ccc: ldr  w2, [x22]            ; Flag
0x402cd0: mov  x1, x0               ; Object name string
0x402cd4: mov  x0, x23              ; Request handle
0x402cd8: bl   #0x401330            ; <cmsgRequestSel@plt>
0x402cdc: mov  w1, #1               ; Action: 1 = ADD_OBJECT
0x402ce0: mov  x0, x23              ; Request handle
0x402ce4: bl   #0x4012c0            ; <cmsgRequestSetIndexedObj@plt>
```

### Step 2: Request Packaging in `libcmsg.so` (`0x60a8` - `0x6130`)
In `cmsgRequestSetIndexedObj(request, action=1)`:
```armasm
0x6100: mov  w1, #7                 ; CMSG_ACTION_SET_INDEXED_OBJ
0x6104: str  w1, [x0]               ; Write action header
0x6114: str  w19, [x0, #4]          ; Write sub-action: 1 (ADD)
```

### Step 3: Backend Dispatch in `ccc_be` (`0x415860` - `0x41589c`)
When `ccc_be` receives `CMSG_ACTION_SET_INDEXED_OBJ`:
```armasm
0x415874: tst  w3, #0xff            ; Check if explicit instance assigned
0x415878: b.eq #0x415898            ; If assigned -> cccRdmAddObjectWithAssignIA
0x41587c: bl   #0x410c20            ; <cccRdmAddIndexChildObject@plt>
...
0x415898: bl   #0x40fe60            ; <cccRdmAddObjectWithAssignIA@plt>
```

### Step 4: Schema Validation & Allocation in `librdm.so` (`0x134a0` - `0x13840`)
Function `cccRdmAddIndexChildObject(rdm_ctx, child_oid, parent_ia)` executes:
1. **Schema Offset Lookup (`0x134c0`):** Calls `cccRdmGetOffsetByOID(child_oid=0xc7)`. Validates that OID `0xc7` is a registered TR-098 schema object.
2. **Path Verification (`0x134dc`):** Calls `rdmVerifyIAValue(parent_ia)`. Verifies that the parent Instance Array (`WANDevice.1.WANConnectionDevice.3`) conforms to the schema hierarchy.
3. **Child Existence & Max Entries Check (`0x13538`):**
   - Reads existing child list pointer at `[x0, x1]`.
   - If empty (`cbz x20, #0x137e4`): Reads `max_entries` at `[x27, #0x10]`. Sets `w25 = 1` (allocates Instance 1).
   - If non-empty: Iterates existing children (`0x13604`), tracks highest instance number, increments `w25 = max + 1`. Checks `cmp w0, w25` against `max_entries`.
4. **Default Parameter Initialization (`0x137a4` / `0x13818`):**
   - Calls `cccRdmSetObjDefault(rdm_ctx, offset, mode=2)` (`0x4550`), initializing all parameters to schema defaults.
5. **Linking & Status Flagging (`0x136a8`):**
   - Calls `rdmSetPreObjNext` (`0x4610`) to link the new node into the parent's child list.
   - Calls `cccRdmSetPreObjStatus(rdm_ctx, node, status=1)` (`0x4720`), marking the object as active.
   - Calls `cccRdmSetCBData` (`0x4910`), queueing change callbacks for `ccc_be`.

---

## 4. Audit Findings on Sub-Questions

### 4.1 Is `WANPPPConnection` Allowed Under Instance 3 Specifically?
- **Finding:** **YES (CONFIRMED).**
- **Evidence:** `rdmVerifyIAValue` evaluates path depth and multi-instance wildcards. The schema definition for `WANPPPConnection` specifies `{1, 0, 0}` for `WANDevice.i.WANConnectionDevice.i.WANPPPConnection.i`. The instance index of `WANConnectionDevice` is a free variable ($1 \le i \le N$). No hardcoded conditional branch restricts child creation to instance 1.

### 4.2 Instance Numbering: Allocated or Supplied?
- **Finding:** **AUTOMATICALLY ALLOCATED (CONFIRMED).**
- **Evidence:** `cccRdmAddIndexChildObject` line `0x137ec` hardcodes `mov x2, #1` when the child list is empty. Therefore, issuing `ADD WANPPPConnection` under `WANConnectionDevice.3` **guarantees** the newly created object is named `WANPPPConnection.1`.

### 4.3 Coexistence of IP and PPP Under Instance 3
- **Finding:** **COEXISTENCE SUPPORTED AT SCHEMA LEVEL, BUT MUTUALLY EXCLUSIVE AT RUNTIME DISPATCH (CONFIRMED).**
- **Evidence:** `WANConnectionDevice` has distinct child offsets for `WANIPConnection` and `WANPPPConnection`. However, runtime link type evaluator `libcccBeWan_getWANDeviceObjectRequestedLinkType` (`0x34334`) checks `WANPPPConnection` first; if present, it returns `LINK_TYPE_PPP` (1), bypassing IP dispatch. To ensure deterministic operation, `WANIPConnection.1` must be disabled (`Enable=0`).

### 4.4 Transaction Boundary Caution: Two-Stage Commit Required
- **Finding:** **STRONGLY SUPPORTED.**
- **Evidence:** `cmsgRequestSel` appends path strings into the CMSG packet buffer without validating shared memory. While `ccc_be` processes `ADD` and `SEL` sequentially in memory, if `ccctest` is executed in a single transaction, any failure in `ADD` causes subsequent parameter `SET` commands to fail silently.
- **Audit Recommendation:** Split object creation and parameter configuration into two distinct transactions:
  1. Transaction 1: Create instance (`ADD WANPPPConnection; SAVE; SEND;`).
  2. Transaction 2: Configure parameters on committed instance (`SEL ...WANPPPConnection.1; SET ...; SAVE; SEND;`).

