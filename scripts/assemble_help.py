#!/usr/bin/env python3
import base64, subprocess
from pathlib import Path
parts = [Path(f"scripts/hp{i}.txt").read_text().strip() for i in range(3)]
Path("scripts/patch_help_articles.py").write_bytes(base64.b64decode("".join(parts)))
print("assembled", Path("scripts/patch_help_articles.py").stat().st_size)
subprocess.check_call(["python3", "scripts/patch_help_articles.py"])
