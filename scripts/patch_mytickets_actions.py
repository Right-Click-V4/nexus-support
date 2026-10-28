#!/usr/bin/env python3
"""My Tickets: fuller layout, green nav, guide icon, Action column with menu."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-actions-v1" in c:
    print("already")
    raise SystemExit(0)

if "MoreVertical" not in c:
    c = c.replace(
        "  Flag, ListTree, Lightbulb, Clock3, ClipboardList,\n} from 'lucide-react';",
        "  Flag, ListTree, Lightbulb, Clock3, ClipboardList, MoreVertical, Info, Send,\n} from 'lucide-react';",
        1,
    )
    if "MoreVertical" not in c:
        c = re.sub(
            r"import \{([^}]+)\} from 'lucide-react';",
            lambda m: "import { "
            + ", ".join(sorted(set([x.strip() for x in m.group(1).split(",") if x.strip()] + ["MoreVertical", "Info", "Send"])))
            + " } from 'lucide-react';",
            c,
            count=1,
        )
    print("imports ok")

c = c.replace(
    "  mytickets: { title: 'My Tickets', desc: 'Review tickets you have opened with support.', iconColor: 'text-blue-600 dark:text-blue-400' },",
    "  mytickets: { title: 'My Tickets', desc: 'Review tickets you have opened with support.', iconColor: 'text-emerald-600 dark:text-emerald-400' },",
)
c = c.replace(
    'mytickets: "text-blue-600 dark:text-blue-400"',
    'mytickets: "text-emerald-600 dark:text-emerald-400"',
)

if "myTicketMenuId" not in c:
    c = c.replace(
        "  const [myTicketsDateTo, setMyTicketsDateTo] = useState('');",
        "  const [myTicketsDateTo, setMyTicketsDateTo] = useState('');\n"
        "  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);\n"
        "  const [followUpTicket, setFollowUpTicket] = useState<TicketType | null>(null);\n"
        "  const [followUpText, setFollowUpText] = useState('');\n"
        "  const [followUpBusy, setFollowUpBusy] = useState(false);",
        1,
    )
    print("state ok")

c = c.replace(
    '<div className="w-full max-w-6xl space-y-4">',
    '<div className="w-full space-y-5">',
)
c = c.replace(
    '<div className="max-w-5xl mx-auto w-full space-y-4">',
    '<div className="w-full space-y-5">',
)
c = c.replace(
    'className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start"',
    'className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-start"',
)
c = c.replace(
    'className="lg:col-span-8 portal-mytickets-panel',
    'className="xl:col-span-8 portal-mytickets-panel min-h-[420px] flex flex-col',
)
c = c.replace(
    'className="lg:col-span-4 portal-mytickets-guide',
    'className="xl:col-span-4 portal-mytickets-guide',
)

old_guide_h = """                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Status guidelines</h2>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                        What each status means for your ticket.
                      </p>
                    </div>"""
new_guide_h = """                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-xl bg-emerald-500/15 dark:bg-emerald-400/15 flex items-center justify-center shrink-0">
                        <Info size={18} className="text-emerald-600 dark:text-emerald-400" />
                      </div>
                      <div>
                        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Status Guidelines</h2>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
                          What each status means for your ticket.
                        </p>
                      </div>
                    </div>"""
if old_guide_h in c:
    c = c.replace(old_guide_h, new_guide_h, 1)
    print("guide header ok")
else:
    c = c.replace("Status guidelines", "Status Guidelines")
    if "Info size={18}" not in c:
        c = c.replace(
            """                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Status Guidelines</h2>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                        What each status means for your ticket.
                      </p>
                    </div>""",
            new_guide_h,
            1,
        )
    print("guide header alt")

if ">Action<" not in c and "Submitted</th>" in c:
    c = c.replace(
        """                            <th className="px-4 py-2.5 font-semibold">Submitted</th>
                          </tr>""",
        """                            <th className="px-4 py-2.5 font-semibold">Submitted</th>
                            <th className="px-4 py-2.5 font-semibold text-right">Action</th>
                          </tr>""",
        1,
    )
    print("action th ok")

old_row_end = """                              <td className="px-4 py-3 text-xs text-zinc-500 dark:text-zinc-400 whitespace-nowrap">
                                {new Date(t.created_at).toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                              </td>
                            </tr>"""
new_row_end = """                              <td className="px-4 py-3 text-xs text-zinc-500 dark:text-zinc-400 whitespace-nowrap">
                                {new Date(t.created_at).toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                              </td>
                              <td className="px-4 py-3 text-right relative">
                                <button
                                  type="button"
                                  className="inline-flex p-1.5 rounded-lg text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-100 hover:bg-zinc-500/10"
                                  aria-label="Ticket actions"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setMyTicketMenuId((id) => (id === t.id ? null : t.id));
                                  }}
                                >
                                  <MoreVertical size={16} />
                                </button>
                                {myTicketMenuId === t.id && (
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
                                )}
                              </td>
                            </tr>"""
if old_row_end in c:
    c = c.replace(old_row_end, new_row_end, 1)
    print("action cell ok")
else:
    print("action cell miss")

modal = r'''
                {followUpTicket && (
                  <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4" onClick={() => !followUpBusy && setFollowUpTicket(null)}>
                    <div className="w-full max-w-md rounded-2xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 p-5 shadow-xl" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-2 mb-3">
                        <Send size={16} className="text-emerald-600 dark:text-emerald-400" />
                        <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Send Follow-Up</h3>
                      </div>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-2">{followUpTicket.id} · {followUpTicket.title}</p>
                      <textarea
                        value={followUpText}
                        onChange={(e) => setFollowUpText(e.target.value)}
                        rows={4}
                        placeholder="Add an update or extra details for support\u2026"
                        className="w-full text-sm rounded-xl border border-zinc-200 dark:border-white/15 bg-zinc-50 dark:bg-zinc-950/50 px-3 py-2 text-zinc-900 dark:text-zinc-100 mb-3"
                      />
                      <div className="flex justify-end gap-2">
                        <button type="button" disabled={followUpBusy} onClick={() => setFollowUpTicket(null)} className="px-3 py-2 text-xs font-medium rounded-lg border border-zinc-200 dark:border-white/15">Cancel</button>
                        <button
                          type="button"
                          disabled={followUpBusy || !followUpText.trim()}
                          onClick={() => {
                            void (async () => {
                              if (!followUpTicket || !followUpText.trim()) return;
                              setFollowUpBusy(true);
                              try {
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
                              }
                            })();
                          }}
                          className="px-3 py-2 text-xs font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40"
                        >
                          {followUpBusy ? 'Sending\u2026' : 'Send'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
'''

if "Send Follow-Up</h3>" not in c:
    idx = c.find("            {view === 'mytickets'")
    idx2 = c.find("            {view === 'help'", idx)
    if idx >= 0 and idx2 > idx:
        c = c[:idx2].replace(
            "              );\n            })()}",
            modal + "              );\n            })()}",
            1,
        ) + c[idx2:]
        print("modal ok")
    else:
        print("modal miss")

if "mytickets-actions-v1" not in c:
    c = "/* mytickets-actions-v1 */\n" + c
cp.write_text(c)
print("done")
