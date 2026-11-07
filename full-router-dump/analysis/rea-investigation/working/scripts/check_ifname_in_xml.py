import re

with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

matches = re.findall(r'<([^>]*X_5067F0_IfName[^>]*)>(.*?)</\1>', text)
print(f"Found {len(matches)} occurrences of X_5067F0_IfName:")
for tag, val in matches:
    print(f"  <{tag}>{val}</{tag}>")

# Also search for "options_" or "nas0" or "omci" in aot-current-pdm-config.xml
for term in ['options_', 'nas0', 'omci', 'ppp111']:
    print(f"\nOccurrences of '{term}':")
    for line in text.splitlines():
        if term in line:
            print(f"  {line.strip()}")


