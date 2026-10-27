#!/usr/bin/env python3
from pathlib import Path
import base64
a = Path("scripts/pcc_new_a.b64").read_text().strip()
b = Path("scripts/pcc_new_b.b64").read_text().strip()
Path("src/components/PortalCommunityChat.tsx").write_bytes(base64.b64decode(a + b))
print("PortalCommunityChat written", Path("src/components/PortalCommunityChat.tsx").stat().st_size)
