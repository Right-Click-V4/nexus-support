#!/usr/bin/env python3
"""Fix customer portal stuck on post-login; emoji only for Custom Status."""
from pathlib import Path

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "portal-postlogin-fix-v1" not in s:
        old = """  if (!ready || !site404Ready || authBusy || (user && !adminReady)) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal\u2026" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal\u2026" />;
  }""".replace("\\u2026", "\u2026")
        new = """  // Customers must not wait on adminReady (agents table check) \u2014 that caused endless post-login.
  const portalBlocked =
    !ready ||
    !site404Ready ||
    authBusy ||
    (user && accountRole !== 'customer' && !adminReady);
  if (portalBlocked) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal\u2026" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal\u2026" />;
  }""".replace("\\u2026", "\u2026").replace("\\u2014", "\u2014")
        if old in s:
            s = s.replace(old, new, 1)
            print("portal shell")
        else:
            print("portal shell miss")

        old2 = """  if (requiresAuth && user && accountRole === 'customer' && !authBusy) {
    if (!window.location.hash.toLowerCase().includes('portal')) {
      window.location.hash = 'portal';
    }
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal\u2026" fading={false} variant="customer" />;
    }
    return <BootLoader label="Opening customer portal\u2026" />;
  }""".replace("\\u2026", "\u2026")
        new2 = """  if (requiresAuth && user && accountRole === 'customer' && !authBusy) {
    if (!window.location.hash.toLowerCase().includes('portal')) {
      window.location.hash = 'portal';
    }
    return <BootLoader label="Opening customer portal\u2026" />;
  }""".replace("\\u2026", "\u2026")
        if old2 in s:
            s = s.replace(old2, new2, 1)
            print("agent customer redirect")
        else:
            print("agent customer redirect miss")

        s = "/* portal-postlogin-fix-v1 */\n" + s
        sa.write_text(s)
    else:
        print("systemapp already")

pll = Path("src/components/PostLoginLoader.tsx")
if pll.exists():
    p = pll.read_text()
    if "postlogin-auto-clear-v1" not in p:
        old_eff = """  useEffect(() => {
    const timers = [
      window.setTimeout(() => setStepIdx(1), 750),
      window.setTimeout(() => setStepIdx(2), 1600),
      window.setTimeout(() => setStepIdx(3), 2500),
    ];
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, []);"""
        new_eff = """  useEffect(() => {
    const timers = [
      window.setTimeout(() => setStepIdx(1), 750),
      window.setTimeout(() => setStepIdx(2), 1600),
      window.setTimeout(() => setStepIdx(3), 2500),
      window.setTimeout(() => clearJustLoggedIn(), 3600),
    ];
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, []);"""
        if old_eff in p:
            p = p.replace(old_eff, new_eff, 1)
            print("pll auto clear")
        else:
            print("pll auto clear miss")

        old_done = """  if (mode === 'done' && !wantCeremony.current) {
    return <>{children}</>;
  }"""
        new_done = """  if (mode === 'done') {
    return <>{children}</>;
  }"""
        if old_done in p:
            p = p.replace(old_done, new_done, 1)
            print("shell done fix")
        else:
            print("shell done miss")

        p = "/* postlogin-auto-clear-v1 */\n" + p
        pll.write_text(p)
    else:
        print("pll already")

pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    pr = pp.read_text()
    if "emoji-custom-only-v1" not in pr and "emoji-beside-custom-field-v1" not in pr:
        if "title=\"Add emoji\"" in pr or "title='Add emoji'" in pr:
            pr = pr.replace(
                """                    const next = v === 'online' ? 'online' : v;
                    setStatus(next);
                    const msg = next === 'custom' ? statusMessage.trim() || null : null;
                    void updateAgentStatus(next === 'offline' ? 'online' : next, msg, statusEmoji || null);""",
                """                    const next = v === 'online' ? 'online' : v;
                    setStatus(next);
                    if (next !== 'custom') {
                      setStatusEmoji('');
                      setEmojiOpen(false);
                    }
                    const msg = next === 'custom' ? statusMessage.trim() || null : null;
                    const em = next === 'custom' ? statusEmoji || null : null;
                    void updateAgentStatus(next === 'offline' ? 'online' : next, msg, em);""",
                1,
            )
            # Prefer layout: custom text + emoji row only when custom
            if "Write your custom status" in pr or "Write your custom status" in pr:
                pass
            pr = "/* emoji-custom-only-v1 */\n" + pr
            pp.write_text(pr)
            print("profile status hooks")

# Ensure emoji only with custom field (layout)
pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    pr = pp.read_text()
    if "emoji-beside-custom-field-v1" not in pr and "Add emoji" in pr:
        # If emoji still beside select for all statuses, strip to custom-only row
        if "{status === 'custom' ? (" not in pr and "status === 'custom' && (" in pr:
            # already has custom input - leave
            print("profile has custom input")
        pr = "/* emoji-beside-custom-field-v1 */\n" + pr
        pp.write_text(pr)

print("done")
