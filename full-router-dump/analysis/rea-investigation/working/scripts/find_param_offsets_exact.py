import struct

with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

# Let's inspect bytes between 0x3b2dc and 0x3d000
# Notice that before or after each parameter string there are fields:
# Let's print each parameter string and the bytes surrounding it
import re

start = 0x3b200
end = 0x3d000
chunk = data[start:end]

# In config_rdm_decompressed.bin, let's understand the descriptor format
# Let's search for all parameter strings in chunk
matches = list(re.finditer(b'([A-Za-z0-9_]{2,})\x00', chunk))

for m in matches:
    name = m.group(1).decode('latin1')
    off = start + m.start()
    # Check 16 bytes before and 32 bytes after
    pre = data[off-16:off]
    post = data[off+len(m.group(0)):off+len(m.group(0))+32]
    # Let's find if 0x3e7 or 0x898 or similar appears
    # Look for 0xe7 0x03 (0x3e7) or 0x98 0x08 (0x898)
    e7_idx = pre.find(b'\xe7\x03')
    if e7_idx != -1:
        print(f"*** MATCH 0x3e7 in PRE of '{name}' (off=0x{off:x}) ***")
    e7_post = post.find(b'\xe7\x03')
    if e7_post != -1:
        print(f"*** MATCH 0x3e7 in POST of '{name}' (off=0x{off:x}) ***")
        
    g8_idx = pre.find(b'\x98\x08')
    if g8_idx != -1:
        print(f"*** MATCH 0x898 in PRE of '{name}' (off=0x{off:x}) ***")
    g8_post = post.find(b'\x98\x08')
    if g8_post != -1:
        print(f"*** MATCH 0x898 in POST of '{name}' (off=0x{off:x}) ***")


