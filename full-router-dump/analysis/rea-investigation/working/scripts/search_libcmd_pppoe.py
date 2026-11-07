import os
from elftools.elf.elffile import ELFFile

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

print(f"Analyzing: {libcmd_path}")
print(f"File exists: {os.path.exists(libcmd_path)}")
print(f"File size: {os.path.getsize(libcmd_path)} bytes")

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    print(f"ELF Class: {elf.header['e_ident']['EI_CLASS']}")
    print(f"Machine: {elf.header['e_machine']}")
    
    # Check sections
    for sec in elf.iter_sections():
        if sec['sh_size'] > 0:
            print(f"Section {sec.name}: addr=0x{sec['sh_addr']:x}, offset=0x{sec['sh_offset']:x}, size=0x{sec['sh_size']:x}")

    f.seek(0)
    data = f.read()

patterns = [
    b"/bin/pppd -d file /etc/ppp/options_%s %s",
    b"/bin/ls /var/run | grep ppp%s.pid || /bin/pppd -d file /etc/ppp/options_%s %s &",
    b"/bin/ls /var/run | grep ppp%s.pid || /bin/pppd file /etc/ppp/options_%s %s &",
    b"/bin/pppd",
    b"/etc/ppp/options",
    b"options_%s",
    b"grep ppp",
    b"/var/run"
]

print("\n--- Pattern Search Results in libCmd.so ---")
for p in patterns:
    matches = []
    idx = 0
    while True:
        pos = data.find(p, idx)
        if pos == -1:
            break
        # Find start and end of null-terminated string
        start = data.rfind(b'\x00', 0, pos) + 1
        end = data.find(b'\x00', pos)
        if end == -1:
            end = pos + len(p) + 40
        matches.append((pos, data[start:end]))
        idx = pos + len(p)
    print(f"Pattern '{p.decode('latin1', errors='replace')}': {len(matches)} matches")
    for pos, s in matches[:10]:
        print(f"  Offset 0x{pos:x}: {s.decode('latin1', errors='replace')}")


