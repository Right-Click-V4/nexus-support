#!/usr/bin/env python3
"""Redesign Customer Portal Help Articles tab."""
from pathlib import Path
import re

p = Path("src/components/CustomerPortal.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
if "help-articles-glass-v1" in t and "How these articles help" in t:
    print("help articles already patched")
    raise SystemExit(0)

articles = Path("scripts/help_articles_block.txt").read_text()
help_inner = Path("scripts/help_view_inner.txt").read_text()

if "LifeBuoy" not in t:
    t = t.replace("Copy, Check,", "Copy, Check, LifeBuoy,", 1)
    if "LifeBuoy" not in t:
        t = t.replace("} from 'lucide-react';", ", LifeBuoy } from 'lucide-react';", 1)

art = articles if articles.endswith("\n") else articles + "\n"
t2, n = re.subn(r"const HELP_ARTICLES = \[[\s\S]*?\];\n", art, t, count=1)
print("articles", n)
t = t2 if n else t

pat = re.compile(
    r"[ \t]*\{view === 'help' && \([\s\S]*?\n[ \t]*\)\}\s*\n(?=[ \t]*\{view === 'account')",
    re.M,
)
m = pat.search(t)
if not m:
    print("FAIL: help view not found")
    raise SystemExit(1)
replacement = help_inner
if not replacement.rstrip().endswith(")}"):
    replacement = replacement.rstrip() + "\n            )}\n"
elif not replacement.endswith("\n"):
    replacement += "\n"

t = t[: m.start()] + replacement + t[m.end() :]
print("view replaced")

if "help-articles-glass-v1" not in t:
    t = "/* help-articles-glass-v1 */\n" + t
p.write_text(t)
print("done", "How these articles help" in t, "LifeBuoy" in t)
print("braces", t.count("{") - t.count("}"))
