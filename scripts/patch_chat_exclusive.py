"""Exclusive live-chat assignment (one agent) + center Still need help."""
from pathlib import Path
import re

pc = Path('src/context/PlatformContext.tsx')
if pc.exists():
    s = pc.read_text()
    if 'CHAT_EXCLUSIVE_AGENT_V1' in s:
        print('PC exclusive already')
    else:
        if 'const claimChatIfNeeded' not in s:
            marker = '  const sendChatMessage = async'
            idx = s.find(marker)
            if idx > 0:
                helper = '''
  // CHAT_EXCLUSIVE_AGENT_V1 — first agent to reply owns the chat
  const claimChatIfNeeded = async (conversationId: string, agentId?: string | null) => {
    if (!agentId) return false;
    const conv = conversations.find((c) => c.id === conversationId);
    const existing = (conv as { agent_id?: string } | undefined)?.agent_id;
    if (existing && existing !== agentId) return false;
    if (existing === agentId) return true;
    setConversations((prev) =>
      prev.map((c) => (c.id === conversationId ? { ...c, agent_id: agentId, status: 'active' as const } : c)),
    );
    if (supabase) {
      try {
        await supabase
          .from('chat_conversations')
          .update({ agent_id: agentId, status: 'active', updated_at: new Date().toISOString() })
          .eq('id', conversationId)
          .is('agent_id', null);
        await supabase
          .from('chat_conversations')
          .update({ agent_id: agentId, updated_at: new Date().toISOString() })
          .eq('id', conversationId);
      } catch (e) {
        console.warn('claimChatIfNeeded', e);
      }
    }
    return true;
  };

'''
                s = s[:idx] + helper + s[idx:]
                print('added claimChatIfNeeded')

        m = re.search(
            r"const sendChatMessage = async \(conversationId: string, text: string, sender: 'agent' \| 'customer'\) => \{",
            s,
        )
        if m:
            s = (
                s[: m.start()]
                + "const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer', agentId?: string) => {\n    // CHAT_EXCLUSIVE_AGENT_V1\n    if (sender === 'agent') {\n      const ok = await claimChatIfNeeded(conversationId, agentId);\n      if (!ok) throw new Error('This chat is already assigned to another agent');\n    }"
                + s[m.end() :]
            )
            print('patched sendChatMessage')
        s = s.replace(
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', agentId?: string) => Promise<void>;",
        )
        pc.write_text(s)
        print('PC written')
else:
    print('PC missing')

lcp = Path('src/components/LiveChatPage.tsx')
if lcp.exists():
    s = lcp.read_text()
    if 'CHAT_EXCLUSIVE_AGENT_V1' in s and 'isAssignedToMe' in s:
        print('LCP exclusive already')
    else:
        if "await sendChatMessage(selected.id, draft.trim(), as);" in s:
            s = s.replace(
                "await sendChatMessage(selected.id, draft.trim(), as);",
                "await sendChatMessage(selected.id, draft.trim(), as, as === 'agent' ? currentAgent?.id : undefined); // CHAT_EXCLUSIVE_AGENT_V1",
                1,
            )
        if "await sendChatMessage(selected.id, body, 'agent');" in s:
            s = s.replace(
                "await sendChatMessage(selected.id, body, 'agent');",
                "await sendChatMessage(selected.id, body, 'agent', currentAgent?.id);",
                1,
            )
        if 'const selected = conversations.find((c) => c.id === selectedId) || null;' in s and 'isAssignedToMe' not in s:
            s = s.replace(
                'const selected = conversations.find((c) => c.id === selectedId) || null;',
                '''const selected = conversations.find((c) => c.id === selectedId) || null;
  // CHAT_EXCLUSIVE_AGENT_V1
  const assignedAgentId = selected?.agent_id || null;
  const isAssignedToMe = !assignedAgentId || assignedAgentId === currentAgent?.id;
  const assignedAgentName =
    assignedAgentId && agents
      ? agents.find((a) => a.id === assignedAgentId)?.name || 'Another agent'
      : assignedAgentId
        ? 'Another agent'
        : null;
''',
                1,
            )
        if 'const { currentAgent, createTicket, findTicket } = useTickets();' in s:
            s = s.replace(
                'const { currentAgent, createTicket, findTicket } = useTickets();',
                'const { currentAgent, createTicket, findTicket, agents } = useTickets();',
                1,
            )
        s = s.replace('sendChatMessage, agents,', 'sendChatMessage,')
        if 'CHAT_EXCLUSIVE_UI' not in s and 'isAssignedToMe' in s:
            banner = '''
                  {/* CHAT_EXCLUSIVE_UI */}
                  {assignedAgentId && !isAssignedToMe && (
                    <div className="mx-4 mt-2 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
                      This chat is exclusive to <strong>{assignedAgentName}</strong>. Only they can reply.
                    </div>
                  )}
                  {!assignedAgentId && selected && (selected.status === 'active' || selected.status === 'waiting' || selected.status === 'open' || selected.status === 'on_hold') && (
                    <div className="mx-4 mt-2 rounded-lg border border-violet-500/30 bg-violet-500/10 px-3 py-2 text-xs text-violet-200">
                      Unassigned — first agent to reply claims this chat exclusively.
                    </div>
                  )}
                  {assignedAgentId && isAssignedToMe && (
                    <div className="mx-4 mt-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-200">
                      Assigned to you — other agents cannot reply.
                    </div>
                  )}
'''
            mark = '<div className="flex-1 overflow-y-auto p-4 space-y-3">'
            if mark in s:
                s = s.replace(mark, banner + '\n              ' + mark, 1)
        if 'disabled={!isAssignedToMe || !draft.trim()' not in s:
            s = s.replace(
                'disabled={busy || !draft.trim()}',
                'disabled={busy || !isAssignedToMe || !draft.trim()}',
                1,
            )
        if 'readOnly={!isAssignedToMe}' not in s and 'Type a reply as agent' in s:
            s = s.replace(
                'placeholder="Type a reply as agent…"\n                    className="flex-1 resize-none',
                'placeholder={isAssignedToMe ? "Type a reply as agent…" : "Assigned to another agent"}\n                    readOnly={!isAssignedToMe}\n                    className="flex-1 resize-none',
                1,
            )
        lcp.write_text(s)
        print('LCP written')
