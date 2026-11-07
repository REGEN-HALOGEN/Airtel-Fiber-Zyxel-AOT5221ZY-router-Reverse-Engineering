# Pre-Implementation Backup Requirements

Before executing any configuration modifications or issuing any CLI commands on the live router, a full non-destructive runtime state backup must be captured:

## 1. RDM Database State Dump
Execute read-only extraction of current RDM state to `/tmp/config_backup.txt`:
```bash
ccctest -d > /tmp/rdm_full_backup.txt
```
Copy `rdm_full_backup.txt` off the router to the local PC via SCP/SFTP.

## 2. Kernel & Switch State Snapshot
Capture current hardware port allocations, network interfaces, and routing tables:
```bash
cat /proc/ni/dev_port_mapping > /tmp/backup_dev_port_mapping.txt
cat /proc/fc/ctrl/wan_port_mask > /tmp/backup_wan_port_mask.txt
ip addr show > /tmp/backup_ip_addr.txt
ip route show > /tmp/backup_ip_route.txt
brctl show > /tmp/backup_brctl.txt
iptables-save > /tmp/backup_iptables.txt
```

## 3. Preservation of Airtel Specific Parameters
Record factory values of the following parameters:
- `InternetGatewayDevice.ManagementServer.URL`
- `InternetGatewayDevice.ManagementServer.Username`
- `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService`
- `InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.Username`

Confirm all backup artifacts are saved securely in `analysis/rea-investigation/evidence/` on the local host prior to proceeding.

