"""Show ticket info + customer/agent names & avatars on customer live chat."""
from pathlib import Path
import re

plv = Path('src/components/PortalLiveChatView.tsx')
if not plv.exists():
    print('PLV missing')
    raise SystemExit(0)

s = plv.read_text()
if 'CUSTOMER_CHAT_IDENTITY_V1' in s:
    print('already applied')
    raise SystemExit(0)

if 'findTicket' not in s:
    s = s.replace(
        'const { agents } = useTickets();',
        'const { agents, findTicket, tickets } = useTickets();',
        1,
    )
    print('findTicket hook')

anchor = '''  const conversation = useMemo(
    () => (chatId ? conversations.find((c) => c.id === chatId) : null),
    [conversations, chatId],
  );
  const messages = conversation?.messages || [];
  const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';'''

helper = '''  const conversation = useMemo(
    () => (chatId ? conversations.find((c) => c.id === chatId) : null),
    [conversations, chatId],
  );
  const messages = conversation?.messages || [];
  const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';

  // CUSTOMER_CHAT_IDENTITY_V1 — ticket strip + party names/avatars
  const linkedTicketId = useMemo(() => {
    const direct = (conversation?.ticket_id || '').trim();
    if (direct) return direct;
    for (const m of messages) {
      const t = (m.text || m.body || '');
      const hit = t.match(/Ticket:\\s*([A-Za-z0-9\\-_]+)/i);
      if (hit) return hit[1];
    }
    return '';
  }, [conversation?.ticket_id, messages]);

  const linkedTicket = useMemo(() => {
    if (!linkedTicketId) return null;
    try {
      if (typeof findTicket === 'function') {
        const t = findTicket(linkedTicketId);
        if (t) return t;
      }
    } catch {}
    const list = tickets || [];
    return (
      list.find((t: any) => String(t.id) === linkedTicketId || String(t.number) === linkedTicketId || String(t.code) === linkedTicketId) ||
      null
    );
  }, [linkedTicketId, findTicket, tickets]);

  const customerName =
    conversation?.customer_name ||
    user?.user_metadata?.full_name ||
    user?.email?.split('@')[0] ||
    'You';
  const customerEmail = conversation?.customer_email || user?.email || '';
  const customerInitials = customerName
    .split(/\\s+/)
    .map((x) => x[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'Y';

  const assignedAgent = useMemo(() => {
    const aid = (conversation as any)?.agent_id;
    if (!aid) return null;
    return (agents || []).find((a: any) => a.id === aid) || null;
  }, [conversation, agents]);

  const agentName = assignedAgent?.name || 'Support agent';
  const agentAvatar = assignedAgent?.avatar_url || '';
  const agentInitials = agentName
    .split(/\\s+/)
    .map((x: string) => x[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'A';
'''

if anchor in s:
    s = s.replace(anchor, helper, 1)
    print('helpers')
else:
    print('anchor miss')

