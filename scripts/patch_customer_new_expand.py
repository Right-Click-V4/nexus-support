#!/usr/bin/env python3
"""Customer My Tickets: New badge after agent update; expandable View details."""
from pathlib import Path
import re

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "customer-new-expand-v1" not in c:
    old = """    const updates: Parameters<typeof updateTicket>[1] = { messages };
    if (!ticket.first_response_at && kind === 'public') updates.first_response_at = msg.created_at;
    await updateTicket(ticketId, updates);"""
    new = """    const updates: Parameters<typeof updateTicket>[1] = { messages };
    if (!ticket.first_response_at && kind === 'public') updates.first_response_at = msg.created_at;
    if (kind === 'public') {
      updates.tags = Array.from(new Set([...(ticket.tags || []).filter((t) => t !== 'customer_unread'), 'customer_unread']));
    }
    await updateTicket(ticketId, updates);"""
    if old in c:
        c = c.replace(old, new, 1)
        print("ctx msg ok")
    else:
        print("ctx msg miss")
    c = "/* customer-new-expand-v1 */\n" + c
    tc.write_text(c)
else:
    print("ctx already")

td = Path("src/components/TicketDetail.tsx")
c = td.read_text()
if "customer-new-expand-v1" not in c:
    old = """        tags: tagsWithPlan(ticket.tags, resolutionPlan, resolutionOther),"""
    new = """        tags: Array.from(new Set([...tagsWithPlan(ticket.tags, resolutionPlan, resolutionOther), 'customer_unread'])),"""
    if old in c:
        c = c.replace(old, new, 1)
        print("td save ok")
    else:
        print("td save miss")
    c = "/* customer-new-expand-v1 */\n" + c
    td.write_text(c)
else:
    print("td already")

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "customer-new-expand-v1" in c:
    print("cp already")
    raise SystemExit(0)

if "expandedTicketId" not in c:
    c = c.replace(
        "  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);",
        "  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);\n  const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);",
        1,
    )
    print("expand state ok")

subj = re.search(
    r'<td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50 max-w-\[200px\]">\s*<div className="truncate" title=\{t\.title\}>\{t\.title\}</div>\s*</td>',
    c,
)
if subj:
    c = c[: subj.start()] + """<td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50 max-w-[240px]">
                                <div className="flex items-center gap-2 min-w-0">
                                  <div className="truncate" title={t.title}>{t.title}</div>
                                  {(t.tags || []).includes('customer_unread') && (
                                    <span className="shrink-0 text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full bg-sky-500 text-white">New</span>
                                  )}
                                </div>
                              </td>""" + c[subj.end() :]
    print("subject badge ok")
else:
    print("subject miss")

old_btn = """                                <button
                                  type="button"
                                  className="inline-flex p-1.5 rounded-lg text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-100 hover:bg-zinc-500/10"
                                  aria-label="Ticket actions"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setMyTicketMenuId((id) => (id === t.id ? null : t.id));
                                  }}
                                >
                                  <MoreVertical size={16} />
                                </button>"""
new_btn = """                                <button
                                  type="button"
                                  className="relative inline-flex p-1.5 rounded-lg text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-100 hover:bg-zinc-500/10"
                                  aria-label="Ticket actions"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setMyTicketMenuId((id) => (id === t.id ? null : t.id));
                                  }}
                                >
                                  <MoreVertical size={16} />
                                  {(t.tags || []).includes('customer_unread') && (
                                    <span className="absolute -top-0.5 -right-0.5 min-w-[14px] h-3.5 px-0.5 rounded-full bg-sky-500 text-white text-[9px] font-bold leading-[14px] text-center">1</span>
                                  )}
                                </button>"""
if old_btn in c:
    c = c.replace(old_btn, new_btn, 1)
    print("menu badge ok")
else:
    print("menu badge miss")

new_view_click = """                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        const open = expandedTicketId !== t.id;
                                        setExpandedTicketId(open ? t.id : null);
                                        if (open && (t.tags || []).includes('customer_unread')) {
                                          void updateTicket(t.id, {
                                            tags: (t.tags || []).filter((x) => x !== 'customer_unread'),
                                          });
                                        }
                                      }}
                                    >
                                      {expandedTicketId === t.id ? 'Collapse' : 'View'}
                                    </button>"""
