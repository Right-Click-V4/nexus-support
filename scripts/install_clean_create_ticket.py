#!/usr/bin/env python3
"""Install clean createTicket into TicketContext.tsx (session refresh + plain insert)."""
from pathlib import Path

p = Path("src/context/TicketContext.tsx")
if not p.exists():
    raise SystemExit("missing TicketContext")

t = p.read_text()
start = t.find("  const createTicket = async")
end = t.find("  const updateTicket = async")
if start < 0 or end < 0 or end <= start:
    print("WARN: createTicket bounds not found", start, end)
    raise SystemExit(0)

new_fn = r"""  const createTicket = async (data: CreateTicketInput): Promise<Ticket> => {
    const id = `NX-${Date.now().toString(36).toUpperCase()}${Math.floor(Math.random() * 900 + 100)}`;
    const now = new Date().toISOString();
    let priority = String(data.priority || 'medium').toLowerCase() as Priority;
    if (!['critical', 'high', 'medium', 'low'].includes(priority)) priority = 'medium';
    let tags = [...(data.tags || [])];
    try {
      const rules = await loadRules();
      const applied = applyTicketCreatedAutomations(
        {
          title: data.title,
          description: data.description,
          priority,
          branch: data.branch,
          customer_name: data.customer_name,
        },
        rules,
      );
      if (applied.priority) {
        const p = String(applied.priority).toLowerCase() as Priority;
        if (['critical', 'high', 'medium', 'low'].includes(p)) priority = p;
      }
      if (applied.tagAdds?.length) tags = Array.from(new Set([...tags, ...applied.tagAdds]));
    } catch {
      /* rules optional */
    }
    // Prefer live session email (fixes stale/broken client state for one account)
    let sessionEmail = (data.customer_email || user?.email || '').trim();
    if (supabase) {
      try {
        const { data: refreshed, error: refreshErr } = await supabase.auth.refreshSession();
        if (refreshErr) {
          console.warn('[createTicket] refreshSession', refreshErr.message);
        }
        const email = refreshed?.session?.user?.email || (await supabase.auth.getUser()).data.user?.email;
        if (email) sessionEmail = email.trim();
      } catch (e) {
        console.warn('[createTicket] session check failed', e);
      }
      if (!sessionEmail) {
        throw new Error('Your login session expired. Sign out, sign back in, then submit again.');
      }
    }
    const sla_due_at = computeSlaDue(priority, now);
    const ticket: Ticket = {
      id,
      title: data.title,
      description: data.description || '',
      priority,
      status: 'open',
      channel: data.channel || 'portal',
      assignee_id: data.assignee_id || null,
      customer_name: data.customer_name,
      customer_email: sessionEmail,
      branch: data.branch?.trim() || undefined,
      tags: Array.from(new Set([...(tags || []), 'unread'])),
      created_at: now,
      updated_at: now,
      notes: [],
      messages: [],
      attachments: [],
      sla_due_at,
    };
    if (supabase) {
      const row: Record<string, unknown> = {
        id: ticket.id,
        title: ticket.title,
        description: ticket.description || '',
        priority: ticket.priority,
        status: 'open',
        channel: (ticket.channel as string) || 'portal',
        customer_name: ticket.customer_name,
        customer_email: sessionEmail,
      };
      if (ticket.branch) row.branch = ticket.branch;
      if (ticket.sla_due_at) row.sla_due_at = ticket.sla_due_at;

      const { error } = await supabase.from('tickets').insert(row);
      if (error) {
        const { error: error2 } = await supabase.from('tickets').insert({
          id: ticket.id,
          title: ticket.title,
          description: ticket.description || '',
          priority: ticket.priority,
          status: 'new',
          channel: 'email',
          customer_name: ticket.customer_name,
          customer_email: sessionEmail,
        });
        if (error2) {
          const msg = [error2.message, error2.code, error2.details, error2.hint].filter(Boolean).join(' | ');
          const low = (msg || '').toLowerCase();
          if (low.includes('jwt') || low.includes('session') || low.includes('unauthorized') || low === 'bad request') {
            throw new Error(
              'Login session problem for this account. Sign out → clear site data for this site → sign in as ' +
                sessionEmail +
                ' again. (' +
                (msg || 'Bad Request') +
                ')',
            );
          }
          throw new Error(msg || error.message || 'Could not create ticket');
        }
      }
      setTickets((prev) => (prev.some((t) => t.id === ticket.id) ? prev : [ticket, ...prev]));
      try {
        if (typeof BroadcastChannel !== 'undefined') {
          const bc = new BroadcastChannel('nexus-tickets-sync');
          bc.postMessage({ type: 'ticket_created', id: ticket.id, at: Date.now() });
          bc.close();
        }
      } catch {
        /* ignore */
      }
      void refresh({ silent: true });
    } else {
      setTickets((prev) => [ticket, ...prev]);
    }
    void notifyAgents({
      title: 'New ticket',
      body: `${ticket.id}: ${ticket.title} · ${ticket.customer_name}${ticket.channel ? ` (${ticket.channel})` : ''}`,
      link: 'tickets',
    });
    pushAudit({
      entity: 'ticket',
      entity_id: ticket.id,
      action: 'create',
      detail: ticket.title,
      actor: currentAgent?.name || user?.email || 'Agent',
    });
    return ticket;
  };

"""

t2 = t[:start] + new_fn + t[end:]
p.write_text(t2)
print("installed clean createTicket", len(t2))
