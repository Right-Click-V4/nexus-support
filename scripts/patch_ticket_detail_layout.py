#!/usr/bin/env python3
"""Branch/Priority as read-only + Edit; themed conversation fields; cleaner layout."""
from pathlib import Path
import re

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "ticket-detail-layout-v1" in d:
    print("already")
    raise SystemExit(0)

if "Pencil" not in d:
    d = re.sub(
        r"import \{([^}]+)\} from 'lucide-react';",
        lambda m: (
            "import { "
            + ", ".join(sorted(set([x.strip() for x in m.group(1).split(",") if x.strip()] + ["Pencil"])))
            + " } from 'lucide-react';"
        ),
        d,
        count=1,
    )

if "editingBranch" not in d:
    d = d.replace(
        "  const [branch, setBranch] = useState(ticket.branch || '');",
        """  const [branch, setBranch] = useState(ticket.branch || '');
  const [editingBranch, setEditingBranch] = useState(false);
  const [editingPriority, setEditingPriority] = useState(false);""",
        1,
    )
    print("state ok")

old_fields = """          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Branch</label>
            <select value={branch} onChange={(e) => setBranch(e.target.value)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="">Unassigned</option>
              {branchOptions.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
            <select value={status} onChange={(e) => setStatus(e.target.value as Status)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="new">New</option>
              <option value="open">Open</option>
              <option value="pending">Pending</option>
              <option value="on-hold">On Hold</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
            <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Assignee</label>
            <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="">Unassigned</option>
              {agents.map((a) => (
                <option key={a.id} value={a.id}>{a.name}{a.is_admin ? ' (Admin)' : ''}</option>
              ))}
            </select>
          </div>

          <button type="button" onClick={save} disabled={saving} className="w-full py-2.5 bg-sky-600 text-white text-sm font-medium rounded-lg hover:bg-sky-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>"""

new_fields = """          <div className="grid sm:grid-cols-2 gap-4">
            <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Branch</div>
                {!editingBranch ? (
                  <button type="button" onClick={() => setEditingBranch(true)} className="inline-flex items-center gap-1 text-[11px] font-medium text-violet-600 dark:text-violet-300 hover:underline">
                    <Pencil size={12} /> Edit
                  </button>
                ) : (
                  <button type="button" onClick={() => setEditingBranch(false)} className="text-[11px] font-medium text-slate-500 hover:underline">Done</button>
                )}
              </div>
              {editingBranch ? (
                <select value={branch} onChange={(e) => setBranch(e.target.value)} className="ticket-input w-full px-3 py-2 text-sm rounded-lg">
                  <option value="">Unassigned</option>
                  {branchOptions.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              ) : (
                <div className="text-sm font-semibold text-slate-900 dark:text-slate-50">{branch || '—'}</div>
              )}
            </div>

            <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Priority</div>
                {!editingPriority ? (
                  <button type="button" onClick={() => setEditingPriority(true)} className="inline-flex items-center gap-1 text-[11px] font-medium text-violet-600 dark:text-violet-300 hover:underline">
                    <Pencil size={12} /> Edit
                  </button>
                ) : (
                  <button type="button" onClick={() => setEditingPriority(false)} className="text-[11px] font-medium text-slate-500 hover:underline">Done</button>
                )}
              </div>
              {editingPriority ? (
                <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className="ticket-input w-full px-3 py-2 text-sm rounded-lg">
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              ) : (
                <div className="text-sm font-semibold capitalize text-slate-900 dark:text-slate-50">{priority}</div>
              )}
            </div>

            <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">Status</div>
              <select value={status} onChange={(e) => setStatus(e.target.value as Status)} className="ticket-input w-full px-3 py-2 text-sm rounded-lg">
                <option value="new">New</option>
                <option value="open">Open</option>
                <option value="pending">Pending</option>
                <option value="on-hold">On Hold</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">Assignee</div>
              <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} className="ticket-input w-full px-3 py-2 text-sm rounded-lg">
                <option value="">Unassigned</option>
                {agents.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}{a.is_admin ? ' (Admin)' : ''}</option>
                ))}
              </select>
            </div>
          </div>

          <button type="button" onClick={save} disabled={saving} className="w-full sm:w-auto px-5 py-2.5 bg-sky-600 text-white text-sm font-medium rounded-lg hover:bg-sky-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>"""

if old_fields in d:
    d = d.replace(old_fields, new_fields, 1)
    print("fields ok")
else:
    print("fields miss")

d = d.replace(
    'placeholder="Public reply\u2026" className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/30"',
    'placeholder="Public reply\u2026" className="ticket-input flex-1 px-3 py-2 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/30"',
    1,
)
d = d.replace(
    'placeholder="Internal note\u2026" className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg"',
    'placeholder="Internal note\u2026" className="ticket-input flex-1 px-3 py-2 text-sm rounded-lg"',
    1,
)
# also try unicode ellipsis variants already in file
d = d.replace(
    'className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/30"',
    'className="ticket-input flex-1 px-3 py-2 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/30"',
    1,
)
d = d.replace(
    'className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg"',
    'className="ticket-input flex-1 px-3 py-2 text-sm rounded-lg"',
    1,
)

d = d.replace(
    "className={`rounded-lg px-3 py-2 text-sm ${n.kind === 'public' ? 'bg-sky-50 border border-sky-100' : 'bg-slate-50'}`}",
    "className={`ticket-thread-msg rounded-lg px-3 py-2 text-sm ${n.kind === 'public' ? 'ticket-thread-public' : 'ticket-thread-internal'}`}",
    1,
)

if "ticket-detail-layout-v1" not in d:
    d = "/* ticket-detail-layout-v1 */\n" + d
td.write_text(d)
print("td done")

css = """

/* ticket-detail-layout-v1 — themed inputs + meta blocks */
.ticket-input {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #0f172a;
}
.ticket-input::placeholder {
  color: #94a3b8;
}
html.nexus-dark .ticket-input,
.dark .ticket-input {
  background: rgba(15, 12, 30, 0.75);
  border-color: rgba(167, 139, 250, 0.28);
  color: #f1f5f9;
}
html.nexus-dark .ticket-input::placeholder,
.dark .ticket-input::placeholder {
  color: #94a3b8;
}
html.nexus-dark .ticket-input option,
.dark .ticket-input option {
  background: #1e1b2e;
  color: #f1f5f9;
}
.ticket-meta-block {
  background: rgba(248, 250, 252, 0.8);
}
html.nexus-dark .ticket-meta-block,
.dark .ticket-meta-block {
  background: rgba(15, 12, 30, 0.45);
}
.ticket-thread-public {
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.2);
  color: #0f172a;
}
html.nexus-dark .ticket-thread-public,
.dark .ticket-thread-public {
  background: rgba(56, 189, 248, 0.12);
  border-color: rgba(56, 189, 248, 0.25);
  color: #e2e8f0;
}
.ticket-thread-internal {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #0f172a;
}
html.nexus-dark .ticket-thread-internal,
.dark .ticket-thread-internal {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "ticket-detail-layout-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
