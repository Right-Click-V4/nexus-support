#!/usr/bin/env python3
"""Anchor action menu to 3-dots; polish agent toast (below topbar, slide-in, theme glass)."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-menu-anchor-v2" not in c:
    old_math = """                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 88;
                                    const menuW = 168;
                                    const openUp = rect.bottom + menuH + 8 > window.innerHeight;
                                    const top = openUp ? rect.top - menuH - 6 : rect.bottom + 6;
                                    const left = Math.min(
                                      Math.max(8, rect.right - menuW),
                                      window.innerWidth - menuW - 8,
                                    );
                                    setMyTicketMenuPos({ top, left, openUp });
                                    setMyTicketMenuId(t.id);"""
    new_math = """                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 84;
                                    const menuW = 160;
                                    const gap = 4;
                                    const spaceBelow = window.innerHeight - rect.bottom;
                                    const openUp = spaceBelow < menuH + 12;
                                    const top = openUp
                                      ? Math.max(8, rect.top - menuH - gap)
                                      : rect.bottom + gap;
                                    let left = rect.right - menuW;
                                    if (left < 8) left = 8;
                                    if (left + menuW > window.innerWidth - 8) {
                                      left = window.innerWidth - menuW - 8;
                                    }
                                    setMyTicketMenuPos({ top, left, openUp });
                                    setMyTicketMenuId(t.id);"""
    if old_math in c:
        c = c.replace(old_math, new_math, 1)
        print("cp math ok")
    elif "menuH = 88" in c:
        c = c.replace(
            """                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 88;
                                    const menuW = 168;
                                    const openUp = rect.bottom + menuH + 8 > window.innerHeight;
                                    const top = openUp ? rect.top - menuH - 6 : rect.bottom + 6;
                                    const left = Math.min(
                                      Math.max(8, rect.right - menuW),
                                      window.innerWidth - menuW - 8,
                                    );""",
            """                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 84;
                                    const menuW = 160;
                                    const gap = 4;
                                    const spaceBelow = window.innerHeight - rect.bottom;
                                    const openUp = spaceBelow < menuH + 12;
                                    const top = openUp
                                      ? Math.max(8, rect.top - menuH - gap)
                                      : rect.bottom + gap;
                                    let left = rect.right - menuW;
                                    if (left < 8) left = 8;
                                    if (left + menuW > window.innerWidth - 8) {
                                      left = window.innerWidth - menuW - 8;
                                    }""",
            1,
        )
        print("cp math alt")
    else:
        print("cp math miss")

    old_menu = """                                  <div
                                    className="portal-mytickets-action-menu fixed z-[9998] w-42 min-w-[10.5rem] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-2xl py-1 text-left"
                                    style={{ top: myTicketMenuPos.top, left: myTicketMenuPos.left }}
                                  >"""
    new_menu = """                                  <div
                                    className="portal-mytickets-action-menu fixed z-[9998] w-40 rounded-xl border border-zinc-200/90 dark:border-white/15 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md shadow-xl py-1 text-left"
                                    style={{
                                      top: myTicketMenuPos.top,
                                      left: myTicketMenuPos.left,
                                      transformOrigin: myTicketMenuPos.openUp ? 'bottom right' : 'top right',
                                    }}
                                  >"""
    if old_menu in c:
        c = c.replace(old_menu, new_menu, 1)
        print("cp menu style ok")
    elif "portal-mytickets-action-menu fixed" in c:
        c = re.sub(
            r'className="portal-mytickets-action-menu fixed[^"]*"\s*style=\{\{\s*top: myTicketMenuPos\.top,\s*left: myTicketMenuPos\.left\s*\}\}',
            '''className="portal-mytickets-action-menu fixed z-[9998] w-40 rounded-xl border border-zinc-200/90 dark:border-white/15 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md shadow-xl py-1 text-left"
                                    style={{
                                      top: myTicketMenuPos.top,
                                      left: myTicketMenuPos.left,
                                      transformOrigin: myTicketMenuPos.openUp ? 'bottom right' : 'top right',
                                    }}''',
            c,
            count=1,
        )
        print("cp menu regex")
    else:
        print("cp menu miss")

    c = "/* mytickets-menu-anchor-v2 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "agent-toast-polish-v1" not in s:
    if "agent-toast-followup" in s:
        s = re.sub(
            r'\{agentToast && \(\s*<div className="agent-toast-followup[^"]*"[^>]*>[\s\S]*?</div>\s*</div>\s*\)\}',
            """{agentToast && (
        <div
          className="agent-toast-followup fixed z-[9999] max-w-sm w-[min(100vw-2rem,22rem)] rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md
            top-[4.25rem] right-4
            border-violet-300/50 bg-white/80 text-zinc-900
            dark:border-violet-400/35 dark:bg-zinc-900/75 dark:text-zinc-50
            animate-agent-toast-in"
          role="status"
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5 w-8 h-8 rounded-lg bg-violet-500/20 text-violet-700 dark:bg-violet-500/25 dark:text-violet-200 flex items-center justify-center shrink-0">
              <Bell size={16} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold leading-snug text-zinc-900 dark:text-white">{agentToast.title}</div>
              <div className="text-xs text-zinc-600 dark:text-zinc-300 mt-1 whitespace-pre-line leading-relaxed">{agentToast.body}</div>
            </div>
            <button
              type="button"
              onClick={() => setAgentToast(null)}
              className="text-zinc-400 hover:text-zinc-800 dark:hover:text-white text-lg leading-none px-1"
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
        </div>
      )}""",
            s,
            count=1,
        )
        print("sa toast replaced")
    else:
        print("sa toast miss")
    s = "/* agent-toast-polish-v1 */\n" + s
    sa.write_text(s)
    print("sa done")
else:
    print("sa already")

css = Path("src/index.css")
if css.exists():
    t = css.read_text()
    if "agent-toast-in" not in t:
        t += """

/* agent-toast-polish-v1 — slide in from right */
@keyframes agent-toast-in {
  from {
    opacity: 0;
    transform: translateX(120%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.animate-agent-toast-in {
  animation: agent-toast-in 0.38s cubic-bezier(0.22, 1, 0.36, 1) both;
}
"""
        css.write_text(t)
        print("css ok")
    else:
        print("css already")
else:
    print("css miss")

print("done")
