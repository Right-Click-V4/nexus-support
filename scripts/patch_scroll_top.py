#!/usr/bin/env python3
"""Scroll Customer Portal main content to top on every view change."""
from pathlib import Path
import re

p = Path("src/components/CustomerPortal.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
if "portal-scroll-top-v1" in t and "mainRef.current" in t:
    print("already")
    raise SystemExit(0)

# Ensure useRef imported (already is)
if "useRef" not in t.split("from 'react'")[0]:
    t = t.replace("import { useState, useMemo, useEffect", "import { useState, useMemo, useEffect, useRef")

# Add mainRef after view state
needle = "const [view, setView] = useState<PortalView>('home');"
if "mainRef" not in t:
    if needle not in t:
        print("FAIL: view state not found")
        raise SystemExit(1)
    t = t.replace(
        needle,
        needle + "\n  const mainRef = useRef<HTMLElement>(null);\n  useEffect(() => {\n    mainRef.current?.scrollTo({ top: 0, behavior: 'auto' });\n    // Also reset window scroll if any outer container scrolled\n    try { window.scrollTo(0, 0); } catch { /* ignore */ }\n  }, [view]);",
        1,
    )
    print("added mainRef + effect")
else:
    print("mainRef present")

# Attach ref to <main
if 'ref={mainRef}' not in t:
    t2, n = re.subn(
        r"<main\n(\s+)className=\{`",
        r"<main\n\1ref={mainRef}\n\1className={`",
        t,
        count=1,
    )
    if n != 1:
        t2, n = re.subn(
            r"<main(\s+)className=",
            r"<main\1ref={mainRef}\1className=",
            t,
            count=1,
        )
    if n != 1:
        print("FAIL: main not patched", n)
        raise SystemExit(1)
    t = t2
    print("main ref attached")
else:
    print("main ref already")

if "portal-scroll-top-v1" not in t:
    t = "/* portal-scroll-top-v1 */\n" + t
p.write_text(t)
print("done", "mainRef" in t, t.count("{") - t.count("}"))
