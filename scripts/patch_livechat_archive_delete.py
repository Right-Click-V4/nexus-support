#!/usr/bin/env python3
"""Live Chat banner, delete confirm, archive + 30d purge, fix delete API."""
from pathlib import Path
import re

lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists():
    t = lcp.read_text()
    if "livechat-archive-delete-v1" not in t:
        t = t.replace("startConversation,", "createChat,")
        t = t.replace("deleteConversation,", "deleteChat,\n    archiveChat,")
        if "Archive" not in t.split("lucide-react")[0]:
            t = t.replace(
                "ExternalLink } from 'lucide-react'",
                "ExternalLink, Archive } from 'lucide-react'",
            )
        if "confirmDeleteId" not in t:
            t = t.replace(
                "const [as, setAs] = useState<'agent' | 'customer'>('agent');\n  const bottomRef",
                "const [as, setAs] = useState<'agent' | 'customer'>('agent');\n"
                "  const [listTab, setListTab] = useState<'live' | 'archive'>('live');\n"
                "  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);\n"
                "  const [deleteBusy, setDeleteBusy] = useState(false);\n"
                "  const bottomRef",
            )
        t = re.sub(
            r"const id = await startConversation\(\{[\s\S]*?\}\);\s*setSelectedId\(id\);",
            "const conv = await createChat(newName.trim());\n      setSelectedId(conv.id);",
            t,
            count=1,
        )
        t = t.replace("await startConversation(", "await createChat(")
        t = t.replace("await deleteConversation(", "await deleteChat(")

        helpers = '''
  const requestDelete = (id: string) => setConfirmDeleteId(id);

  const confirmDelete = async () => {
    if (!confirmDeleteId) return;
    setDeleteBusy(true);
    try {
      await deleteChat(confirmDeleteId);
      if (selectedId === confirmDeleteId) setSelectedId(null);
      setConfirmDeleteId(null);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to delete chat');
    } finally {
      setDeleteBusy(false);
    }
  };

  const doArchive = async (id: string) => {
    setBusy(true);
    try {
      await archiveChat(id);
      setMsg('Chat archived. It will be removed automatically after 30 days.');
      if (selectedId === id) setSelectedId(null);
      setListTab('archive');
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to archive');
    } finally {
      setBusy(false);
    }
  };

  const liveChats = conversations.filter((c) => (c.status || '') !== 'archived');
  const archivedChats = conversations.filter((c) => (c.status || '') === 'archived');
  const list = listTab === 'archive' ? archivedChats : liveChats;
  const activeCount = liveChats.filter((c) => c.status !== 'ended').length;
'''
        if "const requestDelete" not in t:
            if re.search(r"const remove = async \(id: string\) => \{[\s\S]*?\n  \};", t):
                t = re.sub(r"const remove = async \(id: string\) => \{[\s\S]*?\n  \};", helpers.strip(), t, count=1)
            else:
                t = t.replace(
                    "\n  return (\n    <div className=\"space-y-3\">",
                    "\n" + helpers + "\n  return (\n    <div className=\"space-y-3\">",
                    1,
                )

        t = t.replace(
            '<div className="bg-brand-50 border border-brand-100 rounded-xl px-4 py-3 text-sm text-brand-800">\n'
            '        <strong>Chat \u2194 ticket:</strong> Convert a chat into a ticket, or open a linked ticket ID. Files use Supabase Storage when available.\n'
            '      </div>',
            '<div className="rounded-xl px-4 py-3 text-sm border border-violet-400/30 bg-violet-950/50 text-white">\n'
            '        <strong className="text-white">Chat \u2194 ticket:</strong>{" "}\n'
            '        <span className="text-violet-100">Convert a chat into a ticket, or open a linked ticket ID. Files use Supabase Storage when available.</span>\n'
            '      </div>',
        )

        old_h = (
            '          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between gap-2">\n'
            '            <span className="text-sm font-semibold text-slate-800">Live chats ({activeCount})</span>\n'
            '            <button type="button" onClick={() => setShowNew((v) => !v)} className="p-1.5 text-brand-600 hover:bg-white/5 rounded-lg" title="New chat">\n'
            '              <Plus size={16} />\n'
            '            </button>\n'
            '          </div>'
        )
        new_h = (
            '          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between gap-2">\n'
            '            <span className="text-sm font-semibold text-slate-800">\n'
            "              {listTab === 'archive' ? `Archive (${archivedChats.length})` : `Live chats (${activeCount})`}\n"
            '            </span>\n'
            '            <button type="button" onClick={() => setShowNew((v) => !v)} className="p-1.5 text-brand-600 hover:bg-white/5 rounded-lg" title="New chat">\n'
            '              <Plus size={16} />\n'
            '            </button>\n'
            '          </div>\n'
            '          <div className="px-3 py-2 border-b border-slate-200 flex gap-1">\n'
            "            <button type=\"button\" onClick={() => setListTab('live')} className={clsx('flex-1 text-xs py-1.5 rounded-lg font-medium', listTab === 'live' ? 'bg-brand-600 text-white' : 'text-slate-500 hover:bg-slate-100')}>Live</button>\n"
            "            <button type=\"button\" onClick={() => setListTab('archive')} className={clsx('flex-1 text-xs py-1.5 rounded-lg font-medium', listTab === 'archive' ? 'bg-brand-600 text-white' : 'text-slate-500 hover:bg-slate-100')}>Archive</button>\n"
            '          </div>'
        )
        if old_h in t:
            t = t.replace(old_h, new_h, 1)
        t = t.replace("conversations.map((c)", "list.map((c)", 1)
        t = t.replace("onClick={() => remove(selected.id)}", "onClick={() => requestDelete(selected.id)}")
        t = t.replace(
            """{selected.status === 'ended' && (
                    <button type="button" onClick={() => setChatStatus(selected.id, 'active')} className="inline-flex items-center gap-1 text-xs font-medium text-brand-600 px-2 py-1.5 rounded-lg hover:bg-white/5">
                      <RotateCcw size={14} /> Reopen
                    </button>
                  )}""",
            """{selected.status === 'ended' && (
                    <>
                      <button type="button" onClick={() => setChatStatus(selected.id, 'active')} className="inline-flex items-center gap-1 text-xs font-medium text-brand-600 px-2 py-1.5 rounded-lg hover:bg-white/5">
                        <RotateCcw size={14} /> Reopen
                      </button>
                      <button type="button" disabled={busy} onClick={() => void doArchive(selected.id)} className="inline-flex items-center gap-1 text-xs font-medium text-amber-500 px-2 py-1.5 rounded-lg hover:bg-white/5" title="Archive for 30 days">
                        <Archive size={14} /> Archive
                      </button>
                    </>
                  )}""",
        )
        if "confirmDeleteId &&" not in t and "confirmDeleteId ?" not in t:
            modal = '''
      {confirmDeleteId ? (
        <div className="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-black/50">
          <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-zinc-900/95 text-zinc-100 shadow-xl p-5 space-y-4">
            <div className="text-sm font-semibold text-white">Delete this chat?</div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              This permanently removes the conversation and all messages. Archived chats are auto-deleted after 30 days; this cannot be undone.
            </p>
            <div className="flex justify-end gap-2 pt-1">
              <button type="button" disabled={deleteBusy} onClick={() => setConfirmDeleteId(null)} className="px-3 py-1.5 text-xs rounded-lg border border-white/15 text-zinc-300 hover:bg-white/5">Cancel</button>
              <button type="button" disabled={deleteBusy} onClick={() => void confirmDelete()} className="px-3 py-1.5 text-xs rounded-lg bg-rose-600 text-white hover:bg-rose-500 disabled:opacity-50">
                {deleteBusy ? 'Deleting\u2026' : 'Delete permanently'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
'''
            t = t.replace("\n    </div>\n  );\n}", modal + "\n    </div>\n  );\n}", 1)
        t = re.sub(
            r"const selected = conversations\.find\(\(c\) => c\.id === selectedId\) \|\| null;\n  const activeCount = conversations\.filter\(\(c\) => c\.status !== 'ended'\)\.length;\n  const linkedTicket",
            "const selected = conversations.find((c) => c.id === selectedId) || null;\n  const linkedTicket",
            t,
            count=1,
        )
        t = "/* livechat-archive-delete-v1 */\n" + t
        lcp.write_text(t)
        print("LiveChatPage")

