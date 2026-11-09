#!/usr/bin/env python3
"""Claim button, accurate agent attribution, customer avatars on agent live chat."""
from pathlib import Path
import re

def patch_platform():
    p = Path('src/context/PlatformContext.tsx')
    if not p.exists():
        return
    s = p.read_text()
    if 'claimChat:' not in s:
        s = s.replace(
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;\n  claimChat: (conversationId: string, agentId: string) => Promise<void>;",
            1,
        )
    s = s.replace(
        "const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {",
        "const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => {",
        1,
    )
    s = s.replace(
        "await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });",
        "await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender, author: opts?.agentName || null });",
        1,
    )
    s = s.replace(
        "const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };",
        "const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString(), author: opts?.agentName };",
        1,
    )
    s = s.replace(
        "if (sender === 'agent' && user?.id) _upd.agent_id = user.id;",
        "if (sender === 'agent' && (opts?.agentId || user?.id)) _upd.agent_id = opts?.agentId || user?.id;",
    )
    s = s.replace(
        "if (sender === 'agent' && user?.id) _upd2.agent_id = user.id;",
        "if (sender === 'agent' && (opts?.agentId || user?.id)) _upd2.agent_id = opts?.agentId || user?.id;",
    )
    if 'const claimChat' not in s:
        claim = '''
  const claimChat = async (conversationId: string, agentId: string) => {
    if (!agentId) return;
    setConversations((prev) =>
      prev.map((c) => (c.id === conversationId ? { ...c, agent_id: agentId, status: (c.status === 'waiting' ? 'active' : c.status) as ChatConversation['status'] } : c)),
    );
    if (supabase) {
      const { error } = await supabase
        .from('chat_conversations')
        .update({ agent_id: agentId, status: 'active', updated_at: new Date().toISOString() })
        .eq('id', conversationId);
      if (error) {
        await supabase
          .from('chat_conversations')
          .update({ agent_id: agentId, updated_at: new Date().toISOString() })
          .eq('id', conversationId);
      }
      await refreshPlatform();
    }
  };

'''
        if '  const archiveChat = async' in s:
            s = s.replace('  const archiveChat = async', claim + '  const archiveChat = async', 1)
        else:
            s = s.replace('  const setChatStatus = async', claim + '  const setChatStatus = async', 1)
    if 'claimChat,' not in s[s.find('const value'):] if 'const value' in s else True:
        s = s.replace(
            'createChat, sendChatMessage,',
            'createChat, sendChatMessage,\n    claimChat,',
            1,
        )
    p.write_text(s)
    print('platform claim ok')


def patch_livechat():
    lp = Path('src/components/LiveChatPage.tsx')
    if not lp.exists():
        return
    t = lp.read_text()
    if 'claimChat' not in t:
        t = t.replace(
            '''  const {
    conversations,
    sendChatMessage,
    setChatStatus,
    createChat,
    deleteChat,
    archiveChat,
    linkTicketId,
    refreshPlatform,
  } = usePlatform();
  const { currentAgent, createTicket, findTicket } = useTickets();''',
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
  } = usePlatform();
  const { currentAgent, createTicket, findTicket, agents, customers } = useTickets();''',
            1,
        )
    if 'function resolveChatAgent' not in t:
        t = t.replace(
            'function isConvOnHold',
            '''function resolveChatAgent(
  c: { agent_id?: string } | null | undefined,
  agents: { id: string; name: string; avatar_url?: string | null; user_id?: string | null }[],
) {
  const aid = c?.agent_id;
  if (!aid) return null;
  return agents.find((a) => a.id === aid || a.user_id === aid) || null;
}

function isConvOnHold''',
            1,
        )
    t = t.replace(
        "await sendChatMessage(selected.id, draft.trim(), as);",
        "await sendChatMessage(selected.id, draft.trim(), as, as === 'agent' && currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined);",
    )
    t = t.replace(
        "await sendChatMessage(selected.id, body, 'agent');",
        "await sendChatMessage(selected.id, body, 'agent', currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined);",
    )
    t = t.replace(
        "await sendChatMessage(selected.id, g.url, as);",
        "await sendChatMessage(selected.id, g.url, as, as === 'agent' && currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined);",
    )
    if 'claimChat(selected.id' not in t:
        claim_btn = '''                      {currentAgent && (selected as { agent_id?: string }).agent_id !== currentAgent.id ? (
                        <button
                          type="button"
                          onClick={() => void claimChat(selected.id, currentAgent.id)}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500"
                          title="Claim this chat so the customer sees you"
                        >
                          Claim
                        </button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] text-emerald-400 px-1 font-medium">Yours</span>
                      ) : null}
