import elftools.elf.elffile as elffile

libs = [
    'full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbe.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so'
]

targets = [
    'setWanIpPppInterfaceName',
    'beWanEnablePPPv4Client',
    'beConfigWANByPPPoE',
    'createWANPPPConnectionCfgFile',
    'libccc_executePPPv4Client',
    'libcccBeWan_createWANPPPConnectionCfgFile_wrapper',
    'libcccBeWan_eth_Init',
    'getCurrentWANMode',
    'libcccBeWan_getWANDeviceObjectRequestedLinkType',
    'beWanDoLayer3InterfaceAction',
    'beWanEnableDHCPv4Client'
]

for lib in libs:
    with open(lib, 'rb') as f:
        elf = elffile.ELFFile(f)
        symtab = elf.get_section_by_name('.dynsym')
        found = []
        for sym in symtab.iter_symbols():
            if sym.name in targets:
                found.append((hex(sym['st_value']), sym.name, sym['st_size'], sym['st_shndx']))
        if found:
            print(f"=== {lib} ===")
            for v, n, sz, sh in found:
                print(f"  {v} (size {sz}, shndx {sh}): {n}")

