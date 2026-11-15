#!/usr/bin/env python3
"""Fix: no agent flash on customer login; correct claimed agent; ended-chat message."""
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
        print('PostLoginLoader role storage')
    else:
        print('PostLoginLoader already')
else:
    print('PostLoginLoader skip')

lp = Path('src/components/LoginPage.tsx')
if lp.exists() and lp.stat().st_size > 3000:
    t = lp.read_text()
    if 'ROUTE_BEFORE_SIGNIN_V1' not in t:
        old = "markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');\n    try {\n      await signIn(email, password, role);"
        new = """// ROUTE_BEFORE_SIGNIN_V1 — set portal hash before auth resolves so Agent UI never flashes
    markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');
    try {
      if (role === 'customer') {
        try { window.location.hash = '#/portal'; } catch { /* ignore */ }
      } else {
        try { window.location.hash = '#/'; } catch { /* ignore */ }
      }
      await signIn(email, password, role);"""
        if old in t:
            t = t.replace(old, new, 1)
            print('LoginPage route before signin')
        elif "markJustLoggedIn(role === 'agent' ? 'agent' : 'customer')" in t:
            t = t.replace(
                "markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');",
                """markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');
    // ROUTE_BEFORE_SIGNIN_V1
    try { window.location.hash = role === 'customer' ? '#/portal' : '#/'; } catch { /* ignore */ }""",
                1,
            )
            print('LoginPage soft route')
        else:
            print('LoginPage mark miss')
        lp.write_text(t)
    else:
        print('LoginPage already')
else:
    print('LoginPage skip')

