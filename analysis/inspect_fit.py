# Inspect ubi_k0.bin to see its contents
import struct

with open(r'C:\Users\REGEN\AirtelModemRev\files\ubi_k0.bin', 'rb') as f:
    hdr = f.read(1024)

print('FIT Image Magic:', hdr[:4].hex())
# Look for strings in ubi_k0.bin
fpath = r'C:\Users\REGEN\AirtelModemRev\files\ubi_k0.bin'
with open(fpath, 'rb') as f:
    data = f.read()

for term in [b'/etc/ppp/default_options', b'rp-pppoe.so', b'pppoe.so', b'pppoe-wan', b'nas0_notag', b'options_']:
    idx = data.find(term)
    if idx != -1:
        print(f'Found {term.decode()} in ubi_k0.bin at 0x{idx:x}')
    else:
        print(f'{term.decode()} NOT found in ubi_k0.bin')

