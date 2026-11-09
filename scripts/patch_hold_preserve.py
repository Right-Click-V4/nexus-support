#!/usr/bin/env python3
"""HOLD_PRESERVE_V1 — keep on_hold when agent sends; block customer send while held."""
from pathlib import Path

p = Path('src/context/PlatformContext.tsx')
if not p.exists():
    print('skip: no PlatformContext')
    raise SystemExit(0)
s = p.read_text()
if 'HOLD_PRESERVE_V1' in s:
    print('PlatformContext already HOLD_PRESERVE_V1')
else:
    old = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
    }
  };"""
    new = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    // HOLD_PRESERVE_V1 — never clear on_hold just because someone sent a message.
    const current = conversations.find((c) => c.id === conversationId);
    const curStatus = (current?.status || '').toLowerCase();
    if (curStatus === 'on_hold' && sender === 'customer') {
      return;
    }
    let nextStatus: ChatConversation['status'] = (current?.status as ChatConversation['status']) || 'active';
    if (curStatus === 'on_hold') {
      nextStatus = 'on_hold';
    } else if (curStatus === 'waiting' || !curStatus) {
      nextStatus = 'active';
    } else if (curStatus === 'ended' || curStatus === 'archived' || curStatus === 'closed') {
      nextStatus = 'active';
    } else {
      nextStatus = (current?.status as ChatConversation['status']) || 'active';
    }
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase
        .from('chat_conversations')
        .update({
          preview: msg.text.slice(0, 120),
          status: nextStatus,
          unread: sender === 'customer' ? 1 : 0,
          updated_at: new Date().toISOString(),
        })
        .eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === conversationId
            ? {
                ...c,
                messages: [...(c.messages || []), msg],
                preview: msg.text,
                status: nextStatus,
                unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
              }
            : c,
        ),
      );
    }
  };"""
    if old not in s:
        print('WARN: sendChatMessage pattern not found')
    else:
        p.write_text(s.replace(old, new, 1))
        print('PlatformContext HOLD_PRESERVE_V1 applied')

pv = Path('src/components/PortalLiveChatView.tsx')
if pv.exists():
    t = pv.read_text()
    if 'HOLD_PRESERVE_V1' in t and 'isOnHold) return' in t:
        print('PortalLiveChatView already guarded')
    else:
        t2 = t
        t2 = t2.replace(
            "if (!chatId || chatEnded) return;",
            "if (!chatId || chatEnded || isOnHold) return;",
            1,
        )
        t2 = t2.replace(
            "if (!file || !chatId) return;",
            "if (!file || !chatId || chatEnded || isOnHold) return;",
            1,
        )
        if t2 != t:
            t2 = t2.replace(
                "const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';",
                "const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold'; // HOLD_PRESERVE_V1",
                1,
            )
            pv.write_text(t2)
            print('PortalLiveChatView hold guards applied')
        else:
            print('WARN: PortalLiveChatView patterns not found')
else:
    print('skip PortalLiveChatView')
