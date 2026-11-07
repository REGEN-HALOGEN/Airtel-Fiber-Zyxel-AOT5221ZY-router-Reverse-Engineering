import re

with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

# Let's find WANConnectionDevice blocks
wanc_blocks = re.findall(r'<WANConnectionDevice instance="(\d+)">.*?</WANConnectionDevice>', text, re.DOTALL)
print(f"Found {len(wanc_blocks)} WANConnectionDevice blocks in aot-current-pdm-config.xml")

for m in re.finditer(r'<WANConnectionDevice instance="(\d+)">', text):
    inst = m.group(1)
    start = m.start()
    end = text.find('</WANConnectionDevice>', start)
    chunk = text[start:end+22]
    print(f"\n=== WANConnectionDevice instance {inst} ===")
    lines = chunk.split('\n')
    for line in lines[:25]:
        print(f"  {line}")
    if len(lines) > 25:
        print("  ...")
        for line in lines[-5:]:
            print(f"  {line}")

