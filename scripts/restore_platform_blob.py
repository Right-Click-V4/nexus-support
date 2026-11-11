#!/usr/bin/env python3
import base64, zlib, sys
from pathlib import Path
blob = Path(__file__).resolve().parent.joinpath("blobs/pc.b64")
if not blob.exists():
    print("skip: no blobs/pc.b64")
    sys.exit(0)
try:
    data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
    Path("src/context").mkdir(parents=True, exist_ok=True)
    Path("src/context/PlatformContext.tsx").write_bytes(data)
    print("PlatformContext restored", len(data))
except Exception as e:
    print("restore platform skip:", e)
    sys.exit(0)
