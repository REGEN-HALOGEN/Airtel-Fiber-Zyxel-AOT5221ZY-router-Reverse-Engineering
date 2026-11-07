import json

with open(r'full-router-dump\analysis\rea-investigation\working\scripts\libcmd_symbols.json') as f:
    syms = json.load(f)

print(f"PLT 0x45770: {syms['plt'].get('284528', 'unknown')}")
print(f"Decimal 0x45770 = {0x45770}")
print(f"PLT entry for 0x45770: {syms['plt'].get(str(0x45770), 'unknown')}")


