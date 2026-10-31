#!/usr/bin/env python3
"""Status change republishes desk presence; Live Chat shows text||body; chat poll."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    t = tc.read_text()
    if "status-desk-publish-v1" not in t:
        if "deskPresence" not in t:
            t = t.replace(
                "from '../lib/supabase';",
                "from '../lib/supabase';\nimport { publishDeskPresence } from '../lib/deskPresence';",
                1,
            )
        needle = """    setCurrentAgent(next);
    setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    try {
      localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
    } catch { /* ignore */ }"""
        insert = """    setCurrentAgent(next);
    setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    if (status !== 'offline') {
      void publishDeskPresence({
        id: next.id,
        name: next.name || 'Agent',
        status: next.status || 'online',
        avatar_url: next.avatar_url,
        initials: next.initials,
        color: next.color,
      });
    }
    try {
      localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
    } catch { /* ignore */ }"""
        if needle in t:
            t = t.replace(needle, insert, 1)
        t = "/* status-desk-publish-v1 */\n" + t
        tc.write_text(t)
        print("tc")

lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists():
    l = lcp.read_text()
    if "chat-text-body-v1" not in l:
        l = l.replace("m.body", "(m.text || m.body || '')")
        l = l.replace(
            ".map((m) => `[${m.sender}] ${(m.text || m.body || '')}`)",
            ".map((m) => `[${m.sender}] ${m.text || m.body || ''}`)",
        )
        l = "/* chat-text-body-v1 */\n" + l
        lcp.write_text(l)
        print("lcp")

pc = Path("src/context/PlatformContext.tsx")
if pc.exists():
    p = pc.read_text()
    if "chat-sync-v1" not in p:
        p = p.replace(
            "await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });",
            "await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });",
            1,
        )
        if "}, [refreshAnnouncementsLight]);" in p and "refreshPlatform(); }, 3000)" not in p:
            p = p.replace(
                "}, [refreshAnnouncementsLight]);",
                """}, [refreshAnnouncementsLight]);

  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 3000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);
""",
                1,
            )
        p = p.replace(
            "messages: byConv[c.id] || c.messages || [],",
            """messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          })),""",
            1,
        )
        p = "/* chat-sync-v1 */\n" + p
        pc.write_text(p)
        print("pc")
print("done")
