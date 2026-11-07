with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    data = f.read()

idx = data.find(b'beConfigWANByPPPoE')
print(f"Index: 0x{idx:x}")
print(f"Surrounding bytes: {data[max(0, idx-20):idx+40]}")


