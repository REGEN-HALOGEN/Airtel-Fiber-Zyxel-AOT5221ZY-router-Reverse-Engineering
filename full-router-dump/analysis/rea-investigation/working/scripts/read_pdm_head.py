with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    for i in range(50):
        line = f.readline()
        if not line:
            break
        print(line.strip())

