import struct

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    data = f.read()

target = 0x66ee4
pat = struct.pack('<Q', target)

pos = 0
while True:
    idx = data.find(pat, pos)
    if idx == -1: break
    print(f"Pointer to beWanEnablePPPv4Client found at offset 0x{idx:x}")
    pos = idx + 8