pc = Path("src/context/PlatformContext.tsx")
if pc.exists():
    p = pc.read_text()
    if "livechat-archive-api-v1" not in p:
        p = p.replace(
            "setChatStatus: (id: string, status: 'waiting' | 'active' | 'ended') => Promise<void>;",
            "setChatStatus: (id: string, status: 'waiting' | 'active' | 'ended' | 'archived') => Promise<void>;\n"
            "  archiveChat: (id: string) => Promise<void>;\n"
            "  linkTicketId: (conversationId: string, ticketId: string) => Promise<void>;",
        )
        old = (
            "  const setChatStatus = async (id: string, status: 'waiting' | 'active' | 'ended') => {\n"
            "    if (supabase) { await supabase.from('chat_conversations').update({ status }).eq('id', id); await refreshPlatform(); }\n"
            "    else setConversations((p) => p.map((c) => (c.id === id ? { ...c, status } : c)));\n"
            "  };\n"
            "  const deleteChat = async (id: string) => {\n"
            "    if (supabase) {\n"
            "      await supabase.from('chat_messages').delete().eq('conversation_id', id);\n"
            "      await supabase.from('chat_conversations').delete().eq('id', id);\n"
            "      await refreshPlatform();\n"
            "    } else setConversations((p) => p.filter((c) => c.id !== id));\n"
            "  };"
        )
        new = (
            "  const setChatStatus = async (id: string, status: 'waiting' | 'active' | 'ended' | 'archived') => {\n"
            "    if (supabase) {\n"
            "      const patch: Record<string, unknown> = { status, updated_at: new Date().toISOString() };\n"
            "      if (status === 'archived') patch.archived_at = new Date().toISOString();\n"
            "      const { error } = await supabase.from('chat_conversations').update(patch).eq('id', id);\n"
            "      if (error && status === 'archived') {\n"
            "        await supabase.from('chat_conversations').update({ status: 'archived', updated_at: new Date().toISOString() }).eq('id', id);\n"
            "      }\n"
            "      await refreshPlatform();\n"
            "    } else {\n"
            "      setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, status: status as ChatConversation['status'], updated_at: new Date().toISOString() } : c)));\n"
            "    }\n"
            "  };\n"
            "  const archiveChat = async (id: string) => { await setChatStatus(id, 'archived'); };\n"
            "  const deleteChat = async (id: string) => {\n"
            "    try {\n"
            "      if (supabase) {\n"
            "        await supabase.from('chat_messages').delete().eq('conversation_id', id);\n"
            "        const { error } = await supabase.from('chat_conversations').delete().eq('id', id);\n"
            "        if (error) console.error('deleteChat', error);\n"
            "        await refreshPlatform();\n"
            "      } else setConversations((prev) => prev.filter((c) => c.id !== id));\n"
            "    } catch (e) {\n"
            "      console.error('deleteChat', e);\n"
            "      throw e;\n"
            "    }\n"
            "  };\n"
            "  const linkTicketId = async (conversationId: string, ticketId: string) => {\n"
            "    if (supabase) {\n"
            "      await supabase.from('chat_conversations').update({ ticket_id: ticketId, updated_at: new Date().toISOString() }).eq('id', conversationId);\n"
            "      await refreshPlatform();\n"
            "    } else {\n"
            "      setConversations((prev) => prev.map((c) => (c.id === conversationId ? { ...c, ticket_id: ticketId } : c)));\n"
            "    }\n"
            "  };"
        )
        if old in p:
            p = p.replace(old, new, 1)
        p = p.replace(
            "createChat, sendChatMessage, setChatStatus, deleteChat,",
            "createChat, sendChatMessage, setChatStatus, archiveChat, deleteChat, linkTicketId,",
        )
        if "purge-archived-chats-v1" not in p:
            purge = (
                "      // purge-archived-chats-v1\n"
                "      try {\n"
                "        const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;\n"
                "        for (const c of (chats.data || []) as { id: string; status?: string; archived_at?: string; updated_at?: string }[]) {\n"
                "          if ((c.status || '').toLowerCase() !== 'archived') continue;\n"
                "          const ts = new Date(c.archived_at || c.updated_at || 0).getTime();\n"
                "          if (ts && ts < cutoff) {\n"
                "            await supabase.from('chat_messages').delete().eq('conversation_id', c.id);\n"
                "            await supabase.from('chat_conversations').delete().eq('id', c.id);\n"
                "          }\n"
                "        }\n"
                "      } catch { /* ignore */ }\n"
            )
            for marker in [
                "      setConversations(\n        (chats.data as ChatConversation[]).map",
                "      setConversations(\n      (chats.data as ChatConversation[]).map",
            ]:
                if marker in p:
                    p = p.replace(marker, purge + marker, 1)
                    break
        p = "/* livechat-archive-api-v1 */\n" + p
        pc.write_text(p)
        print("PlatformContext")

tp = Path("src/types.ts")
if tp.exists():
    tt = tp.read_text()
    if "'archived'" not in tt:
        tt = tt.replace(
            "status: 'open' | 'closed' | 'waiting' | 'active' | 'ended';",
            "status: 'open' | 'closed' | 'waiting' | 'active' | 'ended' | 'archived';\n  archived_at?: string;",
        )
        tp.write_text(tt)
        print("types")
print("done")
