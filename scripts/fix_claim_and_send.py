#!/usr/bin/env python3
"""Normalize agent_id from assignee_id; expand chat select columns."""
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    raise SystemExit(0)
t = p.read_text()

t2 = re.sub(
    r"supabase\.from\('chat_conversations'\)\.select\('[^']+'\)\.order\('updated_at'",
    "supabase.from('chat_conversations').select('id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,assignee_id,ticket_id,branch,archived_at').order('updated_at'",
    t,
    count=1,
)
if t2 != t:
    t = t2
    print("select expanded")

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
        print("map normalized")

p.write_text(t)
print("fix_claim_and_send done", len(t))
