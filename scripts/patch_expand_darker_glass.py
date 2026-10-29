#!/usr/bin/env python3
"""Darker status glass for expanded ticket detail panel."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "expand-darker-glass-v1" in c:
    print("already")
    raise SystemExit(0)

old = """                                  <div className={`rounded-xl border p-4 sm:p-5 space-y-4 text-left shadow-sm backdrop-blur-md ${
                                    t.status === 'resolved' || t.status === 'closed'
                                      ? 'border-emerald-400/35 bg-white/75 dark:bg-emerald-950/50 dark:border-emerald-400/30'
                                      : t.status === 'pending'
                                        ? 'border-orange-400/35 bg-white/75 dark:bg-orange-950/40 dark:border-orange-400/30'
                                        : t.status === 'on-hold'
                                          ? 'border-yellow-400/35 bg-white/75 dark:bg-yellow-950/35 dark:border-yellow-400/30'
                                          : 'border-violet-400/35 bg-white/75 dark:bg-violet-950/50 dark:border-violet-400/30'
                                  }`}>"""

new = """                                  <div className={`rounded-xl border p-4 sm:p-5 space-y-4 text-left shadow-sm backdrop-blur-md portal-ticket-expand ${
                                    t.status === 'closed'
                                      ? 'portal-ticket-expand--closed border-red-500/40 bg-red-50/80 dark:bg-[#1a0a0c]/90 dark:border-red-400/45'
                                      : t.status === 'resolved'
                                        ? 'portal-ticket-expand--resolved border-emerald-500/40 bg-emerald-50/80 dark:bg-[#0c1f17]/90 dark:border-emerald-400/45'
                                        : t.status === 'pending'
                                          ? 'portal-ticket-expand--pending border-orange-500/40 bg-orange-50/80 dark:bg-[#1a1208]/90 dark:border-orange-400/45'
                                          : t.status === 'on-hold'
                                            ? 'portal-ticket-expand--hold border-yellow-500/40 bg-yellow-50/80 dark:bg-[#1a1808]/90 dark:border-yellow-400/45'
                                            : 'portal-ticket-expand--open border-violet-500/40 bg-violet-50/80 dark:bg-[#12081c]/90 dark:border-violet-400/45'
                                  }`}>"""

if old in c:
    c = c.replace(old, new, 1)
    print("glass replaced")
else:
    m = re.search(
        r"<div className=\{`rounded-xl border p-4 sm:p-5 space-y-4 text-left shadow-sm backdrop-blur-md \$\{[\s\S]*?\}\}>",
        c,
    )
    if m:
        c = c[: m.start()] + new + c[m.end() :]
        print("glass re ok")
    else:
        print("glass miss")

c = c.replace(
    'className="border-b border-zinc-100/80 dark:border-white/5 bg-violet-500/[0.04]"',
    'className="border-b border-zinc-100/80 dark:border-white/5 bg-transparent dark:bg-black/20"',
    1,
)

c = "/* expand-darker-glass-v1 */\n" + c
cp.write_text(c)
print("cp done")

css = Path("src/portal-lounge.css")
s = css.read_text() if css.exists() else ""
if "expand-darker-glass-v1" not in s:
    block = """
/* expand-darker-glass-v1 — ticket expand panel glass by status */
.portal-ticket-expand {
  background: rgba(255, 255, 255, 0.72);
}
html.nexus-dark .portal-ticket-expand {
  background: rgba(12, 8, 22, 0.92);
  color: #f4f4f5;
}
html.nexus-dark .portal-ticket-expand--open {
  background: rgba(18, 8, 32, 0.94);
  box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.35), 0 8px 28px rgba(0, 0, 0, 0.35);
}
html.nexus-dark .portal-ticket-expand--pending {
  background: rgba(28, 16, 6, 0.94);
  box-shadow: inset 0 0 0 1px rgba(251, 146, 60, 0.4), 0 8px 28px rgba(0, 0, 0, 0.35);
}
html.nexus-dark .portal-ticket-expand--hold {
  background: rgba(28, 24, 6, 0.94);
  box-shadow: inset 0 0 0 1px rgba(250, 204, 21, 0.4), 0 8px 28px rgba(0, 0, 0, 0.35);
}
html.nexus-dark .portal-ticket-expand--resolved {
  background: rgba(6, 28, 18, 0.94);
  box-shadow: inset 0 0 0 1px rgba(52, 211, 153, 0.4), 0 8px 28px rgba(0, 0, 0, 0.35);
}
html.nexus-dark .portal-ticket-expand--closed {
  background: rgba(28, 8, 10, 0.94);
  box-shadow: inset 0 0 0 1px rgba(248, 113, 113, 0.4), 0 8px 28px rgba(0, 0, 0, 0.35);
}
html.nexus-dark .portal-ticket-expand .text-zinc-500 {
  color: #a1a1aa;
}
html.nexus-dark .portal-ticket-expand .text-zinc-700,
html.nexus-dark .portal-ticket-expand .text-zinc-800 {
  color: #e4e4e7;
}
"""
    css.write_text(s + "\n" + block)
    print("css ok")
else:
    print("css already")
print("done")
