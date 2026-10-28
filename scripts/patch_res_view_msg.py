#!/usr/bin/env python3
"""Resolution plan placeholder+Other; Save at bottom; customer View shows public msgs."""
from pathlib import Path

p = Path("src/components/TicketDetail.tsx")
c = p.read_text()
if "res-view-msg-v1" in c:
    print("td already")
else:
    old_helpers = """function planFromTags(tags?: string[] | null): string {
  const hit = (tags || []).find((t) => t.startsWith('plan:'));
  return hit ? hit.slice(5) : '';
}

function tagsWithPlan(tags: string[] | undefined, plan: string): string[] {
  const base = (tags || []).filter((t) => !t.startsWith('plan:'));
  if (plan.trim()) base.push(`plan:${plan.trim()}`);
  return base;
}"""
    new_helpers = """function planFromTags(tags?: string[] | null): string {
  const hit = (tags || []).find((t) => t.startsWith('plan:') && !t.startsWith('plan_note:'));
  if (!hit) return '';
  const v = hit.slice(5);
  return v.startsWith('Other') ? 'Other' : v;
}

function planNoteFromTags(tags?: string[] | null): string {
  const note = (tags || []).find((t) => t.startsWith('plan_note:'));
  if (note) return note.slice(10);
  const hit = (tags || []).find((t) => t.startsWith('plan:Other|'));
  return hit ? hit.slice('plan:Other|'.length) : '';
}

function tagsWithPlan(tags: string[] | undefined, plan: string, otherNote = ''): string[] {
  const base = (tags || []).filter((t) => !t.startsWith('plan:') && !t.startsWith('plan_note:'));
  if (!plan.trim()) return base;
  if (plan === 'Other') {
    base.push('plan:Other');
    if (otherNote.trim()) base.push(`plan_note:${otherNote.trim()}`);
  } else {
    base.push(`plan:${plan.trim()}`);
  }
  return base;
}"""
    if old_helpers in c:
        c = c.replace(old_helpers, new_helpers, 1)
        print("helpers ok")
    elif "planNoteFromTags" not in c:
        print("helpers miss")

    if "resolutionOther" not in c:
        c = c.replace(
            "  const [resolutionPlan, setResolutionPlan] = useState(() => planFromTags(ticket.tags));",
            "  const [resolutionPlan, setResolutionPlan] = useState(() => planFromTags(ticket.tags));\n  const [resolutionOther, setResolutionOther] = useState(() => planNoteFromTags(ticket.tags));",
            1,
        )
        print("state ok")

    c = c.replace(
        """  useEffect(() => {
    setResolutionPlan(planFromTags(ticket.tags));
  }, [ticket.id, ticket.tags]);""",
        """  useEffect(() => {
    setResolutionPlan(planFromTags(ticket.tags));
    setResolutionOther(planNoteFromTags(ticket.tags));
  }, [ticket.id, ticket.tags]);""",
        1,
    )
    c = c.replace(
        "tags: tagsWithPlan(ticket.tags, resolutionPlan),",
        "tags: tagsWithPlan(ticket.tags, resolutionPlan, resolutionOther),",
    )

    old_res = """          <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">Resolution Plan</div>
            <select
              value={resolutionPlan}
              onChange={(e) => setResolutionPlan(e.target.value)}
              className="ticket-input w-full px-3 py-2 text-sm rounded-lg"
            >
              <option value="">Select how you plan to resolve\u2026</option>
              {RESOLUTION_PLANS.filter(Boolean).map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
            <p className="mt-1.5 text-[11px] text-slate-500 dark:text-slate-400">
              How the agent intends to fix this ticket (Call, Remote Access, on-site, etc.).
            </p>
          </div>

          <button type="button" onClick={save} disabled={saving} className="w-full sm:w-auto px-5 py-2.5 bg-sky-600 text-white text-sm font-medium rounded-lg hover:bg-sky-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>"""

    new_res = """          <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">Resolution Plan</div>
            <select
              value={resolutionPlan}
              onChange={(e) => {
                setResolutionPlan(e.target.value);
                if (e.target.value !== 'Other') setResolutionOther('');
              }}
              className="ticket-input w-full px-3 py-2 text-sm rounded-lg"
            >
              <option value="" disabled>
                Select how you plan to resolve\u2026
              </option>
              {RESOLUTION_PLANS.filter(Boolean).map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
            {resolutionPlan === 'Other' && (
              <div className="mt-2.5">
                <label className="block text-[11px] font-medium text-slate-500 dark:text-slate-400 mb-1">Describe other plan</label>
                <textarea
                  value={resolutionOther}
                  onChange={(e) => setResolutionOther(e.target.value)}
                  rows={2}
                  placeholder="Explain how you will resolve this ticket\u2026"
                  className="ticket-input w-full px-3 py-2 text-sm rounded-lg resize-y"
                />
              </div>
            )}
            <p className="mt-1.5 text-[11px] text-slate-500 dark:text-slate-400">
              How the agent intends to fix this ticket (Call, Remote Access, on-site, etc.).
            </p>
          </div>"""
    if old_res in c:
        c = c.replace(old_res, new_res, 1)
        print("res ui ok")
    else:
        print("res ui miss")

    anchor = """            <div className="flex gap-2">
              <input value={noteText} onChange={(e) => setNoteText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleAddNote()} placeholder="Internal note\u2026" className="ticket-input flex-1 px-3 py-2 text-sm rounded-lg" />
              <button type="button" onClick={handleAddNote} disabled={!noteText.trim()} className="px-3 py-2 text-sm font-medium bg-slate-100 hover:bg-slate-200 rounded-lg disabled:opacity-40">Note</button>
            </div>
          </div>


        </div>"""
    bottom = """            <div className="flex gap-2">
              <input value={noteText} onChange={(e) => setNoteText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleAddNote()} placeholder="Internal note\u2026" className="ticket-input flex-1 px-3 py-2 text-sm rounded-lg" />
              <button type="button" onClick={handleAddNote} disabled={!noteText.trim()} className="px-3 py-2 text-sm font-medium bg-slate-100 hover:bg-slate-200 rounded-lg disabled:opacity-40">Note</button>
            </div>
          </div>

          <button type="button" onClick={save} disabled={saving} className="w-full sm:w-auto px-5 py-2.5 bg-sky-600 text-white text-sm font-medium rounded-lg hover:bg-sky-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>

        </div>"""
    if "onClick={save}" not in c and anchor in c:
        c = c.replace(anchor, bottom, 1)
        print("bottom save ok")
    elif c.count("onClick={save}") == 0:
        print("bottom save miss")
    else:
        print("save count", c.count("onClick={save}"))

    c = "/* res-view-msg-v1 */\n" + c
    p.write_text(c)
    print("td done")

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "res-view-msg-v1" in c:
    print("cp already")
