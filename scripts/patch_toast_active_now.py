#!/usr/bin/env python3
"""Stop false New ticket toasts; Active Now Online · Status + colored dots; faster presence."""
from pathlib import Path
import re

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "toast-created-window-v1" not in s:
        new = """const isCustomerOrigin = (n: { title?: string; body?: string; link?: string; created_at?: string }) => {
      const t = (n.title || '').toLowerCase();
      const b = (n.body || '').toLowerCase();
      const link = (n.link || '').toLowerCase();
      if (/ticket updated/.test(t)) return false;
      if (/new ticket/.test(t)) return true;
      if (/follow-?up/.test(t) || /follow-?up/.test(b)) return true;
      if (/live\\s*chat|customer message|new message/.test(t) || /live\\s*chat/.test(b)) return true;
      if (link === 'chat' || link === 'livechat') return true;
      return false;
    };
    const isRecent = (n: { created_at?: string }) => {
      if (!n.created_at) return false;
      const age = Date.now() - new Date(n.created_at).getTime();
      return !Number.isNaN(age) && age >= 0 && age < 45_000;
    };
    const fresh = notifications.filter(
      (n) =>
        !prevNotifIdsRef.current.has(n.id) &&
        !n.read &&
        isCustomerOrigin(n) &&
        isRecent(n),
    );
    prevNotifIdsRef.current = ids;
    if (fresh.length === 0) return;
    const latest = fresh[0];
    setAgentToast({
      title: latest.title || 'New notification',
      body: latest.body || '',
    });
    const t = window.setTimeout(() => setAgentToast(null), 7000);
    return () => window.clearTimeout(t);
  }, [notifications]);""".replace("\\\\s", "\\s")

        m = re.search(
            r"const isCustomerOrigin = \(n: \{ title\?: string; body\?: string; link\?: string \}\) => \{[\s\S]*?\}, \[notifications\]\);",
            s,
        )
        if m:
            s = s[: m.start()] + new.strip() + s[m.end() :]
            print("toast filter")
        else:
            print("toast filter miss")

        s = s.replace(
            """      const settle = window.setTimeout(() => {
        prevNotifIdsRef.current = new Set(notifications.map((n) => n.id));
        toastBootRef.current = false;
      }, 1200);""",
            """      const settle = window.setTimeout(() => {
        prevNotifIdsRef.current = new Set(notifications.map((n) => n.id));
        toastBootRef.current = false;
      }, 3500);""",
            1,
        )
        s = s.replace(
            "const id = window.setInterval(tick, 15000);",
            "const id = window.setInterval(tick, 8000);",
            1,
        )
        s = "/* toast-created-window-v1 */\n" + s
        sa.write_text(s)
    else:
        print("systemapp already")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "active-now-online-prefix-v1" not in p:
        p = p.replace(
            "const id = window.setInterval(() => setPresenceTick((n) => n + 1), 10000);",
            "const id = window.setInterval(() => setPresenceTick((n) => n + 1), 5000);",
            1,
        )
        old_sub = """                        <div className="text-[11px] truncate flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full shrink-0 bg-emerald-400" />
                          {a.status_emoji ? <span className="shrink-0">{a.status_emoji}</span> : null}
                          <span
                            className={(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'away') return 'text-sky-400 font-medium';
                              if (st === 'busy') return 'text-yellow-300 font-medium';
                              if (st === 'in_call') return 'text-orange-400 font-medium';
                              if (st === 'custom') return 'text-white font-medium';
                              return 'text-emerald-400 font-medium';
                            })()}
                          >
                            {(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'busy') return 'Busy';
                              if (st === 'away') return 'Away';
                              if (st === 'in_call') return 'In a call';
                              if (st === 'custom') return a.status_message || 'Custom status';
                              return 'Available';
                            })()}
                          </span>
                        </div>"""
        new_sub = """                        <div className="text-[11px] truncate flex items-center gap-1.5">
                          <span
                            className={(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'away') return 'w-1.5 h-1.5 rounded-full shrink-0 bg-sky-400';
                              if (st === 'busy') return 'w-1.5 h-1.5 rounded-full shrink-0 bg-yellow-400';
                              if (st === 'in_call') return 'w-1.5 h-1.5 rounded-full shrink-0 bg-orange-400';
                              if (st === 'custom') return 'w-1.5 h-1.5 rounded-full shrink-0 bg-white';
                              return 'w-1.5 h-1.5 rounded-full shrink-0 bg-emerald-400';
                            })()}
                          />
                          <span className="text-zinc-400 dark:text-zinc-400 font-medium">Online</span>
                          <span className="text-zinc-500">\u00b7</span>
                          {a.status_emoji ? <span className="shrink-0">{a.status_emoji}</span> : null}
                          <span
                            className={(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'away') return 'text-sky-400 font-medium';
                              if (st === 'busy') return 'text-yellow-300 font-medium';
                              if (st === 'in_call') return 'text-orange-400 font-medium';
                              if (st === 'custom') return 'text-white font-medium';
                              return 'text-emerald-400 font-medium';
                            })()}
                          >
                            {(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'busy') return 'Busy';
                              if (st === 'away') return 'Away';
                              if (st === 'in_call') return 'In a call';
                              if (st === 'custom') return a.status_message || 'Custom status';
                              return 'Available';
                            })()}
                          </span>
                        </div>""".replace("\\u00b7", "\u00b7")
        if old_sub in p:
            p = p.replace(old_sub, new_sub, 1)
            print("plc subtitle")
        for a, b in [
            ("if (st === 'busy' || st === 'in_call') return 'bg-amber-400';",
             "if (st === 'busy') return 'bg-yellow-400';\n                              if (st === 'in_call') return 'bg-orange-400';"),
            ("if (st === 'away') return 'bg-yellow-300';", "if (st === 'away') return 'bg-sky-400';"),
            ("if (st === 'away') return 'bg-yellow-400';", "if (st === 'away') return 'bg-sky-400';"),
            ("if (st === 'busy') return 'bg-amber-400';", "if (st === 'busy') return 'bg-yellow-400';"),
            ("if (st === 'in_call') return 'bg-violet-400';", "if (st === 'in_call') return 'bg-orange-400';"),
            ("if (st === 'custom') return 'bg-sky-400';", "if (st === 'custom') return 'bg-white';"),
        ]:
            if a in p:
                p = p.replace(a, b, 1)
        p = "/* active-now-online-prefix-v1 */\n" + p
        plc.write_text(p)
        print("plc done")
    else:
        print("plc already")
print("done")
