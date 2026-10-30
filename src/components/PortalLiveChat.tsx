/* active-now-status-labels-v1 */
/* status-colors-active-v1 */
/* presence-active-filter-v1 */
/* presence-filter-v1 */
/* livechat-active-agents-v1 */
/* livechat-ticket-required-v1 */
/* portal-livechat-v2 */
import { useState, useEffect, useRef, useMemo } from 'react';
import clsx from 'clsx';
import { Send, Paperclip, MessageCircle, Sparkles, Clock, Building2, Ticket, Circle } from 'lucide-react';
import AgentAvatar from './AgentAvatar';
import { usePlatform } from '../context/PlatformContext';
import { useTickets } from '../context/TicketContext';
import { useAuth } from '../context/AuthContext';
import { MAX_CHAT_FILE_BYTES } from '../types';
import { encodeChatAttachment, parseChatAttachment, isImageMime } from '../lib/chatAttachments';

const STORAGE_KEY = 'nexus-portal-chat-id';

const BRANCH_OPTIONS = [
  'Abucay',
  'Abuyog',
  'Avenida',
  'Baybay',
  'Burauen',
  'Calbayog',
  'Carigara',
  'Catarman',
  'Catbalogan',
  'Kananga',
  'Maasin',
  'Ormoc',
  'Palo-Naga',
  'Palo-Pawing',
  'Palo-Schisto',
  'Sogod',
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

export default function PortalLiveChat({ onBack }: Props) {
  const { conversations, createChat, sendChatMessage, refreshPlatform } = usePlatform();
  const { findTicket, agents } = useTickets();
  const { user } = useAuth();

  const accountName =
    (user?.user_metadata?.full_name as string | undefined)?.trim() ||
    (user?.user_metadata?.name as string | undefined)?.trim() ||
    user?.email?.split('@')[0] ||
    '';

  const [name, setName] = useState(accountName);
  const [email, setEmail] = useState(user?.email || '');
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

  useEffect(() => {
    if (accountName) setName(accountName);
  }, [accountName]);

  useEffect(() => {
    if (user?.email) setEmail(user.email);
  }, [user?.email]);

  const conversation = conversations.find((c) => c.id === chatId) || null;
  const messages = conversation?.messages || [];

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

  const [presenceTick, setPresenceTick] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => setPresenceTick((n) => n + 1), 10000);
    return () => window.clearInterval(id);
  }, []);

  const onlineAgents = useMemo(() => {
    const now = Date.now();
    const LIVE_WINDOW_MS = 45_000;
    return (agents || []).filter((a) => {
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved') return false;
      const status = (a.status || 'offline').toLowerCase();
      if (status === 'offline' || status === '') return false;
      const seen = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
      if (!seen || Number.isNaN(seen)) return false;
      return now - seen <= LIVE_WINDOW_MS;
    });
  }, [agents, presenceTick]);

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
      const parts = [`Hi, I'm ${nm}.`];
      if (br) parts.push(`Branch: ${br}.`);
      if (tid) parts.push(`Ticket: ${tid}.`);
      parts.push('I need assistance.');
      await sendChatMessage(c.id, parts.join(' '), 'customer');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not start chat');
    } finally {
      setStarting(false);
    }
  };

  const send = async () => {
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
      const dataUrl = await encodeChatAttachment(file);
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
        <div className="grid lg:grid-cols-12 gap-5 lg:gap-6 items-start">
          <div className="lg:col-span-7 space-y-4">
            <div className="portal-overview-glass rounded-2xl p-5 sm:p-6">
              <div className="flex items-start gap-3 mb-5">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/25 shrink-0">
                  <MessageCircle className="text-white" size={24} />
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-0.5">
                    Connect with a support agent in real time.
                  </p>
                </div>
              </div>

              <form onSubmit={start} className="space-y-4">
                {error && (
                  <div className="text-sm text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-500/30 px-3 py-2 rounded-xl">
                    {error}
                  </div>
                )}

                <div>
                  <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Your name</label>
                  <input
                    value={name}
                    readOnly
                    required
                    className={`${field} opacity-90 cursor-not-allowed bg-white/40 dark:bg-white/5`}
                    title="Filled from your account — cannot be changed"
                  />
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Locked to your registered account name.</p>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Email</label>
                  <input
                    type="email"
                    value={email}
                    readOnly
                    disabled
                    className={`${field} opacity-80 cursor-not-allowed`}
                    placeholder="you@email.com"
                  />
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">
                    Locked to your registered account email.
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
                    Ticket number
                  </label>
                  <input
                    value={ticketId}
                    onChange={(e) => setTicketId(e.target.value)}
                    placeholder="e.g. NX-2841"
                    required
                    className={`${field} font-mono`}
                  />
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">
                    Enter a ticket ID — branch fills in automatically when found.
                  </p>
                  {ticketHint && (
                    <p
                      className={`text-[11px] mt-1 ${
                        ticketHint.startsWith('Found') ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'
                      }`}
                    >
                      {ticketHint}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
                    Branch
                  </label>
                  <select value={branch} onChange={(e) => setBranch(e.target.value)} className={field}>
                    <option value="">Select branch…</option>
                    {branchOptions.map((b) => (
                      <option key={b} value={b}>
                        {b}
                      </option>
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
                  <p className="text-[11px] text-center text-amber-600 dark:text-amber-400 mt-2">
                    Chat is unavailable until an agent or admin is online.
                  </p>
                )}
              </form>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-4">
            <div className="portal-overview-glass rounded-2xl p-4 sm:p-5">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/15 text-emerald-600 dark:text-emerald-300 flex items-center justify-center">
                  <Sparkles size={16} />
                </div>
                <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Before you start</h2>
              </div>
              <ul className="space-y-2.5 text-[13px] text-zinc-600 dark:text-zinc-300">
                <li className="flex gap-2">
                  <span className="text-emerald-500 shrink-0">•</span>
                  <span>Agents are typically available during business hours.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-500 shrink-0">•</span>
                  <span>Link a ticket number if this is about an existing request.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-500 shrink-0">•</span>
                  <span>You can attach screenshots after the chat starts.</span>
                </li>
              </ul>
              <div className="mt-4 flex flex-wrap gap-2 text-[11px] text-zinc-500 dark:text-zinc-400">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-white/20 bg-white/30 dark:bg-white/5">
                  <span className={`w-1.5 h-1.5 rounded-full ${hasAgentOnline ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-400'}`} />
                  {hasAgentOnline ? `${onlineAgents.length} agent${onlineAgents.length === 1 ? '' : 's'} online` : 'No agents online'}
                </span>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-white/20 bg-white/30 dark:bg-white/5">
                  <Clock size={12} /> Typical wait: a few minutes
                </span>
              </div>
            </div>
            <div className="portal-overview-glass rounded-2xl p-4 sm:p-5">
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/15 text-emerald-600 dark:text-emerald-300 flex items-center justify-center">
                    <Circle size={14} className={hasAgentOnline ? 'fill-emerald-500 text-emerald-500' : 'text-zinc-400'} />
                  </div>
                  <div>
                    <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Active now</h2>
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
                      {hasAgentOnline
                        ? `${onlineAgents.length} agent${onlineAgents.length === 1 ? '' : 's'} available`
                        : 'No agents online'}
                    </p>
                  </div>
                </div>
                <span
                  className={`text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full border ${
                    hasAgentOnline
                      ? 'border-emerald-400/40 bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                      : 'border-zinc-400/30 bg-zinc-500/10 text-zinc-500'
                  }`}
                >
                  {hasAgentOnline ? 'Live' : 'Offline'}
                </span>
              </div>
              {hasAgentOnline ? (
                <ul className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                  {onlineAgents.map((a) => (
                    <li
                      key={a.id}
                      className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 dark:bg-black/20 px-2.5 py-2"
                    >
                      <div className="relative shrink-0">
                        <AgentAvatar agent={a} size="sm" />
                        <span
                          className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-zinc-900 ${
                            (() => {
                              const st = (a.status || '').toLowerCase();
                              if (st === 'busy') return 'bg-yellow-400';
                              if (st === 'in_call') return 'bg-orange-400';
                              if (st === 'away') return 'bg-sky-400';
                              if (st === 'custom') return 'bg-white';
                              return 'bg-emerald-400';
                            })()
                          }`}
                          title={(a.status || 'online').toString()}
                        />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium text-zinc-900 dark:text-zinc-50 truncate">
                          {a.name}
                          {a.is_admin ? (
                            <span className="ml-1.5 text-[10px] font-semibold text-violet-500 dark:text-violet-300">Admin</span>
                          ) : null}
                        </div>
                        <div className="text-[11px] truncate flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full shrink-0 bg-emerald-400" />
                          {a.status_emoji ? <span className="shrink-0">{a.status_emoji}</span> : null}
                          <span
                            className={(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'away') return 'text-sky-400 font-medium';
                              if (st === 'busy') return 'text-yellow-300 font-medium';
                              if (st === 'in_call') return 'text-orange-400 font-medium';
                              if (st === 'custom') return 'text-white font-medium';
                              return 'text-emerald-400 font-medium';
                            })()}
                          >
                            {(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'busy') return 'Busy';
                              if (st === 'away') return 'Away';
                              if (st === 'in_call') return 'In a call';
                              if (st === 'custom') return a.status_message || 'Custom status';
                              return 'Available';
                            })()}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="rounded-xl border border-dashed border-white/15 bg-black/10 px-3 py-6 text-center">
                  <p className="text-sm text-zinc-600 dark:text-zinc-300">No agents or admins are online.</p>
                  <p className="text-[11px] text-zinc-500 mt-1">Please check back during business hours.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] portal-overview-glass rounded-2xl overflow-hidden border border-white/15">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/30 dark:bg-black/20">
        <div className="flex items-center gap-2 min-w-0">
          <MessageCircle size={18} className="text-violet-600 dark:text-violet-300 shrink-0" />
          <div className="min-w-0">
            <div className="text-sm font-semibold text-zinc-900 dark:text-white truncate">Live Chat</div>
            <div className="text-[11px] text-zinc-500 dark:text-zinc-400 truncate">
              {conversation?.status === 'ended' ? 'Chat ended' : 'Connected with support'}
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={() => {
            sessionStorage.removeItem(STORAGE_KEY);
            setChatId(null);
          }}
          className="text-xs text-zinc-500 hover:text-rose-600 dark:hover:text-rose-400 px-2 py-1 rounded-lg hover:bg-white/40 dark:hover:bg-white/5"
        >
          End / new chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-transparent">
        {messages.map((m) => {
          const mine = m.sender === 'customer';
          const att = parseChatAttachment(m.body);
          return (
            <div key={m.id} className={clsx('flex', mine ? 'justify-end' : 'justify-start')}>
              <div
                className={clsx(
                  'max-w-[85%] rounded-2xl px-3.5 py-2 text-sm',
                  mine
                    ? 'bg-violet-600 text-white rounded-br-md'
                    : 'bg-white/70 dark:bg-zinc-900/70 text-zinc-800 dark:text-zinc-100 border border-white/20 dark:border-white/10 rounded-bl-md',
                )}
              >
                {att ? (
                  isImageMime(att.mime) ? (
                    <img src={att.url} alt={att.name} className="max-h-48 rounded-lg" />
                  ) : (
                    <a href={att.url} download={att.name} className="underline">
                      {att.name}
                    </a>
                  )
                ) : (
                  m.body
                )}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {conversation?.status !== 'ended' && (
        <div className="border-t border-white/10 p-3 bg-white/25 dark:bg-black/25 space-y-2">
          <div className="flex flex-wrap gap-1.5">
            {QUICK_REPLIES.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => setDraft(q)}
                className="text-[11px] px-2 py-1 rounded-full border border-white/20 bg-white/40 dark:bg-white/5 text-zinc-600 dark:text-zinc-300 hover:border-violet-400/40"
              >
                {q}
              </button>
            ))}
          </div>
          {fileError && <p className="text-[11px] text-rose-500">{fileError}</p>}
          <div className="flex items-end gap-2">
            <input
              ref={fileRef}
              type="file"
              className="hidden"
              accept="image/*,.pdf,.txt"
              onChange={(e) => void onFile(e.target.files?.[0] || null)}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="p-2.5 rounded-xl border border-white/20 text-zinc-500 hover:text-violet-600 dark:hover:text-violet-300"
              title="Attach"
            >
              <Paperclip size={18} />
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
              placeholder="Type a message…"
              className="flex-1 resize-none px-3 py-2.5 text-sm rounded-xl border border-zinc-200 dark:border-white/15 bg-white/80 dark:bg-zinc-900/70 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={!draft.trim()}
              className="p-2.5 rounded-xl bg-violet-600 text-white hover:bg-violet-500 disabled:opacity-40"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
