#!/usr/bin/env python3
"""Hotfix V2: customerInitials crash, schema columns, status autosave, claim UI."""
from pathlib import Path
import re

ROOT = Path('.')

def fix_portal_crash():
    p = ROOT / 'src/components/PortalLiveChatView.tsx'
    if not p.exists():
        print('no portal livechat')
        return
    s = p.read_text()
    if 'SAFE_IDENTITY_V2' not in s:
        marker = "const { conversations, createChat, sendChatMessage, setChatStatus, refreshPlatform } = usePlatform();"
        inject = marker + """

  // SAFE_IDENTITY_V2 — always defined (prevents customerInitials ReferenceError)
  const conversation = useMemo(
    () => {
      try {
        const id = typeof chatId !== 'undefined' ? chatId : null;
        return id ? (conversations || []).find((c) => c.id === id) : null;
      } catch { return null; }
    },
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
  const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';"""
        if marker in s:
            s = s.replace(marker, inject, 1)
            print('SAFE_IDENTITY_V2')
        else:
            print('marker miss')

    if 'SAFE_IDENTITY_V2' in s and 'CUSTOMER_CHAT_IDENTITY_V1' in s:
        s2 = re.sub(
            r'\n  // CUSTOMER_CHAT_IDENTITY_V1[\s\S]*?(?=\n  const isOnHold|\n  useEffect|\n  const online|\n  const startChat|\n  // CHAT_POLL)',
            '\n',
            s,
            count=1,
        )
        if s2 != s:
            s = s2
            print('stripped old identity')

    while s.count('const conversation = useMemo') > 1:
        first = s.find('const conversation = useMemo')
        second = s.find('const conversation = useMemo', first + 1)
        if second == -1:
            break
        end = s.find(');', second)
        if end == -1:
            break
        chunk_end = end + 2
        tail = s[chunk_end:chunk_end + 250]
        extra = re.match(
            r"\n  const messages = conversation\?\.messages \|\| \[\];\n  const isOnHold = \(conversation\?\.status \|\| ''\)\.toLowerCase\(\) === 'on_hold';",
            tail,
        )
        if extra:
            chunk_end += extra.end()
        s = s[:second] + s[chunk_end:]
        print('removed extra conversation')

    if s.count('const isOnHold =') > 1:
        first = s.find('const isOnHold =')
        rest = s[first + 1:]
        rest2 = re.sub(r'\n  const isOnHold = [^;]+;', '', rest, count=1)
        s = s[: first + 1] + rest2
        print('deduped isOnHold')

    if 'CHAT_POLL_FAST_V2' not in s and 'CHAT_POLL_FAST_V1' not in s:
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
        print('fast poll')

    p.write_text(s)
    print('portal ok', s.count('const customerInitials'), s.count('const conversation = useMemo'))


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
        p.write_text(s)
        print('automations cols')

    for path in (ROOT / 'src').rglob('*.tsx'):
        t = path.read_text()
        if "from('customers')" in t and 'avatar_url' in t:
            t2 = re.sub(
                r"from\('customers'\)\.select\('([^']*)'\)",
                lambda m: "from('customers').select('%s')" % re.sub(r',?\s*avatar_url', '', m.group(1)).strip(',').strip()
                if 'avatar_url' in m.group(1) else m.group(0),
                t,
            )
            if t2 != t:
                path.write_text(t2)
                print('strip avatar', path.name)


def fix_status():
    p = ROOT / 'src/components/TicketDetail.tsx'
    if not p.exists():
        print('no TicketDetail')
        return
    s = p.read_text()
    if 'STATUS_AUTOSAVE_V2' in s:
        print('status already')
        return
    old = """onChange={(e) => setStatus(e.target.value as Status)}
                className=\"ticket-input w-full px-3 py-2 text-sm rounded-lg\""""
    new = """onChange={(e) => {
                  // STATUS_AUTOSAVE_V2
                  const next = e.target.value as Status;
                  setStatus(next);
                  void updateTicket(ticket.id, { status: next }).catch((err) => console.warn('status save', err));
                }}
                className=\"ticket-input w-full px-3 py-2 text-sm rounded-lg\""""
    if old in s:
        p.write_text(s.replace(old, new, 1))
        print('status autosave')
    elif 'setStatus(e.target.value as Status)' in s:
        p.write_text(s.replace(
            'setStatus(e.target.value as Status)',
            "((next) => { setStatus(next); void updateTicket(ticket.id, { status: next }).catch(() => {}); })(e.target.value as Status) /* STATUS_AUTOSAVE_V2 */",
            1,
        ))
        print('status soft')
    else:
        print('status miss')


def restore_claim():
    p = ROOT / 'src/components/LiveChatPage.tsx'
    if not p.exists():
        return
    s = p.read_text()
    claim = """
                      {/* LIVECHAT_MASTER_CLAIM_UI */}
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
"""
    if s.count('Yours</span>') == 1 and 'LIVECHAT_MASTER_CLAIM_UI' in s:
        print('claim ok')
        return
    s = re.sub(r"\s*\{/\* LIVECHAT_MASTER_CLAIM_UI[^\n]*\*/\}\s*", "\n", s)
    while s.count('Yours</span>') > 0:
        s = re.sub(
            r'\s*<span className="text-\[11px\] text-emerald-300[^"]*"[^>]*>Yours</span>',
            '',
            s,
            count=1,
        )
    needle = "{(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? ("
    if needle in s:
        s = s.replace(needle, claim + "\n                      " + needle, 1)
        print('claim restored')
    if 'claimChat' not in s[s.find('usePlatform'):s.find('usePlatform') + 400] if 'usePlatform' in s else True:
        s = s.replace(
            'refreshPlatform,\n  } = usePlatform();',
            'refreshPlatform,\n    claimChat,\n  } = usePlatform();',
            1,
        )
    p.write_text(s)
    print('Yours count', s.count('Yours</span>'))


if __name__ == '__main__':
    fix_portal_crash()
    fix_schema()
    fix_status()
    restore_claim()
    print('HOTFIX V2 DONE')
