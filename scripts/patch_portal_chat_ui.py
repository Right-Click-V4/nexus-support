#!/usr/bin/env python3
"""Portal live chat UI: show agent name when present, avatars, wider layout; stamp agent_id on agent send."""
from pathlib import Path

def patch_platform():
    p = Path('src/context/PlatformContext.tsx')
    if not p.exists():
        return
    s = p.read_text()
    a = (
        "const _ns = _held ? 'on_hold' : 'active';\n"
        "      const _pv = _held ? '__HOLD__' + msg.text.slice(0, 120) : msg.text.slice(0, 120);\n"
        "      await supabase.from('chat_conversations').update({ preview: _pv, status: _ns, unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);"
    )
    b = (
        "const _ns = _held ? 'on_hold' : 'active';\n"
        "      const _pv = _held ? '__HOLD__' + msg.text.slice(0, 120) : msg.text.slice(0, 120);\n"
        "      const _upd: Record<string, unknown> = { preview: _pv, status: _ns, unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() };\n"
        "      if (sender === 'agent' && user?.id) _upd.agent_id = user.id;\n"
        "      await supabase.from('chat_conversations').update(_upd).eq('id', conversationId);"
    )
    if a in s:
        s = s.replace(a, b, 1)
        print('platform agent_id nuclear path')
    a2 = (
        "await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', "
        "unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);"
    )
    b2 = (
        "const _upd2: Record<string, unknown> = { preview: msg.text.slice(0, 120), status: 'active', "
        "unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() };\n"
        "      if (sender === 'agent' && user?.id) _upd2.agent_id = user.id;\n"
        "      await supabase.from('chat_conversations').update(_upd2).eq('id', conversationId);"
    )
    if a2 in s:
        s = s.replace(a2, b2, 1)
        print('platform agent_id stock path')
    p.write_text(s)


def patch_portal():
    pv = Path('src/components/PortalLiveChatView.tsx')
    if not pv.exists():
        return
    t = pv.read_text()

    if 'const assignedAgent' not in t:
        anchor = '  const hasAgentOnline = onlineAgents.length > 0;'
        helper = '''  const hasAgentOnline = onlineAgents.length > 0;

  const customerName = (name || conversation?.customer_name || user?.email?.split('@')[0] || 'You').trim();
  const customerInitials = customerName.split(/\\s+/).map((x) => x[0]).join('').slice(0, 2).toUpperCase() || 'Y';
  const userMeta = (user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata || {};
  const customerAvatar = String(userMeta.avatar_url || userMeta.picture || '').trim();

  const assignedAgent = useMemo(() => {
    const aid = (conversation as { agent_id?: string } | null)?.agent_id;
    if (aid) {
      const hit = (agents || []).find((a) => a.id === aid);
      if (hit) return hit;
    }
    const hasAgentMsg = (messages || []).some((m) => m.sender === 'agent');
    if (!hasAgentMsg) return null;
    if (onlineAgents.length) {
      const full = (agents || []).find((a) => a.id === onlineAgents[0].id);
      if (full) return full;
    }
    return (agents || [])[0] || null;
  }, [conversation, agents, messages, onlineAgents]);

  const agentName = assignedAgent?.name || 'Support agent';
  const agentAvatar = assignedAgent?.avatar_url || '';
  const agentInitials = agentName.split(/\\s+/).map((x) => x[0]).join('').slice(0, 2).toUpperCase() || 'A';
  const agentPresent =
    Boolean(assignedAgent) ||
    (messages || []).some((m) => m.sender === 'agent') ||
    ['active', 'on_hold', 'on-hold'].includes((conversation?.status || '').toLowerCase());
'''
        if anchor in t:
            t = t.replace(anchor, helper, 1)
            print('helpers')
        else:
            print('WARN helpers anchor')

    t = t.replace(
        "{assignedAgent ? 'Agent' : 'Waiting for agent'}",
        "{agentPresent ? 'Chatting with you' : 'Waiting for agent'}",
    )
    t = t.replace('max-w-3xl mx-auto', 'max-w-6xl mx-auto w-full')
    t = t.replace('min-h-[60vh]', 'min-h-[78vh]')
    t = t.replace('min-h-[75vh]', 'min-h-[78vh]')
    t = t.replace('max-h-[50vh]', 'max-h-[min(70vh,720px)]')

    old_cust = '''              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[9px] font-bold text-white overflow-hidden">
                {customerInitials}
              </div>'''
    new_cust = '''              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[9px] font-bold text-white overflow-hidden">
                {customerAvatar ? (
                  <img src={customerAvatar} alt="" className="w-full h-full object-cover" />
                ) : (
                  customerInitials
                )}
              </div>'''
    if old_cust in t:
        t = t.replace(old_cust, new_cust, 1)
    t = t.replace(
        'w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600',
        'w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600',
    )

    start = t.find('{messages.map((m')
    end = t.find('<div ref={bottomRef}', start) if start >= 0 else -1
    if start >= 0 and end >= 0:
        new_map = r'''{messages.map((m, i) => {
            const mine = m.sender === 'customer';
            const parsed = parseChatAttachment(m.text || m.body || '');
            const att = parsed.att;
            const displayText = (parsed.text || m.text || m.body || '').trim();
            const whoName = mine ? customerName : agentName;
            const whoInitials = mine ? customerInitials : agentInitials;
            const whoAvatar = mine ? customerAvatar : agentAvatar;
            return (
              <div
                key={m.id || i}
                className={clsx('flex items-end gap-2', mine ? 'justify-end' : 'justify-start')}
              >
                {!mine && (
                  <div className="shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden">
                    {whoAvatar ? (
                      <img src={whoAvatar} alt="" className="w-full h-full object-cover" />
                    ) : (
                      whoInitials
                    )}
                  </div>
                )}
                <div className={clsx(mine ? 'items-end' : 'items-start')}>
                  <div className={clsx('text-[10px] mb-0.5 px-1 font-medium text-zinc-400', mine ? 'text-right' : 'text-left')}>
                    {whoName}
                  </div>
                  <div
                    className={clsx(
                      'max-w-[min(72vw,520px)] rounded-2xl px-3.5 py-2.5 text-sm shadow-sm',
                      mine
                        ? 'bg-violet-600 text-white rounded-br-md'
                        : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10 rounded-bl-md',
                    )}
                  >
                    {att?.url ? (
                      <div className="space-y-1">
                        {isImageMime(att.mime) ? (
                          <img src={att.url} alt={att.name || 'attachment'} className="max-w-full rounded-lg" />
                        ) : (
                          <a href={att.url} download={att.name} className="underline">
                            {att.name || 'Download file'}
                          </a>
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
                {mine && (
                  <div className="shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden">
                    {whoAvatar ? (
                      <img src={whoAvatar} alt="" className="w-full h-full object-cover" />
                    ) : (
                      whoInitials
                    )}
                  </div>
                )}
              </div>
            );
          })}
          '''
        t = t[:start] + new_map + t[end:]
        print('bubbles')

    pv.write_text(t)
    print('portal ui done', pv.stat().st_size)


patch_platform()
patch_portal()
print('DONE')
