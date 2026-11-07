import json

with open(r'full-router-dump\analysis\rea-investigation\working\scripts\libcmd_symbols.json') as f:
    syms = json.load(f)

for k, v in syms['plt'].items():
    if 'ppp' in v.lower() or 'check' in v.lower():
        print(f"PLT 0x{int(k):x}: {v}")


