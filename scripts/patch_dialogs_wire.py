#!/usr/bin/env python3
"""Replace native confirm/alert with appConfirm/appToast. Idempotent."""
from pathlib import Path

def ensure_import(path: Path, names: str) -> str:
    t = path.read_text()
    if "../lib/dialogs" in t:
        return t
    lines = t.split("\n")
    insert = 0
    for i, line in enumerate(lines):
        if line.startswith("import "):
            insert = i + 1
    lines.insert(insert, f"import {{ {names} }} from '../lib/dialogs';")
    return "\n".join(lines)

p = Path("src/components/CustomersPage.tsx")
if p.exists():
    t = ensure_import(p, "appConfirm, appToast")
    t = t.replace(
        "alert('A branch with that name already exists.');",
        "appToast({ message: 'A branch with that name already exists.', variant: 'warning' });",
    )
    t = t.replace("const deleteBranch = () => {", "const deleteBranch = async () => {")
    t = t.replace(
        "if (!confirm(msg)) return;",
        """const ok = await appConfirm({
      title: 'Delete branch',
      message: msg,
      confirmLabel: 'Delete',
      variant: 'danger',
    });
    if (!ok) return;""",
    )
    p.write_text(t)
    print("CustomersPage:", "appConfirm" in t, "confirm(" not in t)

p = Path("src/components/TicketDetail.tsx")
if p.exists():
    t = ensure_import(p, "appToast")
    t = t.replace(
        "alert('Only admins can permanently delete tickets.');",
        "appToast({ message: 'Only admins can permanently delete tickets.', variant: 'warning' });",
    )
    t = t.replace(
        "alert(e instanceof Error ? e.message : 'Delete failed');",
        "appToast({ message: e instanceof Error ? e.message : 'Delete failed', variant: 'error' });",
    )
    p.write_text(t)
    print("TicketDetail:", "appToast" in t)

p = Path("src/components/PortalCommunityChat.tsx")
if p.exists():
    t = ensure_import(p, "appConfirm, appToast")
    t = t.replace("const leaveGroup = () => {", "const leaveGroup = async () => {")
    t = t.replace(
        "if (!window.confirm(`Leave “${active.name}”?`)) return;",
        """const ok = await appConfirm({ title: 'Leave community', message: `Leave “${active.name}”?`, confirmLabel: 'Leave', variant: 'danger' });
    if (!ok) return;""",
    )
    t = t.replace(
        "if (file.size > 1200000) { window.alert('Image must be under ~1.2MB'); return; }",
        "if (file.size > 1200000) { appToast({ message: 'Image must be under ~1.2MB', variant: 'warning' }); return; }",
    )
    p.write_text(t)
    print("PortalCommunityChat:", "appConfirm" in t)

print("dialog wire done")
