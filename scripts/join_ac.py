#!/usr/bin/env python3
import zlib, base64, subprocess
from pathlib import Path
c = "".join(Path(f"scripts/ac{i}.txt").read_text().strip() for i in range(3))
pad = (-len(c)) % 4
if pad:
    c += "=" * pad
code = zlib.decompress(base64.b64decode(c))
Path("scripts").mkdir(parents=True, exist_ok=True)
Path("scripts/patch_account_cp.py").write_bytes(code)
print("wrote patch_account_cp", len(code))
subprocess.check_call(["python3", "scripts/patch_account_cp.py"])
