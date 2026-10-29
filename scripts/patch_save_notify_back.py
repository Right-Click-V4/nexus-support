#!/usr/bin/env python3
"""Save Changes: notify customer, mark unread, return to Tickets table on OK."""
from pathlib import Path

td = Path("src/components/TicketDetail.tsx")
c = td.read_text()
if "save-notify-back-v1" in c:
    print("already")
    raise SystemExit(0)

if "notifyCustomer" not in c:
    if "from '../lib/slaFormat'" in c:
        c = c.replace(
            "import { formatSlaCountdown } from '../lib/slaFormat';",
            "import { formatSlaCountdown } from '../lib/slaFormat';\nimport { notifyCustomer } from '../lib/agentNotify';",
            1,
        )
    else:
        c = "import { notifyCustomer } from '../lib/agentNotify';\n" + c
    print("import notify ok")

old_save = """  const save = async () => {
    setSaving(true);
    try {
      await updateTicket(ticket.id, {
        status,
        priority,
        assignee_id: assigneeId || null,
        branch: branch.trim() || undefined,
        tags: Array.from(new Set([...tagsWithPlan(ticket.tags, resolutionPlan, resolutionOther), 'customer_unread'])),
      });
      setShowSaved(true);
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
        tags: Array.from(new Set([...tagsWithPlan(ticket.tags, resolutionPlan, resolutionOther), 'customer_unread'])),
      });
      // Explicit customer notify (bell + My Tickets New badge via customer_unread)
      if (ticket.customer_email) {
        void notifyCustomer({
          email: ticket.customer_email,
          title: 'Ticket updated',
          body: `${ticket.title || ticket.id} was updated by support.`,
          link: 'mytickets',
        });
      }
      setShowSaved(true);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };"""

if old_save in c:
    c = c.replace(old_save, new_save, 1)
    print("save ok")
else:
    print("save miss")

old_ok = """            <button
              type="button"
              onClick={() => setShowSaved(false)}
              className="w-full py-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium"
            >
              OK
            </button>"""

new_ok = """            <button
              type="button"
              onClick={() => {
                setShowSaved(false);
                onClose();
              }}
              className="w-full py-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium"
            >
              OK
            </button>"""

if old_ok in c:
    c = c.replace(old_ok, new_ok, 1)
    print("ok btn ok")
else:
    print("ok btn miss")

c = c.replace(
    '{showSaved && (\n        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4" onClick={() => setShowSaved(false)}>',
    '{showSaved && (\n        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4" onClick={() => { setShowSaved(false); onClose(); }}>',
    1,
)

c = "/* save-notify-back-v1 */\n" + c
td.write_text(c)
print("done")
