#!/usr/bin/env python3
"""Master livechat fix applied on every deploy. Safe / idempotent."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def ensure_platform():
    p = ROOT / 'src/context/PlatformContext.tsx'
    if not p.exists() or p.stat().st_size < 5000:
        print('WARN PlatformContext tiny — expect deploy restore')
        return
    s = p.read_text()
    s2, n = re.subn(
        r"supabase\.from\('chat_conversations'\)\.select\('[^']*'\)\.order\('updated_at'",
        "supabase.from('chat_conversations').select('id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,assignee_id,ticket_id,branch,archived_at,agent_name').order('updated_at'",
        s, count=1,
    )
    s = s2
    if n:
        print('select expanded')

    if 'const claimChat' not in s:
        claim = """
  const claimChat = async (conversationId: string, agentId: string, agentName?: string) => {
    if (!agentId) return;
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              agent_id: agentId,
              agent_name: agentName || (c as { agent_name?: string }).agent_name,
              status: ((c.status === 'waiting' || c.status === 'on_hold') ? 'active' : c.status) as ChatConversation['status'],
            }
          : c,
      ),
    );
    if (!supabase) return;
    const now = new Date().toISOString();
    for (const patch of [
      { agent_id: agentId, assignee_id: agentId, agent_name: agentName || null, status: 'active', updated_at: now },
      { agent_id: agentId, status: 'active', updated_at: now },
      { agent_id: agentId, updated_at: now },
    ]) {
      const { error } = await supabase.from('chat_conversations').update(patch).eq('id', conversationId);
      if (!error) break;
    }
    try { await refreshPlatform(); } catch {}
  };

"""
        if '  const setChatStatus = async' in s:
            s = s.replace('  const setChatStatus = async', claim + '  const setChatStatus = async', 1)
            print('claimChat fn')

    if 'claimChat:' not in s:
        s = s.replace(
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;\n  claimChat: (conversationId: string, agentId: string, agentName?: string) => Promise<void>;",
            1,
        )
        print('claimChat type')

    if 'claimChat,' not in s and 'sendChatMessage,' in s:
        s = s.replace('sendChatMessage,', 'sendChatMessage, claimChat,', 1)
        print('claimChat export')

    s = s.replace(
        "const id = window.setInterval(() => { void refreshPlatform(); }, 3000);",
        "const id = window.setInterval(() => { void refreshPlatform(); }, 1500);",
        1,
    )
    p.write_text(s)
    print('platform', len(s), 'claimChat=', 'const claimChat' in s)

def fix_livechat():
    p = ROOT / 'src/components/LiveChatPage.tsx'
    if not p.exists():
        return
    s = p.read_text()

    if 'claimChat' not in s.split('} = usePlatform()')[0]:
        s = s.replace(
            'refreshPlatform,\n  } = usePlatform();',
            'refreshPlatform,\n    claimChat,\n  } = usePlatform();',
            1,
        )
        print('destructure claimChat')

    s = re.sub(r'\s*\{\s*/\*\s*LIVECHAT_MASTER_CLAIM_UI\s*\*/[\s\S]*?\}\s*:\s*null\}\s*', '\n', s)
    s = re.sub(r'\s*\{\s*/\*\s*CLAIM_UI_SINGLE\s*\*/[\s\S]*?\}\s*:\s*null\}\s*', '\n', s)
    while s.count('Yours</span>') > 1:
        s = s.replace(
            '<span className="text-[11px] text-emerald-300 px-2 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>',
            '',
            1,
        )

    claim_ui = """
                      {/* CLAIM_UI_SINGLE */}
                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button type="button" disabled={busy}
                          onClick={async () => { try { setBusy(true); await claimChat(selected.id, currentAgent.id, currentAgent.name); } catch (e) { console.error(e); } finally { setBusy(false); } }}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500">Claim</button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] text-emerald-300 px-2 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>
                      ) : (selected as { agent_id?: string }).agent_id ? (
                        <span className="text-[11px] text-violet-200 px-2 py-1 font-medium rounded-lg bg-violet-500/15 border border-violet-400/30">Claimed</span>
                      ) : null}
