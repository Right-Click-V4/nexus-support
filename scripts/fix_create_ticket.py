#!/usr/bin/env python3
"""Make portal ticket create resilient: minimal payload, fallbacks, clearer errors."""
from pathlib import Path

p = Path('src/context/TicketContext.tsx')
if not p.exists():
    print('skip TicketContext')
    raise SystemExit(0)

t = p.read_text()
orig = t

old = """    if (supabase) {
      const payload: Record<string, unknown> = {
        id: ticket.id,
        title: ticket.title,
        description: ticket.description,
        priority: ticket.priority,
        status: ticket.status,
        channel: ticket.channel,
        assignee_id: ticket.assignee_id,
        customer_name: ticket.customer_name,
        customer_email: ticket.customer_email,
        branch: ticket.branch || null,
        notes: ticket.notes,
        messages: ticket.messages,
        attachments: ticket.attachments,
        sla_due_at: ticket.sla_due_at,
        created_at: ticket.created_at,
        updated_at: ticket.updated_at,
        tags: ticket.tags,
      };
      try {
        const ins = await sbTimeout(supabase.from('tickets').insert(payload), 10000);
        const error = ins && typeof ins === 'object' && 'error' in ins ? (ins as { error: { message?: string } | null }).error : null;
        if (error) {
          delete payload.tags;
          const ins2 = await sbTimeout(supabase.from('tickets').insert(payload), 10000);
          const e2 = ins2 && typeof ins2 === 'object' && 'error' in ins2 ? (ins2 as { error: { message?: string } | null }).error : null;
          if (e2) throw new Error(e2.message || 'Could not create ticket');
        }
      } catch (e) {
        throw e instanceof Error ? e : new Error('Could not create ticket');
      }"""

new = """    if (supabase) {
      const pri = String(ticket.priority || 'medium').toLowerCase();
      const safePriority = ['critical', 'high', 'medium', 'low'].includes(pri) ? pri : 'medium';
      const ch = String(ticket.channel || 'portal').toLowerCase();
      const safeChannel = ['email', 'chat', 'phone', 'portal', 'social'].includes(ch) ? ch : 'email';
      const basePayload: Record<string, unknown> = {
        id: ticket.id,
        title: ticket.title,
        description: ticket.description || '',
        priority: safePriority,
        status: 'open',
        channel: safeChannel,
        customer_name: ticket.customer_name,
        customer_email: ticket.customer_email || '',
        created_at: ticket.created_at,
        updated_at: ticket.updated_at,
      };
      if (ticket.branch) basePayload.branch = ticket.branch;
      if (ticket.sla_due_at) basePayload.sla_due_at = ticket.sla_due_at;
      try {
        const tryInsert = async (payload: Record<string, unknown>) => {
          const ins = await sbTimeout(supabase.from('tickets').insert(payload), 12000);
          const error =
            ins && typeof ins === 'object' && 'error' in ins
              ? (ins as { error: { message?: string; code?: string; details?: string } | null }).error
              : null;
          return error;
        };
        let error = await tryInsert(basePayload);
        if (error) {
          const minimal: Record<string, unknown> = {
            id: ticket.id,
            title: ticket.title,
            description: ticket.description || '',
            priority: safePriority,
            status: 'open',
            channel: 'email',
            customer_name: ticket.customer_name,
            customer_email: ticket.customer_email || '',
          };
          error = await tryInsert(minimal);
        }
        if (error) {
          const minimal2: Record<string, unknown> = {
            id: ticket.id,
            title: ticket.title,
            description: ticket.description || '',
            priority: safePriority,
            status: 'new',
            channel: 'email',
            customer_name: ticket.customer_name,
            customer_email: ticket.customer_email || '',
          };
          error = await tryInsert(minimal2);
        }
        if (error) {
          const msg = (error.message || 'Could not create ticket').toLowerCase();
          if (msg.includes('row-level security') || msg.includes('rls') || msg.includes('policy')) {
            throw new Error(
              'Ticket blocked by database security (RLS). Run scripts/rls_customer_tickets.sql in Supabase SQL Editor so customers can insert/read their tickets.',
            );
          }
          if (msg.includes('bad request') || msg.includes('check constraint') || msg.includes('invalid')) {
            throw new Error(
              (error.message || 'Bad Request') +
                ' — check tickets table allows channel/priority/status values, and customer insert RLS policy is enabled.',
            );
          }
          throw new Error(error.message || error.details || 'Could not create ticket');
        }
        try {
          if (ticket.tags?.length) {
            await supabase.from('tickets').update({ tags: ticket.tags }).eq('id', ticket.id);
          }
        } catch {
          /* optional */
        }
      } catch (e) {
        throw e instanceof Error ? e : new Error('Could not create ticket');
      }"""

if old in t:
    t = t.replace(old, new, 1)
    print('patched createTicket insert')
elif 'safePriority' in t:
    print('createTicket already patched')
else:
    print('WARN: createTicket insert pattern not found')

if t != orig:
    p.write_text(t)
    print('wrote', len(t))
else:
    print('no change')
