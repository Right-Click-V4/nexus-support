#!/usr/bin/env python3
"""Dry-run chat reliability: optimistic send, body fallback, merge, slower poll."""
from pathlib import Path
import re

p = Path('src/context/PlatformContext.tsx')
if not p.exists():
    print('skip: no PlatformContext')
    raise SystemExit(0)
s = p.read_text()

# 1) Poll 8s
s2 = s.replace(
    "const id = window.setInterval(() => { void refreshPlatform(); }, 3000);",
    "const id = window.setInterval(() => { void refreshPlatform(); }, 8000);",
)
if s2 != s:
    print('poll -> 8s')
    s = s2
else:
    print('poll skip')

# 2) sendChatMessage
pat = re.compile(
    r"  const sendChatMessage = async \(conversationId: string, text: string, sender: 'agent' \| 'customer'\) => \{.*?\n  \};\n\n  const setChatStatus",
    re.S,
)
new_send = r'''  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const now = new Date().toISOString();
    const msg: ChatMessage = {
      id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      text,
      sender,
      created_at: now,
    };
    setConversations((prev) => {
      const exists = prev.some((c) => c.id === conversationId);
      if (!exists) {
        return [
          {
            id: conversationId,
            customer_name: 'Customer',
            status: 'active' as const,
            preview: text.slice(0, 120),
            unread: sender === 'customer' ? 1 : 0,
            messages: [msg],
            created_at: now,
            updated_at: now,
          } as ChatConversation,
          ...prev,
        ];
      }
      return prev.map((c) => {
        if (c.id !== conversationId) return c;
        const existing = c.messages || [];
        if (
          existing.some(
            (x) =>
              x.sender === sender &&
              (x.text || '') === text &&
              Math.abs(new Date(x.created_at || 0).getTime() - Date.now()) < 4000,
          )
        ) {
          return c;
        }
        return {
          ...c,
          messages: [...existing, msg],
          preview: text.slice(0, 120),
          status: 'active' as const,
          unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
          updated_at: now,
        };
      });
    });
    if (!supabase) return;
    try {
      let ins = await supabase
        .from('chat_messages')
        .insert({ conversation_id: conversationId, text, body: text, sender });
      if (ins.error) {
        ins = await supabase
          .from('chat_messages')
          .insert({ conversation_id: conversationId, text, sender });
      }
      if (ins.error) console.warn('chat_messages insert', ins.error.message);
      await supabase
        .from('chat_conversations')
        .update({
          preview: text.slice(0, 120),
          status: 'active',
          unread: sender === 'customer' ? 1 : 0,
          updated_at: now,
        })
        .eq('id', conversationId);
    } catch (e) {
      console.warn('sendChatMessage', e);
    }
    try {
      await refreshPlatform();
    } catch (e) {
      console.warn('refresh after send', e);
    }
  };

  const setChatStatus'''

if pat.search(s):
    s = pat.sub(new_send, s, count=1)
    print('sendChatMessage ok')
else:
    print('sendChatMessage pattern miss')

# 3) Flag message select errors
if "chat_messages select failed" not in s:
    s = s.replace(
        "if (chats.data) {\n      const messages = (msgs.data || []) as ChatMessage[];",
        "if (chats.data) {\n      if (msgs.error) {\n        console.warn('chat_messages select failed', msgs.error.message);\n      }\n      const messages = (msgs.data || []) as ChatMessage[];",
        1,
    )
    print('msgs.error warn ok')

p.write_text(s)
print('written', p.stat().st_size)
