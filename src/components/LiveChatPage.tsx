/* livechat-emoji-gif-avatar-v1 */
/* hold-resume-toggle-v1 */
/* delete-hold-ui-v1 */
/* livechat-archive-delete-v1 */
/* chat-text-body-v1 */
/* chat-viewer-publish-v1 */
/* livechat-text-field-v1 */
import { useState, useEffect, useRef } from 'react';
import clsx from 'clsx';
import { Send, Plus, Trash2, UserRound, RotateCcw, Paperclip, Ticket, ExternalLink, Archive, Smile, Image as ImageIcon, X } from 'lucide-react';
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
  const [showEmoji, setShowEmoji] = useState(false);
  const [showGif, setShowGif] = useState(false);
  const [gifQuery, setGifQuery] = useState('hello');
  const [gifResults, setGifResults] = useState<{ id: string; url: string; preview: string }[]>([]);
  const [gifLoading, setGifLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const EMOJIS = [
    '😀','😁','😂','🤣','😊','😍','😘','😎','🤩','😇','🤗','🤔','😏','😢','😭','😡','👍','👎','👏','🙏',
    '🔥','✨','💯','🎉','❤️','💙','💜','✅','❌','⭐','🎯','💬','📌','🙌','💪','🤝','👋','🫡','👌','🤞',
  ];

  const searchGifs = async (q: string) => {
    const query = (q || 'hello').trim() || 'hello';
    setGifLoading(true);
    try {
      // Public Giphy demo key (rate-limited; fine for internal tools)
      const res = await fetch(
        `https://api.giphy.com/v1/gifs/search?api_key=dc6zaTOxFJmzC&q=${encodeURIComponent(query)}&limit=18&rating=g`,
      );
      const data = await res.json();
      const items = (data?.data || []).map((g: { id: string; images?: { fixed_height_small?: { url?: string }; original?: { url?: string } } }) => ({
        id: g.id,
        preview: g.images?.fixed_height_small?.url || g.images?.original?.url || '',
        url: g.images?.original?.url || g.images?.fixed_height_small?.url || '',
      })).filter((x: { url: string }) => x.url);
      setGifResults(items);
    } catch {
      setGifResults([
        { id: '1', url: 'https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif', preview: 'https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif' },
        { id: '2', url: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif', preview: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif' },
        { id: '3', url: 'https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif', preview: 'https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif' },
      ]);
    } finally {
      setGifLoading(false);
    }
  };

  useEffect(() => {
    if (showGif) void searchGifs(gifQuery);
  }, [showGif]);


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
        <strong className="text-white">Chat ↔ ticket:</strong>{' '}
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
          <div className="flex border-b border-slate-200 dark:border-white/10">
            <button
              type="button"
              onClick={() => setListTab('live')}
              className={clsx(
                'flex-1 py-2 text-xs font-medium',
                listTab === 'live' ? 'text-brand-500 border-b-2 border-brand-500' : 'text-slate-500 dark:text-zinc-400',
              )}
            >
              Live
            </button>
            <button
              type="button"
              onClick={() => setListTab('archive')}
              className={clsx(
                'flex-1 py-2 text-xs font-medium',
                listTab === 'archive' ? 'text-brand-500 border-b-2 border-brand-500' : 'text-slate-500 dark:text-zinc-400',
              )}
            >
              Archive
            </button>
          </div>
          {showNew && (
            <div className="p-3 border-b border-slate-200 dark:border-white/10 space-y-2">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Customer name"
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-white/15 bg-white dark:bg-zinc-900"
              />
              <button
                type="button"
                disabled={busy || !newName.trim()}
                onClick={() => void startChat()}
                className="w-full py-2 text-sm rounded-lg bg-brand-600 text-white disabled:opacity-50"
              >
                Start chat
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
                  'w-full text-left px-4 py-3 border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/5',
                  selectedId === c.id && 'bg-violet-50 dark:bg-violet-950/40',
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate">{c.customer_name || 'Customer'}</span>
                  <span
                    className={clsx(
                      'text-[10px] px-1.5 py-0.5 rounded-full shrink-0',
                      (c.status || '').toLowerCase() === 'on_hold' || (c.status || '').toLowerCase() === 'waiting'
                        ? 'bg-amber-500/20 text-amber-300'
                        : (c.status || '').toLowerCase() === 'active'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-zinc-500/20 text-zinc-400',
                    )}
                  >
                    {(c.status || '').toLowerCase() === 'on_hold' || (c.status || '').toLowerCase() === 'waiting'
                      ? 'On Hold'
                      : (c.status || 'active')}
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 dark:text-zinc-500 truncate mt-0.5">
                  {c.branch ? `Branch: ${c.branch}` : c.customer_email || c.id}
                </div>
              </button>
            ))}
            {list.length === 0 && (
              <div className="p-6 text-center text-sm text-slate-500 dark:text-zinc-500">No chats here</div>
            )}
          </div>
        </div>

        <div className="flex-1 flex flex-col min-w-0">
          {selected ? (
            <>
              <div className="px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-slate-800 dark:text-zinc-100 truncate">{selected.customer_name}</div>
                  <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">
                    {selected.customer_email}
                    {selected.branch ? ` · Branch: ${selected.branch}` : ''}
                    {selected.ticket_id ? ` · Ticket: ${selected.ticket_id}` : ''}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {selected.ticket_id ? (
                    <span className="text-[11px] px-2 py-1 rounded-lg bg-violet-600/30 text-violet-200 border border-violet-400/30">
                      {selected.ticket_id}
                    </span>
                  ) : (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void convertToTicket()}
                      className="inline-flex items-center gap-1 text-xs font-medium text-violet-200 border border-violet-400/40 px-2.5 py-1.5 rounded-lg hover:bg-violet-500/20"
                    >
                      <Ticket size={12} /> Convert to ticket
                    </button>
                  )}
                  {(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (
                    <>
                      {(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? (
                        <button
                          type="button"
                          onClick={() => void setChatStatus(selected.id, 'active')}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-emerald-500 text-white px-2.5 py-1.5 rounded-lg hover:bg-emerald-400"
                        >
                          Resume
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => void setChatStatus(selected.id, 'on_hold')}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-amber-500 text-zinc-900 px-2.5 py-1.5 rounded-lg hover:bg-amber-400"
                        >
                          On Hold
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => void setChatStatus(selected.id, 'ended')}
                        className="inline-flex items-center gap-1 text-xs font-medium text-zinc-200 border border-white/20 px-2.5 py-1.5 rounded-lg hover:bg-white/5"
                      >
                        End chat
                      </button>
                    </>
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
                  const isImg = /\.(png|jpe?g|gif|webp)(\?|$)/i.test(body) || body.includes('giphy.com') || body.includes('media.tenor');
                  const agentName = currentAgent?.name || 'Agent';
                  const agentInitials = agentName
                    .split(/\s+/)
                    .map((x) => x[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase();
                  const customerName = selected.customer_name || 'Customer';
                  const customerInitials = customerName
                    .split(/\s+/)
                    .map((x) => x[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase();
                  return (
                    <div
                      key={m.id || i}
                      className={clsx('flex items-end gap-2', isAgent ? 'justify-end' : 'justify-start')}
                    >
                      {!isAgent && (
                        <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10">
                          {customerInitials || 'C'}
                        </div>
                      )}
                      <div
                        className={clsx(
                          'max-w-[75%] rounded-2xl px-3.5 py-2.5 text-sm shadow-sm',
                          isAgent
                            ? 'bg-brand-600 text-white rounded-br-md'
                            : 'bg-slate-100 dark:bg-zinc-800 text-slate-800 dark:text-zinc-100 rounded-bl-md',
                        )}
                      >
                        <div className="text-[10px] font-semibold opacity-70 mb-0.5">
                          {isAgent ? agentName : customerName}
                        </div>
                        {isImg ? (
                          <a href={body} target="_blank" rel="noreferrer" className="block">
                            <img src={body} alt="media" className="max-h-48 rounded-lg" />
                          </a>
                        ) : body.startsWith('http') ? (
                          <a href={body} target="_blank" rel="noreferrer" className="underline break-all inline-flex items-center gap-1">
                            {body} <ExternalLink size={12} />
                          </a>
                        ) : (
                          <div className="whitespace-pre-wrap break-words text-[15px] leading-relaxed">{body}</div>
                        )}
                        <div className="text-[10px] opacity-60 mt-1">
                          {m.created_at
                            ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                            : ''}
                        </div>
                      </div>
                      {isAgent && (
                        <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden">
                          {currentAgent?.avatar_url ? (
                            <img src={currentAgent.avatar_url} alt="" className="w-full h-full object-cover" />
                          ) : (
                            agentInitials || 'A'
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>

              <div className="p-3 border-t border-slate-200 dark:border-white/10 space-y-2 relative">
                {showEmoji && (
                  <div className="absolute bottom-full left-3 right-3 mb-2 z-20 rounded-xl border border-white/10 bg-zinc-900/95 p-2 shadow-xl">
                    <div className="flex items-center justify-between px-1 pb-2">
                      <span className="text-[11px] font-medium text-zinc-300">Emoji</span>
                      <button type="button" onClick={() => setShowEmoji(false)} className="p-1 text-zinc-400 hover:text-white">
                        <X size={14} />
                      </button>
                    </div>
                    <div className="grid grid-cols-10 gap-1 max-h-36 overflow-y-auto">
                      {EMOJIS.map((e) => (
                        <button
                          key={e}
                          type="button"
                          className="text-lg hover:bg-white/10 rounded-md p-1"
                          onClick={() => {
                            setDraft((d) => d + e);
                            setShowEmoji(false);
                          }}
                        >
                          {e}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {showGif && (
                  <div className="absolute bottom-full left-3 right-3 mb-2 z-20 rounded-xl border border-white/10 bg-zinc-900/95 p-3 shadow-xl">
                    <div className="flex items-center gap-2 mb-2">
                      <input
                        value={gifQuery}
                        onChange={(e) => setGifQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && void searchGifs(gifQuery)}
                        placeholder="Search GIFs…"
                        className="flex-1 px-2.5 py-1.5 text-xs rounded-lg border border-white/15 bg-zinc-800 text-zinc-100"
                      />
                      <button
                        type="button"
                        onClick={() => void searchGifs(gifQuery)}
                        className="text-xs px-2.5 py-1.5 rounded-lg bg-brand-600 text-white"
                      >
                        Search
                      </button>
                      <button type="button" onClick={() => setShowGif(false)} className="p-1 text-zinc-400 hover:text-white">
                        <X size={14} />
                      </button>
                    </div>
                    {gifLoading ? (
                      <div className="text-xs text-zinc-400 py-6 text-center">Loading GIFs…</div>
                    ) : (
                      <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
                        {gifResults.map((g) => (
                          <button
                            key={g.id}
                            type="button"
                            className="rounded-lg overflow-hidden border border-white/10 hover:border-violet-400/50"
                            onClick={() => {
                              void (async () => {
                                if (!selected) return;
                                setBusy(true);
                                try {
                                  await sendChatMessage(selected.id, g.url, as);
                                  setShowGif(false);
                                } finally {
                                  setBusy(false);
                                }
                              })();
                            }}
                          >
                            <img src={g.preview || g.url} alt="" className="w-full h-20 object-cover" />
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="flex items-end gap-2 rounded-2xl border border-slate-200 dark:border-white/15 bg-slate-50 dark:bg-zinc-900/80 px-2 py-1.5">
                  <label className="p-2 rounded-xl hover:bg-white/10 cursor-pointer text-slate-400 hover:text-violet-300" title="Attach file">
                    <Paperclip size={18} />
                    <input
                      type="file"
                      className="hidden"
                      onChange={(e) => e.target.files?.[0] && void onAttach(e.target.files[0])}
                    />
                  </label>
                  <button
                    type="button"
                    title="Emoji"
                    onClick={() => {
                      setShowGif(false);
                      setShowEmoji((v) => !v);
                    }}
                    className={clsx(
                      'p-2 rounded-xl text-slate-400 hover:text-amber-300 hover:bg-white/10',
                      showEmoji && 'bg-white/10 text-amber-300',
                    )}
                  >
                    <Smile size={18} />
                  </button>
                  <button
                    type="button"
                    title="GIF"
                    onClick={() => {
                      setShowEmoji(false);
                      setShowGif((v) => !v);
                    }}
                    className={clsx(
                      'p-2 rounded-xl text-slate-400 hover:text-fuchsia-300 hover:bg-white/10',
                      showGif && 'bg-white/10 text-fuchsia-300',
                    )}
                  >
                    <ImageIcon size={18} />
                  </button>
                  <textarea
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        void send();
                      }
                    }}
                    rows={1}
                    placeholder="Type a reply as agent…"
                    className="flex-1 resize-none bg-transparent border-0 outline-none text-sm text-slate-800 dark:text-zinc-100 placeholder:text-slate-400 dark:placeholder:text-zinc-500 py-2 max-h-28"
                  />
                  <button
                    type="button"
                    disabled={busy || !draft.trim()}
                    onClick={() => void send()}
                    className="p-2.5 rounded-xl bg-brand-600 text-white hover:bg-brand-500 disabled:opacity-40 shrink-0"
                  >
                    <Send size={16} />
                  </button>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-zinc-500">
                  <button
                    type="button"
                    onClick={() => setAs((v) => (v === 'agent' ? 'customer' : 'agent'))}
                    className="inline-flex items-center gap-1 hover:text-violet-300"
                  >
                    <UserRound size={12} /> Simulate {as === 'agent' ? 'customer' : 'agent'}
                  </button>
                  <span className="opacity-50">·</span>
                  <span>Sending as <strong className="text-slate-700 dark:text-zinc-300">{as}</strong></span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-sm text-slate-500 dark:text-zinc-500">
              Select a chat to reply
            </div>
          )}
        </div>
      </div>

      {confirmDeleteId ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-sm rounded-xl border border-white/10 bg-zinc-900 p-4 space-y-3 shadow-2xl">
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
                {deleteBusy ? 'Deleting…' : 'Delete permanently'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
