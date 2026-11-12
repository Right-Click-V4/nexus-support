#!/usr/bin/env python3
import base64, zlib
from pathlib import Path
root = Path(__file__).resolve().parent
Path("src/components").mkdir(parents=True, exist_ok=True)
for name, dest in [("lc.b64", "src/components/LiveChatPage.tsx"), ("pv.b64", "src/components/PortalLiveChatView.tsx")]:
    p = root.joinpath("blobs", name)
    if not p.exists():
        continue
    data = zlib.decompress(base64.b64decode(p.read_text().strip()))
    Path(dest).write_bytes(data)
    print(dest, "restored", len(data))
