import lzma
import struct

with open(r'C:\Users\REGEN\AirtelModemRev\files\config.rdm', 'rb') as f:
    raw = f.read()

data = lzma.decompress(raw, format=lzma.FORMAT_ALONE)

# Let's inspect the object header for WANConnectionDevice at 0x36e74
# and WANPPPConnection at 0x3b2dc
for name, off in [('WANConnectionDevice', 0x36e74), ('WANIPConnection', 0x370b4), ('WANPPPConnection', 0x3b2dc)]:
    chunk = data[off-32 : off+48]
    hex_s = ' '.join(f'{b:02x}' for b in chunk)
    print(f'=== {name} (0x{off:x}) ===')
    print(hex_s)

