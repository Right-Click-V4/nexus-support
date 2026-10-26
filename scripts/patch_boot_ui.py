#!/usr/bin/env python3
"""Wire hasJustLoggedIn into SystemApp + AuthGate (after PostLoginLoader is enhanced)."""
from pathlib import Path

sa = Path("src/SystemApp.tsx")
if sa.exists():
    t = sa.read_text()
    t = t.replace(
        "import { PostLoginShell, BootLoader } from './components/PostLoginLoader';",
        "import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn } from './components/PostLoginLoader';",
    )
    t = t.replace(
        "import { PostLoginShell, BootLoader, hasJustLoggedIn } from './components/PostLoginLoader';",
        "import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn } from './components/PostLoginLoader';",
    )
    old = """  if (!ready || !site404Ready || authBusy || (user && !adminReady)) {
    return <BootLoader label="Loading portal…" />;
  }"""
    new = """  if (!ready || !site404Ready || authBusy || (user && !adminReady)) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal…" />;
  }"""
    if old in t:
        t = t.replace(old, new, 1)
        print("PortalShell patched")
    old_c = """  if (requiresAuth && user && accountRole === 'customer' && !authBusy) {
    if (!window.location.hash.toLowerCase().includes('portal')) {
      window.location.hash = 'portal';
    }
    return <BootLoader label="Opening customer portal…" />;
  }"""
    new_c = """  if (requiresAuth && user && accountRole === 'customer' && !authBusy) {
    if (!window.location.hash.toLowerCase().includes('portal')) {
      window.location.hash = 'portal';
    }
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Opening customer portal…" />;
  }"""
    if old_c in t:
        t = t.replace(old_c, new_c, 1)
        print("customer redirect patched")
    sa.write_text(t)
    print("SystemApp written", len(t))

pag = Path("src/components/PortalAuthGate.tsx")
if pag.exists():
    t = pag.read_text()
    t = t.replace(
        "import { PostLoginShell, BootLoader } from './PostLoginLoader';",
        "import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn } from './PostLoginLoader';",
    )
    old = """  if (requiresAuth && loading && !authBusy) {
    return <BootLoader label="Loading portal…" />;
  }"""
    new = """  if (requiresAuth && loading && !authBusy) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal…" />;
  }"""
    if old in t:
        t = t.replace(old, new, 1)
        print("AuthGate patched")
    pag.write_text(t)

print("done")
