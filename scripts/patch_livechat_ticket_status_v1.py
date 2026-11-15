#!/usr/bin/env python3
"""Block Live Chat start for Resolved/Closed tickets; allow open/pending/on-hold/new."""
from pathlib import Path
import re

def patch_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size < 2000:
        print(path.name, 'skip')
        return
    s = path.read_text()
    if 'TICKET_STATUS_CHAT_V1' in s:
        print(path.name, 'already')
        return

    marker = '// TICKET_STATUS_CHAT_V1'

    old_hint = """    const t = findTicket(id);
    if (!t) {
      setTicketHint('Ticket not found yet — you can still start a chat.');
      return;
    }
    if (t.branch) {
      setBranch(t.branch);
      setTicketHint(`Found ${t.id}: ${t.title} → branch set to ${t.branch}`);
    } else {
      setTicketHint(`Found ${t.id}: ${t.title} (no branch on ticket — pick one below if you want)`);
    }"""
    new_hint = """    const t = findTicket(id);
    if (!t) {
      setTicketHint('Ticket not found yet — you can still start a chat.');
      return;
    }
    // TICKET_STATUS_CHAT_V1
    {
      const st = String(t.status || '').toLowerCase().replace(/_/g, '-');
      if (st === 'resolved' || st === 'closed') {
        setTicketHint(`Ticket ${t.id} is ${st} — Live Chat is only available for Open, Pending, or On-Hold tickets.`);
        return;
      }
    }
    if (t.branch) {
      setBranch(t.branch);
      setTicketHint(`Found ${t.id}: ${t.title} → branch set to ${t.branch}`);
    } else {
      setTicketHint(`Found ${t.id}: ${t.title} (no branch on ticket — pick one below if you want)`);
    }"""
    if old_hint in s:
        s = s.replace(old_hint, new_hint, 1)
        print(path.name, 'hint')
    else:
        if 'findTicket(id)' in s and 'TICKET_STATUS_CHAT_V1' not in s:
            s2 = re.sub(
                r"(const t = findTicket\(id\);\s*if \(!t\) \{[\s\S]*?return;\s*\})",
                lambda m: m.group(1) + """
    // TICKET_STATUS_CHAT_V1
    {
      const st = String(t.status || '').toLowerCase().replace(/_/g, '-');
      if (st === 'resolved' || st === 'closed') {
        setTicketHint(`Ticket ${t.id} is ${st} — Live Chat is only available for Open, Pending, or On-Hold tickets.`);
        return;
      }
    }""",
                s,
                count=1,
            )
            if s2 != s:
                s = s2
                print(path.name, 'hint soft')
            else:
                print(path.name, 'hint miss')

    old_start = """    const tid = ticketId.trim();
    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    if (!hasAgentOnline) {
      setError('No agents are online right now. Please try again later.');
      return;
    }"""
    new_start = """    const tid = ticketId.trim();
    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    // TICKET_STATUS_CHAT_V1
    {
      const ticket = findTicket(tid);
      if (ticket) {
        const st = String(ticket.status || '').toLowerCase().replace(/_/g, '-');
        if (st === 'resolved' || st === 'closed') {
          setError(`Ticket ${ticket.id} is ${st}. Live Chat can only be opened for Open, Pending, or On-Hold tickets.`);
          return;
        }
      }
    }
    if (!hasAgentOnline) {
      setError('No agents are online right now. Please try again later.');
      return;
    }"""
    if old_start in s:
        s = s.replace(old_start, new_start, 1)
        print(path.name, 'start')
    elif 'Ticket number is required' in s and 'TICKET_STATUS_CHAT_V1' not in s:
        s = s.replace(
            """    if (!tid) {
      setError('Ticket number is required.');
      return;
    }""",
            """    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    // TICKET_STATUS_CHAT_V1
    {
      const ticket = findTicket(tid);
      if (ticket) {
        const st = String(ticket.status || '').toLowerCase().replace(/_/g, '-');
        if (st === 'resolved' || st === 'closed') {
          setError(`Ticket ${ticket.id} is ${st}. Live Chat can only be opened for Open, Pending, or On-Hold tickets.`);
          return;
        }
      }
    }""",
            1,
        )
        print(path.name, 'start soft')
    else:
        print(path.name, 'start miss')

    if 'disabled={starting || !hasAgentOnline}' in s:
        s = s.replace(
            'disabled={starting || !hasAgentOnline}',
            "disabled={starting || !hasAgentOnline || /\\bis (resolved|closed)\\b/i.test(ticketHint || '')}",
            1,
        )
        print(path.name, 'btn disable')

    path.write_text(s)
    print(path.name, 'braces', s.count('{') - s.count('}'))

patch_file(Path('src/components/PortalLiveChat.tsx'))
plv = Path('src/components/PortalLiveChatView.tsx')
if plv.exists() and 'ticketId' in plv.read_text() and 'findTicket' in plv.read_text():
    patch_file(plv)
else:
    print('PortalLiveChatView no ticket field')

print('patch_livechat_ticket_status_v1 done')
