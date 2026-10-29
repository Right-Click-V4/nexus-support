#!/usr/bin/env python3
"""Silent ticket housekeeping updates + toast only for truly new notifs after hydrate."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
t = tc.read_text()
if "update-silent-notify-v1" not in t:
    old_sig = """  const updateTicket = async (
    id: string,
    updates: Partial<
      Pick<
        Ticket,
        | 'status'
        | 'priority'
        | 'assignee_id'
        | 'title'
        | 'description'
        | 'notes'
        | 'messages'
        | 'first_response_at'
        | 'branch'
        | 'attachments'
        | 'deleted_at'
        | 'tags'
      >
    >
  ) => {"""
    new_sig = """  const updateTicket = async (
    id: string,
    updates: Partial<
      Pick<
        Ticket,
        | 'status'
        | 'priority'
        | 'assignee_id'
        | 'title'
        | 'description'
        | 'notes'
        | 'messages'
        | 'first_response_at'
        | 'branch'
        | 'attachments'
        | 'deleted_at'
        | 'tags'
      >
    >,
    opts?: { silent?: boolean },
  ) => {"""
    if old_sig in t:
        t = t.replace(old_sig, new_sig, 1)
        print("tc sig")
    else:
        print("tc sig miss")

    old_type = """  updateTicket: (
    id: string,
    updates: Partial<
      Pick<
        Ticket,
        | 'status'
        | 'priority'
        | 'assignee_id'
        | 'title'
        | 'description'
        | 'notes'
        | 'messages'
        | 'first_response_at'
        | 'branch'
        | 'attachments'
        | 'deleted_at'
        | 'tags'
      >
    >
  ) => Promise<void>;"""
    new_type = """  updateTicket: (
    id: string,
    updates: Partial<
      Pick<
        Ticket,
        | 'status'
        | 'priority'
        | 'assignee_id'
        | 'title'
        | 'description'
        | 'notes'
        | 'messages'
        | 'first_response_at'
        | 'branch'
        | 'attachments'
        | 'deleted_at'
        | 'tags'
      >
    >,
    opts?: { silent?: boolean },
  ) => Promise<void>;"""
    if old_type in t:
        t = t.replace(old_type, new_type, 1)
        print("tc type")

    old_notify = """    const changed = Object.keys(updates).filter((k) => k !== 'messages' && k !== 'notes' && k !== 'attachments');
    if (changed.length) {
      pushAudit({
        entity: 'ticket',
        entity_id: id,
        action: updates.deleted_at ? 'soft_delete' : updates.deleted_at === null ? 'restore' : 'update',
        detail: changed.map((k) => `${k}=${JSON.stringify((updates as Record<string, unknown>)[k])}`).join(', '),
        actor: currentAgent?.name || user?.email || 'Agent',
      });
      const assignee = updates.assignee_id
        ? agents.find((a) => a.id === updates.assignee_id)
        : ticket?.assignee_id
          ? agents.find((a) => a.id === ticket.assignee_id)
          : null;
      const summary = changed.map((k) => `${k}: ${(updates as Record<string, unknown>)[k]}`).join(', ');
      void notifyAgents({
        title: 'Ticket updated',
        body: `${id}${ticket ? ` · ${ticket.title}` : ''} — ${summary}`,
        link: 'tickets',
        userId: (assignee as Agent & { user_id?: string })?.user_id || undefined,
      });
      if (ticket?.customer_email) {
        void notifyCustomer({
          email: ticket.customer_email,
          title: 'Ticket updated',
          body: `${ticket.title || id} was updated by support.`,
          link: 'mytickets',
        });
      }
    }
  };"""
    new_notify = """    const changed = Object.keys(updates).filter((k) => k !== 'messages' && k !== 'notes' && k !== 'attachments');
    if (changed.length) {
      pushAudit({
        entity: 'ticket',
        entity_id: id,
        action: updates.deleted_at ? 'soft_delete' : updates.deleted_at === null ? 'restore' : 'update',
        detail: changed.map((k) => `${k}=${JSON.stringify((updates as Record<string, unknown>)[k])}`).join(', '),
        actor: currentAgent?.name || user?.email || 'Agent',
      });
      if (!opts?.silent) {
        const assignee = updates.assignee_id
          ? agents.find((a) => a.id === updates.assignee_id)
          : ticket?.assignee_id
            ? agents.find((a) => a.id === ticket.assignee_id)
            : null;
        const summary = changed.map((k) => `${k}: ${(updates as Record<string, unknown>)[k]}`).join(', ');
        void notifyAgents({
          title: 'Ticket updated',
          body: `${id}${ticket ? ` · ${ticket.title}` : ''} — ${summary}`,
          link: 'tickets',
          userId: (assignee as Agent & { user_id?: string })?.user_id || undefined,
        });
        if (ticket?.customer_email) {
          void notifyCustomer({
            email: ticket.customer_email,
            title: 'Ticket updated',
            body: `${ticket.title || id} was updated by support.`,
            link: 'mytickets',
          });
        }
      }
    }
  };"""
    if old_notify in t:
        t = t.replace(old_notify, new_notify, 1)
        print("tc notify")
    else:
        print("tc notify miss")

    t = "/* update-silent-notify-v1 */\n" + t
    tc.write_text(t)
    print("tc done")
else:
    print("tc already")

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "detail-silent-update-v1" not in d:
    old_open = """    void updateTicket(ticket.id, {
      ...(ticket.status === 'new' ? { status: 'open' as Status } : {}),
      tags: nextTags,
    });"""
    new_open = """    void updateTicket(
      ticket.id,
      {
        ...(ticket.status === 'new' ? { status: 'open' as Status } : {}),
        tags: nextTags,
      },
      { silent: true },
    );"""
    if old_open in d:
        d = d.replace(old_open, new_open, 1)
        print("td open")
    else:
        print("td open miss")

    old_sla = """      void updateTicket(ticket.id, { status: 'closed' as Status });"""
    new_sla = """      void updateTicket(ticket.id, { status: 'closed' as Status }, { silent: true });"""
    if old_sla in d:
        d = d.replace(old_sla, new_sla, 1)
        print("td sla")
    else:
        print("td sla miss/partial")

    d = "/* detail-silent-update-v1 */\n" + d
    td.write_text(d)
    print("td done")
else:
    print("td already")

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "toast-hydrate-v1" not in s:
    old_toast = """  /* Toast when new agent notifications arrive (cross-tab / Supabase), not only local event */
  useEffect(() => {
    const ids = new Set(notifications.map((n) => n.id));
    if (toastBootRef.current) {
      prevNotifIdsRef.current = ids;
      toastBootRef.current = false;
      return;
    }
    const fresh = notifications.filter((n) => !prevNotifIdsRef.current.has(n.id) && !n.read);
    prevNotifIdsRef.current = ids;
    if (fresh.length === 0) return;
    const latest = fresh[0];
    setAgentToast({
      title: latest.title || 'New notification',
      body: latest.body || '',
    });
    const t = window.setTimeout(() => setAgentToast(null), 7000);
    return () => window.clearTimeout(t);
  }, [notifications]);"""
    new_toast = """  /* Toast only for notifs that arrive AFTER initial hydrate (avoid spam on refresh) */
  useEffect(() => {
    const ids = new Set(notifications.map((n) => n.id));
    if (toastBootRef.current) {
      prevNotifIdsRef.current = new Set([...prevNotifIdsRef.current, ...ids]);
      const settle = window.setTimeout(() => {
        prevNotifIdsRef.current = new Set(notifications.map((n) => n.id));
        toastBootRef.current = false;
      }, 1200);
      return () => window.clearTimeout(settle);
    }
    const fresh = notifications.filter((n) => !prevNotifIdsRef.current.has(n.id) && !n.read);
    prevNotifIdsRef.current = ids;
    if (fresh.length === 0) return;
    const latest =
      fresh.find((n) => /follow-?up/i.test(n.title || '')) ||
      fresh.find((n) => !/tags\\s*:/i.test(n.body || '')) ||
      fresh[0];
    if (/tags\\s*:/i.test(latest.body || '') && /Ticket updated/i.test(latest.title || '')) {
      return;
    }
    setAgentToast({
      title: latest.title || 'New notification',
      body: latest.body || '',
    });
    const t = window.setTimeout(() => setAgentToast(null), 7000);
    return () => window.clearTimeout(t);
  }, [notifications]);"""
    if old_toast in s:
        s = s.replace(old_toast, new_toast, 1)
        print("sa toast")
    else:
        print("sa toast miss")
    s = "/* toast-hydrate-v1 */\n" + s
    sa.write_text(s)
    print("sa done")
else:
    print("sa already")

print("done")
