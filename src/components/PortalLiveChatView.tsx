/* portal-live-chat-v1 */
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  MessageCircle, Paperclip, Send, X, Sparkles, Circle, Users,
} from 'lucide-react';
import clsx from 'clsx';
import { usePlatform } from '../context/PlatformContext';
import { useTickets } from '../context/TicketContext';
import { useAuth } from '../context/AuthContext';
import { encodeChatFile, parseChatAttachment, isImageMime } from '../lib/chatAttachments';

const QUICK_REPLIES = [
  'I need help with my account',
  'Billing question',
  'Something is broken',
  'Thanks, that fixed it',
];

interface Props {
  onBack?: () => void;
}

export default function PortalLiveChatView({ onBack }: Props) {
  const { user } = useAuth();
  const { agents } = useTickets();
  const { conversations, createChat, sendChatMessage, refreshPlatform } = usePlatform();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [ticketId, setTicketId] = useState('');
  const [branch, setBranch] = useState('');
  const [chatId, setChatId] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [fileError, setFileError] = useState('');
  const fileRef = useRef<HTMLInputElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (user?.email) setEmail(user.email);
    const meta = (user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata || {};
    const nm = String(meta.full_name || meta.name || '').trim();
    if (nm) setName(nm);
  }, [user]);

  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);

  const conversation = useMemo(
    () => (chatId ? conversations.find((c) => c.id === chatId) : null),
    [conversations, chatId],
  );
  const messages = conversation?.messages || [];
  const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';

  const onlineAgents = useMemo(() => {
    return (agents || []).filter((a) => {
      const s = (a.status || '').toLowerCase();
      return s === 'online' || s === 'available' || s === 'busy';
    });
  }, [agents]);
  const hasAgentOnline = onlineAgents.length > 0;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length, chatId]);

  const startChat = async () => {
    setError('');
    const nm = name.trim() || user?.email?.split('@')[0] || 'Customer';
    if (!nm) {
      setError('Please enter your name.');
      return;
    }
    setBusy(true);
    try {
      const c = await createChat(nm, (user?.email || email).trim() || undefined, {
        branch: branch.trim() || undefined,
        ticket_id: ticketId.trim() || undefined,
      });
      setChatId(c.id);
      const lines = [
        `Hi, I need support.`,
        ticketId.trim() ? `Ticket: ${ticketId.trim()}` : '',
        branch.trim() ? `Branch: ${branch.trim()}` : '',
      ].filter(Boolean);
      await sendChatMessage(c.id, lines.join('\n'), 'customer');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start chat');
    } finally {
      setBusy(false);
    }
  };

  const send = async () => {
    if (!chatId) return;
    const text = draft.trim();
    if (!text) return;
    setDraft('');
    await sendChatMessage(chatId, text, 'customer');
  };

  const onFile = async (file: File | null) => {
    if (!file || !chatId) return;
    setFileError('');
    try {
      const payload = await encodeChatFile(file);
      await sendChatMessage(chatId, payload, 'customer');
    } catch (e) {
      setFileError(e instanceof Error ? e.message : 'Upload failed');
    }
  };

  const field =
    'w-full px-3 py-2.5 text-sm rounded-xl border border-zinc-200 dark:border-white/15 bg-white/80 dark:bg-zinc-900/70 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400';

  if (!chatId) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
              <MessageCircle size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Talk to a support agent in real time.
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-zinc-950/40 p-5 space-y-4">
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <div>
            <label className="text-xs font-medium text-zinc-400">Your name</label>
            <input className={field} value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
            <p className="text-[11px] text-zinc-500 mt-1">Locked to your registered account name.</p>
          </div>
          <div>
            <label className="text-xs font-medium text-zinc-400">Email</label>
            <input className={field} value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" />
            <p className="text-[11px] text-zinc-500 mt-1">Locked to your registered account email.</p>
          </div>
          <div>
            <label className="text-xs font-medium text-zinc-400">Ticket number</label>
            <input className={field} value={ticketId} onChange={(e) => setTicketId(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <label className="text-xs font-medium text-zinc-400">Branch</label>
            <input className={field} value={branch} onChange={(e) => setBranch(e.target.value)} placeholder="Optional" />
          </div>
          <button
            type="button"
            disabled={busy}
            onClick={() => void startChat()}
            className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {busy ? 'Connecting…' : 'Start live chat'}
          </button>
          {!hasAgentOnline && (
            <p className="text-xs text-amber-400 text-center">
              No agents appear online right now. You can still start a chat — we will respond when available.
            </p>
          )}
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div className="rounded-2xl border border-white/10 bg-zinc-950/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={16} className="text-violet-400" />
              <h2 className="text-sm font-semibold text-zinc-100">Before you start</h2>
            </div>
            <ul className="text-xs text-zinc-400 space-y-1.5 list-disc pl-4">
              <li>Have your ticket ID ready if this is about an existing request.</li>
              <li>Describe the issue in one short message first.</li>
              <li>You can attach screenshots after the chat starts.</li>
            </ul>
            <div className="flex flex-wrap gap-1.5 mt-3">
              <span className="text-[11px] px-2 py-1 rounded-full border border-white/15 text-zinc-300">
                Avg reply under 5 min
              </span>
              <span className="text-[11px] px-2 py-1 rounded-full border border-white/15 text-zinc-300 flex items-center gap-1">
                <Users size={10} /> {onlineAgents.length} agent{onlineAgents.length === 1 ? '' : 's'} online
              </span>
            </div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-zinc-950/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <Circle size={10} className={hasAgentOnline ? 'text-emerald-400 fill-emerald-400' : 'text-zinc-500'} />
              <h2 className="text-sm font-semibold text-zinc-100">Active now</h2>
              {hasAgentOnline && (
                <span className="text-[10px] font-bold uppercase tracking-wide text-emerald-400 border border-emerald-500/40 px-1.5 py-0.5 rounded">LIVE</span>
              )}
            </div>
            <p className="text-[11px] text-zinc-500 mb-2">
              Agents currently available on the desk.
            </p>
            {onlineAgents.length > 0 ? (
              <ul className="space-y-2">
                {onlineAgents.slice(0, 5).map((a) => (
                  <li key={a.id} className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <div className="min-w-0">
                      <div className="text-xs font-medium text-zinc-100 truncate">{a.name}</div>
                      <div className="text-[11px] text-emerald-400 capitalize">{a.status || 'online'}</div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-zinc-500">No agents are available right now. Please try again later.</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="rounded-2xl border border-white/10 bg-zinc-950/50 overflow-hidden flex flex-col min-h-[60vh]">
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between gap-3">
          <div className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
            <MessageCircle size={16} className="text-violet-400" /> Live Chat
            <span className="text-[11px] font-normal text-zinc-500">
              {conversation ? `Connected · ${conversation.id.slice(0, 8)}` : ''}
            </span>
          </div>
          <button
            type="button"
            onClick={() => {
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
            const parsed = parseChatAttachment(m.text || m.body || '');
            const att = parsed.att;
            const displayText = (parsed.text || m.text || m.body || '').trim();
            return (
              <div key={m.id} className={clsx('flex', mine ? 'justify-end' : 'justify-start')}>
                <div className={clsx(
                  'max-w-[85%] rounded-2xl px-3 py-2 text-sm',
                  mine ? 'bg-violet-600 text-white' : 'bg-white/10 text-zinc-100 border border-white/10',
                )}>
                  {att?.url ? (
                    <div className="space-y-1">
                      {isImageMime(att.mime) ? (
                        <img src={att.url} alt={att.name || 'attachment'} className="max-w-full rounded-lg" />
                      ) : (
                        <a href={att.url} download={att.name} className="underline">{att.name || 'Download file'}</a>
                      )}
                      {displayText ? (
                        <div className="whitespace-pre-wrap break-words">{displayText}</div>
                      ) : null}
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap break-words">{displayText || '…'}</div>
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
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    void send();
                  }
                }}
                placeholder="Type a message…"
              />
              <button
                type="button"
                onClick={() => void send()}
                className="p-2.5 rounded-xl bg-violet-600 text-white hover:bg-violet-500"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
      {onBack && (
        <button type="button" onClick={onBack} className="mt-3 text-xs text-zinc-500 hover:text-zinc-300">
          ← Back to portal
        </button>
      )}
    </div>
  );
}