core = Path('src/SystemAppCore.tsx')
if core.exists() and core.stat().st_size > 2000:
    t = core.read_text()
    if 'NO_AGENT_FLASH_V1' not in t and 'pendingCustomer' not in t:
        if 'getJustLoggedInRole' not in t:
            t = "import { getJustLoggedInRole } from './components/PostLoginLoader';\n" + t
        old_aol = """function AgentOrLogin() {
  const { user, loading: authLoading } = useAuth();
  const [forceReady, setForceReady] = useState(false);
  useEffect(() => {
    const t = window.setTimeout(() => setForceReady(true), 2500);
    return () => window.clearTimeout(t);
  }, []);
  if (!(forceReady || !authLoading)) {
    return <BootLoader label="Loading\u2026" />;
  }
  if (!user) {
    return <LoginPage />;
  }
  return (
    <PostLoginShell ready={!!user} label="Opening agent workspace\u2026" variant="agent">
      <AgentShell />
    </PostLoginShell>
  );
}"""
        # try with actual ellipsis chars from file
        if 'function AgentOrLogin' in t:
            t = t.replace(
                "const { user, loading: authLoading } = useAuth();",
                "const { user, loading: authLoading, accountRole } = useAuth(); // NO_AGENT_FLASH_V1",
                1,
            )
            if 'pendingCustomer' not in t:
                t = t.replace(
                    """  return (
    <PostLoginShell ready={!!user} label="Opening agent workspace\u2026" variant="agent">
      <AgentShell />
    </PostLoginShell>
  );
}""",
                    """  useEffect(() => {
    const role = (typeof getJustLoggedInRole === 'function' ? getJustLoggedInRole() : null) || accountRole;
    if (user && (role === 'customer' || accountRole === 'customer')) {
      const h = (window.location.hash || '').replace(/^#\\/?/, '').toLowerCase();
      if (h !== 'portal' && !h.startsWith('portal/')) {
        try { window.location.hash = '#/portal'; } catch { /* ignore */ }
      }
    }
  }, [user, accountRole]);
  const pendingCustomer =
    accountRole === 'customer' || (typeof getJustLoggedInRole === 'function' && getJustLoggedInRole() === 'customer');
  if (pendingCustomer) {
    return <BootLoader label="Opening customer portal\u2026" />;
  }
  return (
    <PostLoginShell ready={!!user} label="Opening agent workspace\u2026" variant="agent">
      <AgentShell />
    </PostLoginShell>
  );
}""",
                    1,
                )
            # also try unicode ellipsis
            if 'pendingCustomer' not in t:
                t = t.replace(
                    'label="Opening agent workspace\u2026"',
                    'label="Opening agent workspace\u2026"',
                )
                # raw ellipsis
                needle = '  return (\n    <PostLoginShell ready={!!user} label="Opening agent workspace\u2026" variant="agent">\n      <AgentShell />\n    </PostLoginShell>\n  );\n}'
                # File may use real ellipsis character
                for ell in ['\u2026', '...']:
                    block = (
                        '  return (\n'
                        f'    <PostLoginShell ready={{!!user}} label="Opening agent workspace{ell}" variant="agent">\n'
                        '      <AgentShell />\n'
                        '    </PostLoginShell>\n'
                        '  );\n'
                        '}'
                    )
                    if block in t:
                        repl = (
                            '  useEffect(() => {\n'
                            "    const role = (typeof getJustLoggedInRole === 'function' ? getJustLoggedInRole() : null) || accountRole;\n"
                            "    if (user && (role === 'customer' || accountRole === 'customer')) {\n"
                            "      const h = (window.location.hash || '').replace(/^#\\/?/, '').toLowerCase();\n"
                            "      if (h !== 'portal' && !h.startsWith('portal/')) {\n"
                            "        try { window.location.hash = '#/portal'; } catch { /* ignore */ }\n"
                            '      }\n'
                            '    }\n'
                            '  }, [user, accountRole]);\n'
                            '  const pendingCustomer =\n'
                            "    accountRole === 'customer' || (typeof getJustLoggedInRole === 'function' && getJustLoggedInRole() === 'customer');\n"
                            '  if (pendingCustomer) {\n'
                            f'    return <BootLoader label="Opening customer portal{ell}" />;
'
                            '  }\n'
                            + block
                        )
                        t = t.replace(block, repl, 1)
                        print('AgentOrLogin replaced', ell)
                        break
                if 'pendingCustomer' not in t:
                    print('AgentOrLogin pattern miss')
            else:
                print('AgentOrLogin ok')
        core.write_text(t)
        print('SystemAppCore braces', t.count('{') - t.count('}'))
    else:
        print('SystemAppCore already')
else:
    print('SystemAppCore skip')

plc = Path('src/components/PortalLiveChat.tsx')
if not plc.exists() or plc.stat().st_size < 2000:
    print('PortalLiveChat stub — restore at deploy')
