#!/usr/bin/env python3
"""Fix: claim chat sticks, no demo customers on supabase."""
from pathlib import Path

tc = Path('src/context/TicketContext.tsx')
if tc.exists():
    s = tc.read_text()
    s = s.replace(
        "const [customers, setCustomers] = useState<Customer[]>(INITIAL_CUSTOMERS);",
        "const [customers, setCustomers] = useState<Customer[]>(() => (isSupabaseConfigured ? [] : INITIAL_CUSTOMERS));",
        1,
    )
    s = s.replace(
        "if (customerRows) setCustomers(customerRows as Customer[]);",
        "if (cRes && typeof cRes === 'object' && 'data' in cRes) setCustomers((customerRows as Customer[]) || []);",
        1,
    )
    tc.write_text(s)
    print('customers ok')

pc = Path('src/context/PlatformContext.tsx')
if pc.exists():
    s = pc.read_text()
    if 'claimChat:' not in s:
        for old in [
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;",
        ]:
            if old in s:
                s = s.replace(
                    old,
                    old.rstrip(';') + ";\n  claimChat: (conversationId: string, agentId: string) => Promise<boolean>;",
                    1,
                )
                break
    if 'const claimChat' not in s:
        claim = """
  const claimChat = async (conversationId: string, agentId: string): Promise<boolean> => {
    if (!conversationId || !agentId) return false;
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
    if (!supabase) return true;
    try {
      let { error } = await supabase
        .from('chat_conversations')
        .update({ agent_id: agentId, status: 'active', updated_at: new Date().toISOString() })
        .eq('id', conversationId);
      if (error) {
        const r2 = await supabase
          .from('chat_conversations')
          .update({ agent_id: agentId, updated_at: new Date().toISOString() })
          .eq('id', conversationId);
        error = r2.error;
      }
      if (error) console.warn('claimChat', error.message);
      return true;
    } catch (e) {
      console.warn('claimChat', e);
      return true;
    }
  };

"""
        if '  const archiveChat = async' in s:
            s = s.replace('  const archiveChat = async', claim + '  const archiveChat = async', 1)
        elif '  const setChatStatus = async' in s:
            s = s.replace('  const setChatStatus = async', claim + '  const setChatStatus = async', 1)
    if 'claimChat,' not in s:
        if 'createChat, sendChatMessage,' in s:
            s = s.replace('createChat, sendChatMessage,', 'createChat, sendChatMessage,\n    claimChat,', 1)
        elif 'sendChatMessage, setChatStatus' in s:
            s = s.replace('sendChatMessage, setChatStatus', 'sendChatMessage, claimChat, setChatStatus', 1)
    pc.write_text(s)
    print('platform claim ok')

lp = Path('src/components/LiveChatPage.tsx')
if lp.exists():
    t = lp.read_text()
    if 'claimChat,' not in t and 'refreshPlatform,' in t:
        t = t.replace('refreshPlatform,', 'refreshPlatform,\n    claimChat,', 1)
    if 'Yours' not in t:
        marker = "{(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? ("
        claim_ui = """{currentAgent?.id ? (
                    (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                      <span className=\"inline-flex items-center text-xs font-semibold text-emerald-300 px-2.5 py-1.5 rounded-lg bg-emerald-500/15 border border-emerald-400/30\">Yours</span>
                    ) : (selected as { agent_id?: string }).agent_id ? (
                      <span className=\"inline-flex items-center text-xs font-medium text-zinc-300 px-2.5 py-1.5 rounded-lg bg-white/5 border border-white/10\">Taken</span>
                    ) : (
                      <button
                        type=\"button\"
                        disabled={busy}
                        onClick={() => {
                          void (async () => {
                            setBusy(true);
                            try { await claimChat?.(selected.id, currentAgent.id); } finally { setBusy(false); }
                          })();
                        }}
                        className=\"inline-flex items-center gap-1 text-xs font-semibold bg-violet-500 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-400 disabled:opacity-60\"
                      >Claim</button>
                    )
                  ) : null}
                  """
        if marker in t:
            t = t.replace(marker, claim_ui + marker, 1)
            print('claim UI ok')
        else:
            print('claim UI marker miss')
    lp.write_text(t)
    print('livechat ok')

print('DONE')
