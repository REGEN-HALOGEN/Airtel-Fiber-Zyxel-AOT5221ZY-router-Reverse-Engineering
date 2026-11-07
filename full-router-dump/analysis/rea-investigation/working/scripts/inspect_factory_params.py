with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

targets = [
    'WanAutoDetect',
    'WANMode',
    'WANEthernetInterfaceConfig',
    'X_5067F0_GponInterafceConfig',
    'WANConnectionDevice instance="1"',
    'WANConnectionDevice instance="2"',
    'WANConnectionDevice instance="3"',
    'Layer3Forwarding',
    'X_5067F0_IPv6Layer3Forwarding'
]

for t in targets:
    pos = text.find(t)
    if pos != -1:
        print('=== ' + t + ' ===')
        print(text[pos:pos+350])
        print('='*50)
    else:
        print('=== ' + t + ' NOT FOUND ===')

