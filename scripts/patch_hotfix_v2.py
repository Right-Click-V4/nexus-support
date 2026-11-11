#!/usr/bin/env python3
"""Hotfix V2c: identity block without duplicate const declarations (fixes CI build)."""
from pathlib import Path
import re

ROOT = Path('.')


def _dedupe_const(s: str, name: str) -> str:
    """Keep first `const name = ...;` (or useMemo block), remove later ones."""
    pat = re.compile(
        rf'(^\s*const {re.escape(name)}\s*=\s*(?:useMemo\(\(\)\s*=>\s*\{{[\s\S]*?\}}\s*,\s*\[[^\]]*\]\)|[^;]+);)',
        re.M,
    )
    matches = list(pat.finditer(s))
    if len(matches) <= 1:
        return s
    for m in reversed(matches[1:]):
        s = s[: m.start()] + s[m.end() :]
        print(f'dedupe {name}')
    return s


def fix_portal_crash():
    p = ROOT / 'src/components/PortalLiveChatView.tsx'
    if not p.exists():
        print('no portal')
        return
    s = p.read_text()

    if 'SAFE_IDENTITY_V2' in s or 'SAFE_IDENTITY_V2B' in s or 'SAFE_IDENTITY_V2C' in s:
        s = re.sub(
            r'\n  // SAFE_IDENTITY_V2[BC]?[\s\S]*?(?=\n  // MULTI_CHAT|\n  useEffect|\n  const \[desk|\n  const onlineAgents|\n  const hasAgentOnline)',
            '\n',
            s,
            count=3,
        )
        print('cleared old SAFE blocks')

    for name in (
        'conversation',
        'messages',
        'isOnHold',
        'customerName',
        'customerInitials',
        'assignedAgent',
        'agentName',
        'agentAvatar',
        'agentInitials',
        'linkedTicketId',
        'linkedTicket',
        'agentPresent',
    ):
        s = _dedupe_const(s, name)

    if 'const conversation = useMemo' not in s:
        inject_after = None
        for m in [
            "const [chatId, setChatId] = useState<string | null>(null);",
            "const [chatId, setChatId] = useState(null);",
        ]:
            if m in s:
                inject_after = m
                break
        if inject_after:
            block = inject_after + """
  // SAFE_IDENTITY_V2C
  const conversation = useMemo(
    () => (chatId ? (conversations || []).find((c) => c.id === chatId) : null),
    [conversations, chatId],
  );
  const messages = (conversation?.messages || []) as Array<{ id?: string; text?: string; body?: string; sender?: string; author?: string; created_at?: string }>;
  const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';
"""
            s = s.replace(inject_after, block, 1)
            print('SAFE_IDENTITY_V2C minimal')

    if 'const assignedAgent = useMemo' not in s and 'const hasAgentOnline = onlineAgents.length > 0;' in s:
        s = s.replace(
            'const hasAgentOnline = onlineAgents.length > 0;',
            """const hasAgentOnline = onlineAgents.length > 0;
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
""",
            1,
        )
        print('agent helpers added')

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

    for name in (
        'conversation',
        'messages',
        'isOnHold',
        'assignedAgent',
        'agentName',
        'agentAvatar',
        'agentInitials',
        'customerInitials',
    ):
        s = _dedupe_const(s, name)

    p.write_text(s)
    print('messages count', s.count('const messages'))
    print('assignedAgent count', s.count('const assignedAgent'))
    print('portal ok' if s.count('const messages') <= 1 and s.count('const assignedAgent') <= 1 else 'STILL DUP')


def fix_schema():
    p = ROOT / 'src/context/TicketContext.tsx'
    if p.exists():
        s = p.read_text()
        s = re.sub(
            r"const CUSTOMER_COLS = '[^']*';[^\n]*",
            "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at'; // SCHEMA_SAFE_V2",
            s,
            count=1,
        )
        p.write_text(s)
        print('customers cols')
    p = ROOT / 'src/context/PlatformContext.tsx'
    if p.exists() and p.stat().st_size > 5000:
        s = p.read_text()
        s = s.replace(
            "supabase.from('automations').select('*')",
            "supabase.from('automations').select('id, name, enabled, trigger, condition_field, condition_op, condition_value, action, action_value, created_at') // SCHEMA_SAFE_V2",
        )
        s = s.replace(
            "supabase.from('automations').select('id, name, enabled, trigger, condition_field, condition_op, condition_value, action, action_value, actions, created_at')",
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
    print('HOTFIX V2C DONE')
