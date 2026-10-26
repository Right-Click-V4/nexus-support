#!/usr/bin/env python3
import base64
from pathlib import Path
a = Path("scripts/v3a.b64").read_text().strip()
b = Path("scripts/v3b.b64").read_text().strip()
Path("scripts/patch_announce_v3.py").write_bytes(base64.b64decode(a + b))
print("assembled patch_announce_v3.py")