else:
    print('LCP missing')

cp = Path('src/components/CustomerPortal.tsx')
if cp.exists() and cp.stat().st_size > 10000:
    s = cp.read_text()
    if 'STILL_HELP_CENTER_V1' in s:
        print('still help already centered')
    else:
        old = '''                <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center"><LifeBuoy size={16} /></div>
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">We are here when self-serve is not enough</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button type="button" onClick={() => setView('submit')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl bg-brand-600 text-white hover:bg-brand-500"><Ticket size={14} /> Submit a Ticket</button>
                    <button type="button" onClick={() => setView('chat')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-800 dark:text-zinc-100"><MessageSquare size={14} /> Live Chat</button>
                    <button type="button" onClick={() => setView('mytickets')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-800 dark:text-zinc-100"><ClipboardList size={14} /> My Tickets</button>
                  </div>
                </section>'''
        new = '''                <section className="portal-overview-glass rounded-2xl p-4 sm:p-5 flex flex-col items-center text-center /* STILL_HELP_CENTER_V1 */">
                  <div className="flex flex-col items-center gap-2 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center"><LifeBuoy size={18} /></div>
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">We are here when self-serve is not enough</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 justify-center">
                    <button type="button" onClick={() => setView('submit')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl bg-brand-600 text-white hover:bg-brand-500"><Ticket size={14} /> Submit a Ticket</button>
                    <button type="button" onClick={() => setView('chat')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-800 dark:text-zinc-100"><MessageSquare size={14} /> Live Chat</button>
                    <button type="button" onClick={() => setView('mytickets')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-800 dark:text-zinc-100"><ClipboardList size={14} /> My Tickets</button>
                  </div>
                </section>'''
        if old in s:
            s = s.replace(old, new, 1)
            cp.write_text(s)
            print('centered still need help')
        else:
            if 'Still need help?' in s:
                s = s.replace(
                    '<div className="flex flex-wrap gap-2">\n                    <button type="button" onClick={() => setView(\'submit\')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl bg-brand-600 text-white hover:bg-brand-500"><Ticket size={14} /> Submit a Ticket</button>',
                    '<div className="flex flex-wrap gap-2 justify-center /* STILL_HELP_CENTER_V1 */">\n                    <button type="button" onClick={() => setView(\'submit\')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl bg-brand-600 text-white hover:bg-brand-500"><Ticket size={14} /> Submit a Ticket</button>',
                    1,
                )
                s = s.replace(
                    '''                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center"><LifeBuoy size={16} /></div>
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">We are here when self-serve is not enough</p>
                    </div>
                  </div>''',
                    '''                  <div className="flex flex-col items-center gap-2 mb-3 text-center">
                    <div className="w-10 h-10 rounded-xl bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center"><LifeBuoy size={18} /></div>
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">We are here when self-serve is not enough</p>
                    </div>
                  </div>''',
                    1,
                )
                cp.write_text(s)
                print('centered still need help soft')
            else:
                print('still help block not found')
else:
    print('CP skip')

print('DONE')
