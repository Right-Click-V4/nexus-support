#!/usr/bin/env python3
"""Fast live-chat sync: light refreshChats + optimistic send/create + 1s poll."""
from pathlib import Path
import re

p = Path('src/context/PlatformContext.tsx')
if not p.exists():
    raise SystemExit('no PlatformContext')

t = p.read_text()

if 'nexus-chat-rt' in t:
    t = re.sub(
        r"const client = supabase;\s*if \(!client\) return;\s*const chatCh = client\s*\.channel\('nexus-chat-rt'\)[\s\S]*?\.subscribe\(\);\s*",
        '',
        t,
    )
    t = re.sub(r"try \{ void client\.removeChannel\(chatCh\); \} catch \{[^\n]*\}\s*", '', t)
    print('stripped nexus-chat-rt')

if 'const refreshChats =' not in t and 'refreshChats-v1' not in t:
    marker = '  const refreshPlatform = useCallback(async () => {'
    if marker not in t:
        print('WARN no refreshPlatform marker')
    else:
        inject = '''  // refreshChats-v1: lightweight chats-only pull for live chat lag
  const refreshChats = useCallback(async () => {
    if (!isSupabaseConfigured || !supabase) return;
    try {
      const [chats, msgs] = await Promise.all([
        supabase.from('chat_conversations').select('*').order('updated_at', { ascending: false }),
        supabase.from('chat_messages').select('*').order('created_at', { ascending: true }),
      ]);
      if (chats.error) { console.error('refreshChats chats', chats.error); return; }
      if (msgs.error) console.error('refreshChats msgs', msgs.error);
      const messages = (msgs.data || []) as ChatMessage[];
      const byConv: Record<string, ChatMessage[]> = {};
      for (const m of messages) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }
      if (!chats.data) return;
      setConversations((prev) => {
        const fromDb = (chats.data as ChatConversation[]).map((c) => {
          const dbMsgs = (byConv[c.id] || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          }));
          const local = prev.find((x) => x.id === c.id);
          const localOnly = (local?.messages || []).filter(
            (lm) =>
              String(lm.id).startsWith('m-') &&
              !dbMsgs.some(
                (dm) => (dm.text || '') === (lm.text || '') && (dm.sender || '') === (lm.sender || ''),
              ),
          );
          return {
            ...c,
            messages: [...dbMsgs, ...localOnly].sort(
              (a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime(),
            ),
          };
        });
        const dbIds = new Set(fromDb.map((c) => c.id));
        const localOnlyConvs = prev.filter((c) => !dbIds.has(c.id) && String(c.id).startsWith('chat-'));
        return [...localOnlyConvs, ...fromDb];
      });
    } catch (e) {
      console.error('refreshChats', e);
    }
  }, []);

'''
        t = t.replace(marker, inject + marker, 1)
        print('refreshChats injected')

if 'purge-archived-chats-v1' in t:
    t = re.sub(
        r"\s*// purge-archived-chats-v1\s*try \{[\s\S]*?\} catch \{ /\* ignore \*/ \}\s*",
        '\n',
        t,
        count=1,
    )
    print('removed purge from hot path')

NEW_SEND = '''  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
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
      try { await refreshChats(); } catch { try { await refreshPlatform(); } catch (e) { console.error('sendChatMessage refresh', e); } }
    } catch (e) {
      console.error('sendChatMessage', e);
    }
  };'''

m = re.search(
    r"  const sendChatMessage = async \(conversationId: string, text: string, sender: 'agent' \| 'customer'\) => \{.*?\n  \};",
    t,
    re.S,
)
if m:
    t = t[: m.start()] + NEW_SEND + t[m.end() :]
    print('sendChatMessage replaced')
else:
    print('WARN send not found')

NEW_CREATE = '''  const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {
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
        try { await refreshChats(); } catch { try { await refreshPlatform(); } catch (e) { console.error('createChat refresh', e); } }
        return conv;
      }
      const conv = { ...(data as ChatConversation), messages: [] as ChatMessage[] };
      setConversations((prev) => (prev.some((x) => x.id === conv.id) ? prev : [conv, ...prev]));
      try { await refreshChats(); } catch { try { await refreshPlatform(); } catch (e) { console.error('createChat refresh', e); } }
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

m = re.search(
    r"  const createChat = async \(customer_name: string, customer_email\?: string, meta\?: CreateChatMeta\) => \{.*?\n  \};",
    t,
    re.S,
)
if m:
    t = t[: m.start()] + NEW_CREATE + t[m.end() :]
    print('createChat replaced')
else:
    print('WARN create not found')

t = t.replace(
    "const id = window.setInterval(() => { void refreshPlatform(); }, 3000);",
    "const id = window.setInterval(() => { void refreshPlatform(); }, 8000);",
)

if 'fast-chat-poll-v1' not in t:
    poll_effect = '''  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 8000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);'''
    alt = '''  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 3000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);'''
    fast = '''  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 8000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);

  /* fast-chat-poll-v1 */
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    void refreshChats();
    const id = window.setInterval(() => { void refreshChats(); }, 1000);
    return () => window.clearInterval(id);
  }, [refreshChats]);'''
    if poll_effect in t:
        t = t.replace(poll_effect, fast, 1)
        print('fast chat poll added')
    elif alt in t:
        t = t.replace(alt, fast, 1)
        print('fast chat poll added (from 3s)')
    else:
        t = t.replace(
            '}, [refreshPlatform]);',
            '''}, [refreshPlatform]);

  /* fast-chat-poll-v1 */
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    void refreshChats();
    const id = window.setInterval(() => { void refreshChats(); }, 1000);
    return () => window.clearInterval(id);
  }, [refreshChats]);''',
            1,
        )
        print('fast chat poll soft-inserted')

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
    }, 1000);
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
    }, 1000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);''',
        t2,
    )
    p2.write_text(t2)
    print('LiveChatPage 1s poll')

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
    const id = window.setInterval(() => { void refreshPlatform(); }, 1000);
    return () => window.clearInterval(id);
  }, [chatId, refreshPlatform]);''',
            1,
        )
        print('portal 1s poll')
    else:
        t3 = t3.replace('}, 2000);', '}, 1000);').replace('}, 1500);', '}, 1000);')
        print('portal poll interval 1s')
    p3.write_text(t3)

print('chat sync patch done')
