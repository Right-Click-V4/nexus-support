#!/usr/bin/env python3
"""Fix portal ticket create: lowercase priority, no RETURNING/select, unique ids, real errors."""
from pathlib import Path

p = Path('src/context/TicketContext.tsx')
if not p.exists():
    print('skip TicketContext')
    raise SystemExit(0)

t = p.read_text()
orig = t

old_id = '    const id = nextTicketId(tickets);'
new_id = """    const id = `NX-${Date.now().toString(36).toUpperCase()}${Math.floor(Math.random() * 900 + 100)}`;"""
if old_id in t:
    t = t.replace(old_id, new_id, 1)
    print('patched id')
elif 'Date.now().toString(36)' in t:
    print('id already dynamic')

if 'let priority = data.priority;' in t:
    t = t.replace(
        'let priority = data.priority;',
        "let priority = String(data.priority || 'medium').toLowerCase() as Priority;",
        1,
    )
    print('patched priority normalize')

new_block = """    if (supabase) {
      const safePriority = (['critical', 'high', 'medium', 'low'] as const).includes(
        String(priority).toLowerCase() as 'low' | 'medium' | 'high' | 'critical',
      )
        ? String(priority).toLowerCase()
        : 'medium';
      const fmtErr = (error: {
        message?: string;
        code?: string;
        details?: string;
        hint?: string;
      } | null) => {
        if (!error) return 'Could not create ticket';
        return [error.message, error.code && `code=${error.code}`, error.details, error.hint]
          .filter(Boolean)
          .join(' | ') || 'Could not create ticket';
      };
      // Do NOT .select() after insert — RETURNING fails when SELECT RLS is tighter than INSERT (often shows as Bad Request)
      const tryInsert = async (payload: Record<string, unknown>) => {
        const ins = await sbTimeout(supabase.from('tickets').insert(payload), 15000);
        const error =
          ins && typeof ins === 'object' && 'error' in ins
            ? (ins as {
                error: { message?: string; code?: string; details?: string; hint?: string } | null;
              }).error
            : null;
        return error;
      };
      try {
        let error = await tryInsert({
          id: ticket.id,
          title: ticket.title,
          description: ticket.description || '',
          priority: safePriority,
          status: 'new',
          channel: 'email',
          customer_name: ticket.customer_name,
          customer_email: ticket.customer_email || '',
        });
        if (error && ticket.branch) {
          error = await tryInsert({
            id: ticket.id,
            title: ticket.title,
            description: ticket.description || '',
            priority: safePriority,
            status: 'new',
            channel: 'email',
            customer_name: ticket.customer_name,
            customer_email: ticket.customer_email || '',
            branch: ticket.branch,
          });
        }
        if (error) {
          error = await tryInsert({
            id: ticket.id,
            title: ticket.title,
            description: ticket.description || '',
            priority: safePriority,
            status: 'open',
            channel: 'portal',
            customer_name: ticket.customer_name,
            customer_email: ticket.customer_email || '',
            branch: ticket.branch || null,
          });
        }
        if (error) {
          throw new Error(fmtErr(error));
        }
      } catch (e) {
        throw e instanceof Error ? e : new Error('Could not create ticket');
      }"""

ci = t.find('const createTicket')
if ci >= 0:
    si = t.find('    if (supabase) {', ci)
    seti = t.find('      setTickets((prev) => (prev.some((t) => t.id === ticket.id)', si if si > 0 else ci)
    if si > 0 and seti > si:
        t = t[:si] + new_block + '\n' + t[seti:]
        print('replaced supabase insert block')
    else:
        print('WARN bounds', si, seti)
else:
    print('WARN no createTicket')

if t != orig:
    p.write_text(t)
    print('wrote', len(t))
else:
    print('no change')
