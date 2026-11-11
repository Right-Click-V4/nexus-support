#!/usr/bin/env python3
import base64, zlib
from pathlib import Path
b64 = Path(__file__).resolve().parent.joinpath("blobs/lc.b64").read_text().strip()
Path("src/components").mkdir(parents=True, exist_ok=True)
data = zlib.decompress(base64.b64decode(b64))
Path("src/components/LiveChatPage.tsx").write_bytes(data)
print("LiveChatPage restored", len(data))
