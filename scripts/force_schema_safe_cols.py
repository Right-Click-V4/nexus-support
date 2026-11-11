#!/usr/bin/env python3
"""Strip selects of columns that do not exist in production Supabase."""
from pathlib import Path
import re

# --- TicketContext: customers (no avatar_url) + automations (no actions) ---
tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    s = tc.read_text()
    s2 = s
    s2 = s2.replace(
        "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at, avatar_url';",
        "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';",
    )
    s2 = s2.replace(
        "'id, name, enabled, active, trigger, condition_field, condition_op, condition_value, action, action_value, actions, description'",
        "'id, name, enabled, active, trigger, condition_field, condition_op, condition_value, action, action_value, description'",
    )
    s2 = s2.replace(
        '"id, name, enabled, active, trigger, condition_field, condition_op, condition_value, action, action_value, actions, description"',
        '"id, name, enabled, active, trigger, condition_field, condition_op, condition_value, action, action_value, description"',
    )
    # multiline select: drop , actions
    s2 = re.sub(r",\s*actions\b", "", s2)
    if s2 != s:
        tc.write_text(s2)
        print("TicketContext schema-safe")
    else:
        print("TicketContext already safe or patterns differed")
else:
    print("skip TicketContext")

# --- PlatformContext: chat_conversations minimal columns ---
SAFE_CHAT = (
    "id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,ticket_id,branch"
)
pc = Path("src/context/PlatformContext.tsx")
if pc.exists():
    s = pc.read_text()
    s2 = s
    s2 = re.sub(
        r"\.from\('chat_conversations'\)\.select\((['\"])[^'\"]*\1\)",
        f".from('chat_conversations').select('{SAFE_CHAT}')",
        s2,
    )
    s2 = s2.replace(
        "supabase.from('automations').select('*')",
        "supabase.from('automations').select('id, name, enabled, active, trigger, condition_field, condition_op, condition_value, action, action_value, description')",
    )
    s2 = s2.replace(
        "if (nextStatus === 'archived') patch.archived_at = new Date().toISOString();",
        "// archived_at optional — status is enough\n    // if (nextStatus === 'archived') patch.archived_at = new Date().toISOString();",
    )
    if s2 != s:
        pc.write_text(s2)
        print("PlatformContext schema-safe")
    else:
        print("PlatformContext already safe")
else:
    print("skip PlatformContext")

# --- AuthContext: profiles may not have is_admin ---
ac = Path("src/context/AuthContext.tsx")
if ac.exists():
    s = ac.read_text()
    s2 = s.replace(".select('role, is_admin')", ".select('role')")
    s2 = s2.replace(
        "if (prof?.is_admin || prof?.role === 'admin') return 'admin';",
        "if (prof?.role === 'admin') return 'admin';",
    )
    if s2 != s:
        ac.write_text(s2)
        print("AuthContext profiles select softened")
    else:
        print("AuthContext unchanged")
else:
    print("skip AuthContext")

print("force_schema_safe_cols done")
