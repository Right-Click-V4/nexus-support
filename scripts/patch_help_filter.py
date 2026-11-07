"""Help Articles category filter chips."""
from pathlib import Path

cp = Path('src/components/CustomerPortal.tsx')
if not cp.exists() or cp.stat().st_size < 10000:
    print('CP missing'); raise SystemExit(0)
s = cp.read_text()
if 'HELP_FILTER_V1' in s:
    print('help filter already'); raise SystemExit(0)

if "const [view, setView] = useState<PortalView>('home');" in s:
    s = s.replace(
        "const [view, setView] = useState<PortalView>('home');",
        "const [view, setView] = useState<PortalView>('home');\n  // HELP_FILTER_V1\n  const [helpFilter, setHelpFilter] = useState<string>('All');",
        1,
    )

old_map_start = s.find('{HELP_ARTICLES.map((a) => {')
if old_map_start < 0:
    print('map not found'); raise SystemExit(0)
end = s.find('                  })}', old_map_start)
if end < 0:
    print('map end not found'); raise SystemExit(0)
end = end + len('                  })}')
open_grid = s.rfind('<div className="grid', 0, old_map_start)
close_after = s.find('</div>', end)
replacement = """{/* HELP_FILTER_V1 */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {(['All', ...Array.from(new Set(HELP_ARTICLES.map((x) => x.category)))] as string[]).map((cat) => {
                    const on = helpFilter === cat;
                    return (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => setHelpFilter(cat)}
                        className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition-colors ${
                          on
                            ? 'bg-violet-600 text-white border-violet-500 shadow-sm shadow-violet-900/30'
                            : 'bg-white/10 dark:bg-white/5 text-zinc-800 dark:text-zinc-200 border-zinc-300/60 dark:border-white/15 hover:bg-white/20 dark:hover:bg-white/10'
                        }`}
                      >
                        {cat}
                        <span className={`ml-1.5 tabular-nums ${on ? 'text-violet-100' : 'text-zinc-500 dark:text-zinc-400'}`}>
                          {cat === 'All' ? HELP_ARTICLES.length : HELP_ARTICLES.filter((x) => x.category === cat).length}
                        </span>
                      </button>
                    );
                  })}
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  {HELP_ARTICLES.filter((a) => helpFilter === 'All' || a.category === helpFilter).map((a) => {
                    const catColor =
                      a.category === 'Account' ? 'bg-pink-500/15 text-pink-700 dark:text-pink-300'
                      : a.category === 'Tickets' ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                      : a.category === 'Support channels' ? 'bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300'
                      : a.category === 'Billing' ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300'
                      : a.category === 'Integrations' ? 'bg-sky-500/15 text-sky-700 dark:text-sky-300'
                      : 'bg-violet-500/15 text-violet-700 dark:text-violet-300';
                    return (
                      <article key={a.id} className="portal-overview-glass rounded-2xl p-4 sm:p-5 flex flex-col gap-2.5">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 leading-snug">{a.title}</h3>
                          <span className={`shrink-0 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full ${catColor}`}>{a.category}</span>
                        </div>
                        <p className="text-[13px] text-zinc-700 dark:text-zinc-300 leading-relaxed flex-1">{a.body}</p>
                        {a.tip ? (
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-400 rounded-lg border border-zinc-300/50 dark:border-white/10 bg-white/40 dark:bg-white/5 px-2.5 py-1.5">
                            <span className="font-semibold text-indigo-700 dark:text-indigo-300">Tip: </span>{a.tip}
                          </p>
                        ) : null}
                      </article>
                    );
                  })}
                </div>"""
if open_grid > 0 and close_after > end:
    s = s[:open_grid] + replacement + s[close_after + len('</div>'):]
else:
    s = s[:old_map_start] + replacement + s[end:]
cp.write_text(s)
print('help filter ok')
