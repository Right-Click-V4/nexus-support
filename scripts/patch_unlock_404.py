#!/usr/bin/env python3
"""Unlock sticky #404 / site-404 cache so login is always reachable."""
from pathlib import Path

core = Path('src/SystemAppCore.tsx')
if core.exists():
    s = core.read_text()
    if "mode === 'notfound' ? <NotFoundScreen />" in s:
        s = s.replace(
            "mode === 'notfound' ? <NotFoundScreen /> : <AgentShell />",
            """mode === 'notfound' ? (
          <NotFoundScreen
            onGoHome={() => {
              try { localStorage.setItem('nexus-site-404-on', '0'); localStorage.removeItem('nexus-site-404-on'); } catch {}
              window.location.hash = '';
              window.location.reload();
            }}
            onAdminSignIn={() => {
              try { localStorage.setItem('nexus-site-404-on', '0'); localStorage.removeItem('nexus-site-404-on'); } catch {}
              window.location.hash = '';
              window.location.reload();
            }}
          />
        ) : <AgentShell />""",
            1,
        )
        core.write_text(s)
        print('Root NotFound recovery wired')
    else:
        print('Root already has handlers or pattern changed')

main = Path('src/main.tsx')
if main.exists():
    s = main.read_text()
    if 'EARLY_404_UNLOCK' not in s and 'installPollThrottle()' in s:
        inject = """
// EARLY_404_UNLOCK — clear sticky #404 from older ErrorBoundary builds
try {
  const h = (window.location.hash || '').replace(/^#\\/?/, '').toLowerCase()
  if (h === '404' || h === 'notfound') {
    localStorage.setItem('nexus-site-404-on', '0')
    localStorage.removeItem('nexus-site-404-on')
    window.location.hash = ''
  }
} catch { /* ignore */ }

"""
        main.write_text(s.replace('installPollThrottle()\n', 'installPollThrottle()\n' + inject, 1))
        print('main early unlock')
    else:
        print('main skip')

sc = Path('src/context/Site404Context.tsx')
if sc.exists():
    s = sc.read_text()
    if 'BOOT_UNLOCK_404' not in s and 'useState(readSite404Cache)' in s:
        s = s.replace(
            'const [enabled, setEnabledState] = useState(readSite404Cache);',
            """const [enabled, setEnabledState] = useState(() => {
    // BOOT_UNLOCK_404 — do not lock login from stale local cache
    try { writeSite404Cache(false); } catch {}
    return false;
  });""",
            1,
        )
        sc.write_text(s)
        print('Site404 boot force off')
    else:
        print('Site404 skip')

print('unlock patch done')
