#!/usr/bin/env python3
from pathlib import Path
code = "".join(Path(f"scripts/pc_chunk{i}.txt").read_text() for i in range(4))
Path("scripts/patch_community_cloud.py").write_text(code)
exec(compile(code, "patch_community_cloud.py", "exec"))
