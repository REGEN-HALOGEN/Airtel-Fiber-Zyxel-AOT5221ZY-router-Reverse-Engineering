# PPPoE Configuration Generation & Template Analysis

## Generator Function: `beConfigWANByPPPoE`
- **Location:** `files/libbemodules.so` @ Address `0x664a8`
- **Output Target:** `/etc/ppp/options_%s` (evaluates to `/etc/ppp/options_nas0_notag`)

---

## 1. Baseline Template (`/etc/ppp/default_options`)
Contents:
```ini
plugin pppoe
noipdefault
ipcp-accept-remote
usepeerdns
hide-password
holdoff 3 
maxfail 0
```
- `holdoff 3`: Re-attempts PPPoE connection within 3 seconds of drop.
- `maxfail 0`: Never gives up; retries reconnection indefinitely.

---

## 2. Emitted Runtime Options File (`/etc/ppp/options_nas0_notag`)
When instantiated under profile `WANConnectionDevice.3.WANPPPConnection.1`, `beConfigWANByPPPoE` writes:

```ini
plugin pppoe
noipdefault
ipcp-accept-remote
usepeerdns
hide-password
holdoff 3 
maxfail 0
unit 111
user <ISP_USERNAME>
password <ISP_PASSWORD>
logfile /tmp/ppp111Log
mru 1480
mtu 1480
lcp-echo-interval 30
lcp-echo-failure 3
linkname nas0_notag
persist
passive
pppoe_srv_name 3jglobal
```

### Analysis of ISP Parameters
- `pppoe_srv_name 3jglobal`: Successfully formatted and appended at `0x66b3c`.
- `mtu 1480` / `mru 1480`: Populated from TR-098 parameters `X_5067F0_MaxMTUSize` and `MaxMRUSize`.
- `AUTO_AUTH`: When `X_5067F0_PPPAuthenticationProtocol == "AUTO_AUTH"`, no `refuse-*` lines are appended, enabling PAP and CHAP negotiation.

