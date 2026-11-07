"""Chat sync V3: optimistic send, realtime, 2s poll, hard dedupe (no repeats)."""
from pathlib import Path
import re
p = Path("src/context/PlatformContext.tsx")
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
if "CHAT_SYNC_ALWAYS_V3" in s:
    print("already v3"); raise SystemExit(0)

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
    // CHAT_SYNC_ALWAYS_V3
    const now = new Date().toISOString();
    const msg: ChatMessage = { id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, text, sender, created_at: now };
    setConversations((prev) => prev.map((c) => {
      if (c.id !== conversationId) return c;
      const existing = c.messages || [];
      if (existing.some((x) => x.sender === sender && (x.text || '') === text && Math.abs(new Date(x.created_at || 0).getTime() - Date.now()) < 4000)) return c;
      return { ...c, messages: [...existing, msg], preview: text.slice(0, 120), status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0, updated_at: now };
    }));
    if (supabase) {
      try {
        await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
        await supabase.from('chat_conversations').update({ preview: text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: now }).eq('id', conversationId);
      } catch (e) { console.warn(e); }
      try { await refreshPlatform(); } catch (e) { console.warn(e); }
    }
  };"""

if old_send in s:
    s = s.replace(old_send, new_send, 1); print("send ok")
else:
    print("send skip")

old_merge = """    if (chats.data) {
      const messages = (msgs.data || []) as ChatMessage[];
      const byConv: Record<string, ChatMessage[]> = {};
      for (const m of messages) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }"""
new_merge = """    if (chats.data) {
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
if old_merge in s:
    s = s.replace(old_merge, new_merge, 1); print("merge ok")

old_set = """      setConversations(
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
        const norm = (mm: ChatMessage & { body?: string }) => ({ ...mm, text: (mm.text || mm.body || '').toString(), body: (mm.body || mm.text || '').toString() });
        const dedupe = (list: ChatMessage[]) => {
          const best = new Map<string, ChatMessage>();
          for (const m of list) {
            const key = `${m.sender}::${(m.text || m.body || '').toString().trim()}`;
            const prevM = best.get(key);
            if (!prevM) { best.set(key, m); continue; }
            const prevOpt = String(prevM.id || '').startsWith('m-');
            const curOpt = String(m.id || '').startsWith('m-');
            if (prevOpt && !curOpt) best.set(key, m);
            else if (prevOpt === curOpt && new Date(m.created_at || 0).getTime() >= new Date(prevM.created_at || 0).getTime()) best.set(key, m);
          }
          return Array.from(best.values()).sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime());
        };
        return (chats.data as ChatConversation[]).map((c) => {
          const prevMsgs = prevById[c.id]?.messages || [];
          const serverMsgs = byConv[c.id];
          let combined: ChatMessage[];
          if (messages) {
            const serverText = new Set((serverMsgs || []).map((m) => `${m.sender}::${(m.text || m.body || '').toString().trim()}`));
            const now = Date.now();
            const pending = prevMsgs.filter((m) => {
              if (!String(m.id || '').startsWith('m-')) return false;
              const t = (m.text || m.body || '').toString().trim();
              if (serverText.has(`${m.sender}::${t}`)) return false;
              const age = now - new Date(m.created_at || 0).getTime();
              return age >= 0 && age < 8000;
            });
            combined = [...(serverMsgs || []), ...pending];
          } else combined = serverMsgs || prevMsgs || [];
          return { ...c, messages: dedupe(combined.map(norm)) };
        });
      });"""
if old_set in s:
    s = s.replace(old_set, new_set, 1); print("set ok")
else:
    print("set skip")

old_poll = """  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 3000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);"""
new_poll = """  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    let chatChannel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      chatChannel = supabase.channel('nexus-chat-rt-v3')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_messages' }, () => { void refreshPlatform(); })
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_conversations' }, () => { void refreshPlatform(); })
        .subscribe((status) => { if (status === 'SUBSCRIBED') void refreshPlatform(); });
    } catch (err) { console.warn('chat realtime unavailable', err); }
    const id = window.setInterval(() => { void refreshPlatform(); }, 2000);
    return () => {
      window.clearInterval(id);
      try { if (chatChannel && supabase) void supabase.removeChannel(chatChannel); } catch {}
    };
  }, [refreshPlatform]);"""
if old_poll in s:
    s = s.replace(old_poll, new_poll, 1); print("poll ok")
else:
    print("poll skip")

p.write_text(s)
print("done", "CHAT_SYNC_ALWAYS_V3" in s)
