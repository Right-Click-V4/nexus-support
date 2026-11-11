#!/usr/bin/env python3
import base64, zlib, sys
from pathlib import Path
blob = Path(__file__).resolve().parent.joinpath("blobs/lc.b64")
if not blob.exists():
    print("skip: no blobs/lc.b64")
    sys.exit(0)
try:
    data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
    Path("src/components").mkdir(parents=True, exist_ok=True)
    Path("src/components/LiveChatPage.tsx").write_bytes(data)
    print("LiveChatPage restored", len(data))
except Exception as e:
    print("restore livechat skip:", e)
    sys.exit(0)
