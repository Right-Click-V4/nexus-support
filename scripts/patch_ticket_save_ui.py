#!/usr/bin/env python3
"""Stronger status colors; success popup on save; remove delete; stay on detail."""
from pathlib import Path
import re

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "ticket-save-ui-v1" in d:
    print("td already")
else:
    d = re.sub(
        r"import \{([^}]+)\} from 'lucide-react';",
        lambda m: "import { "
        + ", ".join(sorted(set([x.strip() for x in m.group(1).split(",") if x.strip()] + ["Check"])))
        + " } from 'lucide-react';",
        d,
        count=1,
    )

    if "showSaved" not in d:
        d = d.replace(
            "  const [saving, setSaving] = useState(false);",
            "  const [saving, setSaving] = useState(false);\n  const [showSaved, setShowSaved] = useState(false);",
            1,
        )

    old_save = """  const save = async () => {
    setSaving(true);
    try {
      await updateTicket(ticket.id, {
        status,
        priority,
        assignee_id: assigneeId || null,
        branch: branch.trim() || undefined,
      });
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };"""
    new_save = """  const save = async () => {
    setSaving(true);
    try {
      await updateTicket(ticket.id, {
        status,
        priority,
        assignee_id: assigneeId || null,
        branch: branch.trim() || undefined,
      });
      setShowSaved(true);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };"""
    if old_save in d:
        d = d.replace(old_save, new_save, 1)
        print("save ok")
    else:
        print("save miss")

    old_del = """          <hr className="border-slate-200" />

          {isAdmin ? (
            !confirmDelete ? (
              <button type="button" onClick={() => setConfirmDelete(true)} className="w-full py-2 text-sm font-medium text-rose-600 hover:bg-rose-50 rounded-lg flex items-center justify-center gap-2">
                <Trash2 size={16} /> Delete ticket
              </button>
            ) : (
              <div className="flex gap-2">
                <button type="button" onClick={handleDelete} disabled={saving} className="flex-1 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg disabled:opacity-50">Confirm delete</button>
                <button type="button" onClick={() => setConfirmDelete(false)} className="flex-1 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
              </div>
            )
          ) : (
            <p className="text-xs text-slate-400 text-center">Ticket delete is admin-only. Soft-close by setting status to Resolved.</p>
          )}"""
    if old_del in d:
        d = d.replace(old_del, "", 1)
        print("delete removed")
    elif "Delete ticket" in d:
        d = re.sub(
            r"\s*<hr className=\"border-slate-200\" />\s*\{isAdmin \? \([\s\S]*?Ticket delete is admin-only\. Soft-close by setting status to Resolved\.</p>\s*\)\}",
            "\n",
            d,
            count=1,
        )
        print("delete removed regex")
    else:
        print("delete miss")

    if "Updated Successfully" not in d:
        modal = """
      {showSaved && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4" onClick={() => setShowSaved(false)}>
          <div
            className="ticket-success-modal w-full max-w-sm rounded-2xl border border-white/10 shadow-2xl px-6 py-8 text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="ticket-success-check mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full">
              <Check size={28} strokeWidth={3} className="text-emerald-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 mb-1">Updated Successfully</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Ticket changes have been saved.</p>
            <button
              type="button"
              onClick={() => setShowSaved(false)}
              className="w-full py-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium"
            >
              OK
            </button>
          </div>
        </div>
      )}
"""
        if 'return (\n    <div className="ticket-detail-page' in d:
            d = d.replace(
                '  return (\n    <div className="ticket-detail-page',
                '  return (\n    <>\n    <div className="ticket-detail-page',
                1,
            )
            d = d.replace(
                "    </div>\n  );\n}",
                "    </div>\n" + modal + "    </>\n  );\n}",
                1,
            )
            print("modal ok")
        else:
            print("modal insert miss")

    if "ticket-save-ui-v1" not in d:
        d = "/* ticket-save-ui-v1 */\n" + d
    td.write_text(d)
    print("td done")

css = """

/* ticket-save-ui-v1 — stronger dark status colors + success modal */
html.nexus-dark .tickets-row-open,
.dark .tickets-row-open {
  background: rgba(59, 130, 246, 0.22) !important;
  box-shadow: inset 4px 0 0 0 #3b82f6 !important;
}
html.nexus-dark .tickets-row-pending,
.dark .tickets-row-pending {
  background: rgba(249, 115, 22, 0.28) !important;
  box-shadow: inset 4px 0 0 0 #f97316 !important;
}
html.nexus-dark .tickets-row-onhold,
.dark .tickets-row-onhold {
  background: rgba(234, 179, 8, 0.28) !important;
  box-shadow: inset 4px 0 0 0 #eab308 !important;
}
html.nexus-dark .tickets-row-resolved,
.dark .tickets-row-resolved {
  background: rgba(34, 197, 94, 0.22) !important;
  box-shadow: inset 4px 0 0 0 #22c55e !important;
}

.ticket-success-modal {
  background: #ffffff;
  color: #0f172a;
}
html.nexus-dark .ticket-success-modal,
.dark .ticket-success-modal {
  background: rgba(24, 20, 42, 0.98);
  color: #f1f5f9;
  border-color: rgba(167, 139, 250, 0.25);
}
.ticket-success-check {
  background: rgba(16, 185, 129, 0.15);
  border: 2px solid rgba(52, 211, 153, 0.5);
  animation: ticket-check-pop 0.45s ease-out;
}
@keyframes ticket-check-pop {
  0% { transform: scale(0.4); opacity: 0; }
  60% { transform: scale(1.12); opacity: 1; }
  100% { transform: scale(1); }
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "ticket-save-ui-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
