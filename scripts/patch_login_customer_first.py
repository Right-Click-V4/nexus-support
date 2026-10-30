#!/usr/bin/env python3
"""Login page defaults to Customer tab/copy when opening the live site."""
from pathlib import Path

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "login-customer-first-v1" in s:
    print("already")
else:
    old = """  if (requiresAuth && (!user || authBusy)) {
    return (
      <LoginPage
        audience="agent"
        onOpenPortal={() => {
          window.location.hash = 'portal';
        }}
      />
    );
  }"""
    new = """  if (requiresAuth && (!user || authBusy)) {
    return (
      <LoginPage
        audience="customer"
        onOpenPortal={() => {
          window.location.hash = 'portal';
        }}
      />
    );
  }"""
    if old in s:
        s = s.replace(old, new, 1)
        print("systemapp main login")
    else:
        print("systemapp miss")
    s = "/* login-customer-first-v1 */\n" + s
    sa.write_text(s)

lp = Path("src/components/LoginPage.tsx")
if lp.exists():
    t = lp.read_text()
    if "login-customer-first-v1" not in t:
        old_init = "const [audienceTab, setAudienceTab] = useState<'agent' | 'customer'>(audience === 'agent' ? 'agent' : 'customer');"
        new_init = "const [audienceTab, setAudienceTab] = useState<'agent' | 'customer'>('customer');"
        if old_init in t:
            t = t.replace(old_init, new_init, 1)
            print("tab always customer first")
        t = "/* login-customer-first-v1 */\n" + t
        lp.write_text(t)
    else:
        print("login already")
print("done")
