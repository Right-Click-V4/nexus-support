#!/usr/bin/env python3
"""Fix React #310: move AgentOrLogin hooks before any early return."""
from pathlib import Path
import re

core = Path('src/SystemAppCore.tsx')
if not core.exists() or core.stat().st_size < 2000:
    print('SystemAppCore skip')
    raise SystemExit(0)

t = core.read_text()
if 'AGENT_HOOKS_SAFE_V1' in t:
    print('already')
    raise SystemExit(0)

if 'getJustLoggedInRole' not in t:
    if "from './components/PostLoginLoader'" in t:
        t = t.replace(
            "import { BootLoader, PostLoginShell } from './components/PostLoginLoader';",
            "import { BootLoader, PostLoginShell, getJustLoggedInRole } from './components/PostLoginLoader';",
            1,
        )
    else:
        t = "import { getJustLoggedInRole } from './components/PostLoginLoader';\n" + t

new_aol = """function AgentOrLogin() {
  // AGENT_HOOKS_SAFE_V1 - all hooks before any return (fixes React #310)
  const { user, loading: authLoading, accountRole } = useAuth();
  const [forceReady, setForceReady] = useState(false);
  useEffect(() => {
    const t = window.setTimeout(() => setForceReady(true), 2500);
    return () => window.clearTimeout(t);
  }, []);
  useEffect(() => {
    const role =
      (typeof getJustLoggedInRole === 'function' ? getJustLoggedInRole() : null) || accountRole;
    if (user && (role === 'customer' || accountRole === 'customer')) {
      const h = (window.location.hash || '').replace(/^#\\/?/, '').toLowerCase();
      if (h !== 'portal' && !h.startsWith('portal/')) {
        try {
          window.location.hash = '#/portal';
        } catch {
          /* ignore */
        }
      }
    }
  }, [user, accountRole]);

  if (!(forceReady || !authLoading)) {
    return <BootLoader label="Loading..." />;
  }
  if (!user) {
    return <LoginPage />;
  }
  const pendingCustomer =
    accountRole === 'customer' ||
    (typeof getJustLoggedInRole === 'function' && getJustLoggedInRole() === 'customer');
  if (pendingCustomer) {
    return <BootLoader label="Opening customer portal..." />;
  }
  return (
    <PostLoginShell ready={!!user} label="Opening agent workspace..." variant="agent">
      <AgentShell />
    </PostLoginShell>
  );
}
"""

m = re.search(r'function AgentOrLogin\(\) \{[\s\S]*?\n\}\n\nexport function Root', t)
if m:
    t = t[: m.start()] + new_aol + '\nexport function Root' + t[m.end() - len('export function Root') :]
    print('AgentOrLogin replaced')
else:
    m2 = re.search(r'function AgentOrLogin\(\) \{[\s\S]*?\n\}', t)
    if m2:
        t = t[: m2.start()] + new_aol + t[m2.end() :]
        print('AgentOrLogin soft replace')
    else:
        print('AgentOrLogin pattern miss')
        raise SystemExit(1)

bal = t.count('{') - t.count('}')
core.write_text(t)
print('braces', bal)
if bal != 0:
    raise SystemExit('brace imbalance ' + str(bal))
print('patch_agent_hooks_v1 done')
