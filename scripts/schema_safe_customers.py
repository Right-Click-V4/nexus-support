#!/usr/bin/env python3
"""Keep CUSTOMER_COLS including avatar_url when present (AVATAR_SYNC_V1)."""
from pathlib import Path
import re

p = Path("src/context/TicketContext.tsx")
if not p.exists():
    print("no TicketContext")
    raise SystemExit(0)
s = p.read_text()
s2 = re.sub(
    r"const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at'; // SCHEMA_SAFE_NO_AVATAR",
    "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at, avatar_url'; // AVATAR_SYNC_V1",
    s,
)
if "avatar_url" not in s2 and "CUSTOMER_COLS" in s2:
    s2 = re.sub(
        r"const CUSTOMER_COLS = '[^']*';[^\n]*",
        "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at, avatar_url'; // AVATAR_SYNC_V1",
        s2,
        count=1,
    )
if s2 != s:
    p.write_text(s2)
    print("CUSTOMER_COLS avatar-aware")
else:
    print("CUSTOMER_COLS ok")
cols = next((ln for ln in Path("src/context/TicketContext.tsx").read_text().splitlines() if "CUSTOMER_COLS" in ln), "?")
print("FINAL", cols)