"""
    if 'CLAIM_UI_SINGLE' not in s:
        needle = "{(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? ("
        if needle in s:
            s = s.replace(needle, claim_ui + '\n                      ' + needle, 1)
            print('claim ui single')

    if "await claimChat(selected.id" not in s:
        old = """if (selected.status === 'ended') await setChatStatus(selected.id, 'active');
      await sendChatMessage(selected.id, draft.trim(), as);"""
        new = """if (selected.status === 'ended') await setChatStatus(selected.id, 'active');
      if (as === 'agent' && currentAgent && !(selected as { agent_id?: string }).agent_id) {
        try { await claimChat(selected.id, currentAgent.id, currentAgent.name); } catch { /* non-fatal */ }
      }
      await sendChatMessage(selected.id, draft.trim(), as);"""
        if old in s:
            s = s.replace(old, new, 1)
            print('auto-claim on send')

    s = s.replace(
        'void refreshPlatform();\n    }, 4000);',
        'void refreshPlatform();\n    }, 1500);',
        1,
    )

    p.write_text(s)
    print('LiveChat Yours=', s.count('Yours</span>'))

def fix_portal():
    p = ROOT / 'src/components/PortalLiveChatView.tsx'
    if not p.exists():
        return
    s = p.read_text()

    if 'End / new chat' in s:
        s = re.sub(
            r'<button\s+type="button"\s+disabled=\{ending\}[\s\S]*?\{ending \? \'Ending…\' : chatEnded \? \'Start new chat\' : \'End / new chat\'\}\s*</button>',
            '{chatEnded ? (\n            <button type="button" onClick={startNewChat} className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-500">Start new chat</button>\n          ) : (\n            <span className="text-[11px] text-zinc-500 dark:text-zinc-400">Agent will end when resolved</span>\n          )}',
            s,
            count=1,
        )
        print('removed customer End')

    identity = """
        {/* IDENTITY_TICKET_STRIP */}
        {conversation && (
          <div className="px-4 py-2.5 border-b border-zinc-200/50 dark:border-white/10 flex flex-wrap items-center gap-3 bg-white/40 dark:bg-white/5">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
                {(conversation.customer_name || name || 'C').split(/\\s+/).map((x: string) => x[0]).join('').slice(0, 2).toUpperCase()}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 truncate">{conversation.customer_name || name || 'You'}</div>
                <div className="text-[10px] text-zinc-500 truncate">Customer</div>
              </div>
            </div>
            <div className="text-zinc-400 text-xs">↔</div>
            <div className="flex items-center gap-2 min-w-0">
              {(conversation as { agent_id?: string }).agent_id ? (
                <>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
                    {((conversation as { agent_name?: string }).agent_name || 'Agent').split(/\\s+/).map((x: string) => x[0]).join('').slice(0, 2).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 truncate">{(conversation as { agent_name?: string }).agent_name || 'Support agent'}</div>
                    <div className="text-[10px] text-emerald-600 dark:text-emerald-400">Claimed · assisting you</div>
                  </div>
                </>
              ) : (
                <div className="text-xs text-amber-600 dark:text-amber-400">Waiting for an agent to claim…</div>
              )}
            </div>
            {(conversation.ticket_id || ticketId) && (
              <div className="ml-auto text-[11px] px-2.5 py-1 rounded-lg bg-violet-600/20 text-violet-700 dark:text-violet-200 border border-violet-400/30 font-medium">
                Ticket: {conversation.ticket_id || ticketId}
              </div>
            )}
          </div>
        )}
"""
    if 'IDENTITY_TICKET_STRIP' not in s:
        marker = '{isOnHold && !chatEnded && ('
        if marker in s:
            s = s.replace(marker, identity + '\n        ' + marker, 1)
            print('identity strip')

    if 'setInterval(() => { void refreshPlatform(); }, 1500)' not in s:
        poll = """
  useEffect(() => {
    if (!chatId) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 1500);
    return () => window.clearInterval(id);
  }, [chatId, refreshPlatform]);
"""
        needle = '}, [messages.length, chatId]);'
        if needle in s:
            s = s.replace(needle, needle + '\n' + poll, 1)
            print('customer poll')

    p.write_text(s)
    print('portal End=', 'End / new chat' in s, 'identity=', 'IDENTITY_TICKET_STRIP' in s)

if __name__ == '__main__':
    ensure_platform()
    fix_livechat()
    fix_portal()
    print('MASTER SAFE DONE')
