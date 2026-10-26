#!/usr/bin/env python3
from pathlib import Path
import base64
chunks = sorted(Path("scripts").glob("pc_live_chunk_*.b64"))
if not chunks:
    print("no chunks")
    raise SystemExit(0)
raw = "".join(p.read_text().strip() for p in chunks)
text = base64.b64decode(raw).decode()
Path("src/context/PlatformContext.tsx").write_text(text)
print("PlatformContext restored from chunks", len(text))
