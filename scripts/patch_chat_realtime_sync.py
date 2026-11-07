"""Make live chat always sync: optimistic send + chat realtime + faster poll + safe merge."""
from pathlib import Path

p = Path('src/context/PlatformContext.tsx')
if not p.exists():
    print('PlatformContext.tsx missing')
    raise SystemExit(0)

s = p.read_text()
if 'nexus-chat-rt-v2' in s or 'CHAT_SYNC_ALWAYS_V2' in s:
    print('already patched v2')
    raise SystemExit(0)

old_send = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
    }
  };"""

new_send = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    // CHAT_SYNC_ALWAYS_V2
    const msg: ChatMessage = {
      id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      text,
      sender,
      created_at: new Date().toISOString(),
    };
    // Optimistic local update so sender sees the bubble immediately
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              messages: [...(c.messages || []), msg],
              preview: msg.text.slice(0, 120),
              status: 'active' as const,
              unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
              updated_at: new Date().toISOString(),
            }
          : c,
      ),
    );
    if (supabase) {
      try {
        await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
        await supabase
          .from('chat_conversations')
          .update({
            preview: msg.text.slice(0, 120),
            status: 'active',
            unread: sender === 'customer' ? 1 : 0,
            updated_at: new Date().toISOString(),
          })
          .eq('id', conversationId);
      } catch (err) {
        console.warn('sendChatMessage insert failed', err);
      }
      try {
        await refreshPlatform();
      } catch (err) {
        console.warn('sendChatMessage refresh failed', err);
      }
    }
  };"""

if old_send not in s:
    print('sendChatMessage pattern not found')
else:
    s = s.replace(old_send, new_send, 1)
    print('patched sendChatMessage')

old_merge = """    if (chats.data) {
      const messages = (msgs.data || []) as ChatMessage[];
      const byConv: Record<string, ChatMessage[]> = {};
      for (const m of messages) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }"""

new_merge = """    if (chats.data) {
      // Prefer server messages; if msgs query failed, keep prior message lists
      const messages = (msgs.data || null) as ChatMessage[] | null;
      const byConv: Record<string, ChatMessage[]> = {};
      if (messages) {
        for (const m of messages) {
          const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
          if (!cid) continue;
          if (!byConv[cid]) byConv[cid] = [];
          byConv[cid].push(m);
        }
      }"""

if old_merge not in s:
    print('merge pattern not found')
else:
    s = s.replace(old_merge, new_merge, 1)
    print('patched message merge safety')

old_set_orig = """      setConversations(
        (chats.data as ChatConversation[]).map((c) => ({
          ...c,
          messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          })),
        })),
      );"""

new_set = """      setConversations((prev) => {
        const prevById: Record<string, ChatConversation> = {};
        for (const c of prev) prevById[c.id] = c;
        return (chats.data as ChatConversation[]).map((c) => {
          const prevMsgs = prevById[c.id]?.messages || [];
          const serverMsgs = byConv[c.id];
          const raw = serverMsgs || (messages ? [] : prevMsgs) || [];
          const serverKeys = new Set(
            raw.map((m) => `${m.sender}|${(m.text || m.body || '').slice(0, 80)}|${(m.created_at || '').slice(0, 16)}`),
          );
          const temps = prevMsgs.filter((m) => {
            if (!String(m.id || '').startsWith('m-')) return false;
            const k = `${m.sender}|${(m.text || m.body || '').slice(0, 80)}|${(m.created_at || '').slice(0, 16)}`;
            return !serverKeys.has(k);
          });
          const merged = [...raw, ...temps].map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          }));
          merged.sort(
            (a, b) =>
              new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime(),
          );
          return { ...c, messages: merged };
        });
      });"""

if old_set_orig not in s:
    print('setConversations pattern not found')
else:
    s = s.replace(old_set_orig, new_set, 1)
    print('patched setConversations merge')

old_poll = """  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 3000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);"""

new_poll = """  // CHAT_SYNC_ALWAYS_V2 — dedicated chat realtime + 1.5s poll
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;

    let chatChannel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      chatChannel = supabase
        .channel('nexus-chat-rt-v2')
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'chat_messages' },
          () => {
            void refreshPlatform();
          },
        )
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'chat_conversations' },
          () => {
            void refreshPlatform();
          },
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            void refreshPlatform();
          }
        });
    } catch (err) {
      console.warn('chat realtime unavailable', err);
    }

    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 1500);

    return () => {
      window.clearInterval(id);
      try {
        if (chatChannel && supabase) void supabase.removeChannel(chatChannel);
      } catch {
        /* ignore */
      }
    };
  }, [refreshPlatform]);"""

if old_poll not in s:
    print('poll pattern not found')
else:
    s = s.replace(old_poll, new_poll, 1)
    print('patched poll + realtime')

p.write_text(s)
print('done', len(s))
