#!/usr/bin/env python3
"""Post-login ceremony runs exactly once (no double progress cycle)."""
from pathlib import Path
import re

gate = Path("src/components/PortalAuthGate.tsx")
if gate.exists() and gate.stat().st_size > 500:
    g = gate.read_text()
    if "POSTLOGIN_ONCE_V1" not in g:
        old = """  // Session resolving: post-login UI after sign-in; BootLoader only on refresh
  if (loading || authBusy) {
    if (justIn) {
      return <PostLoginLoader label=\"Opening customer portal\u2026\" fading={false} variant=\"customer\" />;
    }
    return <BootLoader label=\"Loading portal\u2026\" />;
  }"""
        new = """  // POSTLOGIN_ONCE_V1 \u2014 static boot while resolving; PostLoginShell runs the single ceremony
  if (loading || authBusy) {
    return <BootLoader label={justIn ? 'Opening customer portal\u2026' : 'Loading portal\u2026'} />;
  }"""
        if old in g:
            g = g.replace(old, new)
            print("PortalAuthGate ok")
        else:
            g2 = re.sub(
                r"if \(loading \|\| authBusy\) \{[\s\S]*?return <BootLoader label=\"Loading portal\u2026\" />;[\s\S]*?\}",
                "if (loading || authBusy) {\n    return <BootLoader label={justIn ? 'Opening customer portal\u2026' : 'Loading portal\u2026'} />;\n  }",
                g,
                count=1,
            )
            if g2 != g:
                g = g2
                print("PortalAuthGate regex")
            else:
                print("PortalAuthGate miss")
        gate.write_text(g)

pl = Path("src/components/PostLoginLoader.tsx")
if pl.exists() and pl.stat().st_size > 1000:
    s = pl.read_text()
    if "POSTLOGIN_ONCE_V1" in s and "POSTLOGIN_ONCE_START" in s:
        print("PostLogin already")
    else:
        third = """  useEffect(() => {
    if (!ready || mode === 'ceremony' || mode === 'fading') return;
    if (!hasJustLoggedIn()) return;
    if (wantCeremony.current && mode === 'done') return;
    wantCeremony.current = true;
    started.current = true;
    setMode('ceremony');
    const t = window.setTimeout(() => setMode('fading'), MIN_MS);
    return () => window.clearTimeout(t);
  }, [ready, mode]);
"""
        if third in s:
            s = s.replace(third, "  // POSTLOGIN_ONCE_V1 \u2014 no re-trigger after ceremony completes\n")
            print("removed re-trigger")
        old_init = "const [mode, setMode] = useState<'wait' | 'ceremony' | 'fading' | 'done'>('wait');"
        new_init = """const [mode, setMode] = useState<'wait' | 'ceremony' | 'fading' | 'done'>(() =>
    hasJustLoggedIn() ? 'ceremony' : 'wait',
  ); // POSTLOGIN_ONCE_V1"""
        if old_init in s:
            s = s.replace(old_init, new_init, 1)
            print("init ceremony")
        if "Login path: only Post-Login UI" in s:
            s = s.replace(
                """    if (hasJustLoggedIn() || wantCeremony.current) {
      return <PostLoginLoader label={label} fading={false} variant={variant} />;
    }
    return <BootLoader label={label} />;""",
                """    // POSTLOGIN_ONCE_V1: static boot; ceremony overlay is the only stepped UI
    return <BootLoader label={label} />;""",
            )
            print("wait boot")
        old_start = """    if (!started.current) {
      started.current = true;
      wantCeremony.current = hasJustLoggedIn();
      if (!wantCeremony.current) {
        setMode('done');
        return;
      }
      // sticky flag so BootLoader paths never win mid-ceremony
      try {
        sessionStorage.setItem(POST_LOGIN_KEY, String(Date.now()));
      } catch {
        /* ignore */
      }
      setMode('ceremony');
      const t = window.setTimeout(() => setMode('fading'), MIN_MS);
      return () => window.clearTimeout(t);
    }"""
        new_start = """    if (!started.current) {
      started.current = true;
      wantCeremony.current = hasJustLoggedIn() || mode === 'ceremony';
      if (!wantCeremony.current) {
        setMode('done');
        return;
      }
      // POSTLOGIN_ONCE_START sticky flag
      try {
        sessionStorage.setItem(POST_LOGIN_KEY, String(Date.now()));
      } catch {
        /* ignore */
      }
      if (mode !== 'ceremony') setMode('ceremony');
      const t = window.setTimeout(() => setMode('fading'), MIN_MS);
      return () => window.clearTimeout(t);
    }"""
        if old_start in s:
            s = s.replace(old_start, new_start)
            print("start once-safe")
        pl.write_text(s)
        print("PostLogin", len(s), "braces", s.count("{") - s.count("}"))

print("patch_postlogin_once done")
