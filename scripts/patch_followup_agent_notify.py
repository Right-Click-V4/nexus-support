#!/usr/bin/env python3
"""Customer Send Follow-Up → agent bell + top-right toast (realtime)."""
from pathlib import Path
import re

an = Path("src/lib/agentNotify.ts")
if an.exists():
    a = an.read_text()
    if "detail: { title, body, link }" not in a:
        a = a.replace(
            "window.dispatchEvent(new CustomEvent(EVENT));\n      return;",
            "window.dispatchEvent(new CustomEvent(EVENT, { detail: { title, body, link } }));\n      return;",
            1,
        )
        an.write_text(a)
        print("agentNotify detail")
    else:
        print("agentNotify already")

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "followup-agent-notify-v1" not in c:
    if "notifyAgents" not in c:
        for needle in [
            "import { useAuth } from '../context/AuthContext';",
            "import { useTickets } from '../context/TicketContext';",
        ]:
            if needle in c:
                c = c.replace(needle, needle + "\nimport { notifyAgents } from '../lib/agentNotify';", 1)
                print("cp import")
                break

    old = """                              try {
                                const prev = followUpTicket.messages || [];
                                const msg = {
                                  id: `msg-${Date.now()}`,
                                  text: followUpText.trim(),
                                  kind: 'public' as const,
                                  author: displayName || user?.email || 'Customer',
                                  created_at: new Date().toISOString(),
                                };
                                await updateTicket(followUpTicket.id, { messages: [...prev, msg] });
                                setFollowUpText('');
                                setFollowUpTicket(null);
                              } catch (err) {
                                console.error(err);
                              } finally {
                                setFollowUpBusy(false);
                              }"""
    new = """                              try {
                                const prev = followUpTicket.messages || [];
                                const customerLabel = displayName || user?.email || 'Customer';
                                const note = followUpText.trim();
                                const msg = {
                                  id: `msg-${Date.now()}`,
                                  text: note,
                                  kind: 'public' as const,
                                  author: customerLabel,
                                  created_at: new Date().toISOString(),
                                };
                                await updateTicket(followUpTicket.id, {
                                  messages: [...prev, msg],
                                  tags: Array.from(
                                    new Set([...(followUpTicket.tags || []), 'follow_up', 'unread']),
                                  ),
                                });
                                const subject = followUpTicket.title || 'Support request';
                                const desc = (followUpTicket.description || '').trim().slice(0, 280);
                                const bodyLines = [
                                  `${customerLabel} wants a follow-up update on this ticket.`,
                                  `Ticket: ${followUpTicket.id}`,
                                  `Subject: ${subject}`,
                                  desc ? `Details: ${desc}` : null,
                                  note ? `Customer note: ${note}` : null,
                                ].filter(Boolean);
                                await notifyAgents({
                                  title: 'Follow-up requested',
                                  body: bodyLines.join('\\n'),
                                  link: 'tickets',
                                });
                                setFollowUpText('');
                                setFollowUpTicket(null);
                              } catch (err) {
                                console.error(err);
                              } finally {
                                setFollowUpBusy(false);
                              }"""
    if old in c:
        c = c.replace(old, new, 1)
        print("cp handler ok")
    elif "await updateTicket(followUpTicket.id, { messages: [...prev, msg] });" in c:
        c = c.replace(
            "await updateTicket(followUpTicket.id, { messages: [...prev, msg] });",
            """await updateTicket(followUpTicket.id, {
                                  messages: [...prev, msg],
                                  tags: Array.from(
                                    new Set([...(followUpTicket.tags || []), 'follow_up', 'unread']),
                                  ),
                                });
                                {
                                  const customerLabel = displayName || user?.email || 'Customer';
                                  const subject = followUpTicket.title || 'Support request';
                                  const desc = (followUpTicket.description || '').trim().slice(0, 280);
                                  const note = followUpText.trim();
                                  const bodyLines = [
                                    `${customerLabel} wants a follow-up update on this ticket.`,
                                    `Ticket: ${followUpTicket.id}`,
                                    `Subject: ${subject}`,
                                    desc ? `Details: ${desc}` : null,
                                    note ? `Customer note: ${note}` : null,
                                  ].filter(Boolean);
                                  await notifyAgents({
                                    title: 'Follow-up requested',
                                    body: bodyLines.join('\\n'),
                                    link: 'tickets',
                                  });
                                }""",
            1,
        )
        print("cp handler alt")
    else:
        print("cp handler miss")
    c = "/* followup-agent-notify-v1 */\n" + c
    cp.write_text(c)
else:
    print("cp already")

