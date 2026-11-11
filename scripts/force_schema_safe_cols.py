#!/usr/bin/env python3
from pathlib import Path
p = Path("src/context/TicketContext.tsx")
if not p.exists():
    print("skip TicketContext")
    raise SystemExit(0)
s = p.read_text()
s2 = s.replace(
    "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at, avatar_url';",
    "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';",
)
if s2 != s:
    p.write_text(s2)
    print("CUSTOMER_COLS schema-safe")
else:
    print("CUSTOMER_COLS already safe or pattern differed")
