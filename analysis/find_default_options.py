import os

for fname in os.listdir(r'C:\Users\REGEN\AirtelModemRev\files'):
    fp = os.path.join(r'C:\Users\REGEN\AirtelModemRev\files', fname)
    if os.path.isfile(fp):
        with open(fp, 'rb') as f:
            data = f.read()
        pos = 0
        while True:
            idx = data.find(b'default_options', pos)
            if idx == -1:
                break
            print(f'{fname} @ 0x{idx:x}')
            pos = idx + 1

