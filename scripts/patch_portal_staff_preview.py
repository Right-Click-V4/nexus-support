#!/usr/bin/env python3
"""Allow agent/admin to preview Customer Portal (fix blank #portal page)."""
from pathlib import Path

p = Path("src/components/CustomerPortal.tsx")
c = p.read_text()
if "portal-staff-preview-v1" in c:
    print("already")
    raise SystemExit(0)

old = """  if (!isCustomerSession) {
    return <PortalAuthGate onBackToAgent={onBackToAgent}>{null}</PortalAuthGate>;
  }"""

new = """  /* Staff (agent/admin) may preview the portal; customers use full session.
     Previously non-customers rendered null → blank white page on #portal. */
  if (requiresAuth && !user) {
    return null;
  }"""

if old in c:
    c = c.replace(old, new, 1)
    print("guard fixed")
else:
    print("guard miss")

c = "/* portal-staff-preview-v1 */\n" + c
p.write_text(c)
print("done")
