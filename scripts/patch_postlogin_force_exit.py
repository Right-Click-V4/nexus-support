#!/usr/bin/env python3
from pathlib import Path

pll = Path("src/components/PostLoginLoader.tsx")
if pll.exists():
    t = pll.read_text()
    if "postlogin-force-exit-v1" not in t:
        if "export function clearJustLoggedIn" not in t:
            t = t.replace("function clearJustLoggedIn() {", "export function clearJustLoggedIn() {", 1)
            print("exported clearJustLoggedIn")
        t = "/* postlogin-force-exit-v1 */\n" + t
        pll.write_text(t)

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "portal-force-ready-v1" not in s:
        if "clearJustLoggedIn" not in s:
            s = s.replace(
                "hasJustLoggedIn } from './components/PostLoginLoader';",
                "hasJustLoggedIn, clearJustLoggedIn } from './components/PostLoginLoader';",
                1,
            )
            print("import clear")

        old = """export function PortalShell() {
  const { enabled, ready } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const { user, accountRole, authBusy } = useAuth();
  const admin = accountRole === 'admin' || isAdmin;

  // Customers must not wait on adminReady (agents table check) — that caused endless post-login.
  const portalBlocked =
    !ready ||
    !site404Ready ||
    authBusy ||
    (user && accountRole !== 'customer' && !adminReady);
  if (portalBlocked) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal…" />;
  }"""

        new = """export function PortalShell() {
  const { enabled, ready } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const { user, accountRole, authBusy } = useAuth();
  const admin = accountRole === 'admin' || isAdmin;
  const [forceReady, setForceReady] = useState(false);

  // Never stick on post-login / boot screens if maintenance/auth checks hang
  useEffect(() => {
    const t = window.setTimeout(() => {
      setForceReady(true);
      try { clearJustLoggedIn(); } catch { /* ignore */ }
    }, 4500);
    return () => window.clearTimeout(t);
  }, []);

  // Customers must not wait on adminReady (agents table check) — that caused endless post-login.
  const portalBlocked =
    !forceReady &&
    (!ready ||
      !site404Ready ||
      authBusy ||
      (user && accountRole !== 'customer' && !adminReady));
  if (portalBlocked) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal…" />;
  }"""

        if old in s:
            s = s.replace(old, new, 1)
            print("portal shell force ready")
        else:
            print("portal shell pattern miss")
        s = "/* portal-force-ready-v1 */\n" + s
        sa.write_text(s)

auth = Path("src/context/AuthContext.tsx")
if auth.exists():
    a = auth.read_text()
    if "supabase-paused-hint-v1" not in a:
        old_msg = (
            "'Cannot reach Supabase (Failed to fetch). Check that VITE_SUPABASE_URL is the full ' +\n"
            "        'https://YOUR_PROJECT.supabase.co URL and that the project is not paused. ' +\n"
            "        'Update GitHub Actions secrets and redeploy if this is the live site.'"
        )
        new_msg = (
            "'Cannot reach Supabase (Failed to fetch). Most common cause: the Supabase project is PAUSED. ' +\n"
            "        'Open supabase.com/dashboard, open project gcpmmbiarqracxfskirp, click Restore. ' +\n"
            "        'Also allow *.supabase.co in the browser if an ad-blocker is on.'"
        )
        if old_msg in a:
            a = a.replace(old_msg, new_msg, 1)
            print("auth error message")
        a = "/* supabase-paused-hint-v1 */\n" + a
        auth.write_text(a)
print("done")
