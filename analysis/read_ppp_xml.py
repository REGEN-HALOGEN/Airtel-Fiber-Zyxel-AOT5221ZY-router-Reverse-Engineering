import xml.etree.ElementTree as ET

tree = ET.parse(r'C:\Users\REGEN\AirtelModemRev\files\aot-current-pdm-config.xml')
root = tree.getroot()

# Find WANPPPConnection.1 in the tree
for ppp in root.iter('WANPPPConnection'):
    for i1 in ppp.findall('i1'):
        for elem in i1:
            print(f'{elem.tag}: {elem.text}')

