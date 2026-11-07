import os

for root, dirs, files in os.walk('full-router-dump/filesystem/rootfs'):
    for f in files:
        if 'pppoe' in f.lower() or 'pppd' in f.lower():
            print(os.path.join(root, f))

