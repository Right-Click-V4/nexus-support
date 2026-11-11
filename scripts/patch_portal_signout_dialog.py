#!/usr/bin/env python3
"""Ensure CustomerPortal Sign out uses appConfirm with import."""
from pathlib import Path
import re

p = Path("src/components/CustomerPortal.tsx")
if not p.exists() or p.stat().st_size < 1000:
    print("skip CP signout")
    raise SystemExit(0)
s = p.read_text()

# Replace window.confirm if present
s2, n = re.subn(
    r"if\s*\(\s*window\.confirm\(\s*['\"]Sign out of the Customer Portal\?['\"]\s*\)\s*\)\s*void\s*signOut\(\)\s*;",
    "void (async () => { const ok = await appConfirm({ title: 'Sign out', message: 'Sign out of the Customer Portal?', confirmLabel: 'Sign out', cancelLabel: 'Cancel', variant: 'danger' }); if (ok) void signOut(); })();",
    s,
)
if n:
    s = s2
    print("replaced window.confirm", n)

# Ensure import if appConfirm used
if "appConfirm" in s and "from '../lib/dialogs'" not in s:
    s2, c = re.subn(
        r"(import \{ useAuth \} from '../context/AuthContext';\n)",
        r"\1import { appConfirm } from '../lib/dialogs';\n",
        s,
        count=1,
    )
    if c:
        s = s2
    else:
        s = "import { appConfirm } from '../lib/dialogs';\n" + s
    print("added appConfirm import")

p.write_text(s)
print("signout dialog ok")
