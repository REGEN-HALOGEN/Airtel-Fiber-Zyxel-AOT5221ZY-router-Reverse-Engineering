with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

chunk = text[22401:24508]
print(chunk)