else:
    s = plc.read_text()
    if 'ENDED_BY_AGENT_V1' not in s:
        s = s.replace(
            "if (st === 'ended' || st === 'archived') {",
            "if (st === 'ended' || st === 'archived' || st === 'closed') { // ENDED_BY_AGENT_V1",
        )
        if 'ended by' not in s.lower():
            marker = '{isOnHold ? ('
            if marker in s:
                inject = (
                    "{(['ended','archived','closed'].includes((conversation?.status || '').toLowerCase())) ? (\n"
                    '        <div className="mx-4 mt-3 rounded-xl border border-rose-400/40 bg-rose-500/15 px-4 py-3 text-sm text-rose-100">\n'
                    '          <div className="font-semibold text-rose-50">\n'
                    '            {/* ENDED_BY_AGENT_V1 */}\n'
                    '            {(() => {\n'
                    "              const aid = (conversation as { agent_id?: string })?.agent_id;\n"
                    '              const agent = (agents || []).find((a) => a.id === aid);\n'
                    "              const nm = agent?.name || 'Support';\n"
                    '              return `This chat was ended by ${nm}.`;\n'
                    '            })()}\n'
                    '          </div>\n'
                    '          <p className="text-xs mt-1 text-rose-100/90">You can start a new conversation anytime.</p>\n'
                    '          <button\n'
                    '            type="button"\n'
                    '            className="mt-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-500"\n'
                    '            onClick={() => {\n'
                    '              try { sessionStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ }\n'
                    '              setChatId(null);\n'
                    '            }}\n'
                    '          >\n'
                    '            Start new chat\n'
                    '          </button>\n'
                    '        </div>\n'
                    '      ) : null}\n\n'
                    '      {isOnHold ? ('
                )
                s = s.replace(marker, inject, 1)
                print('ended banner injected')
        if 'Connected with support' in s:
            s = s.replace(
                "conversation?.status === 'ended' ? 'Chat ended' : chatViewers.length > 0 ? `Connected \u00b7 ${chatViewers.map((v) => v.name).join(', ')}` : 'Connected with support'",
                "['ended','archived','closed'].includes((conversation?.status || '').toLowerCase())\n"
                '                ? (() => {\n'
                "                    const aid = (conversation as { agent_id?: string })?.agent_id;\n"
                '                    const agent = (agents || []).find((a) => a.id === aid);\n'
                "                    return agent?.name ? `Chat ended by ${agent.name}` : 'Chat ended';\n"
                '                  })()\n'
                '                : (() => {\n'
                "                    const aid = (conversation as { agent_id?: string })?.agent_id;\n"
                '                    const agent = (agents || []).find((a) => a.id === aid);\n'
                "                    if (agent?.name) return `Agent: ${agent.name}`;\n"
                "                    if (chatViewers.length > 0) return `Connected \u00b7 ${chatViewers.map((v) => v.name).join(', ')}`;\n"
                "                    return 'Connected with support';\n"
                '                  })()',
            )
            # also try with real middle-dot character
            s = s.replace(
                "conversation?.status === 'ended' ? 'Chat ended' : chatViewers.length > 0 ? `Connected · ${chatViewers.map((v) => v.name).join(', ')}` : 'Connected with support'",
                "['ended','archived','closed'].includes((conversation?.status || '').toLowerCase())\n"
                '                ? (() => {\n'
                "                    const aid = (conversation as { agent_id?: string })?.agent_id;\n"
                '                    const agent = (agents || []).find((a) => a.id === aid);\n'
                "                    return agent?.name ? `Chat ended by ${agent.name}` : 'Chat ended';\n"
                '                  })()\n'
                '                : (() => {\n'
                "                    const aid = (conversation as { agent_id?: string })?.agent_id;\n"
                '                    const agent = (agents || []).find((a) => a.id === aid);\n'
                "                    if (agent?.name) return `Agent: ${agent.name}`;\n"
                "                    if (chatViewers.length > 0) return `Connected · ${chatViewers.map((v) => v.name).join(', ')}`;\n"
                "                    return 'Connected with support';\n"
                '                  })()',
            )
            print('header agent resolve')
        plc.write_text(s)
        print('PortalLiveChat braces', s.count('{') - s.count('}'))
    else:
        print('PortalLiveChat already')

plv = Path('src/components/PortalLiveChatView.tsx')
if plv.exists() and plv.stat().st_size > 3000:
    s = plv.read_text()
    if 'ENDED_BY_AGENT_V1' not in s:
        s = s.replace(
            'This chat was ended by support. You can start a new conversation anytime.',
            "{(() => {\n"
            '              // ENDED_BY_AGENT_V1\n'
            "              const aid = (conversation as { agent_id?: string } | null)?.agent_id;\n"
            '              const agent = (agents || []).find((a) => a.id === aid);\n'
            '              return agent?.name\n'
            '                ? `This chat was ended by ${agent.name}. You can start a new conversation anytime.`\n'
            "                : 'This chat was ended by support. You can start a new conversation anytime.';\n"
            '            })()}',
        )
        plv.write_text(s)
        print('PLV ended-by name')
    else:
        print('PLV already')

print('patch_portal_login_chat_v1 done')