'''
        t = t.replace(
            "{(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (\n                    <>\n                      {isConvOnHold(selected)",
            "{(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (\n                    <>\n                      " + claim_btn + "                      {isConvOnHold(selected)",
            1,
        )
    if 'Claimed by' not in t:
        t = t.replace(
            '''                  <div className="text-sm font-semibold text-slate-800 dark:text-zinc-100 truncate">{selected.customer_name}</div>
                  <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">
                    {selected.customer_email}''',
            '''                  <div className="text-sm font-semibold text-slate-800 dark:text-zinc-100 truncate">{selected.customer_name}</div>
                  <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">
                    {(() => {
                      const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);
                      return claimed ? `Claimed by ${claimed.name} · ` : '';
                    })()}
                    {selected.customer_email}''',
            1,
        )
    if "const agentName = currentAgent?.name || 'Agent';" in t:
        t = t.replace(
            "const agentName = currentAgent?.name || 'Agent';",
            "const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);\n                  const agentName = (m as { author?: string }).author || claimed?.name || currentAgent?.name || 'Agent';\n                  const agentAvatar = claimed?.avatar_url || currentAgent?.avatar_url || '';",
            1,
        )
    old_c = '''                      {!isAgent && (
                        <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10">
                          {customerInitials || 'C'}
                        </div>
                      )}'''
    new_c = '''                      {!isAgent && (
                        <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden">
                          {(() => {
                            const custRow = (customers || []).find(
                              (c) => (c.email || '').toLowerCase() === (selected.customer_email || '').toLowerCase(),
                            ) as { avatar_url?: string } | undefined;
                            const customerAvatar = custRow?.avatar_url || '';
                            return customerAvatar ? (
                              <img src={customerAvatar} alt="" className="w-full h-full object-cover" />
                            ) : (
                              customerInitials || 'C'
                            );
                          })()}
                        </div>
                      )}'''
    if old_c in t:
        t = t.replace(old_c, new_c, 1)
        print('customer avatar bubble')
    lp.write_text(t)
    print('livechat ok')


def patch_portal():
    pv = Path('src/components/PortalLiveChatView.tsx')
    if not pv.exists():
        return
    t = pv.read_text()
    t = t.replace('return (agents || [])[0] || null;', 'return null;')
    t = t.replace(
        "const whoName = mine ? customerName : agentName;",
        "const whoName = mine ? customerName : ((m as { author?: string }).author || agentName);",
    )
    if 'const assignedAgent' not in t and 'const hasAgentOnline = onlineAgents.length > 0;' in t:
        t = t.replace(
            '  const hasAgentOnline = onlineAgents.length > 0;',
            '''  const hasAgentOnline = onlineAgents.length > 0;

  const assignedAgent = useMemo(() => {
    const aid = (conversation as { agent_id?: string } | null)?.agent_id;
    if (!aid) return null;
    return (agents || []).find((a) => a.id === aid || (a as { user_id?: string }).user_id === aid) || null;
  }, [conversation, agents]);
  const agentName = assignedAgent?.name || 'Support agent';
  const agentAvatar = assignedAgent?.avatar_url || '';
  const agentInitials = agentName.split(/\\s+/).map((x) => x[0]).join('').slice(0, 2).toUpperCase() || 'A';
  const agentPresent = Boolean(assignedAgent) || (messages || []).some((m) => m.sender === 'agent');
''',
            1,
        )
    if 'const agentPresent' not in t:
        if "const agentAvatar = assignedAgent?.avatar_url || '';" in t:
            t = t.replace(
                "const agentAvatar = assignedAgent?.avatar_url || '';",
                "const agentAvatar = assignedAgent?.avatar_url || '';\n  const agentPresent = Boolean(assignedAgent) || (messages || []).some((m) => m.sender === 'agent');",
                1,
            )
    if 'const customerAvatar' not in t:
        t = t.replace(
            "const messages = conversation?.messages || [];",
            "const messages = conversation?.messages || [];\n  const customerAvatar = String((user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata?.avatar_url || '').trim();",
            1,
        )
    pv.write_text(t)
    print('portal ok')


def patch_customers():
    tc = Path('src/context/TicketContext.tsx')
    if not tc.exists():
        return
    s = tc.read_text()
    s = s.replace(
        "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';",
        "const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at, avatar_url';",
        1,
    )
    tc.write_text(s)
    print('customers avatar col')


patch_platform()
patch_livechat()
patch_portal()
patch_customers()
print('DONE')
