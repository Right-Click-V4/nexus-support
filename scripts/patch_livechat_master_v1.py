#!/usr/bin/env python3
"""Master live-chat fix: platform helpers, claim UI dedupe, customer agent identity, realtime, customers 400."""
from pathlib import Path
import re

ROOT = Path('.')

def ensure_platform():
    p = ROOT / 'src/context/PlatformContext.tsx'
    if not p.exists() or p.stat().st_size < 5000:
        print('WARN PlatformContext still tiny', p.stat().st_size if p.exists() else 0)
        return False
    s = p.read_text()

    s2, n = re.subn(
        r"supabase\.from\('chat_conversations'\)\.select\('[^']*'\)\.order\('updated_at'",
        "supabase.from('chat_conversations').select('id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,assignee_id,ticket_id,branch,archived_at').order('updated_at'",
        s, count=1,
    )
    s = s2
    if n:
        print('select expanded')

    if 'row.agent_id || row.assignee_id' not in s:
        old = """      setConversations(
        (chats.data as ChatConversation[]).map((c) => ({
          ...c,
          messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          })),
        })),
      );"""
        new = """      setConversations(
        (chats.data as ChatConversation[]).map((c) => {
          const row = c as ChatConversation & { assignee_id?: string };
          const agentId = row.agent_id || row.assignee_id || undefined;
          return {
            ...c,
            agent_id: agentId,
            messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
              ...mm,
              text: mm.text || mm.body || '',
              body: mm.body || mm.text || '',
            })),
          };
        }),
      );"""
        if old in s:
            s = s.replace(old, new, 1)
            print('agent_id map')

    s = s.replace(
        "setInterval(() => { void refreshPlatform(); }, 3000);",
        "setInterval(() => { void refreshPlatform(); }, 1500); // LIVECHAT_MASTER_V1",
        1,
    )

    if 'const claimChat' not in s:
        claim = '''
  const claimChat = async (conversationId: string, agentId: string) => {
    if (!agentId) return;
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              agent_id: agentId,
              status: (c.status === 'waiting' || c.status === 'on_hold' ? 'active' : c.status) as ChatConversation['status'],
            }
          : c,
      ),
    );
    if (!supabase) return;
    const now = new Date().toISOString();
    for (const patch of [
      { agent_id: agentId, assignee_id: agentId, status: 'active', updated_at: now },
      { agent_id: agentId, status: 'active', updated_at: now },
      { assignee_id: agentId, status: 'active', updated_at: now },
    ]) {
      const { error } = await supabase.from('chat_conversations').update(patch).eq('id', conversationId);
      if (!error) break;
    }
    try { await refreshPlatform(); } catch {}
  };

'''
        if '  const archiveChat = async' in s:
            s = s.replace('  const archiveChat = async', claim + '  const archiveChat = async', 1)
        elif '  const setChatStatus = async' in s:
            s = s.replace('  const setChatStatus = async', claim + '  const setChatStatus = async', 1)
        print('claimChat added')

    if 'claimChat:' not in s:
        s = s.replace(
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;\n  claimChat: (conversationId: string, agentId: string) => Promise<void>;",
            1,
        )
        s = s.replace(
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;\n  claimChat: (conversationId: string, agentId: string) => Promise<void>;",
            1,
        )

    if 'LIVECHAT_MASTER_SEND' not in s:
        m = re.search(r"const sendChatMessage = async \([^)]*\) => \{.*?\n  \};", s, re.S)
        if m and 'LIVECHAT_MASTER_SEND' not in m.group(0):
            new_send = '''const sendChatMessage = async (
    conversationId: string,
    text: string,
    sender: 'agent' | 'customer',
    opts?: { agentId?: string; agentName?: string },
  ) => {
    // LIVECHAT_MASTER_SEND — optimistic + claim + server insert
    const msg: ChatMessage = {
      id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      text,
      sender,
      created_at: new Date().toISOString(),
      author: opts?.agentName,
    };
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              messages: [...(c.messages || []), msg],
              preview: text.slice(0, 120),
              status: 'active' as const,
              updated_at: new Date().toISOString(),
              agent_id:
                sender === 'agent'
                  ? opts?.agentId || c.agent_id
                  : c.agent_id,
              unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
            }
          : c,
      ),
    );
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        const bc = new BroadcastChannel('nexus-chat-rt');
        bc.postMessage({ type: 'chat-message', conversationId });
        bc.close();
      }
    } catch {}
    if (!supabase) return;
    try {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      const patch: Record<string, unknown> = {
        preview: text.slice(0, 120),
        status: 'active',
        updated_at: new Date().toISOString(),
        unread: sender === 'customer' ? 1 : 0,
      };
      if (sender === 'agent' && opts?.agentId) patch.agent_id = opts.agentId;
      await supabase.from('chat_conversations').update(patch).eq('id', conversationId);
    } catch (e) {
      console.error('sendChatMessage', e);
    }
    try { await refreshPlatform(); } catch {}
  };'''
            s = s[:m.start()] + new_send + s[m.end():]
            print('send rewritten')

    if 'nexus-chat-rt-channel' not in s:
        inject = '''

  // LIVECHAT_MASTER_V1 realtime
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;
    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      channel = supabase
        .channel('nexus-chat-rt-channel')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_messages' }, () => { void refreshPlatform(); })
        .on('postgres_changes', { event: '*', schema: 'public', table: 'chat_conversations' }, () => { void refreshPlatform(); })
        .subscribe();
    } catch (err) {
      console.warn('chat realtime unavailable', err);
    }
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-chat-rt');
      bc.onmessage = () => { void refreshPlatform(); };
    } catch {}
    const onVis = () => { if (document.visibilityState === 'visible') void refreshPlatform(); };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('focus', onVis);
    return () => {
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('focus', onVis);
      try { bc?.close(); } catch {}
      if (channel && supabase) void supabase.removeChannel(channel);
    };
  }, [refreshPlatform]);
'''
        idx = s.find("setInterval(() => { void refreshPlatform(); }, 1500);")
        if idx == -1:
            idx = s.find("setInterval(() => { void refreshPlatform(); }, 3000);")
        if idx != -1:
            end = s.find('}, [refreshPlatform]);', idx)
            if end != -1:
                end = end + len('}, [refreshPlatform]);')
                s = s[:end] + inject + s[end:]
                print('realtime injected')

    if 'claimChat,' not in s:
        for needle in [
            'createChat, sendChatMessage,',
            'sendChatMessage, setChatStatus,',
        ]:
            if needle in s:
                s = s.replace(needle, needle.replace('sendChatMessage,', 'sendChatMessage, claimChat,'), 1)
                print('value claimChat')
                break

    while s.count("claimChat: (conversationId: string, agentId: string) => Promise<void>;") > 1:
        s = s.replace(
            "claimChat: (conversationId: string, agentId: string) => Promise<void>;\n  claimChat: (conversationId: string, agentId: string) => Promise<void>;",
            "claimChat: (conversationId: string, agentId: string) => Promise<void>;",
            1,
        )
    p.write_text(s)
    print('platform done', len(s))
    return True


