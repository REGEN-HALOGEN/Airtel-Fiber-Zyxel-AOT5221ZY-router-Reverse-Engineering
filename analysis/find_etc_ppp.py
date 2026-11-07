import os

for fn in os.listdir(r'C:\Users\REGEN\AirtelModemRev\files'):
    fp = os.path.join(r'C:\Users\REGEN\AirtelModemRev\files', fn)
    if os.path.isfile(fp):
        with open(fp, 'rb') as f:
            data = f.read()
        pos = 0
        while True:
            idx = data.find(b'/etc/ppp', pos)
            if idx == -1:
                break
            end = data.find(b'\x00', idx)
            if end != -1 and end - idx < 100:
                s = data[idx:end].decode('latin1', errors='replace')
                print(f'{fn} @ 0x{idx:x}: {s}')
            pos = idx + 1
