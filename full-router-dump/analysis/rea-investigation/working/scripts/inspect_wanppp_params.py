import struct
import re

with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

# Let's search around 0x3b2dc (WANPPPConnection)
start = 0x3b2dc
end = start + 0x2500

# Extract strings and types from WANPPPConnection object definition
chunk = data[start:end]
params = re.findall(b'([A-Za-z0-9_]{3,})\x00', chunk)
print(f"Parameters and strings found under WANPPPConnection ({len(params)} found):")
for p in params[:60]:
    name = p.decode('latin1')
    if not name.startswith('3') and not name.startswith('2'):
        print(f"  {name}")

