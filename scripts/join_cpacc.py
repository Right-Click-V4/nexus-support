#!/usr/bin/env python3
import zlib, base64
from pathlib import Path
parts = []
for i in range(8):
    p = Path(f"scripts/cpacc{i}.txt")
    if not p.exists():
        raise SystemExit(f"missing {p}")
    parts.append(p.read_text().strip())
c = "".join(parts)
pad = (-len(c)) % 4
if pad:
    c += "=" * pad
data = zlib.decompress(base64.b64decode(c))
Path("src/components/CustomerPortal.tsx").write_bytes(data)
print("wrote CustomerPortal.tsx", len(data))
