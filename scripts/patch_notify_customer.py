#!/usr/bin/env python3
"""notifyCustomer helper + wire ticket updates and agent chat."""
from pathlib import Path
import re

p = Path("src/lib/agentNotify.ts")
c = p.read_text()
if "notifyCustomer" not in c:
    c += """

const CUSTOMER_KEY = 'nexus-customer-notif-v1';
const CUSTOMER_EVENT = 'nexus-customer-notify';

/** Notify a customer by email (local). link: mytickets | chat */
export async function notifyCustomer(payload: {
  email?: string | null;
  title: string;
  body: string;
  link?: string;
}) {
  const email = (payload.email || '').trim().toLowerCase();
  if (!email) return;
  const created_at = new Date().toISOString();
  const item = {
    id: uid(),
    customer_email: email,
    title: payload.title,
    body: payload.body,
    link: payload.link || 'mytickets',
    read: false,
    created_at,
  };
  try {
    const raw = localStorage.getItem(CUSTOMER_KEY);
    const prev = raw ? JSON.parse(raw) : [];
    const next = [item, ...(Array.isArray(prev) ? prev : [])].slice(0, 80);
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(next));
  } catch {}
  try {
    window.dispatchEvent(new CustomEvent(CUSTOMER_EVENT, { detail: item }));
  } catch {}
}
"""
    p.write_text(c)
    print("notifyCustomer ok")
else:
    print("agentNotify already")

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "notifyCustomer" not in c:
    c = c.replace(
        "import { notifyAgents } from '../lib/agentNotify';",
        "import { notifyAgents, notifyCustomer } from '../lib/agentNotify';",
        1,
    )
    m = re.search(
        r"void notifyAgents\(\{\s*title: 'Ticket updated',[\s\S]*?userId: \(assignee as Agent & \{ user_id\?: string \}\)\?\.user_id \|\| undefined,\s*\}\);",
        c,
    )
    if m:
        old = m.group(0)
        new = old + """
      if (ticket?.customer_email) {
        void notifyCustomer({
          email: ticket.customer_email,
          title: 'Ticket updated',
          body: `${ticket.title || id} was updated by support.`,
          link: 'mytickets',
        });
      }"""
        c = c.replace(old, new, 1)
        print("tc update ok")
    else:
        print("tc update miss")
    if "New reply on your ticket" not in c:
        marker = "title: 'Ticket reply'"
        idx = c.find(marker)
        if idx > 0:
            block_end = c.find("    }\n  };", idx)
            if block_end > 0:
                insert = """
      if (ticket.customer_email) {
        void notifyCustomer({
          email: ticket.customer_email,
          title: 'New reply on your ticket',
          body: ticket.title || ticketId,
          link: 'mytickets',
        });
      }"""
                c = c[:block_end] + insert + "\n" + c[block_end:]
                print("tc msg ok")
    tc.write_text(c)
else:
    print("tc already")

pc = Path("src/context/PlatformContext.tsx")
c = pc.read_text()
if "import type {\nimport { notifyCustomer }" in c:
    c = c.replace(
        "import type {\nimport { notifyCustomer } from '../lib/agentNotify';\n",
        "import { notifyCustomer } from '../lib/agentNotify';\nimport type {\n",
        1,
    )
    print("fixed broken import")

if "from '../lib/agentNotify'" not in c:
    c = c.replace(
        "import type {",
        "import { notifyCustomer } from '../lib/agentNotify';\nimport type {",
        1,
    )
    print("import added before type")

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
    const conv = conversations.find((x) => x.id === conversationId);
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
    }
    if (sender === 'agent' && conv?.customer_email) {
      void notifyCustomer({
        email: conv.customer_email,
        title: 'New live chat message',
        body: text.slice(0, 120),
        link: 'chat',
      });
    }
  };"""
if "sender === 'agent' && conv?.customer_email" not in c:
    if old in c:
        c = c.replace(old, new, 1)
        print("chat notify ok")
    else:
        print("chat notify miss")
else:
    print("chat already")

pc.write_text(c)
print("done")
