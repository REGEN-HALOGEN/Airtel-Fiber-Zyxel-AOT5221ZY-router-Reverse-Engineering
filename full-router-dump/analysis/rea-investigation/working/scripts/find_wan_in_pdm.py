import re

with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

# Let's search for WANDevice or WANConnectionDevice tags
pos = text.find('<WANConnectionDevice>')
if pos != -1:
    print(f"<WANConnectionDevice> found at {pos}")
    print(text[pos:pos+1500])
else:
    print("No <WANConnectionDevice>")
    # search case insensitive
    m = re.search(r'<[^>]*WANConnectionDevice[^>]*>', text, re.IGNORECASE)
    if m:
        print(f"Found: {m.group(0)}")
        p = m.start()
        print(text[p:p+1500])

