#!/usr/bin/env python3
"""Replace window.confirm sign-out in CustomerPortal with styled appConfirm."""
from pathlib import Path
import re

p = Path("src/components/CustomerPortal.tsx")
if not p.exists() or p.stat().st_size < 1000:
    print("skip CP signout")
    raise SystemExit(0)
s = p.read_text()

if "appConfirm" not in s:
    s = re.sub(
        r"(import .+ from 'react';\n)",
        r"\1import { appConfirm } from '../lib/dialogs';\n",
        s,
        count=1,
    )

# Replace common window.confirm sign-out handlers
patterns = [
    (
        r"if\s*\(\s*window\.confirm\(\s*['\"]Sign out of the Customer Portal\?['\"]\s*\)\s*\)\s*void\s*signOut\(\)\s*;",
        "void (async () => { const ok = await appConfirm({ title: 'Sign out', message: 'Sign out of the Customer Portal?', confirmLabel: 'Sign out', cancelLabel: 'Cancel', variant: 'danger' }); if (ok) void signOut(); })();",
    ),
    (
        r"onClick=\{\(\)\s*=>\s*\{\s*if\s*\(\s*window\.confirm\(\s*['\"]Sign out of the Customer Portal\?['\"]\s*\)\s*\)\s*void\s*signOut\(\);\s*\}\}",
        "onClick={() => { void (async () => { const ok = await appConfirm({ title: 'Sign out', message: 'Sign out of the Customer Portal?', confirmLabel: 'Sign out', cancelLabel: 'Cancel', variant: 'danger' }); if (ok) void signOut(); })(); }}",
    ),
]
changed = False
for a, b in patterns:
    n, c = re.subn(a, b, s)
    if c:
        s = n
        changed = True
        print("replaced", c)

if changed:
    p.write_text(s)
    print("CustomerPortal signout dialog patched")
else:
    print("no window.confirm signout found or already patched")
