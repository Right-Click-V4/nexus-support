#!/usr/bin/env python3
from pathlib import Path
import base64, sys
parts = []
for i in range(4):
    p = Path(f'scripts/cpacc_{i}.b64')
    if not p.exists():
        print('missing', p)
        sys.exit(1)
    parts.append(p.read_text().strip())
raw = base64.b64decode(''.join(parts))
out = Path('src/components/CustomerPortal.tsx')
out.write_bytes(raw)
text = raw.decode('utf-8')
assert 'PortalLiveChat' in text
assert 'AccountProfilePanel' in text
assert 'Loading portal update' not in text
print('assembled CustomerPortal', len(raw), 'bytes')
