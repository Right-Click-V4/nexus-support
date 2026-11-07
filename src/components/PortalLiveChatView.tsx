/* nickname-chat-v1 */
/* portal-livechat-view with computeOnlineAgents */
import { useState, useEffect, useRef, useMemo } from 'react';
import clsx from 'clsx';
import { Send, Paperclip, MessageCircle, Sparkles, Clock, Building2, Ticket, Circle } from 'lucide-react';
import AgentAvatar from './AgentAvatar';
import { usePlatform } from '../context/PlatformContext';
import { useTickets } from '../context/TicketContext';
import { useAuth } from '../context/AuthContext';
import { MAX_CHAT_FILE_BYTES } from '../types';
import { encodeChatFile, parseChatAttachment, isImageMime } from '../lib/chatAttachments';
import { watchDeskPresence, type DeskAgent } from '../lib/deskPresence';
import { computeOnlineAgents } from '../lib/onlineAgents';
import { watchChatViewers, type ChatViewer } from '../lib/chatPresence';

const STORAGE_KEY = 'nexus-portal-chat-id';

const BRANCH_OPTIONS = [
  'Abucay', 'Abuyog', 'Avenida', 'Baybay', 'Burauen', 'Calbayog', 'Carigara',
  'Catarman', 'Catbalogan', 'Kananga', 'Maasin', 'Ormoc', 'Palo-Naga',
  'Palo-Pawing', 'Palo-Schisto', 'Sogod',
] as const;

const QUICK_REPLIES = [
  'I need help with my account',
  'Billing question',
  'Something is broken',
  'Thanks, that fixed it',
];

interface Props {
  onBack: () => void;
}

