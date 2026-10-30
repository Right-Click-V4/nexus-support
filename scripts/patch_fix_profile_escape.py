#!/usr/bin/env python3
"""Repair ProfilePage bad \\n escape that breaks TypeScript build."""
from pathlib import Path
p = Path("src/components/ProfilePage.tsx")
if not p.exists():
    print("no ProfilePage")
    raise SystemExit(0)
t = p.read_text()
orig = t
t = t.replace("characters');\\n        if (!supabase)", "characters');\n        if (!supabase)")
t = t.replace("characters');\\n", "characters');\n")
if t != orig:
    p.write_text(t)
    print("repaired ProfilePage escaped newline")
else:
    print("ProfilePage escape ok")
