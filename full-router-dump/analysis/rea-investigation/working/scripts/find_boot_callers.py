import elftools.elf.elffile as elffile
import capstone

def find_callers(elf_path, target_addr, sym_name):
    with open(elf_path, 'rb') as f:
        elf = elffile.ELFFile(f)
        text = elf.get_section_by_name('.text')
        if not text:
            return
        text_data = text.data()
        text_addr = text['sh_addr']
        
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        for ins in md.disasm(text_data, text_addr):
            if ins.mnemonic in ['bl', 'b']:
                try:
                    dest = int(ins.op_str.replace('#', ''), 16)
                    if dest == target_addr:
                        print(f"Direct branch to {sym_name} from 0x{ins.address:x} in {elf_path}")
                except:
                    pass
                    
        # Check rela relocations
        for s in elf.iter_sections():
            if 'rela' in s.name:
                dynsym = elf.get_section_by_name('.dynsym')
                symtab = elf.get_section_by_name('.symtab')
                sym_list = []
                if 'dyn' in s.name and dynsym:
                    sym_list = [sym.name for sym in dynsym.iter_symbols()]
                elif symtab:
                    sym_list = [sym.name for sym in symtab.iter_symbols()]
                for r in s.iter_relocations():
                    if r['r_info_sym'] < len(sym_list) and sym_list[r['r_info_sym']] == sym_name:
                        print(f"Relocation to {sym_name} at 0x{r['r_offset']:x} in {elf_path} ({s.name})")

find_callers('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 0x50d08, 'OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot')
find_callers('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 0x50d08, 'OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot')
find_callers('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 0x50d08, 'OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot')

