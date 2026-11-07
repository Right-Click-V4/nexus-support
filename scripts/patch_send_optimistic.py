#!/usr/bin/env python3
from pathlib import Path
p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
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
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, body: text, sender, created_at: new Date().toISOString() } as ChatMessage;
    setConversations((prev) => {
      const exists = prev.some((c) => c.id === conversationId);
      if (!exists) {
        return [{ id: conversationId, customer_name: 'Customer', status: 'active' as const, preview: text.slice(0, 120), unread: sender === 'customer' ? 1 : 0, messages: [msg], created_at: new Date().toISOString(), updated_at: new Date().toISOString() }, ...prev];
      }
      return prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: text.slice(0, 120), status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0, updated_at: new Date().toISOString() } : c);
    });
    if (supabase) {
      const { error: insErr } = await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      if (insErr) console.error('sendChatMessage insert failed', insErr);
      await supabase.from('chat_conversations').update({ preview: text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      try { await refreshPlatform(); } catch (e) { console.error(e); }
    }
  };"""
if old in t:
    p.write_text(t.replace(old, new))
    print("send patched")
else:
    print("send pattern missing")

p = Path("src/components/LiveChatPage.tsx")
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
    print("poll patched")
else:
    print("poll skip")
