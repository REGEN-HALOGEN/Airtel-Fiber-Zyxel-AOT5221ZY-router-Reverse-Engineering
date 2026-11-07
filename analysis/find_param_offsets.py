import lzma
import struct

with open(r'C:\Users\REGEN\AirtelModemRev\files\config.rdm', 'rb') as f:
    raw = f.read()

data = lzma.decompress(raw, format=lzma.FORMAT_ALONE)

# Let's inspect the parameter descriptors for WANPPPConnection
# WANPPPConnection is at 0x3b2dc
# Look for X_5067F0_InterfaceName at 0x3c010
off = 0x3c010
chunk = data[off-32 : off+48]
for i in range(0, len(chunk), 16):
    c = chunk[i:i+16]
    h = ' '.join(f'{b:02x}' for b in c)
    a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in c)
    print(f'{h:<48} {a}')

# Let's find all parameters in WANPPPConnection and their struct offsets
# RDM parameter records usually have (name, type, offset, size)