def fix_livechat_page():
    p = ROOT / 'src/components/LiveChatPage.tsx'
    if not p.exists():
        return
    s = p.read_text()

    if 'function resolveChatAgent' not in s:
        fn = '''
function resolveChatAgent(
  c: { agent_id?: string } | null | undefined,
  agents: { id: string; name: string; avatar_url?: string | null; user_id?: string | null }[],
) {
  const aid = c?.agent_id;
  if (!aid) return null;
  return agents.find((a) => a.id === aid || a.user_id === aid) || null;
}

'''
        s = s.replace('export default function LiveChatPage', fn + 'export default function LiveChatPage', 1)
        print('resolveChatAgent')

    s = s.replace(
        '''  const {
    conversations,
    sendChatMessage,
    setChatStatus,
    createChat,
    deleteChat,
    archiveChat,
    linkTicketId,
    refreshPlatform,
  } = usePlatform();''',
        '''  const {
    conversations,
    sendChatMessage,
    setChatStatus,
    createChat,
    deleteChat,
    archiveChat,
    linkTicketId,
    refreshPlatform,
    claimChat,
  } = usePlatform();''',
        1,
    )

    s = re.sub(
        r"\s*\{currentAgent && !\(selected as \{ agent_id\?: string \}\)\.agent_id \? \(\s*<button[\s\S]*?Claim\s*</button>\s*\) : currentAgent && \(selected as \{ agent_id\?: string \}\)\.agent_id === currentAgent\.id \? \(\s*<span[^>]*>Yours</span>\s*\) : \(selected as \{ agent_id\?: string \}\)\.agent_id \? \(\s*<span[^>]*>Claimed</span>\s*\) : null\}\s*",
        '\n',
        s,
    )
    while s.count('>Yours</span>') > 1:
        s = re.sub(
            r'\s*<span className="text-\[11px\] text-emerald-400[^"]*"[^>]*>Yours</span>',
            '',
            s,
            count=1,
        )
        print('stripped extra Yours')

    claim_ui = '''
                      {/* LIVECHAT_MASTER_CLAIM_UI — single claim badge */}
                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button
                          type="button"
                          disabled={busy}
                          onClick={async () => {
                            try {
                              setBusy(true);
                              await claimChat(selected.id, currentAgent.id);
                            } catch (e) {
                              console.error(e);
                            } finally {
                              setBusy(false);
                            }
                          }}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500"
                        >
                          Claim
                        </button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] text-emerald-300 px-2 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>
                      ) : (selected as { agent_id?: string }).agent_id ? (
                        <span className="text-[11px] text-violet-200 px-2 py-1 font-medium rounded-lg bg-violet-500/15 border border-violet-400/30">Claimed</span>
                      ) : null}
'''
    if 'LIVECHAT_MASTER_CLAIM_UI' not in s:
        needle = "{(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (\n                    <>\n"
        if needle in s:
            s = s.replace(needle, needle + claim_ui, 1)
            print('claim ui once')

    if 'LIVECHAT_MASTER_SEND_CLAIM' not in s:
        old_send = '''  const send = async () => {
    if (!draft.trim() || !selected) return;
    setBusy(true);
    try {
      if (selected.status === 'ended') await setChatStatus(selected.id, 'active');
      await sendChatMessage(selected.id, draft.trim(), as);
      setDraft('');
    } finally {
      setBusy(false);
    }
  };'''
        new_send = '''  const send = async () => {
    // LIVECHAT_MASTER_SEND_CLAIM
    if (!draft.trim() || !selected) return;
    setBusy(true);
    try {
      if (selected.status === 'ended' || selected.status === 'on_hold') await setChatStatus(selected.id, 'active');
      if (as === 'agent' && currentAgent && !(selected as { agent_id?: string }).agent_id) {
        try { await claimChat(selected.id, currentAgent.id); } catch { /* non-fatal */ }
      }
      await sendChatMessage(
        selected.id,
        draft.trim(),
        as,
        as === 'agent' && currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined,
      );
      setDraft('');
    } catch (e) {
      console.error('send failed', e);
    } finally {
      setBusy(false);
    }
  };'''
        if old_send in s:
            s = s.replace(old_send, new_send, 1)
            print('agent send claim')
        elif 'await sendChatMessage(selected.id, draft.trim(), as)' in s and 'agentId: currentAgent.id' not in s:
            s = s.replace(
                'await sendChatMessage(selected.id, draft.trim(), as);',
                '''if (as === 'agent' && currentAgent && !(selected as { agent_id?: string }).agent_id) {
        try { await claimChat(selected.id, currentAgent.id); } catch { /* non-fatal */ }
      }
      await sendChatMessage(
        selected.id,
        draft.trim(),
        as,
        as === 'agent' && currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined,
      ); // LIVECHAT_MASTER_SEND_CLAIM''',
                1,
            )
            print('send claim soft')

    s = s.replace(
        '''    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 4000);''',
        '''    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 1200); // LIVECHAT_MASTER_POLL''',
        1,
    )
    s = s.replace(
        '''    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 5000);''',
        '''    const id = window.setInterval(() => {
      void refreshPlatform();
    }, 1200); // LIVECHAT_MASTER_POLL''',
        1,
    )

    if 'resolveChatAgent(selected' not in s and 'const agentName = currentAgent' in s:
        s = s.replace(
            "const agentName = currentAgent?.name || 'Agent';",
            '''const claimed = resolveChatAgent(selected, agents || []);
                  const agentName = (m.sender === 'agent'
                    ? (m.author || claimed?.name || currentAgent?.name || 'Agent')
                    : (selected.customer_name || 'Customer'));
                  const agentAvatar = claimed?.avatar_url || currentAgent?.avatar_url || '';''',
            1,
        )
        if 'const { currentAgent, createTicket, findTicket } = useTickets();' in s:
            s = s.replace(
                'const { currentAgent, createTicket, findTicket } = useTickets();',
                'const { currentAgent, createTicket, findTicket, agents } = useTickets();',
                1,
            )
            print('agents for resolve')
        print('bubble attribution')

    p.write_text(s)
    print('Yours count', s.count('>Yours</span>'))
    print('livechat done')


