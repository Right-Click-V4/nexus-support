#!/usr/bin/env python3
"""Expand chat select, normalize agent_id, replace claimChat with durable version."""
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    print("skip: PlatformContext missing/small")
    raise SystemExit(0)
t = p.read_text()

t2, n = re.subn(
    r"supabase\.from\('chat_conversations'\)\.select\('[^']+'\)\.order\('updated_at'",
    "supabase.from('chat_conversations').select('id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,assignee_id,ticket_id,branch,archived_at').order('updated_at'",
    t,
    count=1,
)
t = t2
print("select", n)

if "row.agent_id || row.assignee_id" not in t:
    old = """      setConversations(
        (chats.data as ChatConversation[]).map((c) => ({
          ...c,
          messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          })),
        })),
      );"""
    new = """      setConversations(
        (chats.data as ChatConversation[]).map((c) => {
          const row = c as ChatConversation & { assignee_id?: string };
          const agentId = row.agent_id || row.assignee_id || undefined;
          return {
            ...c,
            agent_id: agentId,
            messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
              ...mm,
              text: mm.text || mm.body || '',
              body: mm.body || mm.text || '',
            })),
          };
        }),
      );"""
    if old in t:
        t = t.replace(old, new)
        print("map ok")
    else:
        print("map pattern miss")

new_claim = r'''  const claimChat = async (conversationId: string, agentId: string) => {
    if (!agentId) return;
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              agent_id: agentId,
              status: (c.status === 'waiting' || c.status === 'on_hold' ? 'active' : c.status) as ChatConversation['status'],
            }
          : c,
      ),
    );
    if (!supabase) return;
    const now = new Date().toISOString();
    const attempts = [
      { agent_id: agentId, assignee_id: agentId, status: 'active', updated_at: now },
      { agent_id: agentId, status: 'active', updated_at: now },
      { assignee_id: agentId, status: 'active', updated_at: now },
      { agent_id: agentId, updated_at: now },
      { assignee_id: agentId, updated_at: now },
    ];
    let ok = false;
    for (const patch of attempts) {
      const { error } = await supabase.from('chat_conversations').update(patch).eq('id', conversationId);
      if (!error) {
        ok = true;
        break;
      }
    }
    if (!ok) {
      console.warn('claimChat: could not persist agent_id/assignee_id — keeping local claim');
      return;
    }
    try {
      const { data } = await supabase
        .from('chat_conversations')
        .select('id,agent_id,assignee_id,status')
        .eq('id', conversationId)
        .maybeSingle();
      if (data) {
        const row = data as { agent_id?: string; assignee_id?: string; status?: string };
        const resolved = row.agent_id || row.assignee_id || agentId;
        setConversations((prev) =>
          prev.map((c) =>
            c.id === conversationId
              ? { ...c, agent_id: resolved, status: (row.status || c.status) as ChatConversation['status'] }
              : c,
          ),
        );
      }
    } catch {
      /* keep optimistic */
    }
  };'''

m = re.search(r'  const claimChat = async \(conversationId: string, agentId: string\) => \{.*?\n  \};', t, re.S)
if m:
    t = t[: m.start()] + new_claim + t[m.end() :]
    print("claimChat replaced")
else:
    print("claimChat pattern miss")

p.write_text(t)
print("done", len(t))
