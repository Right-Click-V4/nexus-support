#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    raise SystemExit(0)
t = p.read_text()

fixed = """  const sendChatMessage = async (
    conversationId: string,
    text: string,
    sender: 'agent' | 'customer',
    opts?: { agentId?: string; agentName?: string },
  ) => {
    if (sender === 'agent') {
      const conv = conversations.find((c) => c.id === conversationId);
      const aid = opts?.agentId || user?.id || '';
      const claimedBy = conv?.agent_id;
      if (claimedBy && aid && claimedBy !== aid) {
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

    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              messages: [...(c.messages || []), msg],
              preview: msg.text,
              status: 'active' as const,
              unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
              agent_id:
                sender === 'agent' && (opts?.agentId || user?.id)
                  ? opts?.agentId || user?.id || c.agent_id
                  : c.agent_id,
            }
          : c,
      ),
    );

    if (!supabase) return;

    let insErr = (
      await supabase.from('chat_messages').insert({
        conversation_id: conversationId,
        text,
        sender,
        author: opts?.agentName || null,
      })
    ).error;
    if (insErr) {
      insErr = (
        await supabase.from('chat_messages').insert({
          conversation_id: conversationId,
          text,
          sender,
        })
      ).error;
    }
    if (insErr) {
      insErr = (
        await supabase.from('chat_messages').insert({
          conversation_id: conversationId,
          body: text,
          sender,
        })
      ).error;
    }
    if (insErr) console.warn('sendChatMessage insert', insErr.message);

    const _upd: Record<string, unknown> = {
      preview: msg.text.slice(0, 120),
      status: 'active',
      unread: sender === 'customer' ? 1 : 0,
      updated_at: new Date().toISOString(),
    };
    if (sender === 'agent' && (opts?.agentId || user?.id)) {
      _upd.agent_id = opts?.agentId || user?.id;
      _upd.assignee_id = opts?.agentId || user?.id;
    }
    const { error: upErr } = await supabase.from('chat_conversations').update(_upd).eq('id', conversationId);
    if (upErr) {
      await supabase
        .from('chat_conversations')
        .update({
          preview: msg.text.slice(0, 120),
          status: 'active',
          updated_at: new Date().toISOString(),
        })
        .eq('id', conversationId);
    }
  };

  const setChatStatus = async"""

m = re.search(r"  const sendChatMessage = async[\s\S]*?\n  const setChatStatus = async", t)
if m:
    t = t[: m.start()] + fixed + t[m.end() :]
    p.write_text(t)
    print("sendChatMessage rewritten", len(t))
else:
    print("sendChatMessage block not found")