def fix_portal_livechat():
    p = ROOT / 'src/components/PortalLiveChatView.tsx'
    if not p.exists():
        return
    s = p.read_text()

    if 'findTicket' not in s:
        s = s.replace(
            'const { agents } = useTickets();',
            'const { agents, findTicket, tickets } = useTickets();',
            1,
        )

    if 'NO_CUSTOMER_END_V1' not in s:
        s = re.sub(
            r'\n  const endChat = async \(\) => \{.*?\n  \};\n',
            '\n  /* NO_CUSTOMER_END_V1 — only agents end chats */\n',
            s, count=1, flags=re.S,
        )
        s = s.replace('  const [ending, setEnding] = useState(false);\n', '')
        s = re.sub(
            r'\n\s*<button\n\s*type="button"\n\s*disabled=\{ending\}[\s\S]*?End / new chat[\s\S]*?</button>',
            '',
            s, count=1,
        )
        print('removed end button')

    if 'CUSTOMER_CHAT_IDENTITY_V1' not in s and 'linkedTicketId' not in s:
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

  // CUSTOMER_CHAT_IDENTITY_V1
  const linkedTicketId = useMemo(() => {
    const direct = (conversation?.ticket_id || '').trim();
    if (direct) return direct;
    for (const m of messages) {
      const t = (m.text || (m as { body?: string }).body || '');
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
    return (tickets || []).find((t: { id?: string; number?: string }) =>
      String(t.id) === linkedTicketId || String(t.number) === linkedTicketId
    ) || null;
  }, [linkedTicketId, findTicket, tickets]);

  const customerName =
    conversation?.customer_name ||
    user?.user_metadata?.full_name ||
    user?.email?.split('@')[0] ||
    'You';
  const customerInitials = (customerName || 'Y')
    .split(/\\s+/)
    .map((x: string) => x[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const assignedAgent = useMemo(() => {
    const aid = (conversation as { agent_id?: string } | null)?.agent_id;
    if (!aid) return null;
    return (agents || []).find((a: { id: string; user_id?: string }) => a.id === aid || a.user_id === aid) || null;
  }, [conversation, agents]);

  const agentName = assignedAgent?.name || 'Support agent';
  const agentAvatar = assignedAgent?.avatar_url || '';
  const agentInitials = (agentName || 'A')
    .split(/\\s+/)
    .map((x: string) => x[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
'''
        if anchor in s:
            s = s.replace(anchor, helper, 1)
            print('identity helpers')

    if 'CHAT_POLL_FAST_V1' not in s:
        s = s.replace(
            '''  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);''',
            '''  useEffect(() => {
    void refreshPlatform();
    // CHAT_POLL_FAST_V1
    const id = window.setInterval(() => { void refreshPlatform(); }, 1200);
    const onVis = () => { if (document.visibilityState === 'visible') void refreshPlatform(); };
    document.addEventListener('visibilitychange', onVis);
    window.addEventListener('focus', onVis);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVis);
      window.removeEventListener('focus', onVis);
    };
  }, [refreshPlatform]);''',
            1,
        )
        print('fast poll')

    if 'Ticket in progress' not in s and 'assignedAgent' in s:
        old_h = '''          <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
            <MessageCircle size={16} className="text-violet-600 dark:text-violet-400" /> Live Chat
            <span className="text-[11px] font-normal text-zinc-500">
              {conversation ? `Connected · ${conversation.id.slice(0, 8)}` : ''}
            </span>
          </div>'''
        new_h = '''          <div className="flex flex-col gap-2 w-full">
            <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
              <MessageCircle size={16} className="text-violet-600 dark:text-violet-400" /> Live Chat
              <span className="text-[11px] font-normal text-zinc-500">
                {conversation ? `Connected · ${conversation.id.slice(0, 8)}` : ''}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-2 rounded-full border border-zinc-200/70 dark:border-white/10 bg-white/70 dark:bg-white/5 px-2.5 py-1">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[9px] font-bold text-white">{customerInitials}</div>
                <div className="leading-tight">
                  <div className="text-[11px] font-semibold text-zinc-800 dark:text-zinc-100">{customerName}</div>
                  <div className="text-[10px] text-zinc-500">You</div>
                </div>
              </div>
              <span className="text-[10px] text-zinc-400">↔</span>
              <div className="inline-flex items-center gap-2 rounded-full border border-violet-300/40 dark:border-violet-400/20 bg-violet-500/10 px-2.5 py-1">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[9px] font-bold text-white overflow-hidden">
                  {agentAvatar ? <img src={agentAvatar} alt="" className="w-full h-full object-cover" /> : agentInitials}
                </div>
                <div className="leading-tight">
                  <div className="text-[11px] font-semibold text-zinc-800 dark:text-zinc-100">{agentName}</div>
                  <div className="text-[10px] text-zinc-500">{assignedAgent ? 'Agent · claimed' : 'Waiting for agent'}</div>
                </div>
              </div>
            </div>
            {(linkedTicketId || linkedTicket) && (
              <div className="rounded-xl border border-amber-400/25 bg-amber-500/10 px-3 py-2 text-xs text-amber-900 dark:text-amber-100">
                <div className="font-semibold tracking-wide uppercase text-[10px] text-amber-700 dark:text-amber-300 mb-0.5">Ticket in progress</div>
                <div className="font-medium">{linkedTicketId}{linkedTicket?.title ? ` · ${linkedTicket.title}` : linkedTicket?.subject ? ` · ${linkedTicket.subject}` : ''}</div>
              </div>
            )}
          </div>'''
        if old_h in s:
            s = s.replace(old_h, new_h, 1)
            print('header identity')

    if 'whoName' not in s and 'messages.map' in s:
        msg_start = s.find('{messages.map((m) => {')
        if msg_start == -1:
            msg_start = s.find('{messages.map((m, i) => {')
        end = s.find('<div ref={bottomRef}', msg_start) if msg_start != -1 else -1
        if msg_start != -1 and end != -1:
            new_map = '''{messages.map((m, i) => {
            const mine = m.sender === 'customer';
            const parsed = parseChatAttachment(m.text || (m as { body?: string }).body || '');
            const att = parsed.att;
            const displayText = (parsed.text || m.text || (m as { body?: string }).body || '').trim();
            const whoName = mine ? customerName : (m.author || agentName);
            const whoInitials = mine ? customerInitials : agentInitials;
            const whoAvatar = mine ? '' : agentAvatar;
            return (
              <div key={m.id || i} className={clsx('flex items-end gap-2', mine ? 'justify-end' : 'justify-start')}>
                {!mine && (
                  <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden ring-2 ring-white/10">
                    {whoAvatar ? <img src={whoAvatar} alt="" className="w-full h-full object-cover" /> : whoInitials}
                  </div>
                )}
                <div className={clsx(
                  'max-w-[75%] rounded-2xl px-3.5 py-2.5 text-sm shadow-sm',
                  mine ? 'bg-violet-600 text-white rounded-br-md' : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10 rounded-bl-md',
                )}>
                  <div className={clsx('text-[10px] font-semibold mb-0.5', mine ? 'opacity-80' : 'opacity-70')}>{whoName}</div>
                  {att?.url ? (
                    <div className="space-y-1">
                      {isImageMime(att.mime) ? (
                        <img src={att.url} alt={att.name || 'attachment'} className="max-w-full rounded-lg" />
                      ) : (
                        <a href={att.url} download={att.name} className="underline">{att.name || 'Download file'}</a>
                      )}
                      {displayText ? <div className="whitespace-pre-wrap break-words">{displayText}</div> : null}
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap break-words">{displayText || '…'}</div>
                  )}
                </div>
                {mine && (
                  <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10">{customerInitials}</div>
                )}
              </div>
            );
          })}
          '''
            s = s[:msg_start] + new_map + s[end:]
            print('bubbles')

    p.write_text(s)
    print('portal livechat done')


def fix_customers_400():
    p = ROOT / 'src/context/TicketContext.tsx'
    if not p.exists():
        return
    s = p.read_text()
    if 'CUSTOMER_COLS_SAFE' not in s:
        s = s.replace(
            "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';",
            "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at'; // CUSTOMER_COLS_SAFE",
            1,
        )
        if "if (customerRows) setCustomers(customerRows as Customer[]);" in s:
            s = s.replace(
                "if (customerRows) setCustomers(customerRows as Customer[]);",
                """if (customerRows) setCustomers(customerRows as Customer[]);
      else if (cRes && typeof cRes === 'object' && 'error' in cRes && (cRes as { error?: { message?: string } }).error) {
        console.warn('customers select', (cRes as { error?: { message?: string } }).error?.message);
        try {
          const fb = await supabase.from('customers').select('id, name, email, branch, status').limit(200);
          if (fb.data) setCustomers(fb.data as Customer[]);
        } catch { /* ignore */ }
      }""",
                1,
            )
        p.write_text(s)
        print('customers cols safe')


if __name__ == '__main__':
    ensure_platform()
    fix_livechat_page()
    fix_portal_livechat()
    fix_customers_400()
    print('MASTER DONE')
