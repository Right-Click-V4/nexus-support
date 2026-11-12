#!/usr/bin/env python3
"""Non-claimer may only use Request to assist — hide Convert/Hold/End/Delete."""
from pathlib import Path

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip")
    raise SystemExit(0)

t = lp.read_text()
if "NONOWNER_LOCK_V4" in t:
    print("already")
    raise SystemExit(0)

old_convert = """                  {selected.ticket_id ? (
                    <span className="text-[11px] px-2 py-1 rounded-lg bg-violet-600/30 text-violet-200 border border-violet-400/30">
                      {selected.ticket_id}
                    </span>
                  ) : (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void convertToTicket()}
                      className="inline-flex items-center gap-1 text-xs font-medium text-violet-200 border border-violet-400/40 px-2.5 py-1.5 rounded-lg hover:bg-violet-500/20"
                    >
                      <Ticket size={12} /> Convert to ticket
                    </button>
                  )}"""

new_convert = """                  {/* NONOWNER_LOCK_V4 */}
                  {selected.ticket_id ? (
                    <span className="text-[11px] px-2 py-1 rounded-lg bg-violet-600/30 text-violet-200 border border-violet-400/30">
                      {selected.ticket_id}
                    </span>
                  ) : (isOwner || !ownerId) ? (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void convertToTicket()}
                      className="inline-flex items-center gap-1 text-xs font-medium text-violet-200 border border-violet-400/40 px-2.5 py-1.5 rounded-lg hover:bg-violet-500/20"
                    >
                      <Ticket size={12} /> Convert to ticket
                    </button>
                  ) : null}"""

if old_convert in t:
    t = t.replace(old_convert, new_convert)
    print("convert gated")
else:
    print("convert pattern miss")

old_del = """                  <button
                    type="button"
                    onClick={() => requestDelete(selected.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg"
                    title="Delete chat permanently"
                  >
                    <Trash2 size={16} />
                  </button>"""

new_del = """                  {(isOwner || !ownerId) ? (
                    <button
                      type="button"
                      onClick={() => requestDelete(selected.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg"
                      title="Delete chat permanently"
                    >
                      <Trash2 size={16} />
                    </button>
                  ) : null}"""

if old_del in t:
    t = t.replace(old_del, new_del)
    print("delete gated")
else:
    print("delete pattern miss")

t = t.replace("Assist mode on - you can send messages.", "Assist request sent — waiting for claimer approval.")

print("braces", t.count("{")-t.count("}"), "parens", t.count("(")-t.count(")"))
lp.write_text(t)
print("nonowner lock done", len(t))
