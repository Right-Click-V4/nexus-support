#!/usr/bin/env python3
"""Heartbeat glow around Submit Ticket form card (light/dark)."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-glow-v1" in c:
    print("cp already")
else:
    old = 'className="portal-overview-glass rounded-2xl p-4 sm:p-5 space-y-3.5 relative z-20"'
    new = 'className="portal-overview-glass portal-submit-form-glow rounded-2xl p-4 sm:p-5 space-y-3.5 relative z-20"'
    if old in c:
        c = c.replace(old, new, 1)
        print("form class ok")
    else:
        print("form class miss")
    if "submit-glow-v1" not in c:
        c = c.replace("/* submit-fill-v1 */", "/* submit-fill-v1 */ /* submit-glow-v1 */", 1)
    cp.write_text(c)
    print("cp done")

css_block = """

/* submit-glow-v1 — heartbeat glow on the fill-out form card */
@keyframes portal-submit-heartbeat {
  0%, 100% {
    box-shadow:
      0 0 0 1px var(--submit-glow-ring),
      0 0 12px 2px var(--submit-glow-soft),
      0 0 28px 4px var(--submit-glow-mid),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  14% {
    box-shadow:
      0 0 0 2px var(--submit-glow-ring-strong),
      0 0 18px 4px var(--submit-glow-mid),
      0 0 36px 8px var(--submit-glow-soft),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  28% {
    box-shadow:
      0 0 0 1px var(--submit-glow-ring),
      0 0 12px 2px var(--submit-glow-soft),
      0 0 24px 4px var(--submit-glow-mid),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  42% {
    box-shadow:
      0 0 0 2px var(--submit-glow-ring-strong),
      0 0 22px 6px var(--submit-glow-mid),
      0 0 42px 10px var(--submit-glow-soft),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  56%, 100% {
    box-shadow:
      0 0 0 1px var(--submit-glow-ring),
      0 0 12px 2px var(--submit-glow-soft),
      0 0 28px 4px var(--submit-glow-mid),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
}

.portal-submit-form-glow {
  --submit-glow-ring: rgba(139, 92, 246, 0.45);
  --submit-glow-ring-strong: rgba(167, 139, 250, 0.75);
  --submit-glow-soft: rgba(139, 92, 246, 0.22);
  --submit-glow-mid: rgba(124, 58, 237, 0.28);
  animation: portal-submit-heartbeat 2.4s ease-in-out infinite;
  border-color: rgba(167, 139, 250, 0.4) !important;
}

html.nexus-light .portal-submit-form-glow {
  --submit-glow-ring: rgba(124, 58, 237, 0.4);
  --submit-glow-ring-strong: rgba(109, 40, 217, 0.65);
  --submit-glow-soft: rgba(167, 139, 250, 0.35);
  --submit-glow-mid: rgba(139, 92, 246, 0.32);
  border-color: rgba(139, 92, 246, 0.45) !important;
  background: rgba(255, 255, 255, 0.62) !important;
}

html.nexus-dark .portal-submit-form-glow {
  --submit-glow-ring: rgba(196, 181, 253, 0.4);
  --submit-glow-ring-strong: rgba(221, 214, 254, 0.7);
  --submit-glow-soft: rgba(139, 92, 246, 0.35);
  --submit-glow-mid: rgba(167, 139, 250, 0.4);
  border-color: rgba(196, 181, 253, 0.45) !important;
  background: rgba(30, 24, 55, 0.5) !important;
}

@media (prefers-reduced-motion: reduce) {
  .portal-submit-form-glow {
    animation: none;
    box-shadow:
      0 0 0 1px var(--submit-glow-ring),
      0 0 16px 3px var(--submit-glow-soft),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    t = path.read_text()
    if "submit-glow-v1" in t:
        print(f"{path.name}: already")
        continue
    path.write_text(t + css_block)
    print(f"{path.name}: css ok")

print("done")
