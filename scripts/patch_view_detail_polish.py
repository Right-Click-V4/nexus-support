#!/usr/bin/env python3
"""Polish My Tickets expandable View: header, Agent Response, plan, attachments."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "view-detail-polish-v1" in c:
    print("already")
    raise SystemExit(0)

old = """                                  <div className=\"rounded-xl border border-zinc-200/70 dark:border-white/10 p-4 space-y-3 text-left\">
                                    <div className=\"flex flex-wrap items-start justify-between gap-2\">
                                      <div>
                                        <div className=\"text-sm font-semibold text-zinc-900 dark:text-zinc-50\">{t.title}</div>
                                        <div className=\"text-xs text-zinc-500 mt-0.5 font-mono\">{t.id} \u00b7 {t.branch || 'No branch'} \u00b7 {t.priority} \u00b7 {t.status}</div>
                                      </div>
                                      <button
                                        type=\"button\"
                                        className=\"text-xs font-medium px-2.5 py-1 rounded-lg border border-zinc-200 dark:border-white/15 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-white/5\"
                                        onClick={() => setExpandedTicketId(null)}
                                      >
                                        Collapse
                                      </button>
                                    </div>
                                    {t.description && (
                                      <div>
                                        <div className=\"text-[10px] font-semibold uppercase tracking-wide text-zinc-500 mb-1\">Description</div>
                                        <p className=\"text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap\">{t.description}</p>
                                      </div>
                                    )}
                                    <div className=\"grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs\">
                                      <div><span className=\"text-zinc-500\">Submitted</span><div className=\"font-medium text-zinc-800 dark:text-zinc-100\">{new Date(t.created_at).toLocaleString()}</div></div>
                                      <div><span className=\"text-zinc-500\">Channel</span><div className=\"font-medium text-zinc-800 dark:text-zinc-100 capitalize\">{t.channel || '\u2014'}</div></div>
                                      <div><span className=\"text-zinc-500\">Status</span><div className=\"font-medium capitalize text-zinc-800 dark:text-zinc-100\">{t.status}</div></div>
                                      <div><span className=\"text-zinc-500\">Priority</span><div className=\"font-medium capitalize text-zinc-800 dark:text-zinc-100\">{t.priority}</div></div>
                                    </div>
                                    <div className=\"pt-2 border-t border-zinc-200/70 dark:border-white/10 space-y-2\">
                                      <div className=\"text-[11px] font-semibold uppercase tracking-wide text-zinc-500\">Conversation</div>
                                      {(t.messages || []).filter((m) => m.kind === 'public').length === 0 && (
                                        <p className=\"text-xs text-zinc-500\">No public replies yet.</p>
                                      )}
                                      {(t.messages || [])
                                        .filter((m) => m.kind === 'public')
                                        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                                        .map((m) => (
                                          <div key={m.id} className=\"rounded-lg px-3 py-2 text-sm bg-white/50 dark:bg-white/5 border border-zinc-200/60 dark:border-white/10\">
                                            <div className=\"text-zinc-800 dark:text-zinc-100 whitespace-pre-wrap\">{m.text}</div>
                                            <div className=\"text-[10px] text-zinc-500 mt-1\">{m.author} \u00b7 {new Date(m.created_at).toLocaleString()}</div>
                                          </div>
                                        ))}
                                    </div>
                                  </div>"""

# Actual file uses middle-dot character · 
old_alt = old.replace("\\u00b7", "\u00b7").replace("\\u2014", "\u2014")

new = open(__file__).read()  # placeholder replaced below
