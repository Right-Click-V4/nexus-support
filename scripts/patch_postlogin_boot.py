#!/usr/bin/env python3
from pathlib import Path
a = Path("scripts/pll_a.tsx.part").read_text()
b = Path("scripts/pll_b.tsx.part").read_text()
Path("src/components/PostLoginLoader.tsx").write_text(a + b)
print("PostLoginLoader written", len(a) + len(b))
