#!/usr/bin/env python3
"""Portal live chat UI: ensure customerAvatar/agentPresent, agent name, avatars, wider layout."""
from pathlib import Path
import re

def ensure_vars(t: str) -> str:
    if 'const customerAvatar' not in t:
        t2, n = re.subn(
            r"(const customerInitials = customerName[\s\S]*?\.toUpperCase\(\) \|\| 'Y';)",
            r"""\1

  const customerAvatar = String(
    (user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata?.avatar_url ||
      (user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata?.picture ||
      '',
  ).trim();
""",
            t,
            count=1,
        )
        if n:
            t = t2
            print('customerAvatar added')
        elif "const messages = conversation?.messages || [];" in t:
            t = t.replace(
                "const messages = conversation?.messages || [];",
                "const messages = conversation?.messages || [];\n  const customerAvatar = String((user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata?.avatar_url || (user as { user_metadata?: Record<string, unknown> } | null)?.user_metadata?.picture || '').trim();",
                1,
            )
            print('customerAvatar emergency')

    if 'const agentPresent' not in t:
        t2, n = re.subn(
            r"(const agentInitials = agentName[\s\S]*?\.toUpperCase\(\) \|\| 'A';)",
            r"""\1

  const agentPresent =
    Boolean(assignedAgent) ||
    (messages || []).some((m) => m.sender === 'agent') ||
    ['active', 'on_hold', 'on-hold'].includes((conversation?.status || '').toLowerCase());
""",
            t,
            count=1,
        )
        if n:
            t = t2
            print('agentPresent added')
        elif "const agentAvatar = assignedAgent?.avatar_url || '';" in t:
            t = t.replace(
                "const agentAvatar = assignedAgent?.avatar_url || '';",
                "const agentAvatar = assignedAgent?.avatar_url || '';\n  const agentPresent =\n    Boolean(assignedAgent) ||\n    (messages || []).some((m) => m.sender === 'agent') ||\n    ['active', 'on_hold', 'on-hold'].includes((conversation?.status || '').toLowerCase());",
                1,
            )
            print('agentPresent via agentAvatar')

    old_aa = """  const assignedAgent = useMemo(() => {
    const aid = (conversation as any)?.agent_id;
    if (!aid) return null;
    return (agents || []).find((a: any) => a.id === aid) || null;
  }, [conversation, agents]);
"""
    new_aa = """  const assignedAgent = useMemo(() => {
    const aid = (conversation as { agent_id?: string } | null)?.agent_id;
    if (aid) {
      const hit = (agents || []).find((a) => a.id === aid || (a as { user_id?: string }).user_id === aid);
      if (hit) return hit;
    }
    return null;
  }, [conversation, agents]);
"""
    if old_aa in t:
        t = t.replace(old_aa, new_aa, 1)
        print('assignedAgent improved')
    t = t.replace('return (agents || [])[0] || null;', 'return null;')

    return t


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
    p.write_text(s)


def patch_portal():
    pv = Path('src/components/PortalLiveChatView.tsx')
    if not pv.exists():
        return
    t = pv.read_text()
    t = ensure_vars(t)
    t = t.replace(
        "{assignedAgent ? 'Agent' : 'Waiting for agent'}",
        "{agentPresent ? 'Chatting with you' : 'Waiting for agent'}",
    )
    t = t.replace('max-w-3xl mx-auto', 'max-w-6xl mx-auto w-full')
    t = t.replace('min-h-[60vh]', 'min-h-[78vh]')
    t = t.replace('min-h-[75vh]', 'min-h-[78vh]')
    t = t.replace('max-h-[50vh]', 'max-h-[min(70vh,720px)]')
    pv.write_text(t)
    print('portal ui done', pv.stat().st_size)
    if 'const customerAvatar' not in t:
        print('WARN customerAvatar missing')
    if 'const agentPresent' not in t:
        print('WARN agentPresent missing')


patch_platform()
patch_portal()
print('DONE')
