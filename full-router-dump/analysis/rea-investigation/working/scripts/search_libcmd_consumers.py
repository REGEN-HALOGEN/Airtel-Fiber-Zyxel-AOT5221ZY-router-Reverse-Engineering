import os

rootfs = r'full-router-dump\filesystem\rootfs'
targets = [b'CheckAndRestartPPP', b'wrapperDoPPP', b'libCmd.so']

for root, dirs, files in os.walk(rootfs):
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'rb') as fp:
                data = fp.read()
                matches = [t for t in targets if t in data]
                if matches:
                    print(f"File {p}: contains {[m.decode() for m in matches]}")
        except:
            pass


