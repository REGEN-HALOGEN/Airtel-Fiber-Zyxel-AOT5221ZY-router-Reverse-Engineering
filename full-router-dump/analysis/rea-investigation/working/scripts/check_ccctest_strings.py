import sys

with open('full-router-dump/filesystem/rootfs/usr/bin/ccctest', 'rb') as f:
    data = f.read()

# search for ascii strings >= 3 chars
import re
strings = re.findall(b'[A-Za-z0-9_]{3,}', data)
cmd_candidates = [s.decode('latin1') for s in strings if s.isupper() or b'sel' in s.lower() or b'add' in s.lower() or b'set' in s.lower()]
print("Matching strings in ccctest:")
for c in set(cmd_candidates):
    if len(c) < 30:
        print(f"  {c}")

