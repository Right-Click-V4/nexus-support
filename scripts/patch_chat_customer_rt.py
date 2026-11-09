"""Remove customer End chat; optimistic + faster realtime message sync."""
from pathlib import Path
import re

plv = Path('src/components/PortalLiveChatView.tsx')
if plv.exists():
    s = plv.read_text()
    if 'NO_CUSTOMER_END_V1' not in s:
        s = re.sub(
            r'\n  const endChat = async \(\) => \{.*?\n  \};\n',
            '\n  /* NO_CUSTOMER_END_V1 — only agents end chats */\n',
            s,
            count=1,
            flags=re.S,
        )
        s = s.replace('  const [ending, setEnding] = useState(false);\n', '')
        s = re.sub(
            r'\n\s*<button\n\s*type="button"\n\s*disabled=\{ending\}.*?\{ending \? \'Ending…\' : \'End / new chat\'\}\n\s*</button>',
            '',
            s,
            count=1,
            flags=re.S,
        )
        if 'CHAT_POLL_FAST_V1' not in s and 'void refreshPlatform();\n  }, [refreshPlatform]);' in s:
            s = s.replace(
                '''  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);''',
                '''  useEffect(() => {
    void refreshPlatform();
    // CHAT_POLL_FAST_V1 — keep messages live without tab switch
    const id = window.setInterval(() => { void refreshPlatform(); }, 1200);
    const onVis = () => { if (document.visibilityState === 'visible') void refreshPlatform(); };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('focus', onVis);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('focus', onVis);
    };
  }, [refreshPlatform]);''',
                1,
            )
        plv.write_text(s)
        print('PLV end removed')
    else:
        print('PLV already')
else:
    print('PLV missing')

pc = Path('src/context/PlatformContext.tsx')
if pc.exists():
    s = pc.read_text()
    if 'CHAT_RT_V5' not in s:
        old_send = '''  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
    }
  };'''
        new_send = '''  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    // CHAT_RT_V5 — optimistic UI always, then sync from server
    const msg: ChatMessage = { id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, text, sender, created_at: new Date().toISOString() };
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
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        const bc = new BroadcastChannel('nexus-chat-rt');
        bc.postMessage({ type: 'chat-message', conversationId, msg });
        bc.close();
      }
    } catch {}
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
      } catch (e) {
        console.error('sendChatMessage insert', e);
      }
      try {
        await refreshPlatform();
      } catch {}
    }
  };'''
        if old_send in s:
            s = s.replace(old_send, new_send, 1)
            print('optimistic send')
        if "setInterval(() => { void refreshPlatform(); }, 3000);" in s:
            s = s.replace(
                "setInterval(() => { void refreshPlatform(); }, 3000);",
                "setInterval(() => { void refreshPlatform(); }, 1500); // CHAT_RT_V5 faster poll",
                1,
            )
        poll_snip = "setInterval(() => { void refreshPlatform(); }, 1500); // CHAT_RT_V5 faster poll"
        poll_snip2 = "setInterval(() => { void refreshPlatform(); }, 3000);"
        extra = '''

  // CHAT_RT_V5 — realtime + cross-tab so messages appear without switching tabs
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      channel = supabase
        .channel('nexus-chat-rt-channel')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_messages' }, () => {
          void refreshPlatform();
        })
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_conversations' }, () => {
          void refreshPlatform();
        })
        .subscribe();
    } catch (err) {
      console.warn('chat realtime unavailable', err);
    }
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-chat-rt');
      bc.onmessage = () => { void refreshPlatform(); };
    } catch {}
    const onVis = () => {
      if (document.visibilityState === 'visible') void refreshPlatform();
    };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('focus', onVis);
    return () => {
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('focus', onVis);
      try { bc?.close(); } catch {}
      if (channel && supabase) void supabase.removeChannel(channel);
    };
  }, [refreshPlatform]);'''
        for snip in (poll_snip, poll_snip2):
            if snip in s and 'nexus-chat-rt-channel' not in s:
                idx = s.find(snip)
                end = s.find('}, [refreshPlatform]);', idx)
                if end != -1:
                    end = end + len('}, [refreshPlatform]);')
                    s = s[:end] + extra + s[end:]
                    print('chat realtime effect')
                    break
        old_map = '''      setConversations(
        (chats.data as ChatConversation[]).map((c) => ({
          ...c,
          messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          })),
        })),
      );'''
        new_map = '''      setConversations((prev) => {
        const prevById = new Map(prev.map((c) => [c.id, c]));
        return (chats.data as ChatConversation[]).map((c) => {
          const serverMsgs = (byConv[c.id] || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          }));
          const local = prevById.get(c.id);
          const temps = (local?.messages || []).filter((m) => {
            const id = String(m.id || '');
            if (!id.startsWith('m-')) return false;
            const key = `${m.sender}|${(m.text || '').slice(0, 80)}`;
            return !serverMsgs.some((sm) => `${sm.sender}|${(sm.text || '').slice(0, 80)}` === key);
          });
          const merged = [...serverMsgs, ...temps].sort(
            (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
          );
          return { ...c, messages: merged };
        });
      });'''
        if old_map in s:
            s = s.replace(old_map, new_map, 1)
            print('merge dedupe')
        pc.write_text(s)
        print('PC written')
    else:
        print('PC already')
else:
    print('PC missing')

lcp = Path('src/components/LiveChatPage.tsx')
if lcp.exists():
    s = lcp.read_text()
    if 'AGENT_CHAT_POLL_V1' not in s:
        old = '''  useEffect(() => {
    if (!selectedId) return;
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 4000);
    return () => window.clearInterval(id);
  }, [selectedId, refreshPlatform]);'''
        new = '''  useEffect(() => {
    if (!selectedId) return;
    // AGENT_CHAT_POLL_V1
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 1200);
    const onVis = () => { if (document.visibilityState === 'visible') void refreshPlatform(); };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('focus', onVis);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('focus', onVis);
    };
  }, [selectedId, refreshPlatform]);'''
        if old in s:
            lcp.write_text(s.replace(old, new, 1))
            print('LCP 4000->1200')
        else:
            print('LCP pattern miss')
    else:
        print('LCP already')
else:
    print('LCP missing')

print('DONE')
