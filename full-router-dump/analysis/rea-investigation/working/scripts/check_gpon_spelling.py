with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

import re
matches = re.findall(b'X_5067F0_Gpon[A-Za-z0-9_]+', data)
for m in set(matches):
    print("Found in config.rdm:", m.decode('latin1'))

with open('full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so', 'rb') as f:
    rdata = f.read()
rmatches = re.findall(b'X_5067F0_Gpon[A-Za-z0-9_]+', rdata)
for m in set(rmatches):
    print("Found in librdm.so:", m.decode('latin1'))

