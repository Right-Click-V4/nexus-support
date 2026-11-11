#!/usr/bin/env python3
import base64, zlib, sys
from pathlib import Path
blob = Path(__file__).resolve().parent.joinpath("blobs/pc.b64")
target = Path("src/context/PlatformContext.tsx")
if not blob.exists():
    print("skip: no blobs/pc.b64")
    sys.exit(0)
try:
    data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
    cur = target.read_text() if target.exists() else ""
    if "PLACEHOLDER" in cur or len(cur) < 5000 or "export function usePlatform" not in cur:
        Path("src/context").mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print("PlatformContext restored", len(data))
    else:
        print("PlatformContext already healthy", len(cur))
except Exception as e:
    print("restore platform skip:", e)
    sys.exit(0)
