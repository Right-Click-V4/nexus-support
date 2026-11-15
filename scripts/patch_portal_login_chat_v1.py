#!/usr/bin/env python3
"""Fix: no agent flash on customer login; claimed agent; ended-chat by agent."""
from pathlib import Path
import re

pl = Path('src/components/PostLoginLoader.tsx')
if pl.exists() and pl.stat().st_size > 500:
    t = pl.read_text()
    if 'POSTLOGIN_ROLE_V1' not in t:
        t = t.replace(
            """export function markJustLoggedIn() {
  try {
    sessionStorage.setItem(POST_LOGIN_KEY, String(Date.now()));
  } catch {
    /* ignore */
  }
}""",
            """export function markJustLoggedIn(role?: 'agent' | 'customer') {
  // POSTLOGIN_ROLE_V1
  try {
    sessionStorage.setItem(POST_LOGIN_KEY, String(Date.now()));
    if (role === 'customer' || role === 'agent') {
      sessionStorage.setItem('nexus_post_login_role', role);
    }
  } catch {
    /* ignore */
  }
}

export function getJustLoggedInRole(): 'agent' | 'customer' | null {
  try {
    const r = sessionStorage.getItem('nexus_post_login_role');
    if (r === 'customer' || r === 'agent') return r;
  } catch { /* ignore */ }
  return null;
}""",
        )
        t = t.replace(
            """export function clearJustLoggedIn() {
  try {
    sessionStorage.removeItem(POST_LOGIN_KEY);
  } catch {
    /* ignore */
  }
}""",
            """export function clearJustLoggedIn() {
  try {
    sessionStorage.removeItem(POST_LOGIN_KEY);
    sessionStorage.removeItem('nexus_post_login_role');
  } catch {
    /* ignore */
  }
}""",
        )
        pl.write_text(t)
        print('PostLoginLoader ok')
    else:
        print('PostLoginLoader already')

lp = Path('src/components/LoginPage.tsx')
if lp.exists() and lp.stat().st_size > 3000:
    t = lp.read_text()
    if 'ROUTE_BEFORE_SIGNIN_V1' not in t:
        if "markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');" in t:
            t = t.replace(
                "markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');",
                "markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');\n"
                "    // ROUTE_BEFORE_SIGNIN_V1\n"
                "    try { window.location.hash = role === 'customer' ? '#/portal' : '#/'; } catch { /* ignore */ }",
                1,
            )
            lp.write_text(t)
            print('LoginPage route')
        else:
            print('LoginPage mark miss')
    else:
        print('LoginPage already')

core = Path('src/SystemAppCore.tsx')
if core.exists() and core.stat().st_size > 2000:
    t = core.read_text()
    if 'pendingCustomer' not in t:
        if 'getJustLoggedInRole' not in t:
            t = "import { getJustLoggedInRole } from './components/PostLoginLoader';\n" + t
        t = t.replace(
            "const { user, loading: authLoading } = useAuth();",
            "const { user, loading: authLoading, accountRole } = useAuth(); // NO_AGENT_FLASH_V1",
            1,
        )
        for ell in ['\u2026', '...']:
            block = (
                "  return (\n"
                f'    <PostLoginShell ready={{!!user}} label="Opening agent workspace{ell}" variant="agent">\n'
                "      <AgentShell />\n"
                "    </PostLoginShell>\n"
                "  );\n"
                "}"
            )
            if block not in t:
                continue
            repl = (
                "  useEffect(() => {\n"
                "    const role = (typeof getJustLoggedInRole === 'function' ? getJustLoggedInRole() : null) || accountRole;\n"
                "    if (user && (role === 'customer' || accountRole === 'customer')) {\n"
                "      const h = (window.location.hash || '').replace(/^#\\/?/, '').toLowerCase();\n"
                "      if (h !== 'portal' && !h.startsWith('portal/')) {\n"
                "        try { window.location.hash = '#/portal'; } catch { /* ignore */ }\n"
                "      }\n"
                "    }\n"
                "  }, [user, accountRole]);\n"
                "  const pendingCustomer =\n"
                "    accountRole === 'customer' || (typeof getJustLoggedInRole === 'function' && getJustLoggedInRole() === 'customer');\n"
                "  if (pendingCustomer) {\n"
                f'    return <BootLoader label="Opening customer portal{ell}" />;\n'
                "  }\n"
                + block
            )
            t = t.replace(block, repl, 1)
            print('AgentOrLogin', ell)
            break
        else:
            print('AgentOrLogin block miss')
        core.write_text(t)
        print('SystemAppCore braces', t.count('{') - t.count('}'))
    else:
        print('SystemAppCore already')

plc = Path('src/components/PortalLiveChat.tsx')
if plc.exists() and plc.stat().st_size > 5000 and 'ENDED_BY_AGENT_V1' not in plc.read_text():
    s = plc.read_text()
    s = s.replace(
        "if (st === 'ended' || st === 'archived') {",
        "if (st === 'ended' || st === 'archived' || st === 'closed') { // ENDED_BY_AGENT_V1",
    )
    if "Connected with support" in s and "agent?.name" not in s:
        s = s.replace(
            "conversation?.status === 'ended' ? 'Chat ended' : chatViewers.length > 0 ? `Connected · ${chatViewers.map((v) => v.name).join(', ')}` : 'Connected with support'",
            "['ended','archived','closed'].includes((conversation?.status || '').toLowerCase())\n"
            "                ? (() => {\n"
            "                    const aid = (conversation as { agent_id?: string })?.agent_id;\n"
            "                    const agent = (agents || []).find((a) => a.id === aid);\n"
            "                    return agent?.name ? `Chat ended by ${agent.name}` : 'Chat ended';\n"
            "                  })()\n"
            "                : (() => {\n"
            "                    const aid = (conversation as { agent_id?: string })?.agent_id;\n"
            "                    const agent = (agents || []).find((a) => a.id === aid);\n"
            "                    if (agent?.name) return `Agent: ${agent.name}`;\n"
            "                    if (chatViewers.length > 0) return `Connected · ${chatViewers.map((v) => v.name).join(', ')}`;\n"
            "                    return 'Connected with support';\n"
            "                  })()",
        )
        print('PLC header agent')
    plc.write_text(s)
    print('PLC braces', s.count('{') - s.count('}'))

plv = Path('src/components/PortalLiveChatView.tsx')
if plv.exists() and plv.stat().st_size > 3000:
    s = plv.read_text()
    if 'ENDED_BY_AGENT_V1' not in s and 'This chat was ended by support' in s:
        s = s.replace(
            'This chat was ended by support. You can start a new conversation anytime.',
            "{(() => {\n"
            "              // ENDED_BY_AGENT_V1\n"
            "              const aid = (conversation as { agent_id?: string } | null)?.agent_id;\n"
            "              const agent = (agents || []).find((a) => a.id === aid);\n"
            "              return agent?.name\n"
            "                ? `This chat was ended by ${agent.name}. You can start a new conversation anytime.`\n"
            "                : 'This chat was ended by support. You can start a new conversation anytime.';\n"
            "            })()}",
        )
        plv.write_text(s)
        print('PLV ended')

print('patch_portal_login_chat_v1 done')
