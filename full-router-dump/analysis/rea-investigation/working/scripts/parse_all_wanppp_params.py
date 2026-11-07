import struct
import re

with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

start = 0x3b2dc
end = 0x3cb00
chunk = data[start:end]

# In config_rdm_decompressed.bin:
# Let's search for parameter entries
# Let's inspect bytes from start
# In OID definition:
# Object header: OID, name, etc.
# Then parameters.
# Let's find every occurrence of parameter strings:
# A parameter string is preceded by a flags/length byte, and followed by type (4 bytes: 's', 'i', 'b', 'u')
# Let's regex search for type bytes b'[sibu]\x00\x00\x00'

matches = []
for m in re.finditer(b'([sibu])\x00\x00\x00', chunk):
    type_char = chr(m.group(1)[0])
    type_pos = m.start()
    # Before type pos is the null-terminated parameter name
    name_end = type_pos
    # find where string starts (non-ascii or null)
    name_start = name_end - 1
    while name_start >= 0 and (32 <= chunk[name_start] < 127) and chunk[name_start] != 0:
        name_start -= 1
    name_start += 1
    name = chunk[name_start:name_end].rstrip(b'\x00').decode('latin1', errors='ignore')
    if len(name) >= 2 and re.match(r'^[A-Za-z0-9_]+$', name):
        # Now let's find the offset preceding the name
        # The offset is typically a uint32 or uint64 at name_start - something
        # Let's inspect 32 bytes before name_start
        pre_bytes = chunk[max(0, name_start-32):name_start]
        matches.append((name_start + start, name, type_char, pre_bytes))

print(f"Found {len(matches)} parameters:")
for pos, name, t, pre in matches:
    # Try to unpack offset from pre
    # Look at pre[-16:]
    if len(pre) >= 16:
        off_cand1 = struct.unpack('<I', pre[-16:-12])[0]
        off_cand2 = struct.unpack('<I', pre[-24:-20])[0] if len(pre) >= 24 else 0
        off_cand3 = struct.unpack('<I', pre[-12:-8])[0]
        print(f"  Pos 0x{pos:x} | Name: {name:32s} | Type: {t} | cand1=0x{off_cand1:x} cand2=0x{off_cand2:x} cand3=0x{off_cand3:x}")
    else:
        print(f"  Pos 0x{pos:x} | Name: {name:32s} | Type: {t}")

