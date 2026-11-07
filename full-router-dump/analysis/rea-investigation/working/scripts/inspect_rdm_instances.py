import struct
import re

with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

print(f"Total decompressed size: {len(data)} bytes")

# Search for strings
for s in [b'WANConnectionDevice', b'Eth_Internet', b'nas0', b'nas0_notag', b'3jglobal', b'WANPPPConnection', b'WANIPConnection']:
    matches = [m.start() for m in re.finditer(re.escape(s), data)]
    print(f"'{s.decode('latin1')}' ({len(matches)} occurrences): {[hex(m) for m in matches[:10]]}")
