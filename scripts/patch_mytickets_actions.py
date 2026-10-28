#!/usr/bin/env python3
"""My Tickets: fuller layout, green nav icon, guide icon, Action menu (View / Follow-Up)."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-actions-v1" in c:
    print("already")
    raise SystemExit(0)

if "MoreVertical" not in c:
    c = c.replace(
        "  Flag, ListTree, Lightbulb, Clock3, ClipboardList,\n} from 'lucide-react';",
        "  Flag, ListTree, Lightbulb, Clock3, ClipboardList, MoreVertical, Info, Send,\n} from 'lucide-react';",
        1,
    )
    print("imports ok")

c = c.replace(
    "  mytickets: { title: 'My Tickets', desc: 'Review tickets you have opened with support.', iconColor: 'text-blue-600 dark:text-blue-400' },",
    "  mytickets: { title: 'My Tickets', desc: 'Review tickets you have opened with support.', iconColor: 'text-emerald-600 dark:text-emerald-400' },",
    1,
)
c = c.replace(
    'mytickets: "text-blue-600 dark:text-blue-400"',
    'mytickets: "text-emerald-600 dark:text-emerald-400"',
)

if "myTicketMenuId" not in c:
    c = c.replace(
        "  const [myTicketsDateTo, setMyTicketsDateTo] = useState('');",
        """  const [myTicketsDateTo, setMyTicketsDateTo] = useState('');
  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);
  const [followUpTicket, setFollowUpTicket] = useState<TicketType | null>(null);
  const [followUpText, setFollowUpText] = useState('');
  const [followUpBusy, setFollowUpBusy] = useState(false);""",
        1,
    )
    print("state ok")

start = c.find("            {view === 'mytickets' && (() => {")
end = c.find("            {view === 'help' && (", start)
if start < 0 or end < 0:
    print("block miss")
    raise SystemExit(1)

# Use the already-built new_block from local successful run - read from file
new_block = Path("/tmp/ma/src/components/CustomerPortal.tsx").read_text()
s2 = new_block.find("            {view === 'mytickets' && (() => {")
e2 = new_block.find("            {view === 'help' && (", s2)
if s2 < 0:
    print("local block miss")
    raise SystemExit(1)
new_block = new_block[s2:e2]

c = c[:start] + new_block + c[end:]
if "mytickets-actions-v1" not in c:
    c = "/* mytickets-actions-v1 */\n" + c
cp.write_text(c)
print("done")
