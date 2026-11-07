with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    data = f.read()

target = b'\xa8\x64\x06\x00'
pos = 0
while True:
    idx = data.find(target, pos)
    if idx == -1: break
    print(f"Match for \\xa8\\x64\\x06\\x00 at file offset 0x{idx:x}")
    pos = idx + 4


