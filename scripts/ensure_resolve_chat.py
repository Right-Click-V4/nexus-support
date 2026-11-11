#!/usr/bin/env python3
"""Ensure resolveChatAgent exists in LiveChatPage (prevents runtime 404 crash)."""
from pathlib import Path

p = Path("src/components/LiveChatPage.tsx")
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
if "function resolveChatAgent" in s:
    print("resolveChatAgent already present")
    raise SystemExit(0)
fn = """
function resolveChatAgent(
  c: { agent_id?: string } | null | undefined,
  agents: { id: string; name: string; avatar_url?: string | null; user_id?: string | null }[],
) {
  const aid = c?.agent_id;
  if (!aid) return null;
  return agents.find((a) => a.id === aid || a.user_id === aid) || null;
}

"""
if "export default function LiveChatPage" in s:
    s = s.replace("export default function LiveChatPage", fn + "export default function LiveChatPage", 1)
    p.write_text(s)
    print("injected resolveChatAgent")
else:
    print("LiveChatPage pattern not found")
