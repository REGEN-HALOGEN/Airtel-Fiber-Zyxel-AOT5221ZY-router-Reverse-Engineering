with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

pos = 0
while True:
    idx = text.find('WANPPPConnection', pos)
    if idx == -1: break
    print(f"Found WANPPPConnection at index {idx}:")
    print(text[max(0, idx-50):min(len(text), idx+300)])
    pos = idx + len('WANPPPConnection')


