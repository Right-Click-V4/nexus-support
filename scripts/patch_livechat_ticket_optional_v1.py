#!/usr/bin/env python3
"""Live Chat: optional ticket, required branch, resolved/closed popup with agent+date."""
from pathlib import Path
import re

plc = Path('src/components/PortalLiveChat.tsx')
if not plc.exists() or plc.stat().st_size < 5000:
    print('PortalLiveChat skip/stub')
    raise SystemExit(0)

s = plc.read_text()
if 'TICKET_OPTIONAL_BRANCH_REQUIRED_V1' in s and 'This ticket is already' in s and s.count('{') == s.count('}'):
    print('PortalLiveChat already ok')
    raise SystemExit(0)

# Fix stray brace left by older broken applies
s = re.sub(
    r"(// TICKET_OPTIONAL_BRANCH_REQUIRED_V1[^\n]*\n)\s*\}\s*\n(\s*if \(!branch)",
    r"\1\2",
    s,
)

if 'resolvedModal' not in s:
    s = s.replace(
        "const [error, setError] = useState('');",
        "const [error, setError] = useState('');\n"
        "  // TICKET_OPTIONAL_BRANCH_REQUIRED_V1\n"
        "  const [resolvedModal, setResolvedModal] = useState<{\n"
        "    ticketId: string;\n"
        "    agentName: string;\n"
        "    dateLabel: string;\n"
        "    status: string;\n"
        "  } | null>(null);",
        1,
    )
    print('state')

s = re.sub(
    r"\n\s*const tid = ticketId\.trim\(\);\n\s*if \(!tid\) \{\n\s*setError\('Ticket number is required\.'\);\n\s*return;\n\s*\}\n",
    "\n    const tid = ticketId.trim();\n    // TICKET_OPTIONAL_BRANCH_REQUIRED_V1 — ticket optional; branch required\n",
    s,
    count=1,
)

s = re.sub(
    r"\n\s*// TICKET_STATUS_CHAT_V1\n\s*\{\n\s*const ticket = findTicket\(tid\);[\s\S]*?return;\s*\}\s*\}\n",
    "\n",
    s,
    count=1,
)

if 'Branch is required so we can route' not in s:
    needle = "    if (!hasAgentOnline) {\n      setError('No agents are online right now. Please try again later.');\n      return;\n    }"
    insert = """    if (!branch.trim()) {
      setError('Branch is required so we can route your chat.');
      return;
    }
    if (tid) {
      const ticket = findTicket(tid);
      if (ticket) {
        const st = String(ticket.status || '').toLowerCase().replace(/_/g, '-');
        if (st === 'resolved' || st === 'closed') {
          const assignee =
            (ticket as { assignee?: { name?: string } | null }).assignee ||
            (agents || []).find((a) => a.id === (ticket as { assignee_id?: string }).assignee_id);
          const agentName = assignee?.name || 'Support';
          const raw =
            (ticket as { resolved_at?: string }).resolved_at ||
            (ticket as { closed_at?: string }).closed_at ||
            (ticket as { updated_at?: string }).updated_at ||
            (ticket as { created_at?: string }).created_at ||
            '';
          let dateLabel = 'an earlier date';
          if (raw) {
            try {
              dateLabel = new Date(raw).toLocaleString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
              });
            } catch { /* ignore */ }
          }
          setResolvedModal({ ticketId: ticket.id, agentName, dateLabel, status: st });
          setError('');
          return;
        }
      }
    }
    if (!hasAgentOnline) {
      setError('No agents are online right now. Please try again later.');
      return;
    }"""
    if needle in s:
        s = s.replace(needle, insert, 1)
        print('start validation')
    else:
        print('start needle miss')

s = s.replace(
    """      const c = await createChat(nm, (user?.email || email).trim() || undefined, {
        branch: br,
        ticket_id: tid,
      });""",
    """      const c = await createChat(nm, (user?.email || email).trim() || undefined, {
        branch: br,
        ...(tid ? { ticket_id: tid } : {}),
      });""",
    1,
)

s = s.replace('Ticket number\n', 'Ticket number <span className="text-zinc-400 font-normal">(optional)</span>\n', 1)
s = re.sub(r'(value=\{ticketId\}[\s\S]{0,120}?)required', r'\1', s, count=1)
s = s.replace(
    '<select value={branch} onChange={(e) => setBranch(e.target.value)} className={field}>',
    '<select value={branch} onChange={(e) => setBranch(e.target.value)} className={field} required>',
    1,
)
s = s.replace('Branch\n', 'Branch <span className="text-rose-400">*</span>\n', 1)
s = s.replace(
    'Enter a ticket ID — branch fills in automatically when found.',
    'Optional — link an open ticket. Resolved or closed tickets cannot start a new chat.',
)
s = s.replace(
    'Link a ticket number if this is about an existing request.',
    'Branch is required. Ticket number is optional for open cases only.',
)

