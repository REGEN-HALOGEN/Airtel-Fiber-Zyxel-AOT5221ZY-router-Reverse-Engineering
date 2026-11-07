import os

rootfs = r'full-router-dump\filesystem\rootfs'
pattern = b'beConfigWANByPPPoE\x00'

for root, dirs, files in os.walk(rootfs):
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'rb') as fp:
                data = fp.read()
                if pattern in data:
                    print(f"Literal string found in {p}")
        except:
            pass


