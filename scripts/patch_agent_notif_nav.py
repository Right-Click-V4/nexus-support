#!/usr/bin/env python3
"""Toast only customer-origin; notif click navigates + marks read; no agent toast on agent save."""
from pathlib import Path

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "agent-notif-nav-v1" not in s:
    old_block = """    const fresh = notifications.filter((n) => !prevNotifIdsRef.current.has(n.id) && !n.read);
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
    });"""
    new_block = """    const isCustomerOrigin = (n: { title?: string; body?: string; link?: string }) => {
      const t = (n.title || '').toLowerCase();
      const b = (n.body || '').toLowerCase();
      const link = (n.link || '').toLowerCase();
      if (/new ticket/.test(t)) return true;
      if (/follow-?up/.test(t) || /follow-?up/.test(b)) return true;
      if (/live\\s*chat|customer message|new message/.test(t) || /live\\s*chat/.test(b)) return true;
      if (link === 'chat' || link === 'livechat') return true;
      if (/ticket updated/.test(t)) return false;
      return false;
    };
    const fresh = notifications.filter(
      (n) => !prevNotifIdsRef.current.has(n.id) && !n.read && isCustomerOrigin(n),
    );
    prevNotifIdsRef.current = ids;
    if (fresh.length === 0) return;
    const latest = fresh[0];
    setAgentToast({
      title: latest.title || 'New notification',
      body: latest.body || '',
    });"""
    if old_block in s:
        s = s.replace(old_block, new_block, 1)
        print("toast ok")
    else:
        print("toast miss")

    old_item = """                            <button type="button" className="text-left flex-1" onClick={() => void markNotificationRead(n.id)}>
                              <div className="font-medium text-zinc-800">{n.title}</div>
                              {n.body && <div className="text-zinc-500 mt-0.5">{n.body}</div>}
                            </button>"""
    new_item = """                            <button
                              type="button"
                              className="text-left flex-1"
                              onClick={() => {
                                void markNotificationRead(n.id);
                                setNotifOpen(false);
                                const link = (n.link || '').toLowerCase();
                                const title = (n.title || '').toLowerCase();
                                const body = (n.body || '').toLowerCase();
                                if (
                                  link === 'chat' ||
                                  link === 'livechat' ||
                                  /live\\s*chat|customer message|new message/.test(title) ||
                                  /live\\s*chat/.test(body)
                                ) {
                                  setActiveNav('chat');
                                } else if (
                                  link === 'tickets' ||
                                  link === 'ticket' ||
                                  /ticket|follow-?up|new ticket/.test(title) ||
                                  /ticket|follow-?up/.test(body)
                                ) {
                                  setActiveNav('tickets');
                                } else if (link === 'dashboard' || link === 'overview') {
                                  setActiveNav('dashboard');
                                } else if (link) {
                                  setActiveNav(link);
                                }
                              }}
                            >
                              <div className={`font-medium ${n.read ? 'text-zinc-600' : 'text-zinc-900'}`}>{n.title}</div>
                              {n.body && <div className="text-zinc-500 mt-0.5 line-clamp-3 whitespace-pre-line">{n.body}</div>}
                            </button>"""
    if old_item in s:
        s = s.replace(old_item, new_item, 1)
        print("item ok")
    else:
        print("item miss")

    old_evt = """      setAgentToast({ title, body });
      window.setTimeout(() => setAgentToast(null), 7000);
      void refreshPlatform?.();
    };
    window.addEventListener('nexus-agent-notify', onEvt);"""
    new_evt = """      const tLow = title.toLowerCase();
      const bLow = (body || '').toLowerCase();
      const customer =
        /new ticket/.test(tLow) ||
        /follow-?up/.test(tLow) ||
        /follow-?up/.test(bLow) ||
        /live\\s*chat|customer message|new message/.test(tLow);
      if (!customer) return;
      setAgentToast({ title, body });
      window.setTimeout(() => setAgentToast(null), 7000);
      void refreshPlatform?.();
    };
    window.addEventListener('nexus-agent-notify', onEvt);"""
    if old_evt in s:
        s = s.replace(old_evt, new_evt, 1)
        print("evt ok")
    else:
        print("evt miss")

    old_toast = """          className="agent-toast-followup fixed z-[9999] max-w-sm w-[min(100vw-2rem,22rem)] rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md
            top-[4.25rem] right-4
            border-violet-300/50 bg-white/80 text-zinc-900
            dark:border-violet-400/35 dark:bg-zinc-900/75 dark:text-zinc-50
            animate-agent-toast-in"
          role="status"
        >"""
    new_toast = """          className="agent-toast-followup fixed z-[9999] max-w-sm w-[min(100vw-2rem,22rem)] rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md
            top-[4.25rem] right-4
            border-violet-300/50 bg-white/80 text-zinc-900
            dark:border-violet-400/35 dark:bg-zinc-900/75 dark:text-zinc-50
            animate-agent-toast-in cursor-pointer"
          role="status"
          onClick={() => {
            const t = (agentToast.title || '').toLowerCase();
            const b = (agentToast.body || '').toLowerCase();
            if (/live\\s*chat|customer message|new message/.test(t) || /live\\s*chat/.test(b)) {
              setActiveNav('chat');
            } else {
              setActiveNav('tickets');
            }
            setAgentToast(null);
          }}
        >"""
    if old_toast in s:
        s = s.replace(old_toast, new_toast, 1)
        print("toast click ok")
    else:
        print("toast click miss")

    s = "/* agent-notif-nav-v1 */\n" + s
    sa.write_text(s)
    print("sa done")
else:
    print("sa already")

tc = Path("src/context/TicketContext.tsx")
t = tc.read_text()
if "no-agent-toast-on-save-v1" not in t:
    old = """      if (!opts?.silent) {
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
      }"""
    new = """      if (!opts?.silent) {
        if (ticket?.customer_email) {
          void notifyCustomer({
            email: ticket.customer_email,
            title: 'Ticket updated',
            body: `${ticket.title || id} was updated by support.`,
            link: 'mytickets',
          });
        }
      }"""
    if old in t:
        t = t.replace(old, new, 1)
        print("tc ok")
    else:
        print("tc miss")
    t = "/* no-agent-toast-on-save-v1 */\n" + t
    tc.write_text(t)
    print("tc done")
else:
    print("tc already")
print("done")
