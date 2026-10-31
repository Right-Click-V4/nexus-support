#!/usr/bin/env python3
import zlib, base64, subprocess
from pathlib import Path
c = "".join(Path(f"scripts/hc{i}.txt").read_text().strip() for i in range(4))
Path("scripts").mkdir(parents=True, exist_ok=True)
code = zlib.decompress(base64.b64decode(c))
Path("scripts/patch_help_articles.py").write_bytes(code)
print("wrote", len(code))
subprocess.check_call(["python3", "scripts/patch_help_articles.py"])
