# Transition Comparison: Linkdetection vs Clean CCC Orchestration

## 1. Executive Summary
Two distinct mechanisms exist to transition the router into Ethernet WAN mode:
1. **Vendor Daemon Execution (`linkdetection` routine `0x402454`):** Dangerous and destructive.
2. **Clean CCC Orchestration (`ccc_das` via RDM):** Safe, controlled, and reversible.

## 2. Comparative Matrix

| Evaluation Criterion | Vendor `linkdetection` Routine | Clean CCC Orchestration (`ccc_das`) |
| :--- | :--- | :--- |
| **Trigger Mechanism** | Polling Port 3 PHY link state for 6 ticks | User-controlled command execution via `ccc_das` |
| **ACS URL Side Effect** | **Clobbers ACS URL** to test server (`:8103`) | **ACS URL untouched** (retains Airtel production URL) |
| **Profile Selection** | Forces IP/DHCP (`Eth_Internet`, TR069) | Directly provisions `Eth_PPPoE` (Internet, PPPoE) |
| **Default GW Assignment**| Overwrites to `WANIPConnection.1` | Points cleanly to `WANPPPConnection.1` |
| **Reversibility** | Hard to revert (auto-switches on link drop) | 100% reversible via inverse CCC script |
| **LAN3 AP Preservation**| Preserves LAN3 (mask `0x08`) | Preserves LAN3 (mask `0x08`) |
| **Safety Verdict** | **CRITICAL RISK** (Breaks TR069 and WAN data) | **SAFE & DETERMINISTIC** |

## 3. Disarming Strategy
By setting:
```
InternetGatewayDevice.X_5067F0_Ext.WANSwitch.WanAutoDetect = 0
```
the `linkdetection` binary is disarmed in its `main` event loop (`0x401e10: b.ne #0x401b7c`). This allows clean CCC orchestration to govern the router without interference from the background daemon.

