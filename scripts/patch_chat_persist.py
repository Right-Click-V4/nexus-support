#!/usr/bin/env python3
"""Persist deleted/archived chat IDs across refresh; On Hold \u2194 Resume toggle."""
from pathlib import Path
import re

pc = Path("src/context/PlatformContext.tsx")
if pc.exists():
    p = pc.read_text()
    if "chat-persist-overrides-v1" not in p:
        helper = r'''
const CHAT_DELETED_KEY = 'nexus-chat-deleted-v1';
const CHAT_ARCHIVED_KEY = 'nexus-chat-archived-v1';

function readChatDeleted(): Set<string> {
  try {
    const raw = localStorage.getItem(CHAT_DELETED_KEY);
    const arr = raw ? (JSON.parse(raw) as string[]) : [];
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}
function writeChatDeleted(ids: Set<string>) {
  try {
    localStorage.setItem(CHAT_DELETED_KEY, JSON.stringify([...ids]));
  } catch { /* ignore */ }
}
function readChatArchived(): Record<string, string> {
  try {
    const raw = localStorage.getItem(CHAT_ARCHIVED_KEY);
    const obj = raw ? JSON.parse(raw) : {};
    return obj && typeof obj === 'object' ? obj : {};
  } catch {
    return {};
  }
}
function writeChatArchived(map: Record<string, string>) {
  try {
    localStorage.setItem(CHAT_ARCHIVED_KEY, JSON.stringify(map));
  } catch { /* ignore */ }
}
function markChatDeleted(id: string) {
  const s = readChatDeleted();
  s.add(id);
  writeChatDeleted(s);
  const arch = readChatArchived();
  if (arch[id]) {
    delete arch[id];
    writeChatArchived(arch);
  }
}
function markChatArchived(id: string) {
  const arch = readChatArchived();
  arch[id] = new Date().toISOString();
  writeChatArchived(arch);
}
function clearChatArchived(id: string) {
  const arch = readChatArchived();
  if (arch[id]) {
    delete arch[id];
    writeChatArchived(arch);
  }
}
'''
        p = p.replace(
            "export function PlatformProvider",
            helper + "\nexport function PlatformProvider",
            1,
        )
        new_block = """{
        const deleted = readChatDeleted();
        const archivedMap = readChatArchived();
        const rows = (chats.data as ChatConversation[])
          .filter((c) => c?.id && !deleted.has(String(c.id)))
          .map((c) => {
            const id = String(c.id);
            const forceArchived = !!archivedMap[id];
            const st = forceArchived
              ? 'archived'
              : (c.status === 'ended' ? 'archived' : c.status);
            return {
              ...c,
              status: st as ChatConversation['status'],
              archived_at: forceArchived
                ? archivedMap[id]
                : (c as { archived_at?: string }).archived_at,
              messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
                ...mm,
                text: mm.text || mm.body || '',
                body: mm.body || mm.text || '',
              })),
            };
          });
        setConversations(rows);
      }"""
        m = re.search(
            r"setConversations\(\s*\(chats\.data as ChatConversation\[\]\)\.map\([\s\S]{20,900}?\)\s*\);",
            p,
        )
        if m:
            p = p[: m.start()] + new_block + p[m.end() :]
        p = p.replace(
            "const deleteChat = async (id: string) => {\n    setConversations((prev) => prev.filter((c) => c.id !== id));",
            "const deleteChat = async (id: string) => {\n    markChatDeleted(id);\n    setConversations((prev) => prev.filter((c) => c.id !== id));",
            1,
        )
        if "markChatArchived(id)" not in p:
            p = p.replace(
                "if (status === 'ended') nextStatus = 'archived';",
                "if (status === 'ended') nextStatus = 'archived';\n    if (nextStatus === 'archived') markChatArchived(id);\n    if (status === 'active' || nextStatus === 'active') clearChatArchived(id);",
                1,
            )
        p = "/* chat-persist-overrides-v1 */\n" + p
        pc.write_text(p)

lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists():
    t = lcp.read_text()
    if "hold-resume-toggle-v1" not in t:
        new_controls = """{/* hold-resume-toggle-v1 */}
                  {(selected.status === 'on_hold' || selected.status === 'waiting') ? (
                    <button
                      type="button"
                      onClick={() => void setChatStatus(selected.id, 'active')}
                      className="inline-flex items-center gap-1 text-xs font-medium text-white bg-emerald-600 px-2.5 py-1.5 rounded-lg hover:bg-emerald-500"
                    >
                      <RotateCcw size={14} /> Resume
                    </button>
                  ) : selected.status !== 'archived' && selected.status !== 'ended' ? (
                    <button
                      type="button"
                      onClick={() => void setChatStatus(selected.id, 'on_hold')}
                      className="inline-flex items-center gap-1 text-xs font-medium text-amber-950 bg-amber-400 px-2.5 py-1.5 rounded-lg hover:bg-amber-300"
                    >
                      On Hold
                    </button>
                  ) : null}
                  {selected.status !== 'archived' && selected.status !== 'ended' ? (
                    <button
                      type="button"
                      onClick={() => void setChatStatus(selected.id, 'ended')}
                      className="inline-flex items-center gap-1 text-xs font-medium text-zinc-200 border border-white/20 px-2.5 py-1.5 rounded-lg hover:bg-white/5"
                    >
                      End chat
                    </button>
                  ) : (
                    <span className="text-[11px] text-zinc-400 px-1">Archived</span>
                  )}"""
        t2 = re.sub(r'<select[\s\S]*?</select>', new_controls, t, count=1)
        if t2 != t:
            t = t2
        t = t.replace(
            "const liveChats = conversations.filter((c) => (c.status || '') !== 'archived');",
            "const liveChats = conversations.filter((c) => { const s = (c.status || '').toLowerCase(); return s !== 'archived' && s !== 'ended'; });",
        )
        t = t.replace(
            "const archivedChats = conversations.filter((c) => (c.status || '') === 'archived');",
            "const archivedChats = conversations.filter((c) => { const s = (c.status || '').toLowerCase(); return s === 'archived' || s === 'ended'; });",
        )
        t = "/* hold-resume-toggle-v1 */\n" + t
        lcp.write_text(t)
print("done")
