# Evidence Inventory — Primary Binary & Configuration Files

All SHA-256 digests in this catalog were freshly computed from disk on Windows 11 host using Python 3.12 `hashlib.sha256`.

| Relative Path | Size (Bytes) | SHA-256 Digest | Format / Class | Provenance & Architectural Role |
| :--- | :---: | :--- | :--- | :--- |
| `files/linkdetection` | 22,896 | `36d219bd3c86704721fe44ba5eb214dadb5ebcae9eed4b41f74e323ebf1a9f93` | ELF64 AArch64 EXEC | Mode transition daemon; calls `rt_port_link_get` & CMSG IPC; routine `0x402454`. |
| `files/ccc_be` | 122,064 | `1da56bc3181df59aab087bdb5034ec8334f7ea58d0f34646fcabea3af549805f` | ELF64 AArch64 EXEC | Central CCC backend daemon; handles RDM mutations, CMSG events, network startup. |
| `files/ccc_das` | 112,704 | `911685fbebbd6278f43c24427e13a9b6aeb339c57581add2ce3cff325cc4c5ab` | ELF64 AArch64 EXEC | CCC CLI and script agent; executes `REQUEST`, `SEL`, `SET`, `ADD`, `SEND`. |
| `files/libbemodules.so` | 1,074,680 | `1de450de0a9a00aed959b2bf7a7076328d6aabd2850f718e9ef631880ee9a513` | ELF64 AArch64 DYN | Core business logic: L3/L4 WAN config, `constructL3WANDevName`, `beConfigWANByPPPoE`. |
| `files/libcccbe.so` | 377,312 | `ddacad88fc7598a19a890d8c8cecdf9999ba5e9da53e4f0fefa51e6d2d976022` | ELF64 AArch64 DYN | Platform layer: SMUX control, Realtek port mapping (`rtk_wan_port_mapping`), `pppd` launcher. |
| `files/librtk.so` | 2,204,184 | `54f58020848bd4d3b2d34fea1b3687276a367c49495074c297a17aabfc654e0e` | ELF64 AArch64 DYN | Realtek switch & hardware NAT HAL driver library (contains symbols). |
| `files/ca-rtk.ko` | 392,040 | `155ca47508b260c065ff772c3bde2cd708ff0bac96a46f2ab50cec9e38178dc9` | ELF64 AArch64 REL | Kernel driver: Realtek Ethernet switch/MAC core. |
| `files/ca-ne.ko` | 3,975,376 | `fb4166f8ca75e16ba59b0546662151ff1d6201527661cec2bf4b94654cb384d3` | ELF64 AArch64 REL | Kernel driver: Network Engine, SerDes, EPON/GPON MAC interface. |
| `files/fc_8277c.ko` | 2,088,432 | `c9116160081ef242f69315e11e408e5423d061cfeedf7b8f235af31ee884ecf0` | ELF64 AArch64 REL | Kernel module: Flow Control / Fastpath acceleration engine. |
| `full-router-dump/filesystem/rootfs/bin/pppd` | 236,432 | `c94df0226cd33298f27007d74c73ff335e745c4ed50c5d7cf36dfd0e7e7f0596` | ELF64 AArch64 EXEC | Linux Point-to-Point Protocol daemon with `rp-pppoe.so` dynamic plugin. |
| `full-router-dump/filesystem/rootfs/bin/smuxctl` | 536,16 | `3b97d99f84f242f4774906116e84073570029efa1066381a004e9e0ab5e50638` | ELF64 AArch64 EXEC | Realtek SMUX interface control utility (`--if-create-name`, `--set-if-rsmux`). |
| `files/config.rdm` | 63,005 | `fb50191e922a0b90dfa565fa973f854fdf52611aba40ff067d4e7f853f7b70e7` | LZMA-compressed | Factory default RDM database (decompresses to 3,145,728 bytes). |
| `files/aot-current-pdm-config.xml` | 583,313 | `6177ef897a056811b5fdd2f2bc5a5f5b8f4f0d1a4969b4b93ec5348bdcc9f308` | UTF-8 XML | Current active PDM XML configuration export from device. |
| `files/ether-backup.lz` | 23,485 | `bba43ffa6698b61d83cd9fdf23f07584cd4b9f1072bd46bbbe23194e05781b1a` | LZMA-compressed | Configuration backup captured during previous Ethernet WAN testing. |

