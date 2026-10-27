#!/usr/bin/env python3
from pathlib import Path
import base64
parts = [Path(f"scripts/pcc_chunk_{i}.b64").read_text().strip() for i in range(4)]
Path("src/components/PortalCommunityChat.tsx").write_bytes(base64.b64decode("".join(parts)))
print("PortalCommunityChat written", Path("src/components/PortalCommunityChat.tsx").stat().st_size)
