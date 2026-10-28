#!/usr/bin/env python3
"""Ticket detail: resolution plan dropdown (Call, Remote Access, etc.)."""
from pathlib import Path

p = Path("src/components/TicketDetail.tsx")
c = p.read_text()
if "resolution-plan-v1" in c:
    print("already")
    raise SystemExit(0)

marker = "from '../types';"
insert = """
const RESOLUTION_PLANS = [
  '',
  'Call',
  'Remote Access',
  'Screen Share',
  'On-site Visit',
  'Email / Chat Support',
  'Knowledge Base Guide',
  'Software Update / Patch',
  'Hardware Replacement',
  'Account Reset',
  'Escalation to Vendor',
  'Internal Investigation',
  'Other',
] as const;

function planFromTags(tags?: string[] | null): string {
  const hit = (tags || []).find((t) => t.startsWith('plan:'));
  return hit ? hit.slice(5) : '';
}

function tagsWithPlan(tags: string[] | undefined, plan: string): string[] {
  const base = (tags || []).filter((t) => !t.startsWith('plan:'));
  if (plan.trim()) base.push(`plan:${plan.trim()}`);
  return base;
}
"""
idx = c.find(marker)
if idx < 0:
    print("types import miss")
else:
    end = c.find("\n", idx) + 1
    c = c[:end] + insert + c[end:]
    print("constants ok")

old_state = "  const [assigneeId, setAssigneeId] = useState(ticket.assignee_id || '');"
new_state = """  const [assigneeId, setAssigneeId] = useState(ticket.assignee_id || '');
  const [resolutionPlan, setResolutionPlan] = useState(() => planFromTags(ticket.tags));"""
if old_state in c and "resolutionPlan" not in c:
    c = c.replace(old_state, new_state, 1)
    print("state ok")
else:
    print("state miss/skip")

sync = """  useEffect(() => {
    setResolutionPlan(planFromTags(ticket.tags));
  }, [ticket.id, ticket.tags]);
"""
if "setResolutionPlan(planFromTags" not in c:
    needle = "  const branchOptions = useMemo(() => {"
    if needle in c:
        c = c.replace(needle, sync + "\n" + needle, 1)
        print("sync ok")
    else:
        print("sync miss")

old_save = """      await updateTicket(ticket.id, {
        status,
        priority,
        assignee_id: assigneeId || null,
        branch: branch.trim() || undefined,
      });"""
new_save = """      await updateTicket(ticket.id, {
        status,
        priority,
        assignee_id: assigneeId || null,
        branch: branch.trim() || undefined,
        tags: tagsWithPlan(ticket.tags, resolutionPlan),
      });"""
if old_save in c:
    c = c.replace(old_save, new_save, 1)
    print("save ok")
else:
    print("save miss")

old_btn = """          <button type="button" onClick={save} disabled={saving} className="w-full sm:w-auto px-5 py-2.5 bg-sky-600 text-white text-sm font-medium rounded-lg hover:bg-sky-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>"""
new_ui = """          <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
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
if old_btn in c and "Resolution Plan" not in c:
    c = c.replace(old_btn, new_ui, 1)
    print("ui ok")
else:
    print("ui miss/skip")

if "resolution-plan-v1" not in c:
    c = "/* resolution-plan-v1 */\n" + c
p.write_text(c)
print("done")
