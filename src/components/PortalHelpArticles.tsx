import { useMemo, useState } from 'react';
import { BookOpen, Search, ChevronDown, ChevronUp } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

function catClass(category: string) {
  const c = (category || '').toLowerCase();
  if (c.includes('account') || c.includes('auth')) return 'bg-pink-500/15 text-pink-700 dark:text-pink-300';
  if (c.includes('ticket')) return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300';
  if (c.includes('bill')) return 'bg-amber-500/15 text-amber-700 dark:text-amber-300';
  if (c.includes('api') || c.includes('integrat')) return 'bg-sky-500/15 text-sky-700 dark:text-sky-300';
  if (c.includes('support') || c.includes('channel')) return 'bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300';
  return 'bg-violet-500/15 text-violet-700 dark:text-violet-300';
}

export default function PortalHelpArticles() {
  const { articles } = usePlatform();
  const [q, setQ] = useState('');
  const [cat, setCat] = useState('All');
  const [openId, setOpenId] = useState<string | null>(null);

  const published = useMemo(
    () =>
      (articles || []).filter((a) => a.published !== false && (a.title || '').trim()),
    [articles],
  );

  const categories = useMemo(() => {
    const set = new Set<string>();
    published.forEach((a) => set.add(a.category || 'General'));
    return ['All', ...Array.from(set).sort()];
  }, [published]);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    return published.filter((a) => {
      if (cat !== 'All' && (a.category || 'General') !== cat) return false;
      if (!query) return true;
      const hay = `${a.title} ${a.body} ${a.category || ''}`.toLowerCase();
      return hay.includes(query);
    });
  }, [published, q, cat]);

  return (
    <div className="w-full max-w-5xl mx-auto space-y-4 pb-2">
      <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-5">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-700 dark:text-indigo-300/90">
          Knowledge base
        </p>
        <h1 className="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Help Articles
        </h1>
        <p className="mt-1.5 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed max-w-3xl">
          Guides published by support. Read these first to solve common issues yourself or to prepare a clearer ticket.
        </p>
      </section>

      <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/15 text-indigo-600 dark:text-indigo-300 flex items-center justify-center">
            <BookOpen size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">How these articles help</h2>
            <p className="text-[11px] text-zinc-600 dark:text-zinc-400">
              Same Knowledge Base agents use · published articles only
            </p>
          </div>
        </div>
        <div className="grid sm:grid-cols-3 gap-2.5">
          {[
            { t: 'Solve common issues', d: 'Password resets, status meanings, and where to click—without waiting in queue.' },
            { t: 'Write better tickets', d: 'Know what details agents need so your request is routed and resolved sooner.' },
            { t: 'Pick the right channel', d: 'When to use Live Chat, Community, or a formal ticket for account-specific work.' },
          ].map((x) => (
            <div key={x.t} className="rounded-xl border border-white/25 dark:border-white/10 bg-white/25 dark:bg-black/20 px-3 py-2.5">
              <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">{x.t}</div>
              <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-snug mt-0.5">{x.d}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="flex flex-wrap gap-2 items-center">
        <div className="relative flex-1 min-w-[12rem]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search help articles…"
            className="w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-white/25 dark:border-white/10 bg-white/30 dark:bg-black/30 text-zinc-900 dark:text-zinc-100"
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {categories.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCat(c)}
              className={`text-xs font-medium px-2.5 py-1.5 rounded-full border transition ${
                cat === c
                  ? 'bg-violet-600 text-white border-violet-500'
                  : 'border-white/25 dark:border-white/10 text-zinc-700 dark:text-zinc-300 bg-white/20 dark:bg-black/20'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="portal-overview-glass rounded-2xl p-8 text-center text-sm text-zinc-500 dark:text-zinc-400">
          {published.length === 0
            ? 'No published help articles yet. Support will add guides in Knowledge Base.'
            : 'No articles match your search.'}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-3">
          {filtered.map((a) => {
            const open = openId === a.id;
            return (
              <article
                key={a.id}
                className="portal-overview-glass rounded-2xl p-4 sm:p-5 flex flex-col gap-2 border border-white/20 dark:border-white/10 bg-white/30 dark:bg-black/25 backdrop-blur-md"
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 leading-snug">{a.title}</h3>
                  <span className={`shrink-0 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full ${catClass(a.category || 'General')}`}>
                    {a.category || 'General'}
                  </span>
                </div>
                <p className={`text-[13px] text-zinc-700 dark:text-zinc-300 leading-relaxed ${
                  open ? '' : 'line-clamp-3'
                }`}>
                  {a.body}
                </p>
                {(a.body || '').length > 160 && (
                  <button
                    type="button"
                    onClick={() => setOpenId(open ? null : a.id)}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-600 dark:text-indigo-300 self-start"
                  >
                    {open ? (
                      <>
                        Show less <ChevronUp size={14} />
                      </>
                    ) : (
                      <>
                        Read more <ChevronDown size={14} />
                      </>
                    )}
                  </button>
                )}
              </article>
            );
          })}
        </div>
      )}

      <p className="text-[11px] text-center text-zinc-500 dark:text-zinc-400">
        Showing {filtered.length} of {published.length} published article{published.length === 1 ? '' : 's'} from the agent Knowledge Base
      </p>
    </div>
  );
}
