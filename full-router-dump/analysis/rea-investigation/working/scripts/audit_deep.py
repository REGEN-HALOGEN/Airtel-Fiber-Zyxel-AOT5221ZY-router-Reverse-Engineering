import os
import sys
import elftools.elf.elffile as elffile

def inspect_elf(path):
    print(f"=== Inspecting {path} ===")
    with open(path, 'rb') as f:
        elf = elffile.ELFFile(f)
        for s in elf.iter_sections():
            if s.name in ['.dynsym', '.symtab']:
                print(f"Section {s.name}: {s.num_symbols()} symbols")
                for sym in s.iter_symbols():
                    print(f"  {hex(sym['st_value'])} ({sym['st_shndx']}): {sym.name}")

if __name__ == '__main__':
    inspect_elf('full-router-dump/filesystem/rootfs/usr/bin/ccctest')
