#!/usr/bin/env python3
"""Ensure customers land on #/portal and AgentShell redirects them."""
from pathlib import Path

lp = Path('src/components/LoginPage.tsx')
if lp.exists():
    s = lp.read_text()
    if "signIn(email, password, role)" not in s and "await signIn(email, password);" in s:
        s = s.replace(
            "await signIn(email, password);",
            "await signIn(email, password, role);\n    try { window.location.hash = role === 'customer' ? '#/portal' : '#/'; } catch {}",
            1,
        )
        print('login signIn role')
    if "window.location.hash = role === 'customer'" not in s and "signIn(email, password, role)" in s:
        s = s.replace(
            "await signIn(email, password, role);",
            "await signIn(email, password, role);\n    // ROUTE_BY_ROLE_V1\n    try { window.location.hash = role === 'customer' ? '#/portal' : '#/'; } catch {}",
            1,
        )
        print('login hash')
    lp.write_text(s)

core = Path('src/SystemAppCore.tsx')
if core.exists():
    c = core.read_text()
    if "accountRole" not in c.split('function AgentShell')[1][:900]:
        c = c.replace(
            'const { user, loading: authLoading, signOut } = useAuth();',
            "const { user, loading: authLoading, signOut, accountRole } = useAuth();",
            1,
        )
        print('accountRole destructure')
    if 'CUSTOMER_FORCE_PORTAL_V1' not in c:
        inject = """
  // CUSTOMER_FORCE_PORTAL_V1 — never keep customers on the agent desk
  useEffect(() => {
    if (!user) return;
    if (accountRole === 'customer') {
      try {
        const h = (window.location.hash || '').replace(/^#\\/?/, '').toLowerCase();
        if (h !== 'portal' && !h.startsWith('portal/')) {
          window.location.hash = '#/portal';
        }
      } catch { /* ignore */ }
    }
  }, [user, accountRole]);

"""
        if 'const authKnown = forceReady || !authLoading;' in c:
            c = c.replace(
                'const authKnown = forceReady || !authLoading;',
                inject + '  const authKnown = forceReady || !authLoading;',
                1,
            )
            print('force portal effect')
    core.write_text(c)

print('customer route patch done')
