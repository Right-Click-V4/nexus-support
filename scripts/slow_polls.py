#!/usr/bin/env python3
"""CI safety net: strip high-frequency PlatformContext Supabase polls."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "src" / "context" / "PlatformContext.tsx"
if not p.exists():
    raise SystemExit(0)
t = p.read_text(encoding="utf-8")
orig = t
t = t.replace(
    "window.setInterval(() => { void refreshPlatform(); }, 3000)",
    "window.setInterval(() => { void refreshPlatform(); }, 180000)",
)
t = t.replace(
    "window.setInterval(() => { void refreshPlatform(); }, 3000);",
    "window.setInterval(() => { void refreshPlatform(); }, 180000);",
)
t = t.replace(
    """    const poll = window.setInterval(() => {
      void refreshAnnouncementsLight();
    }, 2000);""",
    """    const poll = window.setInterval(() => {
      void refreshAnnouncementsLight();
    }, 90000);""",
)
t = t.replace("const tick = window.setInterval(pull, 500);", "const tick = window.setInterval(pull, 5000);")
if t != orig:
    p.write_text(t, encoding="utf-8")
    print("slow_polls: patched PlatformContext")
else:
    print("slow_polls: already slow or patterns missing")
