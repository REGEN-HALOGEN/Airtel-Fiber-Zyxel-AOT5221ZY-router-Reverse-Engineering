import xml.etree.ElementTree as ET

tree = ET.parse(r'C:\Users\REGEN\AirtelModemRev\files\aot-current-pdm-config.xml')
root = tree.getroot()

for wandev in root.iter('WANDevice'):
    for i1 in wandev.findall('i1'):
        for conndev in i1.findall('WANConnectionDevice'):
            for i3 in conndev.findall('i3'):
                print('Found WANConnectionDevice.3:')
                for child in i3:
                    print(f'  Child: {child.tag}')
                    for sub in child:
                        print(f'    Sub: {sub.tag}')
                        for leaf in sub:
                            print(f'      {leaf.tag}: {leaf.text}')

