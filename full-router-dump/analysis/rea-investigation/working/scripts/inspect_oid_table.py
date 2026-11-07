import capstone
import elftools.elf.elffile as ef
import struct

p = r'c:\Users\REGEN\AirtelModemRev\files\librdm.so'

with open(p, 'rb') as f:
    elf = ef.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym = [s for s in dynsym.iter_symbols() if s.name == 'OIDTable'][0]
    val = sym.entry.st_value
    sz = sym.entry.st_size
    
    text_sec = elf.get_section_by_name('.text')
    sec_addr = text_sec['sh_addr']
    sec_data = text_sec.data()
    
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    # In AArch64, adrp page is (val & ~0xfff)
    page = val & ~0xfff
    offset = val & 0xfff
    print(f'OIDTable at 0x{val:x} (Page: 0x{page:x}, Offset: 0x{offset:x})')
    
    for ins in md.disasm(sec_data, sec_addr):
        if ins.mnemonic == 'adrp' and hex(page) in ins.op_str:
            print(f'Reference at 0x{ins.address:x}: {ins.mnemonic} {ins.op_str}')

