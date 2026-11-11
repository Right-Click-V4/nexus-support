#!/usr/bin/env python3
"""Safe livechat master — no catastrophic regex."""
from pathlib import Path
import re

ROOT = Path('.')

def ensure_platform():
    p = ROOT / 'src/context/PlatformContext.tsx'
    if not p.exists() or p.stat().st_size < 5000:
        print('WARN PlatformContext tiny')
        return
    s = p.read_text()
    s2, n = re.subn(
        r"supabase\.from\('chat_conversations'\)\.select\('[^']*'\)\.order\('updated_at'",
        "supabase.from('chat_conversations').select('id,customer_name,customer_email,status,preview,unread,updated_at,created_at,agent_id,assignee_id,ticket_id,branch,archived_at').order('updated_at'",
        s, count=1,
    )
    s = s2
    if n:
        print('select expanded')
    if 'const claimChat' not in s:
        claim = '''
  const claimChat = async (conversationId: string, agentId: string) => {
    if (!agentId) return;
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? { ...c, agent_id: agentId, status: (c.status === 'waiting' || c.status === 'on_hold' ? 'active' : c.status) as ChatConversation['status'] }
          : c,
      ),
    );
    if (!supabase) return;
    const now = new Date().toISOString();
    for (const patch of [
      { agent_id: agentId, assignee_id: agentId, status: 'active', updated_at: now },
      { agent_id: agentId, status: 'active', updated_at: now },
    ]) {
      const { error } = await supabase.from('chat_conversations').update(patch).eq('id', conversationId);
      if (!error) break;
    }
    try { await refreshPlatform(); } catch {}
  };

'''
        if '  const setChatStatus = async' in s:
            s = s.replace('  const setChatStatus = async', claim + '  const setChatStatus = async', 1)
            print('claimChat')
    if 'claimChat,' not in s and 'sendChatMessage,' in s:
        s = s.replace('sendChatMessage,', 'sendChatMessage, claimChat,', 1)
    if 'LIVECHAT_MASTER_SEND' not in s and 'const sendChatMessage = async' in s:
        s = s.replace('const sendChatMessage = async (', 'const sendChatMessage = async ( /* LIVECHAT_MASTER_SEND */ ', 1)
        print('send marked')
    p.write_text(s)
    print('platform', len(s))

def fix_livechat():
    p = ROOT / 'src/components/LiveChatPage.tsx'
    if not p.exists():
        return
    s = p.read_text()
    if 'claimChat,' not in s:
        s = s.replace('refreshPlatform,\n  } = usePlatform();', 'refreshPlatform,\n    claimChat,\n  } = usePlatform();', 1)
    if 'Yours</span>' not in s:
        claim = '''
                      {/* LIVECHAT_MASTER_CLAIM_UI */}
                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button type="button" disabled={busy} onClick={async () => { try { setBusy(true); await claimChat(selected.id, currentAgent.id); } catch (e) { console.error(e); } finally { setBusy(false); } }}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500">Claim</button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] text-emerald-300 px-2 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>
                      ) : (selected as { agent_id?: string }).agent_id ? (
                        <span className="text-[11px] text-violet-200 px-2 py-1 font-medium rounded-lg bg-violet-500/15 border border-violet-400/30">Claimed</span>
                      ) : null}
'''
        needle = "{(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? ("
        if needle in s:
            s = s.replace(needle, claim + '\n                      ' + needle, 1)
            print('claim ui')
    p.write_text(s)
    print('Yours', s.count('Yours</span>'))

if __name__ == '__main__':
    ensure_platform()
    fix_livechat()
    print('MASTER SAFE DONE')
