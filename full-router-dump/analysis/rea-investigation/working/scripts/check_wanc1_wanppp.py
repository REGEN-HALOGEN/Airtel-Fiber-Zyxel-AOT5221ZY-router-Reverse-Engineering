with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

# Find WANConnectionDevice.1.WANPPPConnection.1
pos = text.find('WANConnectionDevice instance="1"')
if pos != -1:
    end = text.find('</WANPPPConnection>', pos)
    chunk = text[pos:end+20]
    for line in chunk.splitlines():
        if any(k in line for k in ['IfName', 'InterfaceName', 'Name', 'Enable', 'Username', 'VLANID']):
            print(line.strip())


