# PPPoE Authentication Analysis

## Supported Protocols
The firmware supports PAP, CHAP, MS-CHAP, and dynamic auto-negotiation (`AUTO_AUTH`).

## Authentication Parsing in `beConfigWANByPPPoE`
Addresses `0x6670c` - `0x667a4` in `libbemodules.so`:

```armasm
0x6670c: add x1, x1, #0x6d8   ; "PAP"
0x66714: bl  #0x1e4a0          ; strcmp
0x66720: add x1, x1, #0x728   ; "CHAP"
0x66728: bl  #0x1e4a0          ; strcmp
0x66734: add x1, x1, #0x740   ; "MS-CHAP"
0x6673c: bl  #0x1e4a0          ; strcmp
```

### Behavior Matrix:
| Parameter Value (`X_5067F0_PPPAuthenticationProtocol`) | Emitted pppd Options | Negotiation Behavior |
| :--- | :--- | :--- |
| `"PAP"` | `refuse-chap`, `refuse-mschap`, `refuse-mschap-v2`, `refuse-eap` | Forces PAP authentication only |
| `"CHAP"` | `refuse-pap`, `refuse-mschap`, `refuse-mschap-v2`, `refuse-eap` | Forces CHAP authentication only |
| `"MS-CHAP"` | `refuse-pap`, `refuse-chap`, `refuse-eap` | Forces MS-CHAP authentication only |
| `"AUTO_AUTH"` | *(None emitted)* | **Permits both PAP and CHAP negotiation based on ISP BRAS challenge** |

## ISP Parameter Compliance
For our ISP (which specifies `AUTO_AUTH`), configuring:
```ini
SET X_5067F0_PPPAuthenticationProtocol string AUTO_AUTH;
```
ensures that no refuse options are placed in `/etc/ppp/options_nas0_notag`, allowing clean authentication negotiation with the BRAS.

