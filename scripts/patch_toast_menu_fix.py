#!/usr/bin/env python3
"""Fix agent toast (show on notif refresh) + My Tickets action menu fixed positioning."""
from pathlib import Path
import re

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "agent-toast-from-notif-v1" not in s:
    if "prevNotifIdsRef" not in s:
        s = s.replace(
            "const [agentToast, setAgentToast] = useState<{ title: string; body: string } | null>(null);",
            """const [agentToast, setAgentToast] = useState<{ title: string; body: string } | null>(null);
  const prevNotifIdsRef = useRef<Set<string>>(new Set());
  const toastBootRef = useRef(true);""",
            1,
        )
        print("sa refs")

    watch = """
  /* Toast when new agent notifications arrive (cross-tab / Supabase), not only local event */
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
  }, [notifications]);

"""
    if "toastBootRef.current" not in s or "agent-toast-from-notif-v1" not in s:
        marker = "  useEffect(() => {\n    const onEvt = (e: Event) => {"
        if marker in s and "const ids = new Set(notifications.map" not in s:
            s = s.replace(marker, watch + marker, 1)
            print("sa watch ok")
        elif "const ids = new Set(notifications.map" not in s:
            marker2 = "  /* Badge: New or unopened"
            if marker2 in s:
                s = s.replace(marker2, watch + marker2, 1)
                print("sa watch alt")
            else:
                print("sa watch miss")

    s = s.replace(
        'className="agent-toast-followup fixed top-4 right-4 z-[200]',
        'className="agent-toast-followup fixed top-4 right-4 z-[9999]',
        1,
    )
    s = "/* agent-toast-from-notif-v1 */\n" + s
    sa.write_text(s)
    print("sa done")
else:
    print("sa already")

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-menu-fixed-v1" not in c:
    if "myTicketMenuPos" not in c:
        c = c.replace(
            "const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);",
            """const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);
  const [myTicketMenuPos, setMyTicketMenuPos] = useState<{ top: number; left: number; openUp: boolean }>({
    top: 0,
    left: 0,
    openUp: false,
  });""",
            1,
        )
        print("cp pos state")

    if "setMyTicketMenuId((id) => (id === t.id ? null : t.id))" in c:
        c = c.replace(
            "setMyTicketMenuId((id) => (id === t.id ? null : t.id));",
            """if (myTicketMenuId === t.id) {
                                      setMyTicketMenuId(null);
                                      return;
                                    }
                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 88;
                                    const menuW = 168;
                                    const openUp = rect.bottom + menuH + 8 > window.innerHeight;
                                    const top = openUp ? rect.top - menuH - 6 : rect.bottom + 6;
                                    const left = Math.min(
                                      Math.max(8, rect.right - menuW),
                                      window.innerWidth - menuW - 8,
                                    );
                                    setMyTicketMenuPos({ top, left, openUp });
                                    setMyTicketMenuId(t.id);""",
            1,
        )
        print("cp btn")
    elif "setMyTicketMenuPos" in c and "getBoundingClientRect" in c:
        print("cp btn already")
    else:
        print("cp btn miss")

    old_menu = """                                {myTicketMenuId === t.id && (
                                  <div className="portal-mytickets-action-menu absolute right-0 top-full mt-1 z-[100] w-40 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl py-1 text-left">"""
    new_menu = """                                {myTicketMenuId === t.id && (
                                  <div
                                    className="portal-mytickets-action-menu fixed z-[9998] w-42 min-w-[10.5rem] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-2xl py-1 text-left"
                                    style={{ top: myTicketMenuPos.top, left: myTicketMenuPos.left }}
                                  >"""
    if old_menu in c:
        c = c.replace(old_menu, new_menu, 1)
        print("cp menu ok")
    elif "portal-mytickets-action-menu absolute" in c:
        c = re.sub(
            r'\{myTicketMenuId === t\.id && \(\s*<div className="portal-mytickets-action-menu absolute[^"]*"[^>]*>',
            """{myTicketMenuId === t.id && (
                                  <div
                                    className="portal-mytickets-action-menu fixed z-[9998] w-42 min-w-[10.5rem] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-2xl py-1 text-left"
                                    style={{ top: myTicketMenuPos.top, left: myTicketMenuPos.left }}
                                  >""",
            c,
            count=1,
        )
        print("cp menu regex")
    elif "portal-mytickets-action-menu fixed" in c:
        print("cp menu already")
    else:
        print("cp menu miss")

    c = "/* mytickets-menu-fixed-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

print("done")
