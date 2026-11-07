# RDM Evidence Index — Offsets & Hex Dumps

## 1. `WANSwitch` (Offset `0x227d0`)
```
50 00 00 00 44 00 00 00 03 00 01 00 32 00 00 00 57 41 4e 53 77 69 74 63 68 ...
```
- Parameters: `WanAutoDetect`, `WANMode`.

## 2. `WANEthernetInterfaceConfig` (Offset `0x3696c`)
```
78 01 00 00 0c 01 00 00 09 00 00 00 32 00 00 00 57 41 4e 45 74 68 65 72 6e 65 74 49 6e 74 65 72 66 61 63 65 43 6f 6e 66 69 67 ...
```
- Parameters: `Enable`, `Status`, `X_5067F0_IfName`.

## 3. `WANConnectionDevice` (Offset `0x36e74`)
```
00 00 00 00 00 00 00 00 00 00 01 00 32 00 00 00 57 41 4e 43 6f 6e 6e 65 63 74 69 6f 6e 44 65 76 69 63 65 ...
```
- Multi-instance child counts:
  - `WANIPConnectionNumberOfEntries` (Offset `0x36f51`, OID `0x44`).
  - `WANPPPConnectionNumberOfEntries` (Offset `0x36f95`, OID `0x45`).

## 4. `WANPPPConnection` (Offset `0x3b2dc`)
```
00 00 00 00 00 00 00 00 00 00 00 00 32 00 00 00 57 41 4e 50 50 50 43 6f 6e 6e 65 63 74 69 6f 6e ...
```
- Child of `WANConnectionDevice` instantiated at runtime via `ADD WANPPPConnection`.

