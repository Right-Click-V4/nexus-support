/* chat-viewer-publish-v1 */
/* livechat-text-field-v1 */
import { useState, useEffect, useRef } from 'react';
import clsx from 'clsx';
import { Send, Plus, Trash2, UserRound, RotateCcw, Paperclip, Ticket, ExternalLink } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import { useTickets } from '../context/TicketContext';
import { publishChatViewer, clearChatViewer } from '../lib/chatPresence';
import { uploadAttachment } from '../lib/storage';

export default function LiveChatPage() {
  const {
    conversations,
    sendChatMessage,
    setChatStatus,
    startConversation,
    deleteConversation,
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
    const id = window.setInterval(() => { void refreshPlatform(); }, 4000);
    return () => window.clearInterval(id);
  }, [selectedId, refreshPlatform]);

  const selected = conversations.find((c) => c.id === selectedId) || null;
  const activeCount = conversations.filter((c) => c.status !== 'ended').length;
  const linkedTicket = selected?.ticket_id ? findTicket(selected.ticket_id) : undefined;

  const startChat = async () => {
    if (!newName.trim()) return;
    setBusy(true);
    try {
      const id = await startConversation({
        customer_name: newName.trim(),
        status: 'active',
      });
      setSelectedId(id);
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
        .map((m) => `[${m.sender}] ${m.body}`)
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
        /* local fallback: keep filename note */
      }
      await sendChatMessage(selected.id, body, 'agent');
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id: string) => {
    await deleteConversation(id);
    if (selectedId === id) setSelectedId(null);
  };

  return (
    <div className="space-y-3">
      <div className="bg-brand-50 border border-brand-100 rounded-xl px-4 py-3 text-sm text-brand-800">
        <strong>Chat ↔ ticket:</strong> Convert a chat into a ticket, or open a linked ticket ID. Files use Supabase Storage when available.
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex h-[calc(100vh-12rem)] min-h-[420px]">
        <div className="w-72 border-r border-slate-200 flex flex-col">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-slate-800">Live chats ({activeCount})</span>
            <button type="button" onClick={() => setShowNew((v) => !v)} className="p-1.5 text-brand-600 hover:bg-white/5 rounded-lg" title="New chat">
              <Plus size={16} />
            </button>
          </div>

          {showNew && (
            <div className="p-3 border-b border-slate-100 space-y-2 bg-slate-50">
              <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Customer name" className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded-lg" onKeyDown={(e) => e.key === 'Enter' && startChat()} />
              <button type="button" disabled={busy} onClick={startChat} className="w-full py-1.5 text-xs font-medium text-white bg-brand-600 rounded-lg disabled:opacity-50">Start conversation</button>
            </div>
          )}

          <div className="flex-1 overflow-y-auto">
            {conversations.length === 0 && (
              <p className="text-xs text-slate-400 p-4 text-center">No chats yet. Customers use portal → Live chat.</p>
            )}
            {conversations.map((c) => (
              <div
                key={c.id}
                className={clsx(
                  'group border-b border-slate-100/80',
                  selectedId === c.id
                    ? 'bg-violet-600/35 border-l-2 border-l-violet-400'
                    : 'hover:bg-white/5 border-l-2 border-l-transparent'
                )}
              >
                <button type="button" onClick={() => setSelectedId(c.id)} className="w-full text-left px-4 py-3 transition-colors">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-slate-800 truncate">{c.customer_name}</span>
                    {c.unread > 0 && <span className="bg-emerald-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{c.unread}</span>}
                  </div>
                  {(c.branch || c.ticket_id) && (
                    <div className="text-[11px] text-slate-500 mt-0.5 truncate">
                      {c.branch || '—'}
                      {c.ticket_id ? ` · ${c.ticket_id}` : ''}
                    </div>
                  )}
                  <div className="text-xs text-slate-500 truncate mt-0.5">
                    {c.preview || (c.messages?.[c.messages.length - 1]?.body ?? 'No messages')}
                  </div>
                  <div className="text-[11px] mt-1 capitalize text-slate-400">{c.status}</div>
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 flex flex-col min-w-0">
          {!selected ? (
            <div className="flex-1 flex items-center justify-center text-sm text-slate-400">Select a conversation</div>
          ) : (
            <>
              <div className="px-4 py-3 border-b border-slate-200 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-slate-900">{selected.customer_name}</div>
                  <div className="text-xs text-slate-500">
                    {selected.customer_email || 'No email'} · <span className="capitalize">{selected.status}</span>
                  </div>
                  {(selected.branch || selected.ticket_id) && (
                    <div className="text-xs text-brand-700 mt-1 font-medium">
                      {selected.branch && <span>Branch: {selected.branch}</span>}
                      {selected.branch && selected.ticket_id && <span> · </span>}
                      {selected.ticket_id && <span>Ticket: {selected.ticket_id}</span>}
                    </div>
                  )}
                  {msg && <div className="text-xs text-emerald-700 mt-1">{msg}</div>}
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {selected.ticket_id ? (
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-brand-700 bg-violet-600/20 px-2 py-1.5 rounded-lg">
                      <Ticket size={12} /> {selected.ticket_id}
                      {linkedTicket && <span className="text-slate-500">· {linkedTicket.status}</span>}
                    </span>
                  ) : (
                    <button type="button" disabled={busy} onClick={convertToTicket} className="inline-flex items-center gap-1 text-xs font-medium text-white bg-brand-600 px-2.5 py-1.5 rounded-lg hover:bg-brand-700 disabled:opacity-50">
                      <Ticket size={12} /> Convert to ticket
                    </button>
                  )}
                  <select value={selected.status} onChange={(e) => setChatStatus(selected.id, e.target.value as 'active' | 'waiting' | 'ended')} className="text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white">
                    <option value="waiting">Waiting</option>
                    <option value="active">Active</option>
                    <option value="ended">Ended</option>
                  </select>
                  {selected.status === 'ended' && (
                    <button type="button" onClick={() => setChatStatus(selected.id, 'active')} className="inline-flex items-center gap-1 text-xs font-medium text-brand-600 px-2 py-1.5 rounded-lg hover:bg-white/5">
                      <RotateCcw size={12} /> Reopen
                    </button>
                  )}
                  <button type="button" onClick={() => remove(selected.id)} className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg" title="Delete chat">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {(selected.messages || []).map((m, i) => {
                  const isAgent = m.sender === 'agent';
                  const isImg = typeof m.body === 'string' && /\.(png|jpe?g|gif|webp)(\?|$)/i.test(m.body);
                  return (
                    <div key={m.id || i} className={clsx('max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm', isAgent ? 'ml-auto bg-brand-600 text-white' : 'bg-slate-100 text-slate-800')}>
                      <div className="text-[10px] font-semibold opacity-70 mb-0.5">{isAgent ? 'Agent' : 'Customer'}</div>
                      {isImg ? (
                        <a href={m.body} target="_blank" rel="noreferrer" className="block">
                          <img src={m.body} alt="attachment" className="max-h-48 rounded-lg" />
                        </a>
                      ) : (m.text || (m as { body?: string }).body || '').startsWith('http') ? (
                        <a href={m.body} target="_blank" rel="noreferrer" className="underline break-all inline-flex items-center gap-1">
                          {m.body} <ExternalLink size={12} />
                        </a>
                      ) : (
                        <div className="whitespace-pre-wrap break-words">{m.body}</div>
                      )}
                      <div className="text-[10px] opacity-60 mt-1">
                        {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                      </div>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>

              <div className="p-3 border-t border-slate-200 space-y-2">
                <div className="flex items-center gap-2">
                  <label className="p-2 rounded-lg text-slate-500 hover:bg-white/5 cursor-pointer" title="Attach file">
                    <Paperclip size={18} />
                    <input type="file" className="hidden" onChange={(e) => e.target.files?.[0] && void onAttach(e.target.files[0])} />
                  </label>
                  <input
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), void send())}
                    placeholder={as === 'agent' ? 'Type a reply as agent…' : 'Simulate customer…'}
                    className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-brand-500/30"
                  />
                  <button type="button" disabled={busy || !draft.trim()} onClick={() => void send()} className="p-2.5 rounded-xl bg-brand-600 text-white disabled:opacity-40">
                    <Send size={16} />
                  </button>
                </div>
                <button type="button" onClick={() => setAs((v) => (v === 'agent' ? 'customer' : 'agent'))} className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 px-2 py-1 rounded-lg hover:bg-white/5">
                  <UserRound size={14} /> {as === 'agent' ? 'Simulate customer' : 'Reply as agent'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
