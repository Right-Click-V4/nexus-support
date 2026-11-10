import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

export default function ReleasesPage() {
  const { releases, saveRelease, deleteRelease } = usePlatform();
  const [version, setVersion] = useState('');
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [replacePortal, setReplacePortal] = useState(true);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (replacePortal && releases?.length) {
      for (const r of [...releases]) {
        try {
          await deleteRelease(r.id);
        } catch {
          /* ignore */
        }
      }
    }
    await saveRelease({ version: version.trim(), title: title.trim(), notes: notes.trim() });
    setVersion('');
    setTitle('');
    setNotes('');
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500 dark:text-zinc-400">
        Publish product release notes for agents. Published notes appear under{' '}
        <span className="font-medium text-zinc-700 dark:text-zinc-200">Overview → Patch notes</span> in the Customer
        Portal.
      </p>
      <form
        onSubmit={add}
        className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/60 p-5 shadow-sm space-y-3"
      >
        <div className="grid grid-cols-2 gap-3">
          <input
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            placeholder="Version e.g. 1.3.0"
            required
            className="px-3 py-2 text-sm border border-zinc-200 dark:border-white/10 rounded-lg bg-white dark:bg-zinc-950"
          />
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title"
            required
            className="px-3 py-2 text-sm border border-zinc-200 dark:border-white/10 rounded-lg bg-white dark:bg-zinc-950"
          />
        </div>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Release notes"
          rows={3}
          className="w-full px-3 py-2 text-sm border border-zinc-200 dark:border-white/10 rounded-lg bg-white dark:bg-zinc-950"
        />
        <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300">
          <input
            type="checkbox"
            checked={replacePortal}
            onChange={(e) => setReplacePortal(e.target.checked)}
            className="rounded border-zinc-300"
          />
          Replace previous notes on Customer Portal Overview (recommended)
        </label>
        <button
          type="submit"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-brand-600 hover:bg-brand-500 rounded-lg"
        >
          <Plus size={16} /> Publish
        </button>
      </form>
      <div className="space-y-3">
        {(releases || []).map((r) => (
          <div
            key={r.id}
            className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/60 p-5 shadow-sm flex justify-between gap-3"
          >
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-brand-700 bg-brand-50 dark:bg-brand-500/20 dark:text-brand-200 px-2 py-0.5 rounded">
                  {r.version}
                </span>
                <span className="font-semibold text-zinc-900 dark:text-zinc-50">{r.title}</span>
              </div>
              <p className="text-sm text-zinc-600 dark:text-zinc-300 mt-2 whitespace-pre-wrap">{r.notes}</p>
              <div className="text-xs text-zinc-400 mt-2">
                {r.released_at ? new Date(r.released_at).toLocaleString() : ''}
              </div>
            </div>
            <button
              type="button"
              onClick={() => deleteRelease(r.id)}
              className="text-zinc-400 hover:text-rose-600 shrink-0"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
