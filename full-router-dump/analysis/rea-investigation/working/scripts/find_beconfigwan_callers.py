from elftools.elf.elffile import ELFFile
from capstone import *

def find_callers(so_path, target_sym_name):
    print(f"\n--- Searching callers of {target_sym_name} in {so_path} ---")
    with open(so_path, 'rb') as f:
        elf = ELFFile(f)
        text_sec = elf.get_section_by_name('.text')
        text_data = text_sec.data()
        text_base = text_sec['sh_addr']
        
        dynsym = elf.get_section_by_name('.dynsym')
        target_addr = None
        syms = []
        for s in dynsym.iter_symbols():
            if s.name == target_sym_name:
                target_addr = s['st_value']
            if s['st_info']['type'] == 'STT_FUNC' and s['st_size'] > 0:
                syms.append((s['st_value'], s['st_size'], s.name))
        syms.sort()
        
        if not target_addr:
            # Check PLT
            rela_plt = elf.get_section_by_name('.rela.plt')
            plt_sec = elf.get_section_by_name('.plt')
            if rela_plt and plt_sec:
                for i, r in enumerate(rela_plt.iter_relocations()):
                    sym_idx = r['r_info_sym']
                    if sym_idx < len(list(dynsym.iter_symbols())):
                        s_name = list(dynsym.iter_symbols())[sym_idx].name
                        if s_name == target_sym_name:
                            target_addr = plt_sec['sh_addr'] + 0x20 + i * 0x10
                            print(f"Target found in PLT at 0x{target_addr:x}")
                            break
                            
        if not target_addr:
            print("Symbol not found")
            return
            
        def get_fn(a):
            for s_a, s_s, s_n in syms:
                if s_a <= a < s_a + s_s:
                    return f"{s_n} (0x{s_a:x})"
            return "unknown"
            
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        for insn in md.disasm(text_data, text_base):
            if insn.mnemonic in ['bl', 'b']:
                try:
                    if insn.operands[0].imm == target_addr:
                        print(f"  Called at 0x{insn.address:x} inside {get_fn(insn.address)}")
                except:
                    pass

find_callers(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'beConfigWANByPPPoE')
find_callers(r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so', 'beConfigWANByPPPoE')


