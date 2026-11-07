with open(r'C:\Users\REGEN\AirtelModemRev\files\ubi_k0.bin', 'rb') as f:
    data = f.read()

# Find gzip magic 1f 8b or lzma magic 5d 00 00
import re

for m in [b'\x1f\x8b\x08', b'\x5d\x00\x00', b'\xfd7zXZ']:
    pos = 0
    while True:
        idx = data.find(m, pos)
        if idx == -1:
            break
        print(f'Compressed stream header {m.hex()} at 0x{idx:x}')
        pos = idx + 1
        if pos > 1000000:
            break

