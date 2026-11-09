#!/usr/bin/env python3
"""Restore full CustomerPortal from base64 parts if stub."""
from pathlib import Path
import base64

p = Path('src/components/CustomerPortal.tsx')
parts = []
i = 0
while True:
    f = Path(f'scripts/cp_b64_{i}.txt')
    if not f.exists():
        break
    parts.append(f.read_text().strip())
    i += 1
if not parts:
    print('no b64 parts')
    raise SystemExit(0)
raw = base64.b64decode(''.join(parts))
if len(raw) < 50000:
    print('decoded too small', len(raw))
    raise SystemExit(1)
p.write_bytes(raw)
print('restored CP', len(raw))
t = raw.decode()
assert 'export default function CustomerPortal' in t
print('ok features')
