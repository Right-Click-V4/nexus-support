#!/usr/bin/env python3
from pathlib import Path
import base64, zlib
a = Path("scripts/pcc_z0.b64").read_text().strip()
b = Path("scripts/pcc_z1.b64").read_text().strip()
raw = zlib.decompress(base64.b64decode(a + b))
Path("src/components/PortalCommunityChat.tsx").write_bytes(raw)
print("written", len(raw))
