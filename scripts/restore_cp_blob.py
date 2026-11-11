#!/usr/bin/env python3
import base64, zlib
from pathlib import Path
blob = Path("scripts/blobs/cp.b64")
target = Path("src/components/CustomerPortal.tsx")
if not blob.exists():
    print("skip: no cp.b64")
    raise SystemExit(0)
raw = zlib.decompress(base64.b64decode(blob.read_text().strip()))
cur = target.read_text() if target.exists() else ""
if "PLACEHOLDER" in cur or len(cur) < 50000:
    target.write_bytes(raw)
    print("CustomerPortal from cp.b64", len(raw))
else:
    print("CustomerPortal healthy", len(cur))