export default function PortalLiveChatView({ onBack }: Props) {
  const { conversations, createChat, sendChatMessage, refreshPlatform } = usePlatform();
  const { findTicket, agents, refresh: refreshTickets } = useTickets();
  const { user } = useAuth();

  const legalChatName =
    (user?.user_metadata?.full_name as string | undefined)?.trim() ||
    (user?.user_metadata?.name as string | undefined)?.trim() ||
    user?.email?.split('@')[0] ||
    '';
  const nickChat = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';
  const accountName = nickChat && legalChatName ? `${legalChatName} (${nickChat})` : legalChatName;

  const [name, setName] = useState(accountName);
  const [email, setEmail] = useState(user?.email || '');
  const [branch, setBranch] = useState('');
  const [ticketId, setTicketId] = useState('');
  const [ticketHint, setTicketHint] = useState('');
  const [chatId, setChatId] = useState<string | null>(() => sessionStorage.getItem(STORAGE_KEY));
  const [chatViewers, setChatViewers] = useState<ChatViewer[]>([]);
  const [draft, setDraft] = useState('');
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');
  const [fileError, setFileError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (accountName) setName(accountName);
  }, [accountName]);

  useEffect(() => {
    if (user?.email) setEmail(user.email);
  }, [user?.email]);

  const conversation = conversations.find((c) => c.id === chatId) || null;
  const messages = conversation?.messages || [];
  const isOnHold = ['on_hold', 'waiting'].includes((conversation?.status || '').toLowerCase());

  useEffect(() => {
    const st = (conversation?.status || '').toLowerCase();
    if (st === 'ended' || st === 'archived') {
      try { sessionStorage.removeItem(STORAGE_KEY); } catch {}
      setChatId(null);
      setDraft('');
    }
  }, [conversation?.status]);

  useEffect(() => {
    return watchChatViewers(chatId, setChatViewers);
  }, [chatId]);

  useEffect(() => {
    if (!chatId) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 4000);
    return () => window.clearInterval(id);
  }, [chatId, refreshPlatform]);

  const branchOptions = useMemo(() => {
    const set = new Set<string>([...BRANCH_OPTIONS]);
    try {
      const raw = localStorage.getItem('nexus-branches-v1');
      if (raw) {
        (JSON.parse(raw) as { name: string }[]).forEach((b) => set.add(b.name));
      }
    } catch {}
    if (branch) set.add(branch);
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [branch]);

  const [deskAgents, setDeskAgents] = useState<DeskAgent[]>([]);
  const [presenceTick, setPresenceTick] = useState(0);
  useEffect(() => {
    return watchDeskPresence(setDeskAgents);
  }, []);
  useEffect(() => {
    const id = window.setInterval(() => setPresenceTick((n) => n + 1), 5000);
    return () => window.clearInterval(id);
  }, []);

  const onlineAgents = useMemo(
    () => computeOnlineAgents(agents, deskAgents),
    [agents, presenceTick, deskAgents],
  );

  useEffect(() => {
    const id = window.setInterval(() => {
      void refreshTickets?.({ silent: true });
    }, 8000);
    void refreshTickets?.({ silent: true });
    return () => window.clearInterval(id);
  }, [refreshTickets]);

  const hasAgentOnline = onlineAgents.length > 0;

  useEffect(() => {
    const id = ticketId.trim();
    if (!id) {
      setTicketHint('');
      return;
    }
    const t = findTicket(id);
    if (!t) {
      setTicketHint('Ticket not found yet — you can still start a chat.');
      return;
    }
    if (t.branch) {
      setBranch(t.branch);
      setTicketHint(`Found ${t.id}: ${t.title} → branch set to ${t.branch}`);
    } else {
      setTicketHint(`Found ${t.id}: ${t.title} (no branch on ticket — pick one below if you want)`);
    }
  }, [ticketId, findTicket]);

  useEffect(() => {
    const t = setInterval(() => refreshPlatform(), 3000);
    return () => clearInterval(t);
  }, [refreshPlatform]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length, chatId]);

  const start = async (e: React.FormEvent) => {
    e.preventDefault();
    const nm = (accountName || name).trim();
    if (!nm) {
      setError('Account name is required — sign in again if this is empty.');
      return;
    }
    const tid = ticketId.trim();
    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    if (!hasAgentOnline) {
      setError('No agents are online right now. Please try again later.');
      return;
    }
    setStarting(true);
    setError('');
    try {
      const br = branch.trim() || undefined;
      const c = await createChat(nm, (user?.email || email).trim() || undefined, {
        branch: br,
        ticket_id: tid,
      });
      setChatId(c.id);
      sessionStorage.setItem(STORAGE_KEY, c.id);
      const lines = [
        `Hi, I'm ${nm}.`,
        br ? `Branch: ${br}` : null,
        tid ? `Ticket: ${tid}` : null,
        'I need assistance.',
      ].filter(Boolean) as string[];
      await sendChatMessage(c.id, lines.join('\n'), 'customer');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not start chat');
    } finally {
      setStarting(false);
    }
  };

  const send = async () => {
    if (isOnHold) return;
    if (!chatId || !draft.trim()) return;
    const text = draft.trim();
    setDraft('');
    await sendChatMessage(chatId, text, 'customer');
  };

  const onFile = async (file: File | null) => {
    if (!chatId || !file) return;
    setFileError('');
    if (file.size > MAX_CHAT_FILE_BYTES) {
      setFileError('File is too large.');
      return;
    }
    try {
      const dataUrl = await encodeChatFile(file);
      await sendChatMessage(
        chatId,
        JSON.stringify({ url: dataUrl, name: file.name, mime: file.type || 'application/octet-stream' }),
        'customer',
      );
    } catch {
      setFileError('Could not attach file.');
    }
  };

  const field =
    'w-full px-3 py-2.5 text-sm rounded-xl border border-zinc-200 dark:border-white/15 bg-white/80 dark:bg-zinc-900/70 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400';

  if (!chatId) {
    return (
      <div className="w-full max-w-5xl mx-auto">
        <div className="grid lg:grid-cols-[1fr_320px] gap-4">
          <form onSubmit={start} className="rounded-2xl border border-white/10 bg-zinc-950/60 p-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-violet-600 flex items-center justify-center">
                <MessageCircle size={18} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                  Connect with a support agent in real time.
                </p>
              </div>
            </div>
            {error && <p className="text-sm text-rose-400">{error}</p>}
            <div>
              <label className="text-xs font-medium text-zinc-400">Your name</label>
              <input className={field} value={name} onChange={(e) => setName(e.target.value)} disabled={!!accountName} />
              <p className="text-[11px] text-zinc-500 mt-1">Locked to your registered account name.</p>
            </div>
            <div>
              <label className="text-xs font-medium text-zinc-400">Email</label>
              <input className={field} value={email} onChange={(e) => setEmail(e.target.value)} disabled={!!user?.email} />
              <p className="text-[11px] text-zinc-500 mt-1">Locked to your registered account email.</p>
            </div>
            <div>
              <label className="text-xs font-medium text-zinc-400">Ticket number</label>
              <input className={field} value={ticketId} onChange={(e) => setTicketId(e.target.value)} placeholder="e.g. NX-2841" />
              {ticketHint && <p className="text-[11px] text-zinc-500 mt-1">{ticketHint}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-zinc-400">Branch</label>
              <select className={field} value={branch} onChange={(e) => setBranch(e.target.value)}>
                <option value="">Select branch...</option>
                {branchOptions.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={starting || !hasAgentOnline}
              title={!hasAgentOnline ? 'No agents are online right now' : undefined}
              className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {starting ? 'Connecting…' : !hasAgentOnline ? 'No agents online' : 'Start chat'}
            </button>
            {!hasAgentOnline && (
              <p className="text-xs text-amber-400 text-center">
                Chat is unavailable until an agent or admin is online.
              </p>
            )}
          </form>
          <div className="space-y-3">
            <div className="rounded-2xl border border-white/10 bg-zinc-950/60 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={16} className="text-violet-400" />
                <h2 className="text-sm font-semibold text-zinc-100">Before you start</h2>
              </div>
              <ul className="text-xs text-zinc-400 space-y-1.5 list-disc pl-4">
                <li>Agents are typically available during business hours.</li>
                <li>Link a ticket number if this is about an existing request.</li>
                <li>You can attach screenshots after the chat starts.</li>
              </ul>
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="text-[11px] px-2 py-1 rounded-full border border-white/15 text-zinc-300">
                  {hasAgentOnline ? `${onlineAgents.length} agent${onlineAgents.length === 1 ? '' : 's'} online` : 'No agents online'}
                </span>
                <span className="text-[11px] px-2 py-1 rounded-full border border-white/15 text-zinc-300 flex items-center gap-1">
                  <Clock size={10} /> Typical wait: a few minutes
                </span>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-zinc-950/60 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Circle size={10} className={hasAgentOnline ? 'text-emerald-400 fill-emerald-400' : 'text-zinc-500'} />
                  <h2 className="text-sm font-semibold text-zinc-100">Active now</h2>
                </div>
                {hasAgentOnline && (
                  <span className="text-[10px] font-bold uppercase tracking-wide text-emerald-400 border border-emerald-500/40 px-1.5 py-0.5 rounded">LIVE</span>
                )}
              </div>
              <p className="text-[11px] text-zinc-500 mb-2">
                {hasAgentOnline
                  ? `${onlineAgents.length} agent${onlineAgents.length === 1 ? '' : 's'} available`
                  : 'No agents online'}
              </p>
              <div className="space-y-2">
                {onlineAgents.map((a) => (
                  <div key={a.id} className="flex items-center gap-2 rounded-xl border border-white/10 px-2.5 py-2">
                    <AgentAvatar agent={a as any} size={28} />
                    <div className="min-w-0">
                      <div className="text-xs font-medium text-zinc-100 truncate">{a.name}</div>
                      <div className="text-[11px] text-emerald-400 capitalize">{a.status || 'online'}</div>
                    </div>
                  </div>
                ))}
                {!hasAgentOnline && (
                  <p className="text-sm text-zinc-500">No agents are available right now. Please try again later.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="rounded-2xl border border-white/10 bg-zinc-950/70 overflow-hidden flex flex-col min-h-[420px]">
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
              <MessageCircle size={16} className="text-violet-400" /> Live Chat
            </div>
            <div className="text-[11px] text-zinc-500 truncate">
              Connected with support
              {conversation?.ticket_id ? ` · ${conversation.ticket_id}` : ''}
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              try { sessionStorage.removeItem(STORAGE_KEY); } catch {}
              setChatId(null);
              setDraft('');
            }}
            className="text-xs text-zinc-400 hover:text-zinc-200"
          >
            End / new chat
          </button>
        </div>

        {isOnHold && (
          <div className="px-4 py-2 text-xs bg-amber-500/15 text-amber-700 dark:text-amber-300 border-b border-amber-500/20">
            Chat is on hold — an agent will be with you shortly.
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[50vh]">
          {messages.map((m) => {
            const mine = m.sender === 'customer';
            const att = parseChatAttachment(m.text || m.body || '');
            return (
              <div key={m.id} className={clsx('flex', mine ? 'justify-end' : 'justify-start')}>
                <div className={clsx(
                  'max-w-[85%] rounded-2xl px-3 py-2 text-sm',
                  mine ? 'bg-violet-600 text-white' : 'bg-white/10 text-zinc-100 border border-white/10',
                )}>
                  {att ? (
                    isImageMime(att.mime) ? (
                      <img src={att.url} alt={att.name} className="max-w-full rounded-lg" />
                    ) : (
                      <a href={att.url} download={att.name} className="underline">{att.name}</a>
                    )
                  ) : (
                    <div className="whitespace-pre-wrap break-words">{m.text || m.body || ''}</div>
                  )}
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>

        {!isOnHold && (
          <div className="p-3 border-t border-white/10 space-y-2">
            {fileError && <p className="text-xs text-rose-400">{fileError}</p>}
            <div className="flex flex-wrap gap-1.5">
              {QUICK_REPLIES.map((q) => (
                <button key={q} type="button" onClick={() => setDraft(q)} className="text-[11px] px-2 py-1 rounded-full border border-white/15 text-zinc-300 hover:bg-white/10">{q}</button>
              ))}
            </div>
            <div className="flex items-end gap-2">
              <input ref={fileRef} type="file" className="hidden" onChange={(e) => void onFile(e.target.files?.[0] || null)} />
              <button type="button" onClick={() => fileRef.current?.click()} className="p-2.5 rounded-xl border border-white/15 text-zinc-400 hover:bg-white/10">
                <Paperclip size={16} />
              </button>
              <input
                className={field + ' flex-1'}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(); } }}
                placeholder="Type a message…"
              />
              <button type="button" onClick={() => void send()} className="p-2.5 rounded-xl bg-violet-600 text-white hover:bg-violet-500">
                <Send size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
