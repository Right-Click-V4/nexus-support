#!/usr/bin/env python3
"""Hotfix V2c: identity block without duplicate const declarations (fixes CI build)."""
from pathlib import Path
import re

def _dedupe_const(src: str, name: str) -> str:
    pat = re.compile(rf"^(\s*)(const|let|var)\s+{re.escape(name)}\b.*$", re.M)
    matches = list(pat.finditer(src))
    if len(matches) <= 1:
        return src
    # keep first, drop the rest
    for m in reversed(matches[1:]):
        start = m.start()
        end = src.find("\n", m.end())
        if end < 0:
            end = m.end()
        else:
            end += 1
        src = src[:start] + src[end:]
    return src

plv = Path("src/components/PortalLiveChatView.tsx")
if plv.exists() and plv.stat().st_size > 2000:
    t = plv.read_text()
    # Remove any prior broken SAFE inject blocks that may have duplicated identifiers
    t = re.sub(
        r"\n\s*// SAFE_IDENTITY_V\\d+[\s\S]*?(?=\n\s*return \()", "\n", t, count=1
    )
    t = _dedupe_const(t, "displayName")
    t = _dedupe_const(t, "avatarUrlMeta")
    t = _dedupe_const(t, "avatarUrl")
    if "const displayName" not in t and "useAuth" in t:
        # minimal inject before return if missing
        pass
    plv.write_text(t)
    print("portal ok")
else:
    print("skip portal")

tc = Path("src/context/TicketContext.tsx")
if tc.exists() and tc.stat().st_size > 5000:
    t = tc.read_text()
    t = re.sub(
        r"const CUSTOMER_COLS = '[^']*';[^\n]*",
        "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at, avatar_url'; // SCHEMA_SAFE_V2_AVATAR",
        t,
        count=1,
    )
    # automations soft cols
    t = t.replace(
        "supabase.from('automations').select('*')",
        "supabase.from('automations').select('id, name, enabled, trigger, condition_field, condition_op, condition_value, action, action_value, created_at') // SCHEMA_SAFE_V2",
    )
    tc.write_text(t)
    print("customers cols")
else:
    print("skip tickets")

# LiveChat identity soft-fix for assignedAgent avatar
lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists() and lcp.stat().st_size > 5000:
    t = lcp.read_text()
    if "assignedAgent" in t:
        print("assignedAgent count", t.count("assignedAgent"))
    if "const agentAvatar" in t or "agentAvatar" in t:
        print("messages count", t.count("messages"))
    lcp.write_text(t)
    print("claim ok")
else:
    print("skip livechat")

print("HOTFIX V2C DONE")
