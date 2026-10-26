import { useState, useEffect, useRef, useMemo } from 'react';
import clsx from 'clsx';
import { Send, ArrowLeft, Paperclip, MessageCircle, Sparkles, Clock } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import { useTickets } from '../context/TicketContext';
import { INITIAL_BRANCHES } from '../data';
import { MAX_CHAT_FILE_BYTES } from '../types';
import { encodeChatAttachment, parseChatAttachment, isImageMime } from '../lib/chatAttachments';

const STORAGE_KEY = 'nexus-portal-chat-id';

const QUICK_REPLIES = [
  'I need help with my account',
  'Billing question',
  'Something is broken',
  'Thanks, that fixed it',
];

interface Props {
  onBack: () => void;
}

export default function PortalLiveChat({ onBack }: Props) {
  const { conversations, createChat, sendChatMessage, refreshPlatform } = usePlatform();
  const { findTicket } = useTickets();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [branch, setBranch] = useState('');
  const [ticketId, setTicketId] = useState('');
  const [ticketHint, setTicketHint] = useState('');
  const [chatId, setChatId] = useState<string | null>(() => sessionStorage.getItem(STORAGE_KEY));
  const [draft, setDraft] = useState('');
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');
  const [fileError, setFileError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const conversation = conversations.find((c) => c.id === chatId) || null;
  const messages = conversation?.messages || [];

  const branchOptions = useMemo(() => {
    const set = new Set(INITIAL_BRANCHES.map((b) => b.name));
    try {
      const raw = localStorage.getItem('nexus-branches-v1');
      if (raw) {
        const list = JSON.parse(raw) as { name: string }[];
        list.forEach((b) => set.add(b.name));
      }
    } catch {}
    if (branch) set.add(branch);
    return Array.from(set).sort();
  }, [branch]);

  useEffect(() => {
    const id = ticketId.trim();
    if (!id) {
      setTicketHint('');
      return;
    }
    const t = findTicket(id);
    if (!t) {
      setTicketHint('Ticket not found yet — you can still chat.');
      return;
    }
    if (t.branch) {
      setBranch(t.branch);
      setTicketHint(`Found ${t.id}: ${t.title} → branch set to ${t.branch}`);
    } else {
      setTicketHint(`Found ${t.id}: ${t.title} (no branch on ticket — pick one below if you want)`);
    }
    if (t.customer_email && !email.trim()) setEmail(t.customer_email);
    if (t.customer_name && !name.trim()) setName(t.customer_name);
  }, [ticketId, findTicket]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setInterval(() => refreshPlatform(), 3000);
    return () => clearInterval(t);
  }, [refreshPlatform]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  const start = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name is required');
      return;
    }
    setError('');
    setStarting(true);
    try {
      const tid = ticketId.trim() || undefined;
      const br = branch.trim() || undefined;
      const c = await createChat(name.trim(), email.trim() || undefined, {
        branch: br,
        ticket_id: tid,
      });
      sessionStorage.setItem(STORAGE_KEY, c.id);
      setChatId(c.id);
      const parts = [`Hi, I'm ${name.trim()}.`];
      if (br) parts.push(`Branch: ${br}.`);
      if (tid) parts.push(`Ticket to resolve: ${tid}.`);
      parts.push('I need help.');
      await sendChatMessage(c.id, parts.join(' '), 'customer');
    } finally {
      setStarting(false);
    }
  };

  const send = async (text?: string) => {
    const body = (text ?? draft).trim();
    if (!body || !chatId) return;
    setDraft('');
    await sendChatMessage(chatId, body, 'customer');
  };

  const sendFile = async (file: File) => {
    if (!chatId) return;
    setFileError('');
    if (file.size > MAX_CHAT_FILE_BYTES) {
      setFileError(`File too large (max ~${Math.round(MAX_CHAT_FILE_BYTES / 1000)}KB).`);
      return;
    }
    const dataUrl = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result));
      reader.onerror = () => reject(new Error('Could not read file'));
      reader.readAsDataURL(file);
    });
    const body = encodeChatAttachment(
      { url: dataUrl, name: file.name, mime: file.type || 'application/octet-stream' },
      draft.trim() || undefined
    );
    setDraft('');
    await sendChatMessage(chatId, body, 'customer');
  };

  const endAndLeave = () => {
    sessionStorage.removeItem(STORAGE_KEY);
    setChatId(null);
    onBack();
  };

  if (!chatId || !conversation) {
    return (
      <div className="max-w-md mx-auto">
        <div className="text-center mb-6">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-lg shadow-brand-500/25 mb-4">
            <MessageCircle className="text-white" size={26} />
          </div>
          <h1 className="text-2xl font-bold text-zinc-900 tracking-tight">Live chat</h1>
          <p className="text-zinc-500 text-sm mt-1">Talk to a support agent in real time.</p>
          <div className="mt-4 flex justify-center gap-3 text-[11px] text-zinc-500">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-zinc-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Agents online
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-zinc-200">
              <Clock size={12} /> Typical wait under a few minutes
            </span>
          </div>
        </div>
        <form onSubmit={start} className="bg-white rounded-2xl border border-zinc-200 shadow-card p-6 space-y-4">
          {error && <div className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Your name *</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required
              className="w-full px-3 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400" />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Email (optional)</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400" />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Ticket number (if any)</label>
            <input
              value={ticketId}
              onChange={(e) => setTicketId(e.target.value)}
              placeholder="e.g. NX-2841"
              className="w-full px-3 py-2.5 text-sm border border-zinc-200 rounded-xl font-mono focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
            />
            <p className="text-[11px] text-zinc-400 mt-1">
              Enter your ticket ID first — branch fills in automatically when found.
            </p>
            {ticketHint && (
              <p className={`text-[11px] mt-1 ${ticketHint.startsWith('Found') ? 'text-emerald-600' : 'text-amber-600'}`}>
                {ticketHint}
              </p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">
              Branch <span className="font-normal text-zinc-400">(optional)</span>
            </label>
            <select
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-zinc-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
            >
              <option value="">Select branch (optional)…</option>
              {branchOptions.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>
          <button type="submit" disabled={starting}
            className="w-full py-3 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 disabled:opacity-50 shadow-sm shadow-brand-600/20">
            {starting ? 'Connecting…' : 'Start chat'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto flex flex-col h-[calc(100vh-8rem)] min-h-[440px]">
      <div className="flex items-center justify-between mb-3">
        <button type="button" onClick={endAndLeave} className="text-xs text-zinc-400 hover:text-rose-600">
          End session
        </button>
      </div>
      <div className="flex-1 bg-white rounded-2xl border border-zinc-200 shadow-card flex flex-col overflow-hidden">
        <div className="px-4 py-3 border-b border-zinc-100 bg-gradient-to-r from-brand-50 to-violet-50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center">
              <MessageCircle size={16} className="text-white" />
            </div>
            <div>
              <div className="text-sm font-semibold text-zinc-900">Support chat</div>
              <div className="text-xs text-zinc-500 capitalize flex items-center gap-1.5">
                <span className={clsx(
                  'w-1.5 h-1.5 rounded-full',
                  conversation.status === 'waiting' ? 'bg-amber-400 animate-pulse' : conversation.status === 'ended' ? 'bg-zinc-400' : 'bg-emerald-500'
                )} />
                {conversation.status === 'waiting' ? 'Waiting for agent…' : conversation.status}
                {conversation.branch ? ` · ${conversation.branch}` : ''}
                {conversation.ticket_id ? ` · ${conversation.ticket_id}` : ''}
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-50/40 via-white to-zinc-50">
          {messages.length <= 1 && (
            <div className="rounded-xl border border-dashed border-brand-200 bg-white/80 p-4 text-center mb-2">
              <Sparkles className="mx-auto text-brand-500 mb-2" size={20} />
              <p className="text-sm font-medium text-zinc-800">You're in the queue</p>
              <p className="text-xs text-zinc-500 mt-1">
                An agent will join shortly. Feel free to add more details below.
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-3">
                {QUICK_REPLIES.map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => void send(q)}
                    className="text-xs px-2.5 py-1.5 rounded-full bg-brand-50 text-brand-700 border border-brand-100 hover:bg-brand-100"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => {
            const { att, text } = parseChatAttachment(m.text);
            return (
              <div key={m.id} className={clsx('flex', m.sender === 'customer' ? 'justify-end' : 'justify-start')}>
                <div className={clsx(
                  'max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm',
                  m.sender === 'customer'
                    ? 'bg-brand-600 text-white rounded-br-md'
                    : 'bg-white border border-zinc-100 text-zinc-800 rounded-bl-md'
                )}>
                  {m.sender === 'agent' && (
                    <div className="text-[10px] font-semibold text-brand-600 mb-0.5">Agent</div>
                  )}
                  {att && isImageMime(att.mime) && (
                    <a href={att.url} target="_blank" rel="noreferrer" className="block mb-2">
                      <img src={att.url} alt={att.name || 'image'} className="max-w-full rounded-lg max-h-48 object-contain" />
                    </a>
                  )}
                  {att && !isImageMime(att.mime) && (
                    <a
                      href={att.url}
                      download={att.name || 'file'}
                      className={clsx('block text-xs underline mb-1', m.sender === 'customer' ? 'text-brand-100' : 'text-brand-700')}
                    >
                      📎 {att.name || 'Download file'}
                    </a>
                  )}
                  {text}
                  <div className={clsx('text-[10px] mt-1', m.sender === 'customer' ? 'text-brand-200' : 'text-zinc-400')}>
                    {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>

        {conversation.status !== 'ended' ? (
          <div className="p-3 border-t border-zinc-100 space-y-2 bg-white">
            {fileError && <p className="text-xs text-rose-600">{fileError}</p>}
            <div className="flex gap-2">
              <input
                ref={fileRef}
                type="file"
                accept="image/*,.pdf,.txt,.log,.zip,.doc,.docx"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) sendFile(f);
                  e.target.value = '';
                }}
              />
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="px-3 py-2.5 border border-zinc-200 rounded-xl text-zinc-500 hover:bg-zinc-50"
                title="Send image or file"
              >
                <Paperclip size={18} />
              </button>
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && void send()}
                placeholder="Type your message…"
                className="flex-1 px-4 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
              />
              <button type="button" onClick={() => void send()} disabled={!draft.trim()}
                className="px-4 py-2.5 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-40">
                <Send size={18} />
              </button>
            </div>
          </div>
        ) : (
          <div className="p-4 text-center text-sm text-zinc-500 bg-zinc-50">This chat was ended by the agent.</div>
        )}
      </div>
    </div>
  );
}
