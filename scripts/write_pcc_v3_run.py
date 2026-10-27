#!/usr/bin/env python3
from pathlib import Path
a = Path("scripts/wp3a.txt").read_text()
b = Path("scripts/wp3b.txt").read_text()
Path("scripts/write_pcc_v3.py").write_text(a + b)
exec(compile(a + b, "write_pcc_v3.py", "exec"))
