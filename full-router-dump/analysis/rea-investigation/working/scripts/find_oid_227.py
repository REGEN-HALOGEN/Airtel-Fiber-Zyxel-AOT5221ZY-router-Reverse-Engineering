import xml.etree.ElementTree as ET

tree = ET.parse(r'full-router-dump\analysis\rea-investigation\working\pdm.xml')
root = tree.getroot()

for obj in root.iter('object'):
    oid = obj.attrib.get('oid')
    name = obj.attrib.get('name')
    if oid in ['227', '0xe3', '0xE3']:
        print(f"Found OID {oid}: {name}")
        for param in obj.iter('parameter'):
            print(f"  Param: {param.attrib.get('name')} (id={param.attrib.get('id')}, type={param.attrib.get('type')})")


