#!/usr/bin/env python3
"""Agent topbar: remove search, portal switcher, right-aligned controls, wide-screen layout."""
from pathlib import Path

p = Path("src/SystemApp.tsx")
c = p.read_text()
if "agent-topbar-right-v1" in c:
    print("already")
    raise SystemExit(0)

old_header = """          <header className="nexus-topbar relative z-40 h-14 shrink-0 flex items-center gap-3 px-4 lg:px-6">
            <div className="text-sm font-semibold text-zinc-800">{TITLES[activeNav] || activeNav}</div>
            <div className="flex-1 max-w-xl">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && search.trim()) setActiveNav('tickets');
                  }}
                  placeholder="Search tickets, customers, knowledge…"
                  className="nexus-search w-full pl-9 pr-3 py-2 rounded-lg text-sm outline-none"
                />
              </div>
            </div>
            <div className="flex items-center gap-1 sm:gap-2">
              <a
                href="#portal"
                className="hidden sm:inline-flex items-center gap-1 text-xs text-zinc-500 hover:text-violet-600 px-2 py-1.5 rounded-lg hover:bg-violet-50"
                title="Customer portal"
              >
                <ExternalLink size={14} /> Portal
              </a>
              <ThemeToggle />"""

new_header = """          <header className="nexus-topbar relative z-40 h-14 shrink-0 flex items-center gap-3 px-4 lg:px-6 xl:px-8 w-full">
            <div className="text-sm font-semibold text-zinc-800 dark:text-zinc-100 shrink-0 min-w-0 truncate max-w-[40%]">
              {TITLES[activeNav] || activeNav}
            </div>
            <div className="flex-1 min-w-0" aria-hidden />
            <div className="flex items-center gap-1 sm:gap-2 shrink-0 ml-auto">
              <button
                type="button"
                onClick={() => {
                  window.location.hash = 'portal';
                }}
                className="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-600 dark:text-zinc-300 hover:text-violet-600 dark:hover:text-violet-300 px-2.5 py-1.5 rounded-lg border border-zinc-200/80 dark:border-white/10 bg-white/50 dark:bg-white/5 hover:bg-violet-50 dark:hover:bg-violet-500/10 transition-colors"
                title="Open Customer Portal"
              >
                <ExternalLink size={14} />
                <span className="hidden sm:inline">Customer Portal</span>
              </button>
              <ThemeToggle />"""

if old_header in c:
    c = c.replace(old_header, new_header, 1)
    print("header ok")
else:
    print("header miss")

c = c.replace(
    "{activeNav === 'tickets' && <TicketsPage search={search} />}",
    "{activeNav === 'tickets' && <TicketsPage />}",
    1,
)

if "const [search, setSearch] = useState('');" in c:
    c = c.replace("  const [search, setSearch] = useState('');\n", "", 1)
    print("search state removed")

if 'import { Search, Bell, Settings, ExternalLink }' in c:
    c = c.replace("import { Search, Bell, Settings, ExternalLink }", "import { Bell, Settings, ExternalLink }", 1)
    print("Search import cleaned")
elif "Search, " in c:
    c = c.replace("Search, ", "", 1)
    print("Search import removed")

old_main = '<main className="flex-1 overflow-auto p-4 lg:p-6 relative z-0">'
new_main = '<main className="flex-1 overflow-auto p-4 lg:p-6 xl:px-8 2xl:px-10 relative z-0 w-full max-w-[100vw]">'
if old_main in c:
    c = c.replace(old_main, new_main, 1)
    print("main ok")

c = "/* agent-topbar-right-v1 */\n" + c
p.write_text(c)
print("done")