else:
    old_view = """                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setTrackId(t.id);
                                        setTracked(t);
                                      }}
                                    >
                                      View
                                    </button>"""
    new_view = """                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setTrackId(t.id);
                                        setTracked(t);
                                        setView('track');
                                      }}
                                    >
                                      View
                                    </button>"""
    if old_view in c:
        c = c.replace(old_view, new_view, 1)
        print("view nav ok")

    needle = "  const [tracked, setTracked] = useState<TicketType | null>(null);"
    effect = """  const [tracked, setTracked] = useState<TicketType | null>(null);
  useEffect(() => {
    if (!tracked?.id) return;
    const live = tickets.find((x) => x.id === tracked.id);
    if (live) setTracked(live);
  }, [tickets, tracked?.id]);"""
    if needle in c and "const live = tickets.find" not in c:
        c = c.replace(needle, effect, 1)
        print("sync tracked ok")

    line = """                    <div className="text-xs text-zinc-500">{tracked.branch || 'No branch'} \u00b7 {new Date(tracked.created_at).toLocaleString()}</div>"""
    msgs = """                    <div className="text-xs text-zinc-500">{tracked.branch || 'No branch'} \u00b7 {new Date(tracked.created_at).toLocaleString()}</div>
                    {tracked.description && (
                      <p className="text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap">{tracked.description}</p>
                    )}
                    <div className="pt-2 border-t border-zinc-200/70 dark:border-white/10 space-y-2">
                      <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">Conversation</div>
                      {(tracked.messages || []).filter((m) => m.kind === 'public').length === 0 && (
                        <p className="text-xs text-zinc-500">No public replies yet.</p>
                      )}
                      {(tracked.messages || [])
                        .filter((m) => m.kind === 'public')
                        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                        .map((m) => (
                          <div key={m.id} className="rounded-lg px-3 py-2 text-sm bg-white/40 dark:bg-white/5 border border-zinc-200/60 dark:border-white/10">
                            <div className="text-zinc-800 dark:text-zinc-100 whitespace-pre-wrap">{m.text}</div>
                            <div className="text-[10px] text-zinc-500 mt-1">{m.author} \u00b7 {new Date(m.created_at).toLocaleString()}</div>
                          </div>
                        ))}
                    </div>"""
    # try unicode middle dot variants
    if "No public replies yet" not in c:
        import re
        m = re.search(r"(<div className=\"text-xs text-zinc-500\">\{tracked\.branch \|\| 'No branch'\} .) \{new Date\(tracked\.created_at\)\.toLocaleString\(\)\}</div>)", c)
        if m:
            c = c.replace(m.group(0), msgs.replace(" · ", m.group(1)[-2:] + " " if False else " · "), 1)
            # simpler
        line2 = "{tracked.branch || 'No branch'} · {new Date(tracked.created_at).toLocaleString()}"
        if line2 in c and "No public replies yet" not in c:
            insert_after = c.find(line2)
            end_div = c.find("</div>", insert_after) + len("</div>")
            block = c[c.rfind("<div", 0, insert_after):end_div]
            c = c.replace(block, msgs, 1)
            print("msgs ui ok")
        else:
            print("msgs ui miss")

    c = "/* res-view-msg-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
print("done")
