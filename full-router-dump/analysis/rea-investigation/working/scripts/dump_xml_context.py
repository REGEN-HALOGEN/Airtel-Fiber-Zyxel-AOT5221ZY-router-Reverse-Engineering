with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'X_5067F0_IfName' in line or 'X_5067F0_InterfaceName' in line:
        start = max(0, i - 10)
        end = min(len(lines), i + 10)
        print(f"\n--- Context around line {i+1} ---")
        for j in range(start, end):
            print(f"{j+1:5d}: {lines[j].strip()}")


