with open('files/aot-current-pdm-config.xml', 'r', encoding='latin1') as f:
    text = f.read()

import re
pos = text.find('<WANConnectionDevice>')
end_pos = text.find('</WANConnectionDevice>', pos)
chunk = text[pos:end_pos+25]

# Find all <iX> blocks
for m in re.finditer(r'<i(\d+)>', chunk):
    inst = m.group(1)
    sub_start = m.start()
    sub_end = chunk.find(f'</i{inst}>', sub_start)
    sub = chunk[sub_start:sub_end+len(inst)+5]
    print(f'*** Connection Device i{inst} ***')
    # print first 5 lines and any connection type / name / enable
    lines = [l.strip() for l in sub.split('\n') if l.strip()]
    for l in lines[:10]:
        print(' ', l)
    for l in lines:
        if any(k in l for k in ('<Enable', '<Name', '<ConnectionType', 'WANPPPConnection', 'WANIPConnection')):
            print('  ->', l)

