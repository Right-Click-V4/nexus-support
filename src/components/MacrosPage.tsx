import { useState } from 'react';
import { Plus, Pencil, Trash2, MessageSquareText } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

export default function MacrosPage() {
  const { canned, saveCanned, deleteCanned } = usePlatform();
  const [editing, setEditing] = useState<{ id?: string; title: string; body: string; shortcut: string } | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing?.title.trim() || !editing.body.trim()) return;
    await saveCanned({
      id: editing.id,
      title: editing.title.trim(),
      body: editing.body.trim(),
      shortcut: editing.shortcut.trim() || undefined,
    });
    setEditing(null);
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex flex-col gap-4 w-full max-w-5xl mx-auto">
      <div className="rounded-xl border border-brand-100 bg-brand-50/60 px-4 py-3 text-sm text-brand-900">
        <strong>Macros</strong> are canned replies. Use them on ticket replies and live chat. Optional shortcuts like{' '}
        <code className="bg-white/80 px-1 rounded">/hi</code> appear as quick chips.
      </div>

      <div className="flex justify-between items-center gap-3">
        <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <MessageSquareText size={18} /> Canned responses ({canned.length})
        </h2>
        <button
          type="button"
          onClick={() => setEditing({ title: '', body: '', shortcut: '' })}
          className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700"
        >
          <Plus size={16} /> New macro
        </button>
      </div>

      {editing && (
        <form onSubmit={submit} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3">
          <div className="text-sm font-semibold text-slate-800">{editing.id ? 'Edit macro' : 'New macro'}</div>
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500">Title *</label>
              <input
                value={editing.title}
                onChange={(e) => setEditing({ ...editing, title: e.target.value })}
                required
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg"
                placeholder="Greeting"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Shortcut</label>
              <input
                value={editing.shortcut}
                onChange={(e) => setEditing({ ...editing, shortcut: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg"
                placeholder="/hi"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-500">Body *</label>
            <textarea
              value={editing.body}
              onChange={(e) => setEditing({ ...editing, body: e.target.value })}
              required
              rows={5}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg"
              placeholder="Reply text…"
            />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg">
              Save
            </button>
            <button type="button" onClick={() => setEditing(null)} className="px-4 py-2 text-sm text-slate-600">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex-1 min-h-[420px]">
        {canned.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-16">No macros yet. Create one to speed up replies.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {canned.map((m) => (
              <li key={m.id} className="px-5 py-4 flex items-start justify-between gap-4 hover:bg-white/5">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold text-slate-800">{m.title}</span>
                    {m.shortcut && (
                      <span className="text-[11px] font-mono px-1.5 py-0.5 rounded-md bg-violet-500/15 text-violet-300 border border-violet-400/30">
                        {m.shortcut}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-600 mt-1 whitespace-pre-wrap">{m.body}</p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <button
                    type="button"
                    onClick={() =>
                      setEditing({
                        id: m.id,
                        title: m.title,
                        body: m.body,
                        shortcut: m.shortcut || '',
                      })
                    }
                    className="p-2 text-slate-400 hover:text-violet-500 rounded-lg"
                    title="Edit"
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    type="button"
                    onClick={() => m.id && void deleteCanned(m.id)}
                    className="p-2 text-slate-400 hover:text-rose-500 rounded-lg"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
