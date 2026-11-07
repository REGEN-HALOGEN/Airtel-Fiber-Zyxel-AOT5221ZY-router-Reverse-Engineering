# Routing / NAT / Firewall Analysis

- **Mission:** Airtel AOT5221ZY (Zyxel PX5311-R0, Realtek Taurus RTL9607C, AArch64, Linux 5.10.138) — LAN4 Ethernet WAN + PPPoE via external Syrotech GPON ONT.
- **Date:** 2026-11-07. **Branch:** `research/ethernet-wan-pppoe`. **Base commit:** `5b1dfca` (only commit on `main`).
- **Safety boundary:** STATIC ANALYSIS ONLY. No router, SSH, LAN or runtime access was used or attempted. No PPPoE credentials are recorded anywhere in these reports (presence-only, `[REDACTED]`). Nothing here is a runtime test result.
- **Confidence legend:** CONFIRMED STATIC = decoded from the binaries/image in this session · CONFIRMED FROM EXISTING RUNTIME EVIDENCE = supplied by prior runtime logs/reports, not re-derived · STRONGLY INFERRED = cross-function reconstruction with one unobserved link · HYPOTHESIS = plausible, unproven · UNKNOWN = not settled statically · DISPROVEN = contradicted by the artifacts.
- **Tools (this session):** git 2.43.0; Python 3.12.3 + Capstone 5.0.7 + LIEF 1.0.0-d05b3499b + pyelftools (venv); GNU binutils 2.42 `file/readelf/nm/strings` (host `objdump` has **x86 targets only, no AArch64** — all disassembly is Capstone, PLT resolved from `.rela.plt`); `sha256sum`. Ghidra/IDA/radare2: **not installed** in this sandbox (recorded as a tooling limitation; Capstone re-disassembly spot-matched the prior `analysis/` and `working/` disassembly files).
- **Scope:** Default route selection, NAT, firewall zone, DNS, MSS, fastpath, LAN3 preservation — generic vs GPON-specific.
- **Files examined:** libbemodules.so, libbeEvents.so, libcccbe.so, rootfs etc/ppp/*, factory PDM XML

## Key artifact hashes
| Artifact | Size | SHA-256 |
|---|---|---|
| DUMPFILES/broadband.cgi | 61,760 B | `78eaacd575b9884778a76ead57cc895e95944cc939c465136ee3da390f3671fa` |
| DUMPFILES/wanRemoteNode_ETH_Edit.cgi | 47,424 B | `59ee3ba6b9a946650eb9112fb0ebc2561e2e9ee5e0589ec2ada55517c4af5899` |
| DUMPFILES/wanRemoteNode_GPON_Edit.cgi | 47,416 B | `69f9a176397c742d0ee50fe07313646cf5ca27743ba1c29facf54b7c6eb148e1` |
| DUMPFILES/linkdetection | 23 KB | `36d219bd3c86704721fe44ba5eb214dadb5ebcae9eed4b41f74e323ebf1a9f93` |
| DUMPFILES/libcccbe.so | 369 KB | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` |
| DUMPFILES/libbemodules.so | 1.1 MB | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` |
| DUMPFILES/libbeEvents.so | 109 KB | `cc9d237437773f9a104ceec09f4217298543e0dc80dcd46f89e95b18c40500d1` |
| DUMPFILES/librdm.so | 280 KB | `65306765251c503d3c36fac4f93bfa348698f2ffe9ed83a646a672b57b331a1d` |
| DUMPFILES/libcccrdm.so | 436 KB | `ed2a1d6a0f70b0d0323cc8b0671d0846b2ef1f529b871104cc45eb61d4376352` |
| DUMPFILES/libcmsg.so | 55 KB | `57155a272eb9cdf9e4d62b3fee07d4f058a93ccb798d4c6503292af4b0094d70` |
| DUMPFILES/ccctest.bin | 23 KB | `4badd3f723df86838e20a199f08c4e844354aec605f286a3cb141f93b5d3f3bf` |
| DUMPFILES/ccc_be | 120 KB | `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f` |
| DUMPFILES/config.rdm (= runtime-config.rdm) | 62 KB | `fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7` |
| DUMPFILES/config_rdm_decompressed.bin | 3,145,728 B | `b1a35a37631b7dd75c1b13f6d78e6a75d6c41bb081e8c868c82330dad1dd5485` |
| rootfs lib/MSTC/libpppoe.so | — | `c6a83bc868fd2e6e0e19abbd43625a68e90e47874ea5f8d87f6437a69577e315` |
| rootfs bin/pppd | — | `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596` |
| rootfs etc/ppp/ip-up | — | `3fcaa848d84b5297bcbabd93dd569e7ed84f17eb50d3cb0d72b5d04c98ee4ae7` |
| rootfs etc/ppp/ip-down | — | `d5a5e2ceb638e9dcc0c3a974f0bb8f4fd869d5168b3bc128ea467e5ec347f51e` |
| rootfs lib/MSTC/libCmd.so | — | `fa8ecde8b14e0ff682faef8152cb5bdf446e11bc90a8a6b29f9e71dc8be3bc8c` |


## Default route (STRONGLY INFERRED end-to-end; components CONFIRMED STATIC)
- `InternetGatewayDevice.Layer3Forwarding.DefaultConnectionService` (OID 0x80 object; param string LENGTH 256) factory value = `…WANConnectionDevice.1.WANPPPConnection.1` (GPON). Vendor per-mode values live on the OID-0x83 child as parameters `DefaultConnectionService_GPON` (= GPON PPP path) and `DefaultConnectionService_ETHER` (= **ConnDev.3.WANIPConnection.1** in factory config — note: the factory ETHER default is the *IP* object; for PPPoE it must be the PPP path).
- broadband.cgi updates DCS only when the form's default-WAN flag is set; linkdetection rewrites it on every mode switch (to the IP object on ETHER).
- Event-206/L3 code resolves the object named by DCS and uses its InterfaceName (`updateDefaultRouteByLinkType`, `layer3Forwarding_wanConnectionUp`, `eventRouteIPChange` symbols in libbeEvents; no GPON literal in that library's strings). **Open link:** whether the route target follows DCS or the event's ifname argument is decided inside handler bodies not re-disassembled this session — runtime check U7 (bring ppp131 up with DCS deliberately pointing elsewhere and observe `ip route`).

## NAT (CONFIRMED STATIC)
Templates in libbemodules only: `iptables -t nat -A NAT_POSTROUTING -o %s -j MASQUERADE`, `… -o %s -s %s/24 -j MASQUERADE`, SNAT variants `… -j SNAT --to %s`. Grep counts: libbemodules 4 MASQUERADE strings; libbeEvents 0; libcccbe 0. NAT is keyed by interface name + the connection's NATEnabled — fully generic for ppp131. Prior claim of a literal `-o ppp111` rule in `FullNatControl` (libbeEvents) is DISPROVEN (no such string; that audit's libbeEvents hash also matches no file in the repo).

## Firewall (partly UNKNOWN)
No literal ppp111/GPON zone assignment exists in any binary; forwarding/ACL templates in libbemodules are interface-parameterised (`-i %s`, `-o %s`). The specific `FORWARD -i br0 -o ppp111 -j ACCEPT` + RELATED,ESTABLISHED pair quoted in prior reports was **not found as a string** — it may be built by concatenation, applied by a generic WAN-zone routine, or paraphrased. Verdict: generic-by-design STRONGLY INFERRED; exact rule set UNKNOWN — runtime check U8 (`iptables -S FORWARD` with the session up).

## DNS (STRONGLY INFERRED)
ip-up does nothing for DNS. Peer DNS flows: pppd `usepeerdns` (static template) → `/etc/ppp/resolv_%s.conf`; ccc_be side: libbeEvents `DNS_EventHandlerFunc`, `configDNSServers`, `Add_Static_Route_For_DNS_Servers`, `Dnsmasq_Conf_Creation`, `Restart_Dnsmasq`. No interface-specific code identified. Runtime check U9.

## IPv6
NDPPD / IPv6PD retargeting exists in linkdetection (points IPv6 PD at the active WAN object — IP object on ETHER; for PPPoE it should name the PPP object). IPv6 DefaultConnectionService twin (OID 0x84/0x87) mirrors v4. The ISP profile in the brief is IPv4 PPPoE; IPv6 behaviour is UNKNOWN and out of the deployment's critical path. ip6tables TCPMSS twin exists.

## MSS (CONFIRMED STATIC)
`addTCPMSSDefaultRule`/`delTCPMSSDefaultRule` (libbemodules): `iptables -t filter -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu` (+ ip6tables). Global and interface-agnostic; with MTU 1480 the clamped MSS is 1440 as computed by netfilter (no literal 1440 exists). Prior attribution of this rule to beConfigWANByPPPoE / Event 206 is DISPROVEN. Call timing UNKNOWN (check U10).

## Fastpath / hardware acceleration (UNKNOWN beyond init)
Only proven fc coupling: `/proc/fc/ctrl/wan_port_mask` written at init (0x08 Ethernet). libcccbe also references `/proc/fc/ctrl/hwnat`, `flow_flush`, `skbmark_*` (QoS/flow-classification family). Prior claim "Event 206 programs fc_8277c ASIC flow tables for the session" is UNSUPPORTED by any string/disasm found. Whether ppp131 flows are offloaded is UNKNOWN (check U10).

## LAN3 + Wi-Fi preservation (STRONGLY INFERRED)
- Port 2 (LAN3, mask 0x04) is never referenced by WAN init/mapping/L3 code examined; the WAN mask is a single-port selector (0x08), not a bridge bitmap; no code examined removes a port from br0.
- Wi-Fi interfaces are not referenced by any WAN/PPP function examined.
- Caveat: bridge membership is managed by L2/bridge config code not audited this session, so preservation is "no code path found that breaks it", not a positive proof. Runtime check U11 (`bridge link` before/after) is mandatory in the deployment plan.