pc = Path("src/context/PlatformContext.tsx")
p = pc.read_text()
if "followup-agent-notify-v1" not in p:
    if "onAgentNotify" not in p:
        if "import { notifyCustomer } from '../lib/agentNotify';" in p:
            p = p.replace(
                "import { notifyCustomer } from '../lib/agentNotify';",
                "import { notifyCustomer, onAgentNotify } from '../lib/agentNotify';",
                1,
            )
        else:
            p = p.replace(
                "import { useAuth } from './AuthContext';",
                "import { useAuth } from './AuthContext';\nimport { onAgentNotify } from '../lib/agentNotify';",
                1,
            )
        print("pc import")
    anchor = "  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);"
    extra = """  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);

  /* Real-time agent notifications (follow-ups, etc.) */
  useEffect(() => {
    const unsub = onAgentNotify(() => {
      void refreshPlatform();
    });
    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    if (isSupabaseConfigured && supabase && user?.id) {
      channel = supabase
        .channel(`nexus-agent-notifs-${user.id}`)
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'notifications' },
          () => {
            void refreshPlatform();
          },
        )
        .subscribe();
    }
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'nexus-notif-v1') void refreshPlatform();
    };
    window.addEventListener('storage', onStorage);
    return () => {
      unsub();
      window.removeEventListener('storage', onStorage);
      if (channel && supabase) void supabase.removeChannel(channel);
    };
  }, [refreshPlatform, user?.id]);"""
    if "nexus-agent-notifs-" not in p and anchor in p:
        p = p.replace(anchor, extra, 1)
        print("pc realtime")
    else:
        print("pc realtime skip")
    p = "/* followup-agent-notify-v1 */\n" + p
    pc.write_text(p)
else:
    print("pc already")

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "followup-agent-toast-v1" not in s:
    if "from './lib/agentNotify'" not in s:
        if "import ThemeToggle from './components/ThemeToggle';" in s:
            s = s.replace(
                "import ThemeToggle from './components/ThemeToggle';",
                "import ThemeToggle from './components/ThemeToggle';\nimport { onAgentNotify } from './lib/agentNotify';",
                1,
            )
            print("sa import")

    if "agentToast" not in s:
        s = s.replace(
            "const [notifOpen, setNotifOpen] = useState(false);",
            """const [notifOpen, setNotifOpen] = useState(false);
  const [agentToast, setAgentToast] = useState<{ title: string; body: string } | null>(null);""",
            1,
        )
        print("sa state")

    m = re.search(r"const \{([^}]+)\} = usePlatform\(\);", s)
    if m and "refreshPlatform" not in m.group(1):
        s = s.replace(m.group(0), m.group(0).replace("unreadCount,", "unreadCount,\n    refreshPlatform,"), 1)
        print("sa refreshPlatform")

    toast_fx = """  useEffect(() => {
    const onEvt = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      let title = 'Follow-up requested';
      let body = 'A customer asked for an update on their ticket.';
      if (detail && !Array.isArray(detail) && detail.title) {
        title = detail.title;
        body = detail.body || body;
      } else if (Array.isArray(detail) && detail[0]?.title) {
        title = detail[0].title;
        body = detail[0].body || body;
      } else {
        try {
          const raw = localStorage.getItem('nexus-notif-v1');
          const list = raw ? JSON.parse(raw) : [];
          if (Array.isArray(list) && list[0]?.title) {
            title = list[0].title;
            body = list[0].body || body;
          }
        } catch { /* ignore */ }
      }
      setAgentToast({ title, body });
      window.setTimeout(() => setAgentToast(null), 7000);
      void refreshPlatform?.();
    };
    window.addEventListener('nexus-agent-notify', onEvt);
    return () => window.removeEventListener('nexus-agent-notify', onEvt);
  }, [refreshPlatform]);

"""
    if "setAgentToast({ title, body })" not in s:
        marker = "  /* Badge: New or unopened (unread tag) tickets only — clears when agent opens the ticket */"
        if marker in s:
            s = s.replace(marker, toast_fx + marker, 1)
            print("sa effect")
        else:
            print("sa effect miss marker")

    toast_jsx = """
      {agentToast && (
        <div className="agent-toast-followup fixed top-4 right-4 z-[200] max-w-sm w-[min(100vw-2rem,22rem)] rounded-xl border border-violet-400/40 bg-zinc-950/95 text-white shadow-2xl shadow-violet-900/40 backdrop-blur-md px-4 py-3">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 w-8 h-8 rounded-lg bg-violet-500/25 text-violet-200 flex items-center justify-center shrink-0">
              <Bell size={16} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold text-white leading-snug">{agentToast.title}</div>
              <div className="text-xs text-zinc-300 mt-1 whitespace-pre-line leading-relaxed">{agentToast.body}</div>
            </div>
            <button
              type="button"
              onClick={() => setAgentToast(null)}
              className="text-zinc-400 hover:text-white text-lg leading-none px-1"
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
        </div>
      )}
"""
    if "agent-toast-followup" not in s:
        if '<div className="app-cosmos flex' in s:
            s = s.replace('<div className="app-cosmos flex', toast_jsx + '\n      <div className="app-cosmos flex', 1)
            print("sa jsx")
        else:
            print("sa jsx miss")

    s = "/* followup-agent-toast-v1 */\n" + s
    sa.write_text(s)
else:
    print("sa already")

print("done")
