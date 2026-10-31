#!/usr/bin/env python3
from pathlib import Path
import base64
root = Path(__file__).resolve().parents[1]
parts = []
for i in range(3):
    p = root / 'scripts' / f'cpacc_{i}.b64'
    if not p.exists():
        raise SystemExit(f'missing {p}')
    parts.append(base64.b64decode(p.read_text().strip()).decode())
out = root / 'src' / 'components' / 'CustomerPortal.tsx'
text = ''.join(parts)
out.write_text(text)
print(f'wrote {out} ({len(text)} chars)')
