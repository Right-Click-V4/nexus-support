#!/usr/bin/env python3
"""Customer portal: fetch tickets scoped by email (RLS-friendly) + skip soft-deleted."""
from pathlib import Path

p = Path('src/context/TicketContext.tsx')
if not p.exists():
    print('skip TicketContext')
    raise SystemExit(0)

t = p.read_text()
orig = t

old = """    try {
      const [tRes, aRes, cRes] = await Promise.all([
        withTimeout(
          supabase.from('tickets').select(TICKET_COLS).order('created_at', { ascending: false }).limit(120),
          5000,
        ),
        withTimeout(supabase.from('agents').select(AGENT_COLS).limit(80), 4000),
        withTimeout(supabase.from('customers').select(CUSTOMER_COLS).limit(200), 4000),
      ]);
      const agentRows = aRes && typeof aRes === 'object' && 'data' in aRes ? (aRes as { data: Agent[] | null }).data : null;
      const customerRows = cRes && typeof cRes === 'object' && 'data' in cRes ? (cRes as { data: Customer[] | null }).data : null;
      const ticketRows = tRes && typeof tRes === 'object' && 'data' in tRes ? (tRes as { data: Ticket[] | null }).data : null;"""

new = """    try {
      const email = (user?.email || '').trim();
      const customerScoped = accountRole === 'customer' && !!email;
      const ticketsQuery = customerScoped
        ? supabase
            .from('tickets')
            .select(TICKET_COLS)
            .ilike('customer_email', email)
            .order('created_at', { ascending: false })
            .limit(200)
        : supabase.from('tickets').select(TICKET_COLS).order('created_at', { ascending: false }).limit(120);
      const [tRes, aRes, cRes] = await Promise.all([
        withTimeout(ticketsQuery, 8000),
        withTimeout(supabase.from('agents').select(AGENT_COLS).limit(80), 4000),
        withTimeout(supabase.from('customers').select(CUSTOMER_COLS).limit(200), 4000),
      ]);
      const agentRows = aRes && typeof aRes === 'object' && 'data' in aRes ? (aRes as { data: Agent[] | null }).data : null;
      const customerRows = cRes && typeof cRes === 'object' && 'data' in cRes ? (cRes as { data: Customer[] | null }).data : null;
      const ticketRows = tRes && typeof tRes === 'object' && 'data' in tRes ? (tRes as { data: Ticket[] | null }).data : null;
      if (customerScoped && Array.isArray(ticketRows) && ticketRows.length === 0) {
        console.warn('[tickets] 0 rows for', email, '- check RLS + customer_email on tickets table');
      }"""

if old in t:
    t = t.replace(old, new, 1)
    print('patched refresh query')
elif 'customerScoped' in t:
    print('refresh already patched')
else:
    print('WARN: refresh pattern not found')

for a, b in [
    ("  }, []);\n\n  useEffect(() => {\n    void refresh();\n  }, [refresh]);",
     "  }, [user?.email, accountRole]);\n\n  useEffect(() => {\n    void refresh();\n  }, [refresh]);"),
]:
    if a in t:
        t = t.replace(a, b, 1)
        print('patched refresh deps')
        break

old_fe = """const ticketsForEmail = (email: string) =>
    tickets.filter((t) => (t.customer_email || '').toLowerCase() === email.toLowerCase());"""
new_fe = """const ticketsForEmail = (email: string) =>
    tickets.filter((t) => {
      if ((t as { deleted_at?: string | null }).deleted_at) return false;
      return (t.customer_email || '').toLowerCase().trim() === email.toLowerCase().trim();
    });"""
if old_fe in t:
    t = t.replace(old_fe, new_fe, 1)
    print('patched ticketsForEmail')

if t != orig:
    p.write_text(t)
    print('wrote', p, len(t))
else:
    print('no file changes')
