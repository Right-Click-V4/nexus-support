#!/usr/bin/env python3
from pathlib import Path
import base64
parts = sorted(Path("scripts/pc_chunks").glob("pc_*.b64"), key=lambda p: int(p.stem.split("_")[1]))
if not parts:
    raise SystemExit("no chunks")
data = "".join(p.read_text().strip() for p in parts)
Path("src/context/PlatformContext.tsx").write_text(base64.b64decode(data).decode())
print("PlatformContext restored", Path("src/context/PlatformContext.tsx").stat().st_size)
