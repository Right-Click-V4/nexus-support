#!/usr/bin/env python3
"""Store agent_id on chat messages so avatars resolve to the sender, not the viewer."""
from pathlib import Path

p = Path("src/context/PlatformContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    print("skip")
    raise SystemExit(0)

t = p.read_text()
if "MSG_AGENT_ID_V1" in t:
    print("already")
    raise SystemExit(0)

old = """    const msg: ChatMessage = {
      id: `m-${Date.now()}`,
      text,
      sender,
      created_at: new Date().toISOString(),
      author: opts?.agentName,
    };"""

new = """    // MSG_AGENT_ID_V1
    const msg: ChatMessage = {
      id: `m-${Date.now()}`,
      text,
      sender,
      created_at: new Date().toISOString(),
      author: opts?.agentName,
      agent_id: opts?.agentId || undefined,
    } as ChatMessage;"""

if old in t:
    t = t.replace(old, new)
    print("msg agent_id local")
else:
    print("local msg pattern miss")

if "author: opts?.agentName || null," in t and "agent_id: opts?.agentId" not in t:
    t = t.replace(
        "author: opts?.agentName || null,",
        "author: opts?.agentName || null,\n        agent_id: opts?.agentId || null,",
        1,
    )
    print("insert agent_id soft")

p.write_text(t)
print("done", len(t))
