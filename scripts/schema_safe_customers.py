#!/usr/bin/env python3
"""Force CUSTOMER_COLS to include avatar_url (AVATAR_SYNC)."""
from pathlib import Path
import re

p = Path("src/context/TicketContext.tsx")
if not p.exists():
    print("no TicketContext")
    raise SystemExit(0)
s = p.read_text()
s2 = re.sub(
    r"const CUSTOMER_COLS = '[^']*';[^\n]*",
    "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at, avatar_url'; // AVATAR_SYNC_V1",
    s,
    count=1,
)
p.write_text(s2)
cols = next((ln for ln in s2.splitlines() if "CUSTOMER_COLS" in ln), "?")
print("FINAL", cols)
if "avatar_url" not in cols:
    raise SystemExit("avatar_url missing from CUSTOMER_COLS")
