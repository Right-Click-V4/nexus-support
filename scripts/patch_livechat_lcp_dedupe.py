#!/usr/bin/env python3
"""Fix LiveChatPage duplicate useTickets import/destructure that breaks build."""
from pathlib import Path
import re

p = Path("src/components/LiveChatPage.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
lines = t.splitlines(True)
seen = False
out = []
for line in lines:
    if "import { useTickets } from '../context/TicketContext';" in line:
        if seen:
            continue
        seen = True
    out.append(line)
t = "".join(out)
t = re.sub(
    r"(const \{ currentAgent, createTicket, findTicket \} = useTickets\(\);\n)(?:const \{[^}]*\} = useTickets\(\);\n)+",
    r"\1",
    t,
)
t = re.sub(
    r"(const \{ createTicket, findTicket \} = useTickets\(\);\n)(?:const \{ createTicket, findTicket \} = useTickets\(\);\n)+",
    r"\1",
    t,
)
t = re.sub(
    r"const \{ createTicket, findTicket \} = useTickets\(\);\n\s*const \{ currentAgent, createTicket, findTicket \} = useTickets\(\);",
    "const { currentAgent, createTicket, findTicket } = useTickets();",
    t,
)
t = re.sub(
    r"const \{ currentAgent, createTicket, findTicket \} = useTickets\(\);\n\s*const \{ createTicket, findTicket \} = useTickets\(\);",
    "const { currentAgent, createTicket, findTicket } = useTickets();",
    t,
)
p.write_text(t)
print("LiveChatPage deduped")
