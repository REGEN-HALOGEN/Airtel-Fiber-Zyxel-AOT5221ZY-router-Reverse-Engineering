import os
from elftools.elf.elffile import ELFFile

# In librdm.so, let's find the RDM schema descriptor for OID 0xe3
# In MSTC RDM, each object has an array of parameter descriptors:
# struct RDM_ParamDesc {
#    uint32_t param_id;
#    uint32_t type;
#    uint32_t offset;
#    uint32_t size;
#    char name[...];
# } or similar.

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_data = rodata.data()
    ro_addr = rodata['sh_addr']
    
    # Let's search ro_data for parameter names of WANPPPConnection
    # like "X_5067F0_InterfaceName"
    target = b"X_5067F0_InterfaceName"
    pos = 0
    while True:
        idx = ro_data.find(target, pos)
        if idx == -1: break
        print(f"Found '{target.decode()}' at rodata offset 0x{idx:x} (addr 0x{ro_addr + idx:x})")
        # Look around this offset
        chunk = ro_data[max(0, idx-32): min(len(ro_data), idx+64)]
        print(f"  Surrounding: {chunk}")
        pos = idx + len(target)


