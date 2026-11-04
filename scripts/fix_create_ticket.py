#!/usr/bin/env python3
"""Resilient portal ticket create — unique ids, minimal columns, full error text."""
from pathlib import Path

p = Path('src/context/TicketContext.tsx')
if not p.exists():
    print('skip TicketContext')
    raise SystemExit(0)

t = p.read_text()
orig = t

old_id = '    const id = nextTicketId(tickets);'
new_id = """    const id = `NX-${Date.now().toString(36).toUpperCase()}${Math.floor(Math.random() * 1000)
      .toString()
      .padStart(3, '0')}`;"""
if old_id in t and 'Date.now().toString(36)' not in t:
    t = t.replace(old_id, new_id, 1)
    print('patched ticket id generation')

new_block = """    if (supabase) {
      const pri = String(ticket.priority || 'medium').toLowerCase();
      const safePriority = (['critical', 'high', 'medium', 'low'] as const).includes(
        pri as 'critical' | 'high' | 'medium' | 'low',
      )
        ? pri
        : 'medium';
      const fmtErr = (error: { message?: string; code?: string; details?: string; hint?: string } | null) => {
        if (!error) return 'Could not create ticket';
        const parts = [error.message, error.code && `code=${error.code}`, error.details, error.hint].filter(
          Boolean,
        );
        return parts.join(' | ') || 'Could not create ticket';
      };
      const tryInsert = async (payload: Record<string, unknown>) => {
        const ins = await sbTimeout(supabase.from('tickets').insert(payload).select('id').maybeSingle(), 15000);
        const error =
          ins && typeof ins === 'object' && 'error' in ins
            ? (ins as { error: { message?: string; code?: string; details?: string; hint?: string } | null }).error
            : null;
        return error;
      };
      try {
        // Attempt A: minimal columns (matches supabase-schema.sql)
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
        // Attempt B: add branch if present
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
        // Attempt C: portal channel + open status
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
          });
        }
        // Attempt D: no custom id
        if (error) {
          error = await tryInsert({
            title: ticket.title,
            description: ticket.description || '',
            priority: safePriority,
            status: 'new',
            channel: 'email',
            customer_name: ticket.customer_name,
            customer_email: ticket.customer_email || '',
          });
        }
        if (error) {
          const raw = fmtErr(error);
          const low = raw.toLowerCase();
          if (low.includes('row-level security') || low.includes('rls') || low.includes('42501')) {
            throw new Error(
              'Blocked by RLS. In Supabase SQL Editor run scripts/rls_customer_tickets.sql (INSERT policy required). Detail: ' +
                raw,
            );
          }
          throw new Error(raw);
        }
      } catch (e) {
        throw e instanceof Error ? e : new Error('Could not create ticket');
      }"""

if 'fmtErr' in t and 'Attempt A: minimal' in t:
    print('createTicket already fully patched')
elif 'const createTicket' in t:
    ci = t.find('const createTicket')
    si = t.find('    if (supabase) {', ci)
    seti = t.find('      setTickets((prev) => (prev.some((t) => t.id === ticket.id)', si)
    if si > 0 and seti > si:
        t = t[:si] + new_block + '\n' + t[seti:]
        print('replaced createTicket supabase block')
    else:
        print('WARN: could not locate createTicket insert bounds', si, seti)
else:
    print('WARN: no createTicket')

if t != orig:
    p.write_text(t)
    print('wrote', len(t))
else:
    print('no file change')
