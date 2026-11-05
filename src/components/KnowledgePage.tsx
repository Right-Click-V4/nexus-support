import { useState, useMemo } from 'react';
import { Search, BookOpen, ChevronRight, Plus, Pencil, Trash2 } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

export default function KnowledgePage() {
  const { articles, saveArticle, deleteArticle } = usePlatform();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [openId, setOpenId] = useState<string | null>(null);
  const [editing, setEditing] = useState<{
    id?: string;
    title: string;
    category: string;
    body: string;
    published: boolean;
  } | null>(null);

  const categories = ['All', ...Array.from(new Set(articles.map((a) => a.category || 'General')))];

  const filtered = useMemo(() => {
    return articles.filter((a) => {
      if (category !== 'All' && (a.category || 'General') !== category) return false;
      if (search) {
        const q = search.toLowerCase();
        if (!a.title.toLowerCase().includes(q) && !a.body.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [articles, search, category]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    await saveArticle({
      id: editing.id,
      title: editing.title,
      category: editing.category || 'General',
      body: editing.body,
      published: editing.published !== false,
    });
    setEditing(null);
  };

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-brand-100 bg-brand-50/60 dark:bg-violet-500/10 dark:border-violet-400/20 px-4 py-3 text-sm text-brand-900 dark:text-violet-200">
        <strong>Published</strong> articles appear on the <strong>Customer Portal → Help Articles</strong>. Drafts stay agent-only.
      </div>

      <div className="flex flex-wrap gap-3 items-center justify-between">
        <div className="flex flex-wrap gap-3 items-center flex-1">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search knowledge base..."
              className="w-full pl-9 pr-3 py-2 text-sm bg-white dark:bg-zinc-900 border border-slate-200 dark:border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {categories.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setCategory(c)}
                className={`text-xs font-medium px-2.5 py-1.5 rounded-full border ${
                  category === c
                    ? 'bg-violet-600 text-white border-violet-500'
                    : 'border-slate-200 dark:border-white/10 text-slate-600 dark:text-zinc-300'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
        <button
          type="button"
          onClick={() =>
            setEditing({ title: '', category: 'General', body: '', published: true })
          }
          className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg"
        >
          <Plus size={16} /> New article
        </button>
      </div>

      {editing && (
        <form onSubmit={submit} className="bg-white dark:bg-zinc-900 rounded-xl border border-slate-200 dark:border-white/10 p-5 space-y-3 shadow-sm">
          <input
            value={editing.title}
            onChange={(e) => setEditing({ ...editing, title: e.target.value })}
            placeholder="Title"
            required
            className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-white/10 rounded-lg dark:bg-zinc-950"
          />
          <input
            value={editing.category}
            onChange={(e) => setEditing({ ...editing, category: e.target.value })}
            placeholder="Category (e.g. Account, Billing)"
            className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-white/10 rounded-lg dark:bg-zinc-950"
          />
          <textarea
            value={editing.body}
            onChange={(e) => setEditing({ ...editing, body: e.target.value })}
            placeholder="Article body"
            rows={6}
            required
            className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-white/10 rounded-lg dark:bg-zinc-950"
          />
          <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-zinc-300">
            <input
              type="checkbox"
              checked={editing.published !== false}
              onChange={(e) => setEditing({ ...editing, published: e.target.checked })}
            />
            Published on customer portal (Help Articles)
          </label>
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg">
              Save
            </button>
            <button type="button" onClick={() => setEditing(null)} className="px-4 py-2 text-sm text-slate-600 dark:text-zinc-300">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="bg-white dark:bg-zinc-900/90 rounded-xl border border-slate-200 dark:border-white/10 divide-y divide-slate-100 dark:divide-white/5 overflow-hidden">
        {filtered.map((a) => (
          <div key={a.id} className="flex items-center gap-3 px-4 py-3">
            <BookOpen size={18} className="text-violet-500 shrink-0" />
            <button type="button" className="flex-1 text-left min-w-0" onClick={() => setOpenId(openId === a.id ? null : a.id)}>
              <div className="font-medium text-slate-900 dark:text-zinc-100 truncate">{a.title}</div>
              <div className="text-xs text-slate-500 dark:text-zinc-400 flex items-center gap-2">
                <span>{a.category || 'General'}</span>
                <span className={a.published !== false ? 'text-emerald-600' : 'text-amber-600'}>
                  {a.published !== false ? 'Published' : 'Draft'}
                </span>
              </div>
              {openId === a.id && (
                <p className="mt-2 text-sm text-slate-600 dark:text-zinc-300 whitespace-pre-wrap">{a.body}</p>
              )}
            </button>
            <button type="button" onClick={() => setOpenId(openId === a.id ? null : a.id)} className="p-1.5 text-slate-400">
              <ChevronRight size={16} className={openId === a.id ? 'rotate-90' : ''} />
            </button>
            <button
              type="button"
              onClick={() =>
                setEditing({
                  id: a.id,
                  title: a.title,
                  category: a.category || 'General',
                  body: a.body,
                  published: a.published !== false,
                })
              }
              className="p-1.5 text-slate-400 hover:text-violet-600"
            >
              <Pencil size={16} />
            </button>
            <button type="button" onClick={() => a.id && void deleteArticle(a.id)} className="p-1.5 text-slate-400 hover:text-rose-600">
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="p-8 text-center text-sm text-slate-500">No articles yet</div>
        )}
      </div>
    </div>
  );
}
