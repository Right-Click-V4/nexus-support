/* hold-resume-toggle-v1 */
/* delete-hold-ui-v1 */
/* livechat-archive-delete-v1 */
/* chat-text-body-v1 */
/* chat-viewer-publish-v1 */
/* livechat-text-field-v1 */
import { useState, useEffect, useRef } from 'react';
import clsx from 'clsx';
import { Send, Plus, Trash2, UserRound, RotateCcw, Paperclip, Ticket, ExternalLink, Archive } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import { useTickets } from '../context/TicketContext';
import { publishChatViewer, clearChatViewer } from '../lib/chatPresence';
import { uploadAttachment } from '../lib/storage';

export default function LiveChatPage() {
  const {
    conversations,
    sendChatMessage,
    setChatStatus,
    createChat,
    deleteChat,
    archiveChat,
    linkTicketId,
    refreshPlatform,
  } = usePlatform();
  const { currentAgent, createTicket, findTicket } = useTickets();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [showNew, setShowNew] = useState(false);
  const [newName, setNewName] = useState('');
  const [as, setAs] = useState<'agent' | 'customer'>('agent');
  const [listTab, setListTab] = useState<'live' | 'archive'>('live');
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!selectedId && conversations[0]) setSelectedId(conversations[0].id);
  }, [conversations, selectedId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, selectedId]);

  useEffect(() => {
    if (!selectedId || !currentAgent) return;
    const beat = () =>
      publishChatViewer(selectedId, { id: currentAgent.id, name: currentAgent.name || 'Agent' });
    beat();
    const t = window.setInterval(beat, 5000);
    return () => {
      window.clearInterval(t);
      clearChatViewer(selectedId, currentAgent.id);
    };
  }, [selectedId, currentAgent?.id, currentAgent?.name]);

  useEffect(() => {
    if (!selectedId) return;
    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 4000);
    return () => window.clearInterval(id);
  }, [selectedId, refreshPlatform]);

  const selected = conversations.find((c) => c.id === selectedId) || null;
  const linkedTicket = selected?.ticket_id ? findTicket(selected.ticket_id) : undefined;

  const startChat = async () => {
    if (!newName.trim()) return;
    setBusy(true);
    try {
      const conv = await createChat(newName.trim());
      setSelectedId(conv.id);
      setNewName('');
      setShowNew(false);
    } finally {
      setBusy(false);
    }
  };

  const convertToTicket = async () => {
    if (!selected) return;
    setBusy(true);
    setMsg('');
    try {
      if (selected.ticket_id && findTicket(selected.ticket_id)) {
        setMsg(`Already linked to ${selected.ticket_id}`);
        return;
      }
      const transcript = (selected.messages || [])
        .map((m) => `[${m.sender}] ${m.text || m.body || ''}`)
        .join('\n');
      const ticket = await createTicket({
        title: `Chat: ${selected.customer_name}`,
        description: transcript || 'Converted from live chat',
        priority: 'medium',
        status: 'open',
        customer_name: selected.customer_name,
        customer_email: selected.customer_email,
        branch: selected.branch,
      });
      await linkTicketId(selected.id, ticket.id);
      setMsg(`Linked to ${ticket.id}`);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to convert');
    } finally {
      setBusy(false);
    }
  };

  const send = async () => {
    if (!draft.trim() || !selected) return;
    setBusy(true);
    try {
      if (selected.status === 'ended') await setChatStatus(selected.id, 'active');
      await sendChatMessage(selected.id, draft.trim(), as);
      setDraft('');
    } finally {
      setBusy(false);
    }
  };

  const onAttach = async (file: File) => {
    if (!selected) return;
    setBusy(true);
    try {
      if (selected.status === 'ended') await setChatStatus(selected.id, 'active');
      let body = `Attachment: ${file.name}`;
      try {
        const up = await uploadAttachment(file, `chat/${selected.id}`);
        if (up?.url) body = up.url;
      } catch {
        /* local fallback */
      }
      await sendChatMessage(selected.id, body, 'agent');
    } finally {
      setBusy(false);
    }
  };

  const requestDelete = (id: string) => setConfirmDeleteId(id);

  const confirmDelete = async () => {
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
  };

  const liveChats = conversations.filter((c) => {
    const s = (c.status || '').toLowerCase();
    return s !== 'archived' && s !== 'ended';
  });
  const archivedChats = conversations.filter((c) => {
    const s = (c.status || '').toLowerCase();
    return s === 'archived' || s === 'ended';
  });
  const list = listTab === 'archive' ? archivedChats : liveChats;
  const activeCount = liveChats.filter((c) => c.status !== 'ended').length;

  return (
    <div className="space-y-3">
      <div className="rounded-xl px-4 py-3 text-sm border border-violet-400/30 bg-violet-950/50 text-white">
        <strong className="text-white">Chat \u2194 ticket:</strong>{' '}
        <span className="text-violet-100">
          Convert a chat into a ticket, or open a linked ticket ID. Files use Supabase Storage when available.
        </span>
      </div>

      {msg ? <div className="text-xs text-violet-200 px-1">{msg}</div> : null}

      <div className="bg-white dark:bg-zinc-950 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm overflow-hidden flex h-[calc(100vh-12rem)] min-h-[420px]">
        <div className="w-72 border-r border-slate-200 dark:border-white/10 flex flex-col">
          <div className="px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-slate-800 dark:text-zinc-100">
              {listTab === 'archive' ? `Archive (${archivedChats.length})` : `Live chats (${activeCount})`}
            </span>
            <button type="button" onClick={() => setShowNew((v) => !v)} className="p-1.5 text-brand-600 hover:bg-white/5 rounded-lg" title="New chat">
              <Plus size={16} />
            </button>
          </div>
          <div className="px-3 py-2 border-b border-slate-200 dark:border-white/10 flex gap-1">
            <button type="button" onClick={() => setListTab('live')} className={clsx('flex-1 text-xs py-1.5 rounded-lg font-medium', listTab === 'live' ? 'bg-brand-600 text-white' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5')}>
              Live
            </button>
            <button type="button" onClick={() => setListTab('archive')} className={clsx('flex-1 text-xs py-1.5 rounded-lg font-medium', listTab === 'archive' ? 'bg-brand-600 text-white' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5')}>
              Archive
            </button>
          </div>

          {showNew && (
            <div className="p-3 border-b border-slate-100 dark:border-white/10 space-y-2 bg-slate-50 dark:bg-white/5">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Customer name"
                className="w-full px-2.5 py-1.5 text-sm border border-slate-200 dark:border-white/15 rounded-lg bg-white dark:bg-zinc-900"
                onKeyDown={(e) => e.key === 'Enter' && void startChat()}
              />
              <button type="button" disabled={busy} onClick={() => void startChat()} className="w-full py-1.5 text-xs font-medium text-white bg-brand-600 rounded-lg disabled:opacity-50">
                Start conversation
              </button>
            </div>
          )}

          <div className="flex-1 overflow-y-auto">
            {list.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedId(c.id)}
                className={clsx(
                  'w-full text-left px-4 py-3 transition-colors border-b border-slate-100 dark:border-white/5',
                  selectedId === c.id ? 'bg-violet-600/20' : 'hover:bg-slate-50 dark:hover:bg-white/5',
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate">{c.customer_name}</span>
                  {(c.unread || 0) > 0 ? (
                    <span className="text-[10px] font-bold bg-emerald-500 text-white rounded-full px-1.5">{c.unread}</span>
                  ) : null}
                </div>
                <div className="text-[11px] text-slate-500 truncate mt-0.5">
                  {[c.branch, c.ticket_id].filter(Boolean).join(' \u00b7 ') || c.customer_email || ''}
                </div>
                <div className="text-[11px] mt-1 text-slate-400 truncate">{c.preview || 'No messages'}</div>
                <div className="text-[11px] mt-1 capitalize text-slate-400">{c.status}</div>
              </button>
            ))}
            {!list.length ? (
              <div className="p-4 text-xs text-slate-400 text-center">No chats here.</div>
            ) : null}
          </div>
        </div>

        <div className="flex-1 flex flex-col min-w-0">
          {selected ? (
            <>
              <div className="px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-slate-900 dark:text-white truncate">{selected.customer_name}</div>
                  <div className="text-[11px] text-slate-500 truncate">
                    {selected.customer_email || 'No email'} \u00b7 <span className="capitalize">{selected.status}</span>
                  </div>
                  {(selected.branch || selected.ticket_id) && (
                    <div className="text-[11px] text-violet-400 truncate">
                      {[selected.branch && `Branch: ${selected.branch}`, selected.ticket_id && `Ticket: ${selected.ticket_id}`]
                        .filter(Boolean)
                        .join(' \u00b7 ')}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 flex-wrap justify-end">
                  {selected.ticket_id ? (
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-brand-700 bg-violet-600/20 px-2 py-1.5 rounded-lg">
                      <Ticket size={12} /> {selected.ticket_id}
                      {linkedTicket && <span className="text-slate-500">\u00b7 {linkedTicket.status}</span>}
                    </span>
                  ) : (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void convertToTicket()}
                      className="inline-flex items-center gap-1 text-xs font-medium text-white bg-brand-600 px-2.5 py-1.5 rounded-lg hover:bg-brand-700 disabled:opacity-50"
                    >
                      <Ticket size={12} /> Convert to ticket
                    </button>
                  )}
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
                  )}
                  <button
                    type="button"
                    onClick={() => requestDelete(selected.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg"
                    title="Delete chat permanently"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {(selected.messages || []).map((m, i) => {
                  const isAgent = m.sender === 'agent';
                  const body = (m.text || m.body || '').toString();
                  const isImg = /\.(png|jpe?g|gif|webp)(\?|$)/i.test(body);
                  return (
                    <div
                      key={m.id || i}
                      className={clsx(
                        'max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm',
                        isAgent ? 'ml-auto bg-brand-600 text-white' : 'bg-slate-100 dark:bg-zinc-800 text-slate-800 dark:text-zinc-100',
                      )}
                    >
                      <div className="text-[10px] font-semibold opacity-70 mb-0.5">{isAgent ? 'Agent' : 'Customer'}</div>
                      {isImg ? (
                        <a href={body} target="_blank" rel="noreferrer" className="block">
                          <img src={body} alt="attachment" className="max-h-48 rounded-lg" />
                        </a>
                      ) : body.startsWith('http') ? (
                        <a href={body} target="_blank" rel="noreferrer" className="underline break-all inline-flex items-center gap-1">
                          {body} <ExternalLink size={12} />
                        </a>
                      ) : (
                        <div className="whitespace-pre-wrap break-words">{body}</div>
                      )}
                      <div className="text-[10px] opacity-60 mt-1">
                        {m.created_at
                          ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                          : ''}
                      </div>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>

              <div className="p-3 border-t border-slate-200 dark:border-white/10 space-y-2">
                <div className="flex items-center gap-2">
                  <label className="p-2 rounded-lg hover:bg-white/5 cursor-pointer text-slate-400">
                    <Paperclip size={16} />
                    <input
                      type="file"
                      className="hidden"
                      onChange={(e) => e.target.files?.[0] && void onAttach(e.target.files[0])}
                    />
                  </label>
                  <input
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), void send())}
                    placeholder="Type a reply as agent..."
                    className="flex-1 px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-zinc-900 text-slate-800 dark:text-zinc-100"
                  />
                  <button
                    type="button"
                    disabled={busy || !draft.trim()}
                    onClick={() => void send()}
                    className="p-2.5 rounded-xl bg-brand-600 text-white disabled:opacity-40"
                  >
                    <Send size={16} />
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => setAs((v) => (v === 'agent' ? 'customer' : 'agent'))}
                  className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 dark:hover:text-zinc-300 px-2 py-1 rounded-lg hover:bg-white/5"
                >
                  <UserRound size={12} /> Simulate {as === 'agent' ? 'customer' : 'agent'}
                </button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-sm text-slate-400">Select a conversation</div>
          )}
        </div>
      </div>

      {confirmDeleteId ? (
        <div className="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-black/50">
          <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-zinc-900/95 text-zinc-100 shadow-xl p-5 space-y-4">
            <div className="text-sm font-semibold text-white">Delete this chat?</div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              This permanently removes the conversation and all messages. This cannot be undone.
            </p>
            <div className="flex justify-end gap-2 pt-1">
              <button
                type="button"
                disabled={deleteBusy}
                onClick={() => setConfirmDeleteId(null)}
                className="px-3 py-1.5 text-xs rounded-lg border border-white/15 text-zinc-300 hover:bg-white/5"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={deleteBusy}
                onClick={() => void confirmDelete()}
                className="px-3 py-1.5 text-xs rounded-lg bg-rose-600 text-white hover:bg-rose-500 disabled:opacity-50"
              >
                {deleteBusy ? 'Deleting\u2026' : 'Delete permanently'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
