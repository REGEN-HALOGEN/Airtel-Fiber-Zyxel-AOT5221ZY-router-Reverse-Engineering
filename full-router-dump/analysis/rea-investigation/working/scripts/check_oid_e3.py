import os
from elftools.elf.elffile import ELFFile

# Check OID 0xe3 (227) in RDM tables or scripts
# Let's inspect lookup_oids.py or inspect_oid_table.py from earlier
# Let's write a quick script to find OID 0xe3 (227)

with open(r'full-router-dump\analysis\rea-investigation\working\scripts\inspect_oid_table.py', 'r') as f:
    print(f.read()[:500])


