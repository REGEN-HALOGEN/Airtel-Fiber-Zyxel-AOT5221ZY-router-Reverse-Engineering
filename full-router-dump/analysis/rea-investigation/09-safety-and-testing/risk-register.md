# Risk Register & Failure Mode Analysis

| Risk ID | Hazard Description | Likelihood | Impact | Severity | Mitigation Strategy |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **RSK-001** | **`linkdetection` Clobbers ACS URL**<br>Daemon auto-switches to ETHER and overwrites `ManagementServer.URL` to `:8103`. | Low | High | Medium | **Mitigation:** Explicitly set `WanAutoDetect = 0` before any mode change. Disassembling proved `0x401e10` skips all transition checks when 0. |
| **RSK-002** | **Disruption of LAN3 Access Point Uplink**<br>LAN3 port is accidentally reassigned to WAN, isolating local network. | Zero | Critical | Low | **Mitigation:** Switch hardware mask `0x08` strictly binds Port 3 (LAN4). Port 2 (LAN3, mask `0x04`) remains in `br0`. Guaranteed by `HW-002`. |
| **RSK-003** | **Persistent Bricking via Flash Corruption**<br>Corrupt configuration written to NOR/NAND flash partitions. | Zero | Critical | Low | **Mitigation:** Strict prohibition against MTD/UBI flashing. Configuration is applied exclusively via CCC runtime commands in memory. |
| **RSK-004** | **PPPoE Authentication Failure**<br>Incorrect credentials, service name, or auth protocol refusal. | Medium | Medium | Medium | **Mitigation:** Pre-verify credentials on laptop; set `PPPoEServiceName` to `3jglobal` and protocol to `AUTO_AUTH`. |
| **RSK-005** | **ISP VLAN Mismatch**<br>ISP requires 802.1Q tagged frames (e.g. VID 100), but `nas0_notag` emits untagged frames. | Medium | Medium | Medium | **Mitigation:** Test untagged first; if PADI times out, update RDM parameters `X_5067F0_Enable_VLANID = 1` and `X_5067F0_VLANID = <VID>`. |
| **RSK-006** | **RDM Database Inconsistency**<br>Malformed CCC command creates orphan RDM objects. | Low | Medium | Low | **Mitigation:** Execute pre-flight `ccctest -d` dump, parse syntax locally, and verify exact OID hierarchy before sending. |

