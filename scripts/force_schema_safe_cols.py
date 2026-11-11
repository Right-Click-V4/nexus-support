#!/usr/bin/env python3
"""Strip selects of columns that do not exist in production Supabase."""
from pathlib import Path
import re

SAFE_CHAT = "id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,ticket_id,branch"
SAFE_AUTO = "id, name, enabled, action, action_value"

def scrub(path: Path) -> None:
    if not path.exists():
        print("skip", path)
        return
    s = path.read_text()
    s2 = s
    s2 = s2.replace(
        "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at, avatar_url';",
        "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';",
    )
    s2 = re.sub(r",\s*actions\b", "", s2)
    s2 = re.sub(r"\bactions\s*,\s*", "", s2)
    s2 = re.sub(
        r"\.from\(['\"]chat_conversations['\"]\)\.select\(['\"][^'\"]*['\"]\)",
        f".from('chat_conversations').select('{SAFE_CHAT}')",
        s2,
    )
    s2 = re.sub(
        r"\.from\(['\"]automations['\"]\)\.select\(\s*['\"][^'\"]*['\"]\s*\)",
        f".from('automations').select('{SAFE_AUTO}')",
        s2,
    )
    s2 = re.sub(
        r"\.from\(['\"]automations['\"]\)\s*\n\s*\.select\(\s*\n\s*['\"][^'\"]*['\"]\s*,?\s*\n\s*\)",
        f".from('automations').select('{SAFE_AUTO}')",
        s2,
    )
    s2 = s2.replace('.select("description, active")', '.select("id, name")')
    s2 = s2.replace(".select('description, active')", ".select('id, name')")
    s2 = s2.replace(".select('role, is_admin')", ".select('role')")
    s2 = s2.replace('.select("role, is_admin")', '.select("role")')
    s2 = s2.replace(
        "if (prof?.is_admin || prof?.role === 'admin') return 'admin';",
        "if (prof?.role === 'admin') return 'admin';",
    )
    s2 = s2.replace(
        "if (nextStatus === 'archived') patch.archived_at = new Date().toISOString();",
        "// if (nextStatus === 'archived') patch.archived_at = new Date().toISOString();",
    )
    if s2 != s:
        path.write_text(s2)
        print("patched", path)
    else:
        print("unchanged", path)

for p in Path("src").rglob("*.tsx"):
    try:
        t = p.read_text(errors="replace")
    except Exception:
        continue
    if any(x in t for x in ("automations", "chat_conversations", "CUSTOMER_COLS", "profiles", "description, active")):
        scrub(p)
print("force_schema_safe_cols done")
