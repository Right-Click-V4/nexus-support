#!/usr/bin/env python3
"""Community stays below marquee; light-mode glass transparency for galaxy bg."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()

old = """        <main className="relative z-10 flex-1 min-h-0 p-3 lg:p-5 overflow-y-auto">
          {/* Content grows naturally; footer sits below it — page scrolls when needed */}
          <div
            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl'
            }`}
          >
            <div className={view === 'community' ? 'min-h-[calc(100vh-12.5rem)] flex flex-col' : 'pb-1'}>"""

new = """        <main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 ${
            view === 'community' ? 'overflow-hidden flex flex-col' : 'overflow-y-auto'
          }`}
        >
          {/* Community fills space under marquee (no underlap). Other tabs: natural flow + footer after content. */}
          <div
            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl'
            }`}
          >
            <div className={view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1'}>"""

if old in c:
    c = c.replace(old, new, 1)
    print("cp main community layout ok")
elif "overflow-hidden flex flex-col" in c and "view === 'community'" in c:
    print("cp community layout already special")
else:
    t2, n = re.subn(
        r'<main className="relative z-10 flex-1 min-h-0 p-3 lg:p-5 overflow-y-auto">[\s\S]*?<div className=\{view === \'community\' \? \'min-h-\[calc\(100vh-12\.5rem\)\] flex flex-col\' : \'pb-1\'\}>',
        new.strip(),
        c,
        count=1,
    )
    if n:
        c = t2
        print("cp main loose ok")
    else:
        print("cp main miss — try partial")
        c = c.replace(
            '<main className="relative z-10 flex-1 min-h-0 p-3 lg:p-5 overflow-y-auto">',
            """<main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 ${
            view === 'community' ? 'overflow-hidden flex flex-col' : 'overflow-y-auto'
          }`}
        >""",
            1,
        )
        c = c.replace(
            "view === 'community' ? 'max-w-6xl' : 'max-w-5xl'",
            "view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl'",
            1,
        )
        c = c.replace(
            "view === 'community' ? 'min-h-[calc(100vh-12.5rem)] flex flex-col' : 'pb-1'",
            "view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1'",
            1,
        )
        print("cp partial applied")

c = c.replace(
    'className="portal-footer relative z-10 mt-8 mb-4 shrink-0 px-2 py-4 rounded-xl"',
    """className={`portal-footer relative z-10 shrink-0 px-2 py-3.5 rounded-xl ${
              view === 'community' ? 'mt-3 mb-1' : 'mt-8 mb-4'
            }`}""",
    1,
)

if "footer-flow-v2" in c and "community-glass-v1" not in c:
    c = c.replace("/* footer-flow-v2 */", "/* footer-flow-v2 */ /* community-glass-v1 */", 1)

cp.write_text(c)
print("cp written")

pcc = Path("src/components/PortalCommunityChat.tsx")
t = pcc.read_text()
if "community-glass-v1" in t:
    print("pcc already glass")
else:
    t = t.replace(
        "/* community-media-v2 */",
        "/* community-media-v2 */ /* community-glass-v1 */",
        1,
    )
    if "/* community-glass-v1 */" not in t:
        t = t.replace(
            "export default function PortalCommunityChat",
            "/* community-glass-v1 */\nexport default function PortalCommunityChat",
            1,
        )

    t = t.replace(
        'className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/25 dark:bg-[#0c0a14]/55 border-white/20 dark:border-violet-500/20 backdrop-blur-md shadow-sm"',
        'className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/10 dark:bg-[#0c0a14]/45 border-white/25 dark:border-violet-500/25 backdrop-blur-md shadow-sm"',
    )
    t = t.replace(
        'className="w-56 shrink-0 border-r border-white/15 dark:border-white/10 bg-white/20 dark:bg-[#0a0812]/60 flex flex-col hidden sm:flex backdrop-blur-sm"',
        'className="w-56 shrink-0 border-r border-white/20 dark:border-white/10 bg-white/10 dark:bg-[#0a0812]/50 flex flex-col hidden sm:flex backdrop-blur-md"',
    )
    t = t.replace(
        'className="px-3 py-3 border-b border-zinc-200 dark:border-white/10"',
        'className="px-3 py-3 border-b border-white/20 dark:border-white/10"',
        1,
    )
    t = t.replace(
        "activeRow ? 'bg-violet-100/80 text-violet-900' : 'hover:bg-zinc-100 text-zinc-700'",
        "activeRow ? 'bg-violet-500/20 text-violet-900 dark:text-violet-100' : 'hover:bg-white/20 text-zinc-800 dark:text-zinc-200'",
    )
    t = t.replace(
        'className="p-2 border-t border-zinc-200"',
        'className="p-2 border-t border-white/15 dark:border-white/10"',
        1,
    )
    t = t.replace(
        'className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-violet-600 hover:bg-violet-50 rounded-lg"',
        'className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-violet-700 dark:text-violet-300 hover:bg-white/20 dark:hover:bg-white/10 rounded-lg"',
        1,
    )
    t = t.replace(
        'className="flex-1 flex flex-col min-w-0 bg-[#0c0a16]/30"',
        'className="flex-1 flex flex-col min-w-0 bg-violet-950/10 dark:bg-[#0c0a16]/35"',
    )
    t = t.replace(
        'className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/10 bg-[#0c0a16]/55 backdrop-blur"',
        'className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/15 dark:border-white/10 bg-white/15 dark:bg-[#0c0a16]/55 backdrop-blur"',
    )
    t = t.replace(
        'className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-[#0c0a16]/40"',
        'className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-transparent"',
    )
    t = t.replace(
        "border-t border-white/10 bg-[#0c0a16]/55 backdrop-blur",
        "border-t border-white/15 dark:border-white/10 bg-white/15 dark:bg-[#0c0a16]/55 backdrop-blur",
    )
    t = t.replace(
        'className="flex-1 px-3.5 py-2.5 text-sm rounded-xl border border-zinc-200 dark:border-violet-500/20 bg-white/55 dark:bg-[#0e0c18]/90 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30"',
        'className="flex-1 px-3.5 py-2.5 text-sm rounded-xl border border-white/30 dark:border-violet-500/20 bg-white/25 dark:bg-[#0e0c18]/70 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 backdrop-blur-sm"',
    )
    t = t.replace(
        'className="w-72 shrink-0 border-l border-white/10 bg-[#0c0a16]/90 text-zinc-100 flex flex-col overflow-y-auto backdrop-blur-md"',
        'className="w-72 shrink-0 border-l border-white/20 dark:border-white/10 bg-white/15 dark:bg-[#0c0a16]/70 text-zinc-800 dark:text-zinc-100 flex flex-col overflow-y-auto backdrop-blur-md"',
    )
    t = t.replace('border-b border-zinc-800', 'border-b border-white/20 dark:border-zinc-800')
    t = t.replace('text-zinc-100">{active.name}', 'text-zinc-900 dark:text-zinc-100">{active.name}')
    t = t.replace(
        'className="w-14 h-14 rounded-full bg-zinc-800/90 flex items-center justify-center mb-2 ring-1 ring-violet-500/30"',
        'className="w-14 h-14 rounded-full bg-violet-500/15 dark:bg-zinc-800/90 flex items-center justify-center mb-2 ring-1 ring-violet-500/30"',
    )
    t = t.replace(
        'className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-300 hover:bg-white/5"',
        'className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-700 dark:text-zinc-300 hover:bg-white/30 dark:hover:bg-white/5"',
    )
    t = t.replace(
        'className="flex items-center gap-2 text-zinc-400 text-xs mb-1.5"',
        'className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400 text-xs mb-1.5"',
    )
    t = t.replace(
        'className="w-full px-2.5 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-100 placeholder:text-zinc-600 outline-none focus:border-violet-500"',
        'className="w-full px-2.5 py-1.5 text-sm rounded-lg bg-white/40 dark:bg-zinc-900/80 border border-white/30 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500 outline-none focus:border-violet-500"',
    )
    t = t.replace(
        'className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 mb-2"',
        'className="text-[10px] font-semibold uppercase tracking-wider text-zinc-600 dark:text-zinc-500 mb-2"',
    )
    t = t.replace(
        'className="text-xs text-zinc-400 leading-relaxed"',
        'className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed"',
    )

    pcc.write_text(t)
    print("pcc glass ok")

plc = Path("src/portal-lounge.css")
if plc.exists():
    css = plc.read_text()
    if "community-glass-v1" not in css:
        css += """

/* community-glass-v1 — light mode transparent community panels */
html.nexus-light .portal-community-shell {
  background: rgba(255, 255, 255, 0.12) !important;
  border-color: rgba(255, 255, 255, 0.28) !important;
}
html.nexus-dark .portal-community-shell {
  background: rgba(12, 10, 20, 0.45) !important;
}
"""
        plc.write_text(css)
        print("css ok")

print("done")
