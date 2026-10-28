#!/usr/bin/env python3
"""Status guide pills aligned; glass card; Action menu not clipped."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-menu-guide-v1" in c:
    print("already")
    raise SystemExit(0)

c = c.replace(
    "portal-mytickets-panel min-h-[480px] flex flex-col rounded-2xl border border-zinc-200/80 dark:border-white/10 overflow-hidden",
    "portal-mytickets-panel min-h-[480px] flex flex-col rounded-2xl border border-zinc-200/80 dark:border-white/10 overflow-visible",
)
c = c.replace(
    "portal-mytickets-panel min-h-[420px] flex flex-col rounded-2xl border border-zinc-200/80 dark:border-white/10 overflow-hidden",
    "portal-mytickets-panel min-h-[480px] flex flex-col rounded-2xl border border-zinc-200/80 dark:border-white/10 overflow-visible",
)

old_list = """                    <ul className="space-y-3">
                      {statusGuide.map((s) => (
                        <li key={s.key} className="flex gap-3">
                          <span className={`mt-0.5 shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded-full capitalize ${s.color}`}>{s.label}</span>
                          <p className="text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">{s.meaning}</p>
                        </li>
                      ))}
                    </ul>"""
new_list = """                    <ul className="space-y-3.5">
                      {statusGuide.map((s) => (
                        <li key={s.key} className="grid grid-cols-[6.5rem_1fr] gap-x-3 items-start">
                          <span className={`inline-flex justify-center items-center text-[10px] font-semibold px-2 py-1 rounded-full capitalize leading-none ${s.color}`}>{s.label}</span>
                          <p className="text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed pt-0.5">{s.meaning}</p>
                        </li>
                      ))}
                    </ul>"""
if old_list in c:
    c = c.replace(old_list, new_list, 1)
    print("guide list ok")
else:
    print("guide list miss")

old_menu = """                                {myTicketMenuId === t.id && (
                                  <div className="absolute right-2 top-full z-20 mt-1 w-44 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-lg py-1 text-left">
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setTrackId(t.id);
                                        setTracked(t);
                                      }}
                                    >
                                      View
                                    </button>
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setFollowUpTicket(t);
                                        setFollowUpText('');
                                      }}
                                    >
                                      Send Follow-Up
                                    </button>
                                  </div>
                                )}"""
new_menu = """                                {myTicketMenuId === t.id && (
                                  <div className="portal-mytickets-action-menu absolute right-full top-1/2 -translate-y-1/2 mr-1 z-[100] w-44 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl py-1 text-left">
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setTrackId(t.id);
                                        setTracked(t);
                                      }}
                                    >
                                      View
                                    </button>
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setFollowUpTicket(t);
                                        setFollowUpText('');
                                      }}
                                    >
                                      Send Follow-Up
                                    </button>
                                  </div>
                                )}"""
if old_menu in c:
    c = c.replace(old_menu, new_menu, 1)
    print("menu ok")
else:
    if "portal-mytickets-action-menu" not in c and "myTicketMenuId === t.id" in c:
        c = c.replace(
            'className="absolute right-2 top-full z-20 mt-1 w-44 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-lg py-1 text-left"',
            'className="portal-mytickets-action-menu absolute right-full top-1/2 -translate-y-1/2 mr-1 z-[100] w-44 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl py-1 text-left"',
            1,
        )
        print("menu class ok")
    else:
        print("menu miss")

c = c.replace(
    'sticky right-0 z-10 bg-inherit portal-mytickets-action-col">Action</th>',
    'sticky right-0 z-[5] bg-inherit portal-mytickets-action-col">Action</th>',
)
c = c.replace(
    'relative sticky right-0 z-10 portal-mytickets-action-col"',
    'relative sticky right-0 z-[5] portal-mytickets-action-col"',
)

if "mytickets-menu-guide-v1" not in c:
    c = "/* mytickets-menu-guide-v1 */\n" + c
cp.write_text(c)
print("cp done")

css = """

/* mytickets-menu-guide-v1 */
.portal-mytickets-guide {
  background: rgba(255, 255, 255, 0.45) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-color: rgba(148, 163, 184, 0.35) !important;
}
html.nexus-dark .portal-mytickets-guide,
.dark .portal-mytickets-guide {
  background: rgba(24, 20, 42, 0.42) !important;
  border-color: rgba(167, 139, 250, 0.22) !important;
}
.portal-mytickets-action-menu {
  pointer-events: auto;
}
.portal-mytickets-panel .overflow-x-auto {
  overflow-x: auto;
  overflow-y: visible;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "mytickets-menu-guide-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
