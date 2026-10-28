#!/usr/bin/env python3
"""Polish My Tickets expandable View panel."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "view-detail-polish-v1" in c:
    print("already")
    raise SystemExit(0)

c2, n = re.subn(
    r"\{t\.id\} (.) \{t\.branch \|\| 'No branch'\} \1 \{t\.priority\} \1 \{t\.status\}",
    r"{t.id} \1 {t.branch || 'No branch'}",
    c,
    count=1,
)
c = c2
print("header", n)

c = c.replace(
    'tracking-wide text-zinc-500">Conversation</div>',
    'tracking-wide text-zinc-500">Agent Response</div>',
    1,
)

old_msg = """                                          <div key={m.id} className="rounded-lg px-3 py-2 text-sm bg-white/50 dark:bg-white/5 border border-zinc-200/60 dark:border-white/10">
                                            <div className="text-zinc-800 dark:text-zinc-100 whitespace-pre-wrap">{m.text}</div>
                                            <div className="text-[10px] text-zinc-500 mt-1">{m.author} \u00b7 {new Date(m.created_at).toLocaleString()}</div>
                                          </div>"""
new_msg = """                                          <div key={m.id} className="rounded-xl px-3.5 py-3 text-sm bg-white/70 dark:bg-white/[0.06] border border-zinc-200/70 dark:border-white/10 shadow-sm">
                                            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-1.5">
                                              <div className="text-sm font-bold text-zinc-900 dark:text-zinc-50">{m.author}</div>
                                              <div className="text-[10px] text-zinc-500 tabular-nums">{new Date(m.created_at).toLocaleString()}</div>
                                            </div>
                                            <div className="text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap leading-relaxed">{m.text}</div>
                                          </div>"""
if old_msg in c:
    c = c.replace(old_msg, new_msg, 1)
    print("msg ok")
else:
    old_msg2 = old_msg.replace(" \u00b7 ", " · ")
    if old_msg2 in c:
        c = c.replace(old_msg2, new_msg, 1)
        print("msg ok2")
    else:
        print("msg miss")

pat = re.compile(
    r'(\s*)<div className="pt-2 border-t border-zinc-200/70 dark:border-white/10 space-y-2">\s*'
    r'<div className="text-\[11px\] font-semibold uppercase tracking-wide text-zinc-500">(Agent Response|Conversation)</div>',
    re.M,
)
m = pat.search(c)
if m and "Resolution Plan" not in c[m.start() : m.start() + 500]:
    ind = m.group(1)
    repl = f"""
{ind}{{(() => {{
{ind}  const planTag = (t.tags || []).find((x) => x.startsWith('plan:') && !x.startsWith('plan_note:'));
{ind}  const planNote = (t.tags || []).find((x) => x.startsWith('plan_note:'));
{ind}  const plan = planTag ? planTag.slice(5) : '';
{ind}  const note = planNote ? planNote.slice(10) : '';
{ind}  if (!plan) return null;
{ind}  return (
{ind}    <div className="rounded-lg border border-violet-300/40 dark:border-violet-400/25 bg-violet-500/10 px-3.5 py-3">
{ind}      <div className="text-[10px] font-semibold uppercase tracking-wide text-violet-700 dark:text-violet-300 mb-1">Resolution Plan</div>
{ind}      <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{{plan}}</div>
{ind}      {{note && <p className="text-xs text-zinc-600 dark:text-zinc-300 mt-1 whitespace-pre-wrap">{{note}}</p>}}
{ind}    </div>
{ind}  );
{ind}}})()}}

{ind}{{(t.attachments || []).length > 0 && (
{ind}  <div className="rounded-lg border border-zinc-200/60 dark:border-white/10 px-3.5 py-3 space-y-2">
{ind}    <div className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">Attachments</div>
{ind}    <ul className="space-y-1.5">
{ind}      {{(t.attachments || []).map((a) => (
{ind}        <li key={{a.id}}>
{ind}          <a href={{a.url}} target="_blank" rel="noreferrer" className="text-sm font-medium text-sky-600 dark:text-sky-400 hover:underline break-all">{{a.name}}</a>
{ind}          <span className="text-[10px] text-zinc-500 ml-2">{{a.size ? `${{Math.round(a.size / 1024)}} KB` : ''}}</span>
{ind}        </li>
{ind}      ))}}
{ind}    </ul>
{ind}  </div>
{ind})}}

{ind}<div className="pt-1 space-y-2.5">
{ind}  <div className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500">Agent Response</div>"""
    c = c[: m.start()] + repl + c[m.end() :]
    print("plan+attach ok")
else:
    print("plan insert", "found" if m else "miss")

c = c.replace(
    "No public replies yet.",
    "No agent response yet. Support will reply here when they message you.",
    1,
)

c = c.replace(
    'rounded-xl border border-zinc-200/70 dark:border-white/10 p-4 space-y-3 text-left"',
    'rounded-xl border border-zinc-200/70 dark:border-white/10 bg-white/40 dark:bg-white/[0.03] p-4 sm:p-5 space-y-4 text-left shadow-sm"',
    1,
)

c = "/* view-detail-polish-v1 */\n" + c
cp.write_text(c)
print("done")
