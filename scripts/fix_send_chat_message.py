#!/usr/bin/env python3
"""Repair sendChatMessage if assist patch corrupted the function signature."""
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
# Detect broken pattern: type params interrupted by if (sender
broken = (
    "opts?: {\n    // ASSIST_SEND_GUARD" in t
    or "opts?: {\n      // ASSIST_SEND_GUARD" in t
    or (
        "const sendChatMessage" in t
        and "if (sender === 'agent')" in t[t.find("const sendChatMessage") : t.find("const sendChatMessage") + 500]
        and "opts?: { agentId" not in t[t.find("const sendChatMessage") : t.find("const sendChatMessage") + 250]
    )
)
if not broken:
    print("sendChatMessage looks ok")
    raise SystemExit(0)

fixed = '''  const sendChatMessage = async (
    conversationId: string,
    text: string,
    sender: 'agent' | 'customer',
    opts?: { agentId?: string; agentName?: string },
  ) => {
    // ASSIST_SEND_GUARD_V1
    if (sender === 'agent') {
      const conv = conversations.find((c) => c.id === conversationId);
      const aid = opts?.agentId || user?.id || '';
      if (conv?.agent_id && aid && conv.agent_id !== aid) {
        const assistants = [...((conv as { assistant_ids?: string[] }).assistant_ids || [])];
        try {
          const raw = localStorage.getItem('nexus-chat-assist-' + conversationId);
          if (raw) {
            const parsed = JSON.parse(raw) as { assistants?: string[] };
            if (parsed.assistants) assistants.push(...parsed.assistants);
          }
        } catch {
          /* ignore */
        }
        if (!assistants.includes(aid)) {
          throw new Error('This chat is claimed by another agent. Request to Assist to join.');
        }
      }
    }
    const msg: ChatMessage = {
      id: `m-${Date.now()}`,
      text,
      sender,
      created_at: new Date().toISOString(),
      author: opts?.agentName,
    };
    if (supabase) {
      await supabase
        .from('chat_messages')
        .insert({ conversation_id: conversationId, text, sender, author: opts?.agentName || null });
      const _upd: Record<string, unknown> = {
        preview: msg.text.slice(0, 120),
        status: 'active',
        unread: sender === 'customer' ? 1 : 0,
        updated_at: new Date().toISOString(),
      };
      if (sender === 'agent' && (opts?.agentId || user?.id)) _upd.agent_id = opts?.agentId || user?.id;
      await supabase.from('chat_conversations').update(_upd).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === conversationId
            ? {
                ...c,
                messages: [...(c.messages || []), msg],
                preview: msg.text,
                status: 'active' as const,
                unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
                agent_id: sender === 'agent' && (opts?.agentId || user?.id) ? (opts?.agentId || user?.id) : c.agent_id,
              }
            : c,
        ),
      );
    }
  };'''

m = re.search(r"  const sendChatMessage = async[\s\S]*?\n  const setChatStatus = async", t)
if m:
    t = t[: m.start()] + fixed + "\n\n  const setChatStatus = async" + t[m.end() :]
    p.write_text(t)
    print("repaired sendChatMessage")
else:
    print("broken pattern suspected but block not found")
