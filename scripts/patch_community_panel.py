#!/usr/bin/env python3
"""Community: transparent backgrounds, permanent right info rail, search, members sync."""
from pathlib import Path
import re

p = Path("src/components/PortalCommunityChat.tsx")
if not p.exists():
    raise SystemExit("missing PortalCommunityChat")
t = p.read_text()
if "permanent-info-rail" in t or ("bg-white/25" in t and "{active && (" in t and "setShowInfo((v)" not in t):
    print("community panel already patched")
    raise SystemExit(0)

# Transparent shell
t = re.sub(
    r'className="portal-community-shell[^"]*"',
    'className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/25 dark:bg-[#0c0a14]/55 border-white/20 dark:border-violet-500/20 backdrop-blur-md shadow-sm"',
    t,
    count=1,
)

# Groups rail
t = t.replace(
    "w-56 shrink-0 border-r border-zinc-200 bg-zinc-50 flex flex-col hidden sm:flex",
    "w-56 shrink-0 border-r border-white/15 dark:border-white/10 bg-white/20 dark:bg-[#0a0812]/60 flex flex-col hidden sm:flex backdrop-blur-sm",
)
t = t.replace(
    "w-56 shrink-0 border-r border-zinc-200/80 bg-zinc-50/90",
    "w-56 shrink-0 border-r border-white/15 bg-white/20 dark:bg-[#0a0812]/60 backdrop-blur-sm",
)

# Header
t = t.replace(
    "border-b border-zinc-100 bg-white",
    "border-b border-white/10 bg-white/25 dark:bg-[#161225]/70 backdrop-blur",
)
t = t.replace(
    "border-b border-zinc-200/80 dark:border-white/10 bg-white/80 dark:bg-[#161225]/90",
    "border-b border-white/10 bg-white/25 dark:bg-[#161225]/70 backdrop-blur",
)

# Message area background
t = t.replace("bg-zinc-50/40 dark:bg-[#0a0812]/50", "bg-transparent")
t = t.replace("bg-zinc-50/50", "bg-transparent")
t = t.replace("space-y-3 bg-zinc-50/50", "space-y-3 bg-transparent")

# Composer
t = t.replace(
    "bg-white/90 dark:bg-[#14101f]/95",
    "bg-white/30 dark:bg-[#14101f]/80 backdrop-blur",
)

# Input contrast
t = t.replace(
    "bg-zinc-50 dark:bg-[#0e0c18] text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400",
    "bg-white/55 dark:bg-[#0e0c18]/90 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500",
)

# Bubbles
t = t.replace(
    "'bg-white dark:bg-[#1c1830] border border-zinc-200/80 dark:border-violet-500/15 text-zinc-800 dark:text-zinc-100 rounded-bl-md'",
    "'bg-white/70 dark:bg-[#1c1830]/95 border border-white/30 dark:border-violet-500/15 text-zinc-900 dark:text-zinc-100 rounded-bl-md backdrop-blur-sm'",
)
t = t.replace(
    "bg-white border border-zinc-200 text-zinc-800 rounded-bl-md shadow-sm",
    "bg-white/70 dark:bg-[#1c1830]/95 border border-white/30 text-zinc-900 dark:text-zinc-100 rounded-bl-md",
)

# Remove Info toggle button
patterns = [
    r'\n\s*<button\n\s*type="button"\n\s*onClick=\{\(\) => setShowInfo\(\(v\) => !v\)\}[\s\S]*?<Info size=\{18\} />\n\s*</button>',
    r'\n\s*<button[^>]*setShowInfo\(\(v\) => !v\)[^>]*>[\s\S]*?<Info size=\{18\} />\s*</button>',
    r'\n\s*<button[^>]*setShowInfo[^>]*>\s*<Info size=\{18\} />\s*</button>',
]
for pat in patterns:
    t2, n = re.subn(pat, "", t, count=1)
    if n:
        t = t2
        print("removed Info button")
        break
else:
    print("Info button not found (ok if already gone)")

# Permanent panel
t = t.replace("{showInfo && active && (", "{active && (", 1)
t = t.replace("{showInfo && active &&(", "{active && (", 1)

# Remove close X on info panel
t2, n = re.subn(
    r'\n\s*<button type="button" onClick=\{\(\) => setShowInfo\(false\)\}[^>]*>\s*<X size=\{16\} />\s*</button>',
    "",
    t,
    count=1,
)
if n:
    t = t2
    print("removed close")

# Info panel glass
t = t.replace(
    "w-72 shrink-0 border-l border-zinc-200 bg-zinc-950 text-zinc-100 flex flex-col overflow-y-auto",
    "w-72 shrink-0 border-l border-white/10 bg-[#0c0a16]/90 text-zinc-100 flex flex-col overflow-y-auto backdrop-blur-md",
)

# Search: broader match
old_f = """    return active.messages.filter(
      (m) =>
        m.text.toLowerCase().includes(q) ||
        m.author_name.toLowerCase().includes(q)
    );"""
new_f = """    return active.messages.filter((m) => {
      const hay = [m.text || '', m.author_name || '', m.author_email || '', m.gif_url ? 'gif' : '', m.image_data ? 'photo image' : ''].join(' ').toLowerCase();
      return hay.includes(q);
    });"""
if old_f in t:
    t = t.replace(old_f, new_f, 1)
    print("search improved")
else:
    t2, n = re.subn(
        r"return active\.messages\.filter\(\s*\(m\) =>\s*m\.text\.toLowerCase\(\)\.includes\(q\) \|\|\s*m\.author_name\.toLowerCase\(\)\.includes\(q\)\s*\);",
        "return active.messages.filter((m) => { const hay = [m.text || '', m.author_name || '', m.author_email || ''].join(' ').toLowerCase(); return hay.includes(q); });",
        t,
        count=1,
    )
    if n:
        t = t2
        print("search improved alt")
    else:
        print("search pattern miss")

# Members: ensure saveStore broadcasts
if "nexus-community-store-v1" not in t:
    t = t.replace(
        "localStorage.setItem(LS_KEY, JSON.stringify(trimmed));",
        """localStorage.setItem(LS_KEY, JSON.stringify(trimmed));
    try {
      window.dispatchEvent(new CustomEvent('nexus-community-sync'));
      new BroadcastChannel('nexus-community-store-v1').postMessage({ type: 'store', store: trimmed });
    } catch {}""",
        1,
    )
    print("broadcast save")

if "permanent-info-rail" not in t:
    t = t.replace(
        "{/* Info panel */}",
        "{/* Info panel permanent-info-rail */}",
        1,
    )

p.write_text(t)
print("done", len(t))
print("active permanent", "{active && (" in t)
print("transparent", "bg-white/25" in t)
