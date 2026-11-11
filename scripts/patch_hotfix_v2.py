#!/usr/bin/env python3
"""Hotfix V2b: customerInitials after chatId state, schema, status, claim type."""
from pathlib import Path
import re

ROOT = Path('.')

def fix_portal_crash():
    p = ROOT / 'src/components/PortalLiveChatView.tsx'
    if not p.exists():
        print('no portal')
        return
    s = p.read_text()
    if 'SAFE_IDENTITY_V2' in s or 'SAFE_IDENTITY_V2B' in s:
        s = re.sub(
            r'\n  // SAFE_IDENTITY_V2[B]?[\s\S]*?const isOnHold = \(conversation\?\.status \|\| \'\'\)\.toLowerCase\(\) === \'on_hold\';\n',
            '\n',
            s,
            count=2,
        )
        print('cleared old SAFE blocks')

    if 'SAFE_IDENTITY_V2B' not in s:
        inject_after = None
        for m in [
            "const [chatId, setChatId] = useState<string | null>(null);",
            "const [chatId, setChatId] = useState(null);",
        ]:
            if m in s:
                inject_after = m
                break
        if not inject_after:
            print('chatId state miss')
            p.write_text(s)
            return
        block = inject_after + """
  // SAFE_IDENTITY_V2B — after chatId state (avoids used-before-declaration)
  const conversation = useMemo(
    () => (chatId ? (conversations || []).find((c) => c.id === chatId) : null),
    [conversations, chatId],
  );
  const messages = (conversation?.messages || []) as Array<{ id?: string; text?: string; body?: string; sender?: string; author?: string; created_at?: string }>;
  const customerName =
    conversation?.customer_name ||
    (user?.user_metadata as { full_name?: string } | undefined)?.full_name ||
    user?.email?.split('@')[0] ||
    'You';
  const customerInitials = String(customerName || 'Y')
    .split(/\\s+/)
    .map((x) => x[0] || '')
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'Y';
  const assignedAgent = useMemo(() => {
    const aid = (conversation as { agent_id?: string } | null)?.agent_id;
    if (!aid) return null;
    return (agents || []).find((a: { id: string; user_id?: string | null }) => a.id === aid || a.user_id === aid) || null;
  }, [conversation, agents]);
  const agentName = assignedAgent?.name || 'Support agent';
  const agentAvatar = assignedAgent?.avatar_url || '';
  const agentInitials = String(agentName || 'A')
    .split(/\\s+/)
    .map((x) => x[0] || '')
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'A';
  const linkedTicketId = (conversation as { ticket_id?: string } | null)?.ticket_id || '';
  const linkedTicket = null as { title?: string; subject?: string } | null;
  const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';
"""
        s = s.replace(inject_after, block, 1)
        print('SAFE_IDENTITY_V2B')

    while s.count('const conversation = useMemo') > 1:
        first = s.find('const conversation = useMemo')
        second = s.find('const conversation = useMemo', first + 1)
        if second < 0:
            break
        end = s.find(');', second)
        if end < 0:
            break
        s = s[:second] + s[end + 2:]
        print('dedupe conversation')
    while s.count('const isOnHold =') > 1:
        first = s.find('const isOnHold =')
        rest = s[first + 1:]
        rest2 = re.sub(r'\n  const isOnHold = [^;]+;', '', rest, count=1)
        s = s[: first + 1] + rest2
        print('dedupe isOnHold')
    while s.count('const customerInitials') > 1:
        idx = s.find('const customerInitials')
        idx2 = s.find('const customerInitials', idx + 1)
        if idx2 < 0:
            break
        end = s.find(';', idx2)
        s = s[:idx2] + s[end + 1:]
        print('dedupe customerInitials')

    if 'CHAT_POLL_FAST_V2' not in s:
        s = s.replace(
            """  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);""",
            """  useEffect(() => {
    void refreshPlatform();
    // CHAT_POLL_FAST_V2
    const id = window.setInterval(() => { void refreshPlatform(); }, 1200);
    return () => window.clearInterval(id);
  }, [refreshPlatform]);""",
            1,
        )

    p.write_text(s)
    ci = s.find('const customerInitials')
    ch = s.find('const [chatId')
    print('portal order ok' if 0 <= ch < ci else 'ORDER BAD', 'chatId@', ch, 'initials@', ci)


def fix_schema():
    p = ROOT / 'src/context/TicketContext.tsx'
    if p.exists():
        s = p.read_text()
        s = re.sub(r"const CUSTOMER_COLS = '[^']*';[^\n]*", "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at'; // SCHEMA_SAFE_V2", s, count=1)
        p.write_text(s)
        print('customers cols')
    p = ROOT / 'src/context/PlatformContext.tsx'
    if p.exists() and p.stat().st_size > 5000:
        s = p.read_text()
        s = s.replace(
            "supabase.from('automations').select('*')",
            "supabase.from('automations').select('id, name, enabled, trigger, condition_field, condition_op, condition_value, action, action_value, created_at') // SCHEMA_SAFE_V2",
        )
        p.write_text(s)
        print('automations')


def fix_status():
    p = ROOT / 'src/components/TicketDetail.tsx'
    if not p.exists():
        return
    s = p.read_text()
    if 'STATUS_AUTOSAVE_V2' in s:
        print('status already')
        return
    if 'setStatus(e.target.value as Status)' in s:
        s = s.replace(
            'setStatus(e.target.value as Status)',
            "((next) => { setStatus(next); void updateTicket(ticket.id, { status: next }).catch(() => {}); })(e.target.value as Status) /* STATUS_AUTOSAVE_V2 */",
            1,
        )
        p.write_text(s)
        print('status soft')


def restore_claim():
    p = ROOT / 'src/components/LiveChatPage.tsx'
    if not p.exists():
        return
    s = p.read_text()
    if s.count('Yours</span>') == 1:
        print('claim ok')
        return
    claim = """
                      {/* LIVECHAT_MASTER_CLAIM_UI */}
                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button type="button" disabled={busy} onClick={async () => { try { setBusy(true); await claimChat(selected.id, currentAgent.id); } catch (e) { console.error(e); } finally { setBusy(false); } }}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-violet-600 text-white px-2.5 py-1.5 rounded-lg">Claim</button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] text-emerald-300 px-2 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>
                      ) : (selected as { agent_id?: string }).agent_id ? (
                        <span className="text-[11px] text-violet-200 px-2 py-1 font-medium rounded-lg bg-violet-500/15 border border-violet-400/30">Claimed</span>
                      ) : null}
"""
    needle = "{(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? ("
    if needle in s and 'Yours</span>' not in s:
        s = s.replace(needle, claim + "\n                      " + needle, 1)
        print('claim restored')
    p.write_text(s)


def fix_claim_type():
    p = ROOT / 'src/context/PlatformContext.tsx'
    if not p.exists() or p.stat().st_size < 5000:
        return
    s = p.read_text()
    if 'claimChat: (conversationId: string, agentId: string) => Promise<void>;' not in s:
        for old in [
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;",
        ]:
            if old in s:
                s = s.replace(old, old + "\n  claimChat: (conversationId: string, agentId: string) => Promise<void>;", 1)
                print('claim type added')
                break
    p.write_text(s)
    print('claim type count', s.count('claimChat: (conversationId'))


if __name__ == '__main__':
    fix_portal_crash()
    fix_schema()
    fix_status()
    restore_claim()
    fix_claim_type()
    print('HOTFIX V2B DONE')
