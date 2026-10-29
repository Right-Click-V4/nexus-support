/* livechat-ticket-required-v1 */
/* portal-livechat-v2 */
import { useState, useEffect, useRef, useMemo } from 'react';
import clsx from 'clsx';
import { Send, Paperclip, MessageCircle, Sparkles, Clock, Building2, Ticket } from 'lucide-react';
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
  const { findTicket } = useTickets();
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
                  disabled={starting}
                  className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25 disabled:opacity-50 transition-all"
                >
                  {starting ? 'Connecting…' : 'Start chat'}
                </button>
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
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Agents online
                </span>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-white/20 bg-white/30 dark:bg-white/5">
                  <Clock size={12} /> Typical wait: a few minutes
                </span>
              </div>
            </div>
            <div className="portal-overview-glass rounded-2xl p-4 sm:p-5">
              <div className="flex items-center gap-2 mb-2">
                <Building2 size={16} className="text-violet-600 dark:text-violet-300" />
                <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Branch list</h2>
              </div>
              <p className="text-[12px] text-zinc-600 dark:text-zinc-400 mb-2">
                Same branches as Submit a Ticket — pick the site this chat is about.
              </p>
              <div className="flex flex-wrap gap-1.5">
                {BRANCH_OPTIONS.slice(0, 8).map((b) => (
                  <span
                    key={b}
                    className="text-[10px] px-2 py-0.5 rounded-md bg-violet-500/10 text-violet-800 dark:text-violet-200 border border-violet-400/20"
                  >
                    {b}
                  </span>
                ))}
                <span className="text-[10px] px-2 py-0.5 text-zinc-500">+ more in the list</span>
              </div>
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
