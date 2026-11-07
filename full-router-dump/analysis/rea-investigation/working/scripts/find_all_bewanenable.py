import os

rootfs = r'full-router-dump\filesystem\rootfs'
pattern = b'beWanEnablePPPv4Client'

for root, dirs, files in os.walk(rootfs):
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'rb') as fp:
                data = fp.read()
                if pattern in data:
                    print(f"Found in {p}")
        except:
            pass


