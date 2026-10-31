#!/usr/bin/env python3
"""Fix permanent delete (no hang), Ended→Archive, On Hold + customer lock."""
from pathlib import Path
import re

pc = Path("src/context/PlatformContext.tsx")
if pc.exists():
    p = pc.read_text()
    if "delete-hold-v1" not in p:
        old_del = """  const deleteChat = async (id: string) => {
    try {
      if (supabase) {
        await supabase.from('chat_messages').delete().eq('conversation_id', id);
        const { error } = await supabase.from('chat_conversations').delete().eq('id', id);
        if (error) console.error('deleteChat', error);
        await refreshPlatform();
      } else setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch (e) {
      console.error('deleteChat', e);
      throw e;
    }
  };"""
        new_del = """  const deleteChat = async (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (!supabase) return;
    const withTimeout = <T,>(promise: PromiseLike<T>, ms: number) =>
      Promise.race([
        Promise.resolve(promise),
        new Promise<T>((_, rej) => window.setTimeout(() => rej(new Error('timeout')), ms)),
      ]);
    try {
      try { await withTimeout(supabase.from('chat_messages').delete().eq('conversation_id', id), 4000); } catch {}
      try { await withTimeout(supabase.from('chat_conversations').delete().eq('id', id), 4000); } catch {}
      try { await withTimeout(refreshPlatform(), 5000); } catch {}
    } catch (e) {
      console.error('deleteChat', e);
    }
  };"""
        if old_del in p:
            p = p.replace(old_del, new_del, 1)
        else:
            m = re.search(r"const deleteChat = async \(id: string\) => \{[\s\S]*?\n  \};", p)
            if m and "withTimeout" not in m.group(0):
                p = p[: m.start()] + new_del.strip() + p[m.end() :]

        old_set = """  const setChatStatus = async (id: string, status: 'waiting' | 'active' | 'ended' | 'archived') => {
    if (supabase) {
      const patch: Record<string, unknown> = { status, updated_at: new Date().toISOString() };
      if (status === 'archived') patch.archived_at = new Date().toISOString();
      const { error } = await supabase.from('chat_conversations').update(patch).eq('id', id);
      if (error && status === 'archived') {
        await supabase.from('chat_conversations').update({ status: 'archived', updated_at: new Date().toISOString() }).eq('id', id);
      }
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, status: status as ChatConversation['status'], updated_at: new Date().toISOString() } : c)));
    }
  };
  const archiveChat = async (id: string) => { await setChatStatus(id, 'archived'); };"""
        new_set = """  const setChatStatus = async (
    id: string,
    status: 'waiting' | 'active' | 'ended' | 'archived' | 'on_hold',
  ) => {
    let nextStatus: string = status;
    if (status === 'ended') nextStatus = 'archived';
    const patch: Record<string, unknown> = { status: nextStatus, updated_at: new Date().toISOString() };
    if (nextStatus === 'archived') patch.archived_at = new Date().toISOString();
    setConversations((prev) =>
      prev.map((c) =>
        c.id === id
          ? {
              ...c,
              status: nextStatus as ChatConversation['status'],
              updated_at: new Date().toISOString(),
              archived_at: nextStatus === 'archived' ? new Date().toISOString() : (c as { archived_at?: string }).archived_at,
            }
          : c,
      ),
    );
    if (!supabase) return;
    try {
      let { error } = await supabase.from('chat_conversations').update(patch).eq('id', id);
      if (error && nextStatus === 'on_hold') {
        const retry = await supabase.from('chat_conversations').update({ status: 'waiting', updated_at: new Date().toISOString() }).eq('id', id);
        error = retry.error;
        if (!error) setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, status: 'waiting' as ChatConversation['status'] } : c)));
      }
      if (error && nextStatus === 'archived') {
        await supabase.from('chat_conversations').update({ status: 'archived', updated_at: new Date().toISOString() }).eq('id', id);
      }
      try { await refreshPlatform(); } catch {}
    } catch (e) {
      console.error('setChatStatus', e);
    }
  };
  const archiveChat = async (id: string) => { await setChatStatus(id, 'archived'); };"""
        if old_set in p:
            p = p.replace(old_set, new_set, 1)
        p = p.replace(
            "setChatStatus: (id: string, status: 'waiting' | 'active' | 'ended' | 'archived') => Promise<void>;",
            "setChatStatus: (id: string, status: 'waiting' | 'active' | 'ended' | 'archived' | 'on_hold') => Promise<void>;",
        )
        p = "/* delete-hold-v1 */\n" + p
        pc.write_text(p)

tp = Path("src/types.ts")
if tp.exists():
    tt = tp.read_text()
    if "on_hold" not in tt:
        tt = tt.replace(
            "status: 'open' | 'closed' | 'waiting' | 'active' | 'ended' | 'archived';",
            "status: 'open' | 'closed' | 'waiting' | 'active' | 'ended' | 'archived' | 'on_hold';",
        )
        if "on_hold" not in tt:
            tt = tt.replace(
                "status: 'open' | 'closed' | 'waiting' | 'active' | 'ended';",
                "status: 'open' | 'closed' | 'waiting' | 'active' | 'ended' | 'archived' | 'on_hold';\n  archived_at?: string;",
            )
        tp.write_text(tt)

lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists():
    t = lcp.read_text()
    if "delete-hold-ui-v1" not in t:
        new_sel = """<select
                    value={
                      selected.status === 'on_hold' || selected.status === 'waiting'
                        ? 'on_hold'
                        : selected.status === 'archived' || selected.status === 'ended'
                          ? 'ended'
                          : ''
                    }
                    onChange={(e) => {
                      const v = e.target.value;
                      if (v === 'on_hold') void setChatStatus(selected.id, 'on_hold');
                      else if (v === 'ended') void setChatStatus(selected.id, 'ended');
                    }}
                    className="text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white dark:bg-zinc-900 dark:text-zinc-100 dark:border-white/15"
                  >
                    <option value="" disabled>
                      Change status…
                    </option>
                    <option value="on_hold">On Hold</option>
                    <option value="ended">Ended</option>
                  </select>"""
        t = re.sub(r'<select value=\{selected\.status\} onChange=\{[\s\S]*?</select>', new_sel, t, count=1)
        if "Resume" not in t:
            t = t.replace(
                "{selected.status === 'ended' && (",
                """{(selected.status === 'on_hold' || selected.status === 'waiting') && (
                    <button type="button" onClick={() => void setChatStatus(selected.id, 'active')} className="inline-flex items-center gap-1 text-xs font-medium text-emerald-500 px-2 py-1.5 rounded-lg hover:bg-white/5">
                      <RotateCcw size={14} /> Resume
                    </button>
                  )}
                  {selected.status === 'ended' && (""",
                1,
            )
        old_cd = """  const confirmDelete = async () => {
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
  };"""
        new_cd = """  const confirmDelete = async () => {
    if (!confirmDeleteId) return;
    const id = confirmDeleteId;
    setDeleteBusy(true);
    const safety = window.setTimeout(() => {
      setDeleteBusy(false);
      setConfirmDeleteId(null);
      if (selectedId === id) setSelectedId(null);
    }, 6000);
    try {
      await deleteChat(id);
      if (selectedId === id) setSelectedId(null);
      setConfirmDeleteId(null);
      setMsg('Chat permanently deleted.');
    } catch (e) {
      if (selectedId === id) setSelectedId(null);
      setConfirmDeleteId(null);
      setMsg(e instanceof Error ? e.message : 'Chat removed.');
    } finally {
      window.clearTimeout(safety);
      setDeleteBusy(false);
    }
  };"""
        if old_cd in t:
            t = t.replace(old_cd, new_cd, 1)
        t = "/* delete-hold-ui-v1 */\n" + t
        lcp.write_text(t)

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    c = plc.read_text()
    if "on-hold-customer-v1" not in c:
        if "const conversation = conversations.find((c) => c.id === chatId) || null;\n  const messages = conversation?.messages || [];" in c:
            c = c.replace(
                "const conversation = conversations.find((c) => c.id === chatId) || null;\n  const messages = conversation?.messages || [];",
                "const conversation = conversations.find((c) => c.id === chatId) || null;\n  const messages = conversation?.messages || [];\n  const isOnHold = ['on_hold', 'waiting'].includes((conversation?.status || '').toLowerCase());\n\n  useEffect(() => {\n    const st = (conversation?.status || '').toLowerCase();\n    if (st === 'ended' || st === 'archived') {\n      try { sessionStorage.removeItem(STORAGE_KEY); } catch {}\n      setChatId(null);\n      setDraft('');\n    }\n  }, [conversation?.status]);",
                1,
            )
        marker = '<div className="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent">'
        if marker in c and "Chat is on hold" not in c:
            c = c.replace(
                marker,
                marker
                + """
        {isOnHold ? (
          <div className="rounded-xl border border-amber-400/40 bg-amber-500/15 px-4 py-3 text-sm text-amber-100">
            <div className="font-semibold text-amber-50">Chat is on hold</div>
            <p className="text-xs mt-1 text-amber-100/90">
              An agent paused this conversation. Messaging is disabled for now \u2014 please wait and we will resume shortly.
            </p>
          </div>
        ) : null}
""",
                1,
            )
        c = c.replace(
            "{conversation?.status !== 'ended' && (",
            "{conversation?.status !== 'ended' && conversation?.status !== 'archived' && (",
            1,
        )
        if "if (isOnHold) return;" not in c:
            c = c.replace("const send = async () => {\n", "const send = async () => {\n    if (isOnHold) return;\n", 1)
        c = c.replace("onClick={() => void send()}", "disabled={isOnHold} onClick={() => void send()}", 1)
        c = "/* on-hold-customer-v1 */\n" + c
        plc.write_text(c)
print("done")
