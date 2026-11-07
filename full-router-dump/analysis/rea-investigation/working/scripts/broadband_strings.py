from elftools.elf.elffile import ELFFile

path = r'c:\Users\REGEN\AirtelModemRev\files\broadband.cgi'
with open(path, 'rb') as f:
    elf = ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    base = rodata['sh_addr']

# Extract all null-terminated strings >= 3 chars
strings = []
i = 0
while i < len(data):
    end = data.find(b'\x00', i)
    if end == -1:
        break
    s = data[i:end]
    if len(s) >= 3:
        try:
            txt = s.decode('ascii')
            strings.append((base + i, txt))
        except:
            pass
    i = end + 1

# Filter for WAN/PPP/broadband related
keywords = ['WAN', 'wan', 'PPP', 'ppp', 'PPPoE', 'pppoe', 'Enable', 'eth', 'ETH',
            'VLAN', 'vlan', 'MTU', 'MRU', 'mtu', 'mru', 'NAT', 'nat', 'Service',
            'Username', 'Password', 'ConnectionType', 'broadband', 'Broadband',
            'SaveFlag', 'wanType', 'wanIA', 'Radio', 'cmsg', 'rdm', 'RDM',
            'InternetGateway', 'Connection', 'IfName', 'InterfaceName',
            'X_5067F0', 'formSave', 'RN_', 'Delete', 'ADD', 'SEL',
            'OID', 'oid', 'IA', 'Routed', 'Bridge']
for addr, txt in strings:
    for kw in keywords:
        if kw in txt:
            print(f'0x{addr:06x}: {txt[:120]}')
            break

