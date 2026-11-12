#!/usr/bin/env python3
"""Fix ReferenceError: autoAssignee is not defined in createTicket audit detail."""
from pathlib import Path
import re

p = Path("src/context/TicketContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    print("skip TicketContext")
    raise SystemExit(0)

t = p.read_text()
if "AUTO_ASSIGNEE_FIX_V1" in t:
    print("already fixed")
    raise SystemExit(0)

old = """detail: `${ticket.title}${autoAssignee ? ` · assigned ${autoAssignee}` : ''}${priority !== data.priority ? ` · auto priority ${priority}` : ''}`,"""
new = """detail: `${ticket.title}${ticket.assignee_id ? ` · assigned ${ticket.assignee_id}` : ''}${priority !== data.priority ? ` · auto priority ${priority}` : ''}`, // AUTO_ASSIGNEE_FIX_V1"""

if old in t:
    t = t.replace(old, new)
    print("autoAssignee detail fixed")
else:
    t2, n = re.subn(
        r'\$\{autoAssignee \? ` · assigned \$\{autoAssignee\}` : \'\'\\}',
        "${ticket.assignee_id ? ` · assigned ${ticket.assignee_id}` : ''}",
        t,
    )
    if n:
        t = t2
        print("autoAssignee regex fixed", n)
    else:
        print("pattern miss")
        if "autoAssignee" in t:
            for i,l in enumerate(t.splitlines(),1):
                if "autoAssignee" in l:
                    print(i, l[:120])

if "autoAssignee" in t and "AUTO_ASSIGNEE_FIX_V1" not in t:
    t = t.replace("autoAssignee", "ticket.assignee_id")
    print("blanket replace")

if "AUTO_ASSIGNEE_FIX_V1" not in t:
    t = t.replace("const createTicket = async", "/* AUTO_ASSIGNEE_FIX_V1 */\n  const createTicket = async", 1)

p.write_text(t)
print("done", len(t), "remaining autoAssignee", t.count("autoAssignee"))
