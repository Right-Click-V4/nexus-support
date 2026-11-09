#!/usr/bin/env python3
"""Optimistic chat send + always-poll. NO realtime channels (avoids subscribe/.on race)."""
from pathlib import Path
import re

p = Path('src/context/PlatformContext.tsx')
if p.exists():
    t = p.read_text()

    # Strip any broken nexus-chat-rt injection from prior deploys
    if 'nexus-chat-rt' in t:
        t = re.sub(
            r"const client = supabase;\s*"
            r"if \(!client\) return;\s*"
            r"const chatCh = client\s*"
            r"\.channel\('nexus-chat-rt'\)[\s\S]*?\.subscribe\(\);\s*",
            '',
            t,
        )
        t = re.sub(
            r"try \{ void client\.removeChannel\(chatCh\); \} catch \{[^\n]*\}\s*",
            '',
            t,
        )
        t = re.sub(
            r"try \{ void supabase\.removeChannel\(chatCh\); \} catch \{[^\n]*\}\s*",
            '',
            t,
        )
        t = re.sub(
            r"const chatCh = [^\n]*\n(?:.*\n)*?.*\.channel\('nexus-chat-rt'\)[\s\S]*?\.subscribe\(\);\s*",
            '',
            t,
        )
        print('stripped nexus-chat-rt')

    if 'Optimistic UI so sender sees message immediately' not in t:
        m = re.search(
            r"  const sendChatMessage = async \(conversationId: string, text: string, sender: 'agent' \| 'customer'\) => \{.*?\n  \};",
            t,
            re.S,
        )
        if m:
            new_send = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = {
      id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      conversation_id: conversationId,
      text,
      sender,
      created_at: new Date().toISOString(),
    } as ChatMessage;
    // Optimistic UI so sender sees message immediately
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
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          } as ChatConversation,
          ...prev,
        ];
      }
      return prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              messages: [...(c.messages || []), msg],
              preview: text.slice(0, 120),
              status: 'active' as const,
              unread: sender === 'customer' ? (c.unread || 0) + 1 : c.unread,
              updated_at: new Date().toISOString(),
            }
          : c,
      );
    });
    if (!supabase) return;
    try {
      let ins = await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, body: text, sender });
      if (ins.error) ins = await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      if (ins.error) ins = await supabase.from('chat_messages').insert({ conversation_id: conversationId, body: text, sender });
      if (ins.error) console.error('sendChatMessage insert failed', ins.error);
      await supabase.from('chat_conversations').update({ preview: text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      try { await refreshPlatform(); } catch (e) { console.error('sendChatMessage refresh', e); }
    } catch (e) {
      console.error('sendChatMessage', e);
    }
  };"""
            t = t[: m.start()] + new_send + t[m.end() :]
            print('send replaced')
        else:
            print('send regex miss')
    else:
        print('send already optimistic')

    t = t.replace(
        "const id = window.setInterval(() => { void refreshPlatform(); }, 3000);",
        "const id = window.setInterval(() => { void refreshPlatform(); }, 2000);",
    )
    p.write_text(t)

p2 = Path('src/components/LiveChatPage.tsx')
if p2.exists():
    t2 = p2.read_text()
    old = """  useEffect(() => {
    if (!selectedId) return;
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 4000);
    return () => window.clearInterval(id);
  }, [selectedId, refreshPlatform]);"""
    new = """  useEffect(() => {
    void refreshPlatform();
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 2000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);"""
    if old in t2:
        p2.write_text(t2.replace(old, new))
        print('livechat page poll')
    else:
        print('livechat page poll skip or already')

p3 = Path('src/components/PortalLiveChatView.tsx')
if p3.exists():
    t3 = p3.read_text()
    if 'livechat-poll-v1' not in t3:
        old = """  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);"""
        new = """  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);

  /* livechat-poll-v1 */
  useEffect(() => {
    if (!chatId) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 2000);
    return () => window.clearInterval(id);
  }, [chatId, refreshPlatform]);"""
        if old in t3:
            p3.write_text(t3.replace(old, new, 1))
            print('portal poll')
        else:
            print('portal marker miss')
    else:
        print('portal already')

print('chat sync patch done')
