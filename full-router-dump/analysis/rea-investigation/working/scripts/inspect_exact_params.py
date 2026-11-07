with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

# Let's inspect the structure of parameter descriptors in RDM
# At 0x3b2dc is WANPPPConnection object header
# In MSTC RDM, object header is followed by parameter descriptors:
# Usually: uint32_t type; uint32_t offset; char name[...];
# Let's search for parameter names in this region and print their details
import re

start = 0x3b2dc
end = start + 0x3000
chunk = data[start:end]

# Search for common parameter names
target_params = [
    'Enable', 'Name', 'ConnectionType', 'Username', 'Password',
    'PPPAuthenticationProtocol', 'PPPoEServiceName', 'MaxMRUSize',
    'MaxMTUSize', 'X_5067F0_MaxMTUSize', 'NATEnabled', 'X_5067F0_InterfaceName',
    'X_5067F0_Enable_VLANID', 'X_5067F0_VLANID', 'X_5067F0_WANService',
    'X_5067F0_PPPAuthenticationProtocol'
]

for p in target_params:
    matches = [m.start() for m in re.finditer(p.encode('latin1') + b'\x00', chunk)]
    if matches:
        for m in matches:
            abs_off = start + m
            # print surrounding 16 bytes before and after
            prefix = data[abs_off-16:abs_off]
            suffix = data[abs_off+len(p)+1:abs_off+len(p)+17]
            print(f"Param '{p}' at {hex(abs_off)}:")
            print(f"  pre: {prefix.hex()}")
            print(f"  post: {suffix.hex()}")
    else:
        print(f"Param '{p}' NOT FOUND in WANPPPConnection region!")

