import xml.etree.ElementTree as ET

tree = ET.parse('files/aot-current-pdm-config.xml')
root = tree.getroot()

def print_all(elem, prefix=""):
    for child in elem:
        if len(child) == 0:
            print(f"{prefix}{child.tag}: {child.text}")
        else:
            print(f"{prefix}[{child.tag}]")
            print_all(child, prefix + "  ")

p1 = root.find('.//WANConnectionDevice/i1/WANPPPConnection/i1')
print("=== WANConnectionDevice.1.WANPPPConnection.1 ===")
print_all(p1)

p3 = root.find('.//WANConnectionDevice/i3/WANIPConnection/i1')
print("\n=== WANConnectionDevice.3.WANIPConnection.1 ===")
print_all(p3)

