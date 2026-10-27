#!/usr/bin/env python3
from pathlib import Path
import base64, zlib
parts = []
for i in range(2):
    parts.append(Path(f"scripts/pcc_cloud_{i}.b64").read_text().replace("\n","").replace("\r","").strip())
if all(parts) and len(parts[0]) > 100:
    raw = zlib.decompress(base64.b64decode("".join(parts)))
    Path("src/components/PortalCommunityChat.tsx").write_bytes(raw)
    print("community cloud component written", len(raw))
else:
    import subprocess
    print("fallback patch_community_cloud")
    subprocess.call(["python3", "scripts/patch_community_cloud.py"])
