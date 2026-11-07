# PPPoE Component Inventory

## Complete PPP & PPPoE Subsystem Matrix

| Component Path | Class / Machine | Size (Bytes) | SHA-256 Digest | Role in Architecture |
| :--- | :--- | :---: | :--- | :--- |
| `filesystem/rootfs/bin/pppd` | ELF64 EXEC / AArch64 | 236,432 | `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596` | Linux Point-to-Point Protocol daemon; dynamic plugin host. |
| `filesystem/rootfs/lib/MSTC/libpppoe.so` | ELF64 DYN / AArch64 | 35,864 | `3ba88a385f02c61148419615ec6696fa049d586745f928f09d84594c7b275467` | Roaring Penguin PPPoE plugin; exports `pppoe_plugin_init` and `setdevname_pppoe`. |
| `files/libbemodules.so` | ELF64 DYN / AArch64 | 1,074,680 | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` | Business logic: options file generator (`0x664a8`), device name builder (`0x698dc`). |
| `files/libcccbe.so` | ELF64 DYN / AArch64 | 377,312 | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` | Daemon invocation wrapper (`0x348f4`); `setWanIpPppInterfaceName` (`0x346d0`). |
| `filesystem/rootfs/lib/modules/5.10.138/pppoe.ko` | ELF64 REL / AArch64 | 23,120 | `a4929cfaad885c34ad17430489958bc59e94c9d961e0bbd3876e5ec1bc42a492` | Linux kernel PPPoE socket driver (`AF_PPPOX`). |
| `filesystem/rootfs/lib/modules/5.10.138/pppox.ko` | ELF64 REL / AArch64 | 7,624 | `dfa73229b1580ca03ef3e3d93d3d6fa8ad7b3d34468f7634f19fc0237d8e8211` | Kernel PPPoX protocol abstraction layer. |
| `filesystem/rootfs/lib/modules/5.10.138/ppp_generic.ko` | ELF64 REL / AArch64 | 60,648 | `eb4d1421c6ba03893638f38bc602b92f70355f30325fa124115456fef464dbb0` | Core Linux PPP netdevice driver (`ppp%d`). |
| `filesystem/rootfs/lib/modules/5.10.138/ppp_async.ko` | ELF64 REL / AArch64 | 19,064 | `3ecf359196b6e8284534f31c778fa9b35b6df8d06fb6b6271c6670ef60b377b7` | Async serial/TTY PPP support driver. |
| `filesystem/rootfs/etc/ppp/default_options` | Text Configuration | 97 | `f6a47a7b977799be52467b7e8083bf2f280145c2f0f03f707f502d6b3531bcf9` | Baseline template copied to `/etc/ppp/options_nas0_notag`. |
| `filesystem/rootfs/etc/ppp/ip-up` | Shell Script | 455 | `07f597fe21f4bc74d081bce2e2db6986555df3d0a64fb566355fa08fc678fae3` | Event notification script fired upon IPCP address acquisition (`EVENTNOTIFY 206`). |
| `filesystem/rootfs/etc/ppp/ip-down` | Shell Script | 572 | `58c9735d554a9d0339d67dfc8eb6940a4e76810c97e742875150824b22c262ce` | Event notification script fired upon session disconnect (`EVENTNOTIFY 207`). |

