#!/usr/bin/env python3
"""Push local avatar to agents.avatar_url so other agents/customers see the photo."""
from pathlib import Path
import re

tc = Path("src/context/TicketContext.tsx")
if tc.exists() and tc.stat().st_size > 5000:
    t = tc.read_text()
    if "AVATAR_PUSH_DB_V1" not in t and "function hydrateAvatar" in t:
        new = """function hydrateAvatar(agent: Agent): Agent {
  // AVATAR_PUSH_DB_V1
  if (agent.avatar_url) return agent;
  try {
    const local = localStorage.getItem(`nexus-avatar-${agent.id}`);
    if (local) {
      try {
        if (supabase && agent.id) {
          void supabase.from('agents').update({ avatar_url: local }).eq('id', agent.id);
        }
      } catch { /* non-fatal */ }
      return { ...agent, avatar_url: local };
    }
  } catch {
    /* ignore */
  }
  return agent;
}"""
        m = re.search(r"function hydrateAvatar\(agent: Agent\): Agent \{.*?\n\}", t, re.S)
        if m:
            t = t[: m.start()] + new + t[m.end() :]
            tc.write_text(t)
            print("hydrateAvatar pushes to DB")
        else:
            print("hydrateAvatar regex miss")
    else:
        print("avatar push already or no hydrate")
else:
    print("skip TicketContext")

lp = Path("src/components/LiveChatPage.tsx")
if lp.exists() and lp.stat().st_size > 5000:
    t = lp.read_text()
    if "AVATAR_RESOLVE_V4" not in t:
        old = "                  const agentAvatar = msgAgent?.avatar_url || '';"
        new = """                  // AVATAR_RESOLVE_V4
                  let agentAvatar = msgAgent?.avatar_url || '';
                  if (!agentAvatar && msgAgent?.id) {
                    try { agentAvatar = localStorage.getItem('nexus-avatar-' + msgAgent.id) || ''; } catch {}
                  }
                  if (!agentAvatar && claimed?.id) {
                    try { agentAvatar = claimed.avatar_url || localStorage.getItem('nexus-avatar-' + claimed.id) || ''; } catch { agentAvatar = claimed?.avatar_url || ''; }
                  }"""
        if old in t:
            t = t.replace(old, new)
            print("avatar resolve local fallback")
            lp.write_text(t)
        else:
            # V3 already may have set agentAvatar differently
            if "const agentAvatar = msgAgent?.avatar_url" in t:
                t = t.replace(
                    "const agentAvatar = msgAgent?.avatar_url || '';",
                    "let agentAvatar = msgAgent?.avatar_url || '';\n                  // AVATAR_RESOLVE_V4\n                  if (!agentAvatar && msgAgent?.id) { try { agentAvatar = localStorage.getItem('nexus-avatar-' + msgAgent.id) || ''; } catch {} }",
                    1,
                )
                lp.write_text(t)
                print("avatar resolve soft")
            else:
                print("avatar pattern miss")
    print("LiveChat avatar ok")
else:
    print("skip LiveChat avatar")
print("patch_avatar_cross_browser done")
