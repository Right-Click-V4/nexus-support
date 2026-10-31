#!/usr/bin/env python3
import zlib, base64, subprocess
from pathlib import Path
c = "".join(Path(f"scripts/p{i:02d}.txt").read_text().strip() for i in range(12))
c = "".join(c.split())
pad = (-len(c)) % 4
if pad:
    c += "=" * pad
code = zlib.decompress(base64.b64decode(c))
Path("scripts").mkdir(parents=True, exist_ok=True)
Path("scripts/patch_account_cp.py").write_bytes(code)
print("wrote", len(code))
subprocess.check_call(["python3", "scripts/patch_account_cp.py"])