m = re.search(
    r'(<div className="px-4 py-3 border-b border-zinc-200/50 dark:border-white/10 flex items-center justify-between gap-3">.*?</div>\\s*)(\{isOnHold &&)',
    s,
    re.S,
)
if m:
    new_header = '''<div className="px-4 py-3 border-b border-zinc-200/50 dark:border-white/10 space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2 min-w-0">
              <MessageCircle size={16} className="text-violet-600 dark:text-violet-400 shrink-0" />
              <span className="truncate">Live Chat</span>
              <span className="text-[11px] font-normal text-zinc-500 truncate">
                {conversation ? `Connected · ${conversation.id.slice(0, 8)}` : ''}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center gap-2 rounded-full border border-zinc-200/70 dark:border-white/10 bg-white/70 dark:bg-white/5 px-2.5 py-1">
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[9px] font-bold text-white overflow-hidden">
                {customerInitials}
              </div>
              <div className="leading-tight">
                <div className="text-[11px] font-semibold text-zinc-800 dark:text-zinc-100">{customerName}</div>
                <div className="text-[10px] text-zinc-500">You</div>
              </div>
            </div>
            <span className="text-[10px] text-zinc-400">↔</span>
            <div className="inline-flex items-center gap-2 rounded-full border border-violet-300/40 dark:border-violet-400/20 bg-violet-500/10 px-2.5 py-1">
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[9px] font-bold text-white overflow-hidden">
                {agentAvatar ? (
                  <img src={agentAvatar} alt="" className="w-full h-full object-cover" />
                ) : (
                  agentInitials
                )}
              </div>
              <div className="leading-tight">
                <div className="text-[11px] font-semibold text-zinc-800 dark:text-zinc-100">{agentName}</div>
                <div className="text-[10px] text-zinc-500">{assignedAgent ? 'Agent' : 'Waiting for agent'}</div>
              </div>
            </div>
          </div>

          {(linkedTicketId || linkedTicket) && (
            <div className="rounded-xl border border-amber-400/25 bg-amber-500/10 px-3 py-2 text-xs text-amber-900 dark:text-amber-100">
              <div className="font-semibold tracking-wide uppercase text-[10px] text-amber-700 dark:text-amber-300 mb-0.5">Ticket in progress</div>
              <div className="font-medium">
                {linkedTicketId}
                {linkedTicket?.subject ? ` · ${linkedTicket.subject}` : ''}
              </div>
              <div className="text-[11px] opacity-80 mt-0.5 flex flex-wrap gap-x-3 gap-y-0.5">
                {linkedTicket?.status ? <span>Status: {String(linkedTicket.status)}</span> : null}
                {linkedTicket?.branch ? <span>Branch: {String(linkedTicket.branch)}</span> : null}
                {linkedTicket?.priority ? <span>Priority: {String(linkedTicket.priority)}</span> : null}
              </div>
            </div>
          )}
        </div>

        {isOnHold &&'''
    s = s[: m.start(1)] + new_header + s[m.start(2) :]
    print('header replaced')
else:
    print('header regex miss')

msg_start = s.find('{messages.map((m) => {')
if msg_start != -1 and 'whoName' not in s:
    end = s.find('<div ref={bottomRef}', msg_start)
    if end != -1:
        body = '''{att ? (
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
                  )}'''
        new_map = f'''{{messages.map((m, i) => {{
            const mine = m.sender === 'customer';
            const parsed = parseChatAttachment(m.text || m.body || '');
            const att = parsed.att;
            const displayText = (parsed.text || m.text || m.body || '').trim();
            const whoName = mine ? customerName : agentName;
            const whoInitials = mine ? customerInitials : agentInitials;
            const whoAvatar = mine ? '' : agentAvatar;
            return (
              <div
                key={{m.id || i}}
                className={{clsx('flex items-end gap-2', mine ? 'justify-end' : 'justify-start')}}
              >
                {{!mine && (
                  <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden">
                    {{whoAvatar ? (
                      <img src={{whoAvatar}} alt="" className="w-full h-full object-cover" />
                    ) : (
                      whoInitials
                    )}}
                  </div>
                )}}
                <div
                  className={{clsx(
                    'max-w-[75%] rounded-2xl px-3.5 py-2.5 text-sm shadow-sm',
                    mine
                      ? 'bg-violet-600 text-white rounded-br-md'
                      : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10 rounded-bl-md',
                  )}}
                >
                  <div className={{clsx('text-[10px] font-semibold mb-0.5', mine ? 'opacity-80' : 'opacity-70')}}>
                    {{whoName}}
                  </div>
                  {body}
                </div>
                {{mine && (
                  <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10">
                    {{customerInitials}}
                  </div>
                )}}
              </div>
            );
          }})}}
          '''
        s = s[:msg_start] + new_map + s[end:]
        print('bubbles replaced')
    else:
        print('bottomRef not found')
else:
    print('messages.map skip')

plv.write_text(s)
print('DONE')
