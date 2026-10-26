#!/usr/bin/env python3
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
if not cp.exists():
    print("no cp"); raise SystemExit(0)
t = cp.read_text()
if "nexus-announce-tick" in t and "hardReload" in t:
    print("cp reload already"); raise SystemExit(0)

hook = '''
  // Hard-reload this portal tab when Admin publishes/deletes an announcement
  useEffect(() => {
    let lastTick = '';
    try { lastTick = localStorage.getItem('nexus-announce-tick') || ''; } catch { /* ignore */ }

    const hardReload = () => {
      try {
        const url = window.location.href;
        window.location.replace(url);
      } catch {
        try { window.location.reload(); } catch { /* ignore */ }
      }
    };

    const onStorage = (e: StorageEvent) => {
      if (e.key === 'nexus-announce-tick' || e.key === 'nexus-announce' || e.key === 'nexus-announce-channels') {
        hardReload();
      }
    };
    window.addEventListener('storage', onStorage);

    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => hardReload();
    } catch { /* ignore */ }

    const poll = window.setInterval(() => {
      try {
        const t = localStorage.getItem('nexus-announce-tick') || '';
        if (t && t !== lastTick) {
          lastTick = t;
          hardReload();
        }
      } catch { /* ignore */ }
    }, 400);

    return () => {
      window.removeEventListener('storage', onStorage);
      window.clearInterval(poll);
      try { bc?.close(); } catch { /* ignore */ }
    };
  }, []);

'''

needle = "  }, [isCustomerSession, user]);\n"
if needle not in t:
    print("needle miss"); raise SystemExit(1)
t = t.replace(needle, needle + "\n" + hook, 1)
cp.write_text(t)
print("cp hard-reload injected")
