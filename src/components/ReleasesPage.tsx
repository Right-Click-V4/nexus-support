import { useEffect, useState } from 'react';
import { Plus, Trash2, GitBranch, Sparkles } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

type GitDraft = {
  generated_at?: string;
  branch?: string;
  head?: string;
  suggested?: { version: string; title: string; notes: string };
  commits?: { subject: string; sha: string; author: string; date: string; body?: string }[];
};

export default function ReleasesPage() {
  const { releases, saveRelease, deleteRelease } = usePlatform();
  const [version, setVersion] = useState('');
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [replacePortal, setReplacePortal] = useState(true);
  const [draft, setDraft] = useState<GitDraft | null>(null);
  const [draftStatus, setDraftStatus] = useState<string | null>(null);
  const [publishingDraft, setPublishingDraft] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const base = (import.meta as any).env?.BASE_URL || '/';
        const url = `${base}git-changelog-draft.json`.replace(/\/{2,}/g, '/').replace(':/', '://');
        const res = await fetch(url, { cache: 'no-store' });
        if (!res.ok) return;
        const data = (await res.json()) as GitDraft;
        if (!cancelled) setDraft(data);
      } catch {
        /* no draft file in local dev without generate script */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

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

  const loadDraftIntoForm = () => {
    if (!draft?.suggested) return;
    setVersion(draft.suggested.version || '');
    setTitle(draft.suggested.title || '');
    setNotes(draft.suggested.notes || '');
    setDraftStatus('Draft loaded into the form — review, then Publish below.');
  };

  const publishDraftNow = async () => {
    if (!draft?.suggested) return;
    setPublishingDraft(true);
    setDraftStatus(null);
    try {
      const { version: v, title: t, notes: n } = draft.suggested;
      if (replacePortal && releases?.length) {
        for (const r of [...releases]) {
          try {
            await deleteRelease(r.id);
          } catch {
            /* ignore */
          }
        }
      }
      await saveRelease({
        version: (v || '').trim() || new Date().toISOString().slice(0, 10),
        title: (t || '').trim() || 'Latest build',
        notes: (n || '').trim() || 'See git history.',
      });
      setDraftStatus('Published to Customer Portal Overview (Patch notes).');
    } catch (err: any) {
      setDraftStatus(err?.message || 'Could not publish draft.');
    } finally {
      setPublishingDraft(false);
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500 dark:text-zinc-400">
        Publish product release notes for agents. Published notes appear under{' '}
        <span className="font-medium text-zinc-700 dark:text-zinc-200">Overview → Patch notes</span> in the Customer
        Portal. Nothing is shown to customers until you publish.
      </p>

      <section className="rounded-xl border border-violet-300/40 dark:border-violet-400/30 bg-violet-500/5 dark:bg-violet-500/10 p-5 space-y-3">
        <div className="flex items-start gap-2">
          <GitBranch size={18} className="text-violet-500 mt-0.5 shrink-0" />
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
              Automatic draft from git
              <Sparkles size={14} className="text-fuchsia-500" />
            </h2>
            <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-0.5">
              Generated on each deploy from recent commits. Review, then publish only when you want customers to see
              it.
            </p>
          </div>
        </div>

        {!draft?.suggested ? (
          <p className="text-sm text-zinc-500">
            No draft file yet. After the next successful deploy, recent commits will appear here.
          </p>
        ) : (
          <>
            <div className="text-[11px] text-zinc-500 dark:text-zinc-400 flex flex-wrap gap-x-3 gap-y-1">
              {draft.branch && <span>branch: {draft.branch}</span>}
              {draft.head && <span>head: {draft.head}</span>}
              {draft.generated_at && (
                <span>generated: {new Date(draft.generated_at).toLocaleString()}</span>
              )}
            </div>
            <div className="rounded-lg border border-zinc-200 dark:border-white/10 bg-white/70 dark:bg-zinc-950/50 px-3 py-2.5 space-y-1">
              <div className="text-xs font-mono text-violet-700 dark:text-violet-300">
                v{draft.suggested.version}
              </div>
              <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{draft.suggested.title}</div>
              <pre className="text-xs text-zinc-600 dark:text-zinc-300 whitespace-pre-wrap font-sans max-h-40 overflow-y-auto">
                {draft.suggested.notes}
              </pre>
            </div>
            {draft.commits && draft.commits.length > 0 && (
              <details className="text-xs text-zinc-500">
                <summary className="cursor-pointer hover:text-zinc-700 dark:hover:text-zinc-300">
                  {draft.commits.length} commits in draft
                </summary>
                <ul className="mt-2 space-y-1 max-h-36 overflow-y-auto">
                  {draft.commits.map((c) => (
                    <li key={c.sha + c.subject} className="truncate">
                      <span className="font-mono text-violet-600 dark:text-violet-300">{c.sha}</span> {c.subject}
                    </li>
                  ))}
                </ul>
              </details>
            )}
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={loadDraftIntoForm}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg border border-zinc-300 dark:border-white/15 text-zinc-800 dark:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-white/5"
              >
                Load into form
              </button>
              <button
                type="button"
                disabled={publishingDraft}
                onClick={() => void publishDraftNow()}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg bg-brand-600 text-white hover:bg-brand-500 disabled:opacity-60"
              >
                <Plus size={16} />
                {publishingDraft ? 'Publishing…' : 'Publish draft to portal'}
              </button>
              <label className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-300 px-1">
                <input
                  type="checkbox"
                  checked={replacePortal}
                  onChange={(e) => setReplacePortal(e.target.checked)}
                  className="rounded border-zinc-300"
                />
                Replace previous Overview notes
              </label>
            </div>
            {draftStatus && (
              <p className="text-sm text-violet-700 dark:text-violet-200">{draftStatus}</p>
            )}
          </>
        )}
      </section>

      <form
        onSubmit={add}
        className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/60 p-5 shadow-sm space-y-3"
      >
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Manual release notes</h2>
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
