#!/usr/bin/env python3
from pathlib import Path
import base64, zlib, urllib.request
# Prefer committed payload parts if present; else apply API-based patch from communityApi
parts = []
for i in range(2):
    f = Path(f"scripts/pcc_cloud_{i}.b64")
    if f.exists():
        parts.append(f.read_text().strip())
if len(parts) == 2:
    raw = zlib.decompress(base64.b64decode("".join(parts)))
    Path("src/components/PortalCommunityChat.tsx").write_bytes(raw)
    print("community cloud component written", len(raw))
else:
    print("payload parts missing — run patch_community_cloud.py")
    import subprocess
    subprocess.call(["python3", "scripts/patch_community_cloud.py"])
