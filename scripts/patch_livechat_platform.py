#!/usr/bin/env python3
from pathlib import Path

# SystemAppCore heartbeat
p = Path('src/SystemAppCore.tsx')
if p.exists():
    t = p.read_text()
    i = t.find('void touchPresence')
    if i >= 0:
        c = t[i:i + 900]
        c2 = c.replace('90_000', '30_000', 1)
        if c2 != c:
            p.write_text(t[:i] + c2 + t[i + 900:])
            print('heartbeat 30s')

# LiveChatPage always poll
p = Path('src/components/LiveChatPage.tsx')
if p.exists():
    t = p.read_text()
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
    }, 2500);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);"""
    if old in t:
        p.write_text(t.replace(old, new))
        print('poll fixed')
    else:
        print('poll skip')

# PlatformContext
p = Path('src/context/PlatformContext.tsx')
t = p.read_text()
changed = False

if 'nexus-livechat-rt' not in t:
    marker = "  useEffect(() => {\n    if (!isSupabaseConfigured) return;\n    const id = window.setInterval(() => { void refreshPlatform(); }, 3000);"
    insert = """  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      channel = supabase
        .channel('nexus-livechat-rt')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_conversations' }, () => { void refreshPlatform(); })
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_messages' }, () => { void refreshPlatform(); })
        .subscribe();
    } catch (err) { console.warn('livechat realtime unavailable', err); }
    return () => { try { if (channel && supabase) void supabase.removeChannel(channel); } catch {} };
  }, [refreshPlatform]);

"""
    if marker in t:
        t = t.replace(marker, insert + marker, 1)
        changed = True
        print('realtime ok')
    else:
        print('no interval marker')

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
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    setConversations((prev) => {
      const exists = prev.some((c) => c.id === conversationId);
      if (!exists) {
        return [{ id: conversationId, customer_name: 'Customer', status: 'active' as const, preview: msg.text.slice(0, 120), unread: sender === 'customer' ? 1 : 0, messages: [msg], created_at: new Date().toISOString(), updated_at: new Date().toISOString() }, ...prev];
      }
      return prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text.slice(0, 120), status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0, updated_at: new Date().toISOString() } : c);
    });
    if (supabase) {
      const { error: insErr } = await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      if (insErr) console.error('sendChatMessage insert', insErr);
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      try { await refreshPlatform(); } catch (e) { console.error(e); }
    }
  };"""
if old in t:
    t = t.replace(old, new)
    changed = True
    print('send ok')
else:
    print('send skip')

old_c = """      const { data, error } = await supabase.from('chat_conversations').insert(payload).select('*').single();
      if (error || !data) {
        const { data: d2, error: e2 } = await supabase.from('chat_conversations').insert({ customer_name, customer_email, status: 'waiting' }).select('*').single();
        if (e2 || !d2) throw e2 || new Error('create chat failed');
        await refreshPlatform();
        return d2 as ChatConversation;
      }
      await refreshPlatform();
      return data as ChatConversation;"""
new_c = """      const { data, error } = await supabase.from('chat_conversations').insert(payload).select('*').single();
      if (error || !data) {
        console.error('createChat', error);
        const { data: d2, error: e2 } = await supabase.from('chat_conversations').insert({ customer_name, customer_email, status: 'waiting' }).select('*').single();
        if (e2 || !d2) throw e2 || new Error('create chat failed');
        const conv = { ...(d2 as ChatConversation), messages: [] as ChatMessage[], branch: meta?.branch, ticket_id: meta?.ticket_id };
        setConversations((p) => [conv, ...p.filter((c) => c.id !== conv.id)]);
        try { await refreshPlatform(); } catch {}
        return conv;
      }
      const conv = { ...(data as ChatConversation), messages: [] as ChatMessage[], branch: meta?.branch || (data as ChatConversation).branch, ticket_id: meta?.ticket_id || (data as ChatConversation).ticket_id };
      setConversations((p) => [conv, ...p.filter((c) => c.id !== conv.id)]);
      try { await refreshPlatform(); } catch {}
      return conv;"""
if old_c in t:
    t = t.replace(old_c, new_c)
    changed = True
    print('create ok')
else:
    print('create skip')

if changed:
    p.write_text(t)
print('platform done', changed)
