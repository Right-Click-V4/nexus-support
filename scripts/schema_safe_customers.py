#!/usr/bin/env python3
"""Strip avatar_url from CUSTOMER_COLS if present (schema-safe)."""
from pathlib import Path
import re

p = Path("src/context/TicketContext.tsx")
if not p.exists():
    print("no TicketContext")
    raise SystemExit(0)
s = p.read_text()
s2 = re.sub(
    r"const CUSTOMER_COLS = '[^']*';[^\n]*",
    "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at'; // SCHEMA_SAFE_NO_AVATAR",
    s,
    count=1,
)
p.write_text(s2)
cols = next((ln for ln in s2.splitlines() if "CUSTOMER_COLS" in ln), "?")
print("FINAL", cols)
if "avatar_url" in cols:
    raise SystemExit("CUSTOMER_COLS still has avatar_url")
