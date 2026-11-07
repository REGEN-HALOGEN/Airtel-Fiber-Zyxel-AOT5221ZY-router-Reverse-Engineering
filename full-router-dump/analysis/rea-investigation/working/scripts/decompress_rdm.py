import lzma
import os

in_path = 'files/config.rdm'
out_path = 'files/config_rdm_decompressed.bin'

with open(in_path, 'rb') as f:
    compressed_data = f.read()

# MSTC uses LZMA-alone format
decompressed = lzma.decompress(compressed_data, format=lzma.FORMAT_ALONE)
print(f"Decompressed {len(compressed_data)} bytes to {len(decompressed)} bytes")

with open(out_path, 'wb') as f:
    f.write(decompressed)
print(f"Saved to {out_path}")