for old in [
    'disabled={starting || !hasAgentOnline}',
    "disabled={starting || !hasAgentOnline || /\\bis (resolved|closed)\\b/i.test(ticketHint || '')}",
]:
    s = s.replace(old, 'disabled={starting || !hasAgentOnline || !branch.trim() || !!resolvedModal}', 1)

if 'This ticket is already' not in s:
    modal = """
      {resolvedModal && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" role="dialog" aria-modal="true">
          <div className="w-full max-w-md rounded-2xl border border-white/15 bg-zinc-950/95 shadow-2xl shadow-black/50 p-5 text-zinc-100">
            <div className="text-sm font-semibold text-rose-200 mb-2">Ticket already {resolvedModal.status}</div>
            <p className="text-sm text-zinc-200 leading-relaxed">
              This ticket is already {resolvedModal.status} by{' '}
              <span className="font-semibold text-violet-300">{resolvedModal.agentName}</span> on{' '}
              <span className="font-medium text-zinc-100">{resolvedModal.dateLabel}</span>.
            </p>
            <p className="text-[12px] text-zinc-400 mt-2">
              You cannot open Live Chat under ticket <span className="font-mono text-zinc-300">{resolvedModal.ticketId}</span>.
              Clear the ticket field or pick an open ticket, and make sure Branch is selected to start a new chat.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" className="text-xs px-3 py-1.5 rounded-lg border border-white/15 hover:bg-white/5"
                onClick={() => { setTicketId(''); setTicketHint(''); setResolvedModal(null); }}>
                Clear ticket
              </button>
              <button type="button" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-500"
                onClick={() => setResolvedModal(null)}>
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
"""
    if '{error && (' in s:
        s = s.replace('{error && (', modal + '\n              {error && (', 1)
        print('modal')
    elif '<form onSubmit={start}' in s:
        s = s.replace('<form onSubmit={start}', modal + '\n              <form onSubmit={start}', 1)
        print('modal form')

m = re.search(
    r"  useEffect\(\(\) => \{\n    const id = ticketId\.trim\(\);[\s\S]*?\n  \}, \[ticketId, findTicket(?:\, agents)?\]\);",
    s,
)
if m and 'setResolvedModal' not in m.group(0):
    new_hint = """  useEffect(() => {
    const id = ticketId.trim();
    if (!id) {
      setTicketHint('');
      setResolvedModal(null);
      return;
    }
    const t = findTicket(id);
    if (!t) {
      setTicketHint('Ticket not found — you can still start a chat with a branch selected.');
      setResolvedModal(null);
      return;
    }
    // TICKET_OPTIONAL_BRANCH_REQUIRED_V1
    {
      const st = String(t.status || '').toLowerCase().replace(/_/g, '-');
      if (st === 'resolved' || st === 'closed') {
        const assignee =
          (t as { assignee?: { name?: string } | null }).assignee ||
          (agents || []).find((a) => a.id === (t as { assignee_id?: string }).assignee_id);
        const agentName = assignee?.name || 'Support';
        const raw =
          (t as { resolved_at?: string }).resolved_at ||
          (t as { closed_at?: string }).closed_at ||
          (t as { updated_at?: string }).updated_at ||
          (t as { created_at?: string }).created_at ||
          '';
        let dateLabel = 'an earlier date';
        if (raw) {
          try {
            dateLabel = new Date(raw).toLocaleString(undefined, {
              year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
            });
          } catch { /* ignore */ }
        }
        setResolvedModal({ ticketId: t.id, agentName, dateLabel, status: st });
        setTicketHint(`Ticket ${t.id} is ${st} — cannot open Live Chat on this ticket.`);
        if (t.branch) setBranch(t.branch);
        return;
      }
      setResolvedModal(null);
    }
    if (t.branch) {
      setBranch(t.branch);
      setTicketHint(`Found ${t.id}: ${t.title} → branch set to ${t.branch}`);
    } else {
      setTicketHint(`Found ${t.id}: ${t.title} (select a branch below)`);
    }
  }, [ticketId, findTicket, agents]);"""
    s = s[: m.start()] + new_hint + s[m.end() :]
    print('hint effect')

s = re.sub(
    r"(// TICKET_OPTIONAL_BRANCH_REQUIRED_V1[^\n]*\n)\s*\}\s*\n(\s*if \(!branch)",
    r"\1\2",
    s,
)

bal = s.count('{') - s.count('}')
plc.write_text(s)
print('PortalLiveChat braces', bal)
print('has modal', 'This ticket is already' in s)
if bal != 0:
    raise SystemExit(f'brace imbalance {bal}')
print('patch_livechat_ticket_optional_v1 done')
