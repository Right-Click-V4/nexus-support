#!/usr/bin/env python3
"""Add chat realtime + ascending message order + light optimistic updates to PlatformContext.
Runs AFTER slow_polls so it must fix any order/paren issues left by that script.
"""
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    print("skip: no PlatformContext")
    raise SystemExit(0)
t = p.read_text()

# Fix any broken paren from previous patches: )).limit -> ).limit
t2, n = re.subn(r"\)\)\.limit\(", ").limit(", t)
t = t2
if n:
    print("fixed extra paren", n)

# Force chat_messages ascending (Messenger style) regardless of what slow_polls did
t2, n = re.subn(
    r"from\('chat_messages'\)\.select\([^)]*\)\.order\('created_at',\s*\{\s*ascending:\s*(?:true|false)\s*\}",
    "from('chat_messages').select('id,conversation_id,sender,text,body,created_at').order('created_at', { ascending: true })",
    t,
)
t = t2
print("db order ascending", n)

# Also ensure .limit(200) is present after order
t = re.sub(
    r"from\('chat_messages'\)\.select\('id,conversation_id,sender,text,body,created_at'\)\.order\('created_at', \{ ascending: true \}\)(?!\.limit)",
    "from('chat_messages').select('id,conversation_id,sender,text,body,created_at').order('created_at', { ascending: true }).limit(200)",
    t,
)

# Strip non-existent automations.actions column
t = t.replace(
    "action,action_value,actions,description",
    "action,action_value,description",
)

# Messenger-style sort in byConv
if "Messenger-style" not in t:
    old = """      for (const m of messages) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }"""
    new = """      for (const m of messages) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }
      // Messenger-style: oldest first, newest at bottom
      for (const cid of Object.keys(byConv)) {
        byConv[cid].sort((a, b) => {
          const ta = new Date(a.created_at || 0).getTime();
          const tb = new Date(b.created_at || 0).getTime();
          return ta - tb;
        });
      }"""
    if old in t:
        t = t.replace(old, new)
        print("sort ok")
    else:
        print("sort pattern miss")

# CHAT_REALTIME_V1
if "CHAT_REALTIME_V1" not in t and "nexus-chat-rt" not in t:
    markers = [
        """  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 180000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);""",
        """  useEffect(() => {
    if (!isSupabaseConfigured) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 3000);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);""",
    ]
    chat_rt = """

  // CHAT_REALTIME_V1 — new chats + messages without full page refresh
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    let alive = true;
    let debounce: number | null = null;
    const kick = () => {
      if (debounce != null) window.clearTimeout(debounce);
      debounce = window.setTimeout(() => {
        if (alive) void refreshPlatform();
      }, 200);
    };
    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      channel = supabase
        .channel('nexus-chat-rt')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_conversations' }, () => kick())
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_messages' }, () => kick())
        .subscribe();
    } catch (err) {
      console.warn('chat realtime unavailable', err);
    }
    const poll = window.setInterval(() => {
      if (alive) void refreshPlatform();
    }, 5000);
    return () => {
      alive = false;
      if (debounce != null) window.clearTimeout(debounce);
      window.clearInterval(poll);
      try {
        if (channel && supabase) void supabase.removeChannel(channel);
      } catch {
        /* ignore */
      }
    };
  }, [refreshPlatform]);"""
    applied = False
    for marker in markers:
        if marker in t:
            t = t.replace(marker, marker + chat_rt)
            print("realtime ok")
            applied = True
            break
    if not applied:
        print("realtime marker miss")

# Optimistic create
if "OPTIMISTIC_CHAT_V1" not in t:
    old_c = """      await refreshPlatform();
      return data as ChatConversation;"""
    new_c = """      // OPTIMISTIC_CHAT_V1
      setConversations((prev) => {
        const exists = prev.some((c) => c.id === (data as ChatConversation).id);
        if (exists) return prev;
        return [{ ...(data as ChatConversation), messages: [] }, ...prev];
      });
      await refreshPlatform();
      return data as ChatConversation;"""
    if old_c in t:
        t = t.replace(old_c, new_c, 1)
        print("optimistic create ok")

p.write_text(t)
print("done", len(t), "has RT", "CHAT_REALTIME_V1" in t or "nexus-chat-rt" in t)
