#!/usr/bin/env python3
"""New tickets unassigned; lock assignee after save; Transfer link like Branch Edit."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
t = tc.read_text()
if "no-auto-assign-v1" not in t:
    old = """    const autoAssignee =
      data.assignee_id ||
      pickAssignee(agents, tickets, { branch: data.branch?.trim() }) ||
      null;
    const ticket: Ticket = {
      id,
      title: data.title,
      description: data.description || '',
      priority,
      status: 'open',
      channel: data.channel,
      assignee_id: autoAssignee,"""
    new = """    // New tickets stay unassigned until an agent claims/assigns them
    const assigneeId = data.assignee_id || null;
    const ticket: Ticket = {
      id,
      title: data.title,
      description: data.description || '',
      priority,
      status: 'open',
      channel: data.channel,
      assignee_id: assigneeId,"""
    if old in t:
        t = t.replace(old, new, 1)
        print("tc create ok")
    else:
        print("tc create miss")
    t = "/* no-auto-assign-v1 */\n" + t
    tc.write_text(t)
    print("tc done")
else:
    print("tc already")

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "assignee-transfer-v1" not in d:
    if "editingAssignee" not in d:
        d = d.replace(
            "const [editingPriority, setEditingPriority] = useState(false);",
            "const [editingPriority, setEditingPriority] = useState(false);\n"
            "  const [editingAssignee, setEditingAssignee] = useState(false);\n"
            "  const [assigneeLocked, setAssigneeLocked] = useState(() => !!ticket.assignee_id);",
            1,
        )
        print("td state")

    old_sync = """    setPriority(ticket.priority);
    setAssigneeId(ticket.assignee_id || '');
    setBranch(ticket.branch || '');"""
    new_sync = """    setPriority(ticket.priority);
    setAssigneeId(ticket.assignee_id || '');
    setBranch(ticket.branch || '');
    setAssigneeLocked(!!ticket.assignee_id);
    setEditingAssignee(false);"""
    if old_sync in d:
        d = d.replace(old_sync, new_sync, 1)
        print("td sync")
    else:
        print("td sync miss")

    old_save_ok = """      setShowSaved(true);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };"""
    new_save_ok = """      if (assigneeId) {
        setAssigneeLocked(true);
        setEditingAssignee(false);
      } else {
        setAssigneeLocked(false);
      }
      setShowSaved(true);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };"""
    if old_save_ok in d:
        d = d.replace(old_save_ok, new_save_ok, 1)
        print("td save")
    else:
        print("td save miss")

    old_assignee = """            <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">Assignee</div>
              <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} className="ticket-input w-full px-3 py-2 text-sm rounded-lg">
                <option value="">Unassigned</option>
                {agents
                  .filter((a) => {
                    const st = (a.approval_status || 'approved').toLowerCase();
                    return st === 'approved' || st === '';
                  })
                  .map((a) => (
                  <option key={a.id} value={a.id}>{a.name}{a.is_admin ? ' (Admin)' : ''}</option>
                ))}
              </select>
            </div>"""

    new_assignee = """            <div className="ticket-meta-block rounded-xl border border-slate-200 dark:border-white/10 p-3.5">
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Assignee</div>
                {assigneeLocked && !editingAssignee ? (
                  <button
                    type="button"
                    onClick={() => setEditingAssignee(true)}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-violet-600 dark:text-violet-300 hover:underline"
                  >
                    Transfer
                  </button>
                ) : assigneeLocked && editingAssignee ? (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingAssignee(false);
                      setAssigneeId(ticket.assignee_id || '');
                    }}
                    className="text-[11px] font-medium text-slate-500 hover:underline"
                  >
                    Cancel
                  </button>
                ) : null}
              </div>
              {(!assigneeLocked || editingAssignee) ? (
                <select
                  value={assigneeId}
                  onChange={(e) => setAssigneeId(e.target.value)}
                  className="ticket-input w-full px-3 py-2 text-sm rounded-lg"
                >
                  <option value="">Unassigned</option>
                  {agents
                    .filter((a) => {
                      const st = (a.approval_status || 'approved').toLowerCase();
                      return st === 'approved' || st === '';
                    })
                    .map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name}{a.is_admin ? ' (Admin)' : ''}
                      </option>
                    ))}
                </select>
              ) : (
                <div className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                  {agents.find((a) => a.id === assigneeId)?.name
                    || ticket.assignee?.name
                    || '—'}
                </div>
              )}
            </div>"""

    if old_assignee in d:
        d = d.replace(old_assignee, new_assignee, 1)
        print("td ui ok")
    else:
        print("td ui miss")

    d = "/* assignee-transfer-v1 */\n" + d
    td.write_text(d)
    print("td done")
else:
    print("td already")

print("done")
