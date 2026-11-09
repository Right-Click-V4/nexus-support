#!/usr/bin/env python3
"""Force optimistic create/send + always-poll. Never uses realtime channels."""
from pathlib import Path
import re

NEW_SEND = r'''  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
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
  };'''

NEW_CREATE = r'''  const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {
    const payload: Record<string, unknown> = { customer_name, customer_email, status: 'waiting', preview: '', unread: 0 };
    if (meta?.branch) payload.branch = meta.branch;
    if (meta?.ticket_id) payload.ticket_id = meta.ticket_id;
    if (supabase) {
      const { data, error } = await supabase.from('chat_conversations').insert(payload).select('*').single();
      if (error || !data) {
        console.error('createChat primary insert', error);
        const { data: d2, error: e2 } = await supabase.from('chat_conversations').insert({ customer_name, customer_email, status: 'waiting' }).select('*').single();
        if (e2 || !d2) throw e2 || new Error('create chat failed');
        const conv = { ...(d2 as ChatConversation), messages: [] as ChatMessage[] };
        setConversations((prev) => (prev.some((x) => x.id === conv.id) ? prev : [conv, ...prev]));
        try { await refreshPlatform(); } catch (e) { console.error('createChat refresh', e); }
        return conv;
      }
      const conv = { ...(data as ChatConversation), messages: [] as ChatMessage[] };
      setConversations((prev) => (prev.some((x) => x.id === conv.id) ? prev : [conv, ...prev]));
      try { await refreshPlatform(); } catch (e) { console.error('createChat refresh', e); }
      return conv;
    }
    const c: ChatConversation = {
      id: `chat-${Date.now()}`,
      customer_name,
      customer_email,
      status: 'waiting',
      preview: '',
      unread: 0,
      messages: [],
      created_at: new Date().toISOString(),
      branch: meta?.branch,
      ticket_id: meta?.ticket_id,
    };
    setConversations((prev) => [c, ...prev]);
    return c;
  };'''

p = Path('src/context/PlatformContext.tsx')
if p.exists():
    t = p.read_text()

    if 'nexus-chat-rt' in t:
        t = re.sub(
            r"const client = supabase;\s*if \(!client\) return;\s*const chatCh = client\s*\.channel\('nexus-chat-rt'\)[\s\S]*?\.subscribe\(\);\s*",
            '',
            t,
        )
        t = re.sub(r"try \{ void client\.removeChannel\(chatCh\); \} catch \{[^\n]*\}\s*", '', t)
        print('stripped nexus-chat-rt')

    m = re.search(
        r"  const sendChatMessage = async \(conversationId: string, text: string, sender: 'agent' \| 'customer'\) => \{.*?\n  \};",
        t,
        re.S,
    )
    if m:
        t = t[: m.start()] + NEW_SEND + t[m.end() :]
        print('sendChatMessage replaced')
    else:
        print('WARN sendChatMessage not found')

    m = re.search(
        r"  const createChat = async \(customer_name: string, customer_email\?: string, meta\?: CreateChatMeta\) => \{.*?\n  \};",
        t,
        re.S,
    )
    if m:
        t = t[: m.start()] + NEW_CREATE + t[m.end() :]
        print('createChat replaced')
    else:
        print('WARN createChat not found')

    t = t.replace(
        "const id = window.setInterval(() => { void refreshPlatform(); }, 3000);",
        "const id = window.setInterval(() => { void refreshPlatform(); }, 1500);",
    )
    t = t.replace(
        "const id = window.setInterval(() => { void refreshPlatform(); }, 2000);",
        "const id = window.setInterval(() => { void refreshPlatform(); }, 1500);",
    )
    p.write_text(t)

p2 = Path('src/components/LiveChatPage.tsx')
if p2.exists():
    t2 = p2.read_text()
    t2 = re.sub(
        r"  useEffect\(\(\) => \{\n    if \(!selectedId\) return;\n    const id = window\.setInterval\(\(\) => \{\n      void refreshPlatform\(\);\n    \}, \d+\);\n    return \(\) => window\.clearInterval\(id\);\n  \}, \[selectedId, refreshPlatform\]\);",
        '''  useEffect(() => {
    void refreshPlatform();
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 1500);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);''',
        t2,
    )
    t2 = re.sub(
        r"  useEffect\(\(\) => \{\n    void refreshPlatform\(\);\n    const id = window\.setInterval\(\(\) => \{\n      void refreshPlatform\(\);\n    \}, \d+\);\n    return \(\) => window\.clearInterval\(id\);\n  \}, \[refreshPlatform\]\);",
        '''  useEffect(() => {
    void refreshPlatform();
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 1500);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);''',
        t2,
    )
    p2.write_text(t2)
    print('LiveChatPage poll forced')

p3 = Path('src/components/PortalLiveChatView.tsx')
if p3.exists():
    t3 = p3.read_text()
    if 'livechat-poll-v1' not in t3:
        t3 = t3.replace(
            '''  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);''',
            '''  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);

  /* livechat-poll-v1 */
  useEffect(() => {
    if (!chatId) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 1500);
    return () => window.clearInterval(id);
  }, [chatId, refreshPlatform]);''',
            1,
        )
        print('portal poll added')
    else:
        t3 = t3.replace('}, 2000);', '}, 1500);')
        print('portal poll already')
    p3.write_text(t3)

print('chat sync patch done')
