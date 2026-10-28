#!/usr/bin/env python3
"""Darker expand card + Customer Portal notification bell."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "portal-bell-v1" in c:
    print("already")
    raise SystemExit(0)

if "Bell" not in c.split("from 'lucide-react'")[0]:
    c = c.replace(
        "  Flag, ListTree, Lightbulb, Clock3, ClipboardList, MoreVertical, Info, Send,\n} from 'lucide-react';",
        "  Flag, ListTree, Lightbulb, Clock3, ClipboardList, MoreVertical, Info, Send, Bell,\n} from 'lucide-react';",
        1,
    )
    print("import bell ok")

old_plat = "  const { addSurvey, surveys } = usePlatform();"
new_plat = """  const {
    addSurvey,
    surveys,
    notifications,
    unreadCount: platformUnread,
    markNotificationRead,
    markAllNotificationsRead,
    conversations,
  } = usePlatform();"""
if old_plat in c:
    c = c.replace(old_plat, new_plat, 1)
    print("platform ok")

if "portalNotifOpen" not in c:
    c = c.replace(
        "  const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);",
        """  const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);
  const [portalNotifOpen, setPortalNotifOpen] = useState(false);
  const portalNotifRef = useRef<HTMLDivElement>(null);""",
        1,
    )
    print("notif state ok")

if "portal-notif-outside" not in c:
    c = c.replace(
        """  useEffect(() => {
    if (!myTicketMenuId) return;
    const onDoc = (e: MouseEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && t.closest && t.closest('[data-myticket-menu]')) return;
      setMyTicketMenuId(null);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [myTicketMenuId]);""",
        """  useEffect(() => {
    if (!myTicketMenuId) return;
    const onDoc = (e: MouseEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && t.closest && t.closest('[data-myticket-menu]')) return;
      setMyTicketMenuId(null);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [myTicketMenuId]);
  /* portal-notif-outside */
  useEffect(() => {
    if (!portalNotifOpen) return;
    const onDoc = (e: MouseEvent) => {
      if (portalNotifRef.current && !portalNotifRef.current.contains(e.target as Node)) {
        setPortalNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [portalNotifOpen]);""",
        1,
    )
    print("outside ok")

c = c.replace(
    'bg-white/40 dark:bg-white/[0.03] p-4 sm:p-5 space-y-4 text-left shadow-sm"',
    'bg-white/50 dark:bg-zinc-950/80 p-4 sm:p-5 space-y-4 text-left shadow-sm"',
    1,
)
c = c.replace(
    'bg-white/70 dark:bg-white/[0.06] border border-zinc-200/70 dark:border-white/10 shadow-sm"',
    'bg-white/80 dark:bg-zinc-900/90 border border-zinc-200/70 dark:border-white/12 shadow-sm"',
    1,
)
c = c.replace(
    'bg-violet-500/10 px-3.5 py-3"',
    'bg-violet-500/10 dark:bg-violet-950/50 px-3.5 py-3"',
    1,
)
print("card colors ok")

insert_after = "  const btnPrimary =\n    'w-full py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors';"
helper = '''
  const portalNotifs = useMemo(() => {
    const items: {
      id: string;
      title: string;
      body?: string;
      link: PortalView;
      read: boolean;
      created_at: string;
      kind: 'platform' | 'ticket' | 'chat';
      ticketId?: string;
    }[] = [];
    for (const n of notifications) {
      const linkRaw = (n.link || '').toLowerCase();
      let link: PortalView = 'mytickets';
      if (linkRaw.includes('chat') || linkRaw.includes('live')) link = 'chat';
      else if (linkRaw.includes('ticket') || linkRaw.includes('myticket')) link = 'mytickets';
      items.push({
        id: n.id,
        title: n.title,
        body: n.body,
        link,
        read: !!n.read,
        created_at: n.created_at,
        kind: 'platform',
      });
    }
    for (const t of myTickets) {
      if (!(t.tags || []).includes('customer_unread')) continue;
      items.push({
        id: `ticket-${t.id}`,
        title: 'Ticket updated',
        body: t.title || t.id,
        link: 'mytickets',
        read: false,
        created_at: t.updated_at || t.created_at,
        kind: 'ticket',
        ticketId: t.id,
      });
    }
    const email = (user?.email || '').toLowerCase();
    for (const conv of conversations) {
      if (!email) continue;
      const cust = ((conv as { customer_email?: string }).customer_email || '').toLowerCase();
      const blob = JSON.stringify(conv).toLowerCase();
      if (cust !== email && !blob.includes(email)) continue;
      if (conv.status === 'ended') continue;
      const msgs = conv.messages || [];
      const last = msgs[msgs.length - 1];
      if (!last || last.sender !== 'agent') continue;
      items.push({
        id: `chat-${conv.id}`,
        title: 'New live chat message',
        body: (last.text || '').slice(0, 120),
        link: 'chat',
        read: false,
        created_at: last.created_at || (conv as { updated_at?: string }).updated_at || new Date().toISOString(),
        kind: 'chat',
      });
    }
    items.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    const seen = new Set<string>();
    return items.filter((x) => {
      if (seen.has(x.id)) return false;
      seen.add(x.id);
      return true;
    });
  }, [notifications, myTickets, conversations, user?.email]);

  const portalUnread = portalNotifs.filter((n) => !n.read).length;

  const openPortalNotif = async (n: (typeof portalNotifs)[0]) => {
    setPortalNotifOpen(false);
    if (n.kind === 'platform') {
      void markNotificationRead(n.id);
    }
    if (n.kind === 'ticket' && n.ticketId) {
      const t = myTickets.find((x) => x.id === n.ticketId);
      if (t) {
        void updateTicket(t.id, {
          tags: (t.tags || []).filter((x) => x !== 'customer_unread'),
        });
        setExpandedTicketId(t.id);
      }
    }
    setView(n.link);
  };
'''
if insert_after in c and "portalNotifs" not in c:
    c = c.replace(insert_after, insert_after + "\n" + helper, 1)
    print("helper ok")

old_toggle = "          <ThemeToggle />"
bell = '''          <div className="relative z-[50]" ref={portalNotifRef}>
            <button
              type="button"
              onClick={() => setPortalNotifOpen((v) => !v)}
              className="relative p-2 rounded-lg text-zinc-600 dark:text-zinc-300 hover:bg-violet-500/15 dark:hover:bg-white/10 transition-colors"
              title="Notifications"
              aria-label="Notifications"
            >
              <Bell size={18} strokeWidth={2.2} />
              {portalUnread > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-rose-500 text-white text-[10px] font-semibold flex items-center justify-center">
                  {portalUnread > 9 ? '9+' : portalUnread}
                </span>
              )}
            </button>
            {portalNotifOpen && (
              <div className="absolute right-0 mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950 shadow-2xl overflow-hidden">
                <div className="flex items-center justify-between px-3 py-2.5 border-b border-zinc-100 dark:border-white/10">
                  <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-100">Notifications</span>
                  {portalUnread > 0 && (
                    <button
                      type="button"
                      className="text-[11px] text-violet-600 dark:text-violet-400 font-medium"
                      onClick={() => {
                        void markAllNotificationsRead();
                        for (const t of myTickets) {
                          if ((t.tags || []).includes('customer_unread')) {
                            void updateTicket(t.id, {
                              tags: (t.tags || []).filter((x) => x !== 'customer_unread'),
                            });
                          }
                        }
                      }}
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-72 overflow-y-auto">
                  {portalNotifs.length === 0 ? (
                    <div className="px-3 py-8 text-center text-xs text-zinc-400">No notifications yet</div>
                  ) : (
                    portalNotifs.slice(0, 30).map((n) => (
                      <button
                        key={n.id}
                        type="button"
                        onClick={() => void openPortalNotif(n)}
                        className={`w-full text-left px-3 py-2.5 border-b border-zinc-50 dark:border-white/5 text-xs hover:bg-violet-50/60 dark:hover:bg-white/5 transition-colors ${
                          n.read ? 'opacity-60' : 'bg-violet-50/40 dark:bg-violet-500/10'
                        }`}
                      >
                        <div className="font-semibold text-zinc-800 dark:text-zinc-100">{n.title}</div>
                        {n.body && <div className="text-zinc-500 dark:text-zinc-400 mt-0.5 line-clamp-2">{n.body}</div>}
                        <div className="text-[10px] text-zinc-400 mt-1 tabular-nums">{new Date(n.created_at).toLocaleString()}</div>
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          <ThemeToggle />'''
if old_toggle in c and "portalNotifRef" in c:
    c = c.replace(old_toggle, bell, 1)
    print("bell ui ok")

c = "/* portal-bell-v1 */\n" + c
cp.write_text(c)
print("done")