for old_view_click in [
    """                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setTrackId(t.id);
                                        setTracked(t);
                                        setView('track');
                                      }}
                                    >
                                      View
                                    </button>""",
    """                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setTrackId(t.id);
                                        setTracked(t);
                                      }}
                                    >
                                      View
                                    </button>""",
]:
    if old_view_click in c:
        c = c.replace(old_view_click, new_view_click, 1)
        print("view expand ok")
        break
else:
    print("view expand miss")

old_end = """                              </td>
                            </tr>
                          ))}"""
new_end = """                              </td>
                            </tr>
                            {expandedTicketId === t.id && (
                              <tr key={t.id + '-detail'} className="border-b border-zinc-100/80 dark:border-white/5 bg-violet-500/[0.04]">
                                <td colSpan={7} className="px-4 py-4">
                                  <div className="rounded-xl border border-zinc-200/70 dark:border-white/10 p-4 space-y-3 text-left">
                                    <div className="flex flex-wrap items-start justify-between gap-2">
                                      <div>
                                        <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{t.title}</div>
                                        <div className="text-xs text-zinc-500 mt-0.5 font-mono">{t.id} \u00b7 {t.branch || 'No branch'} \u00b7 {t.priority} \u00b7 {t.status}</div>
                                      </div>
                                      <button
                                        type="button"
                                        className="text-xs font-medium px-2.5 py-1 rounded-lg border border-zinc-200 dark:border-white/15 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-white/5"
                                        onClick={() => setExpandedTicketId(null)}
                                      >
                                        Collapse
                                      </button>
                                    </div>
                                    {t.description && (
                                      <div>
                                        <div className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500 mb-1">Description</div>
                                        <p className="text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap">{t.description}</p>
                                      </div>
                                    )}
                                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                                      <div><span className="text-zinc-500">Submitted</span><div className="font-medium text-zinc-800 dark:text-zinc-100">{new Date(t.created_at).toLocaleString()}</div></div>
                                      <div><span className="text-zinc-500">Channel</span><div className="font-medium text-zinc-800 dark:text-zinc-100 capitalize">{t.channel || '\u2014'}</div></div>
                                      <div><span className="text-zinc-500">Status</span><div className="font-medium capitalize text-zinc-800 dark:text-zinc-100">{t.status}</div></div>
                                      <div><span className="text-zinc-500">Priority</span><div className="font-medium capitalize text-zinc-800 dark:text-zinc-100">{t.priority}</div></div>
                                    </div>
                                    <div className="pt-2 border-t border-zinc-200/70 dark:border-white/10 space-y-2">
                                      <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">Conversation</div>
                                      {(t.messages || []).filter((m) => m.kind === 'public').length === 0 && (
                                        <p className="text-xs text-zinc-500">No public replies yet.</p>
                                      )}
                                      {(t.messages || [])
                                        .filter((m) => m.kind === 'public')
                                        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                                        .map((m) => (
                                          <div key={m.id} className="rounded-lg px-3 py-2 text-sm bg-white/50 dark:bg-white/5 border border-zinc-200/60 dark:border-white/10">
                                            <div className="text-zinc-800 dark:text-zinc-100 whitespace-pre-wrap">{m.text}</div>
                                            <div className="text-[10px] text-zinc-500 mt-1">{m.author} \u00b7 {new Date(m.created_at).toLocaleString()}</div>
                                          </div>
                                        ))}
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            )}
                          ))}"""
idx = c.find("Send Follow-Up")
if idx > 0 and old_end in c[idx : idx + 800]:
    c = c[:idx] + c[idx : idx + 800].replace(old_end, new_end, 1) + c[idx + 800 :]
    print("expand row ok")
elif old_end in c:
    pos = c.rfind(old_end)
    c = c[:pos] + new_end + c[pos + len(old_end) :]
    print("expand row rfind ok")
else:
    print("expand row miss")

c = "/* customer-new-expand-v1 */\n" + c
cp.write_text(c)
print("done")
