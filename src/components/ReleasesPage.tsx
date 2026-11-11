import { useEffect, useMemo, useState } from 'react';
import { Plus, Trash2, GitBranch, Sparkles, CheckCircle2 } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

type GitDraftItem = {
  id?: string;
  version: string;
  title: string;
  notes: string;
  customer_lines?: string[];
  date?: string;
  head?: string;
  commit_count?: number;
};

type GitDraft = {
  generated_at?: string;
  branch?: string;
  head?: string;
  suggested?: { version: string; title: string; notes: string };
  history?: GitDraftItem[];
  commits?: { subject: string; sha: string; author: string; date: string; body?: string }[];
  customer_lines?: string[];
};

function rememberNotesBackup(r: { id?: string; version?: string; title?: string; notes?: string }) {
  const notes = (r.notes || '').trim();
  if (!notes) return;
  try {
    const raw = localStorage.getItem('nexus-release-notes-by-id-v1');
    const map = raw ? (JSON.parse(raw) as Record<string, string>) : {};
    if (r.id) map[r.id] = notes;
    if (r.version) map[`v:${r.version}`] = notes;
    if (r.version && r.title) map[`vt:${r.version}|${r.title}`] = notes;
    localStorage.setItem('nexus-release-notes-by-id-v1', JSON.stringify(map));
  } catch {
    /* ignore */
  }
  try {
    localStorage.setItem(
      'nexus-last-patch-notes',
      JSON.stringify({
        id: r.id,
        version: r.version,
        title: r.title,
        notes,
        at: new Date().toISOString(),
      }),
    );
  } catch {
    /* ignore */
  }
}

function recoverNotes(r: { id?: string; version?: string; title?: string; notes?: string }): string {
  if (r.notes && String(r.notes).trim()) return String(r.notes);
  try {
    const raw = localStorage.getItem('nexus-release-notes-by-id-v1');
    const map = raw ? (JSON.parse(raw) as Record<string, string>) : {};
    if (r.id && map[r.id]) return map[r.id];
    if (r.version && map[`v:${r.version}`]) return map[`v:${r.version}`];
    if (r.version && r.title && map[`vt:${r.version}|${r.title}`]) return map[`vt:${r.version}|${r.title}`];
  } catch {
    /* ignore */
  }
  try {
    const raw = localStorage.getItem('nexus-last-patch-notes');
    if (raw) {
      const last = JSON.parse(raw) as { version?: string; notes?: string };
      if (last?.notes && (!r.version || last.version === r.version)) return last.notes;
    }
  } catch {
    /* ignore */
  }
  return '';
}

function isPublished(item: GitDraftItem, releases: { version?: string; title?: string; notes?: string }[]) {
  const v = (item.version || '').trim();
  const t = (item.title || '').trim().toLowerCase();
  return (releases || []).some((r) => {
    const rv = (r.version || '').trim();
    const rt = (r.title || '').trim().toLowerCase();
    if (v && rv === v) return true;
    if (t && rt === t) return true;
    return false;
  });
}

export default function ReleasesPage() {
  const { releases, saveRelease, deleteRelease } = usePlatform();
  const [version, setVersion] = useState('');
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [replacePortal, setReplacePortal] = useState(false);
  const [draft, setDraft] = useState<GitDraft | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [publishingId, setPublishingId] = useState<string | null>(null);

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
        /* no draft */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const patchList: GitDraftItem[] = useMemo(() => {
    if (draft?.history && draft.history.length > 0) return draft.history;
    if (draft?.suggested) {
      return [
        {
          id: `draft-${draft.suggested.version}`,
          version: draft.suggested.version,
          title: draft.suggested.title,
          notes: draft.suggested.notes,
          customer_lines: draft.customer_lines,
          head: draft.head,
        },
      ];
    }
    return [];
  }, [draft]);

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
    const notesText = notes.trim();
    await saveRelease({ version: version.trim(), title: title.trim(), notes: notesText });
    rememberNotesBackup({ version: version.trim(), title: title.trim(), notes: notesText });
    setVersion('');
    setTitle('');
    setNotes('');
    setStatus('Published to Customer Portal Overview (Patch notes).');
  };

  const publishItem = async (item: GitDraftItem) => {
    const key = item.id || item.version || item.title;
    setPublishingId(key);
    setStatus(null);
    try {
      const notesText =
        (item.notes || '').trim() ||
        (item.customer_lines || []).map((x) => `• ${x}`).join('\n');
      if (!notesText) {
        setStatus('This draft has no detail lines to publish.');
        return;
      }
      const v = (item.version || '').trim() || new Date().toISOString().slice(0, 10);
      const t = (item.title || '').trim() || 'Latest build';
      await saveRelease({ version: v, title: t, notes: notesText });
      if (replacePortal && releases?.length) {
        for (const r of [...releases]) {
          const same = r.version === v && r.title === t;
          if (same) continue;
          try {
            await deleteRelease(r.id);
          } catch {
            /* ignore */
          }
        }
      }
      rememberNotesBackup({ version: v, title: t, notes: notesText });
      setStatus(`Published “${t}” to Customer Portal Overview.`);
    } catch (err: any) {
      setStatus(err?.message || 'Could not publish.');
    } finally {
      setPublishingId(null);
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500 dark:text-zinc-400">
        Publish product release notes for agents. Published notes appear under{' '}
        <span className="font-medium text-zinc-700 dark:text-zinc-200">Overview → Patch notes</span> in the Customer
        Portal. Nothing is shown to customers until you publish. Overview shows up to 6 recent published patches.
      </p>

      <section className="rounded-xl border border-violet-300/40 dark:border-violet-400/30 bg-violet-500/5 dark:bg-violet-500/10 p-5 space-y-4">
        <div className="flex items-start gap-2">
          <GitBranch size={18} className="text-violet-500 mt-0.5 shrink-0" />
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
              Deploy patches from git
              <Sparkles size={14} className="text-fuchsia-500" />
            </h2>
            <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-0.5">
              Updated on each deploy from recent commits (grouped by day). Publish any item you want customers to see.
              Already-published items are tagged.
            </p>
          </div>
        </div>

        {draft && (
          <div className="text-[11px] text-zinc-500 dark:text-zinc-400 flex flex-wrap gap-x-3 gap-y-1">
            {draft.branch && <span>branch: {draft.branch}</span>}
            {draft.head && <span>head: {draft.head}</span>}
            {draft.generated_at && (
              <span>generated: {new Date(draft.generated_at).toLocaleString()}</span>
            )}
            <span>
              {patchList.length} patch{patchList.length === 1 ? '' : 'es'}
            </span>
          </div>
        )}

        <label className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-300">
          <input
            type="checkbox"
            checked={replacePortal}
            onChange={(e) => setReplacePortal(e.target.checked)}
            className="rounded border-zinc-300"
          />
          When publishing, replace previous Overview notes (leave unchecked to keep history, up to 6)
        </label>

        {patchList.length === 0 ? (
          <p className="text-sm text-zinc-500">
            No draft patches yet. After the next successful deploy, recent commit days will appear here.
          </p>
        ) : (
          <ul className="space-y-3">
            {patchList.map((item) => {
              const published = isPublished(item, releases || []);
              const key = item.id || item.version || item.title;
              const busy = publishingId === key;
              return (
                <li
                  key={key}
                  className="rounded-lg border border-zinc-200 dark:border-white/10 bg-white/70 dark:bg-zinc-950/50 px-3.5 py-3 space-y-2"
                >
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-mono font-bold text-violet-700 dark:text-violet-300">
                          v{item.version}
                        </span>
                        {item.date && <span className="text-[11px] text-zinc-500">{item.date}</span>}
                        {item.head && (
                          <span className="text-[11px] text-zinc-500 font-mono">{item.head}</span>
                        )}
                        {published ? (
                          <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-800 dark:text-emerald-200">
                            <CheckCircle2 size={12} /> Published
                          </span>
                        ) : (
                          <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-800 dark:text-amber-200">
                            Draft
                          </span>
                        )}
                      </div>
                      <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 mt-1">{item.title}</div>
                    </div>
                    <button
                      type="button"
                      disabled={busy || published}
                      onClick={() => void publishItem(item)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg bg-brand-600 text-white hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                    >
                      <Plus size={14} />
                      {busy ? 'Publishing…' : published ? 'Published' : 'Publish'}
                    </button>
                  </div>
                  <pre className="text-xs text-zinc-600 dark:text-zinc-300 whitespace-pre-wrap font-sans max-h-36 overflow-y-auto">
                    {item.notes}
                  </pre>
                </li>
              );
            })}
          </ul>
        )}

        {status && <p className="text-sm text-violet-700 dark:text-violet-200">{status}</p>}
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
          placeholder="Release notes (one bullet per line)"
          rows={5}
          className="w-full px-3 py-2 text-sm border border-zinc-200 dark:border-white/10 rounded-lg bg-white dark:bg-zinc-950"
        />
        <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300">
          <input
            type="checkbox"
            checked={replacePortal}
            onChange={(e) => setReplacePortal(e.target.checked)}
            className="rounded border-zinc-300"
          />
          Replace previous notes on Customer Portal Overview
        </label>
        <button
          type="submit"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-brand-600 hover:bg-brand-500 rounded-lg"
        >
          <Plus size={16} /> Publish
        </button>
      </form>

      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Published on portal</h2>
        {(releases || []).length === 0 && (
          <p className="text-sm text-zinc-500">No published patch notes yet.</p>
        )}
        {(releases || []).map((r) => (
          <div
            key={r.id}
            className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/60 p-5 shadow-sm flex justify-between gap-3"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono font-bold text-brand-700 bg-brand-50 dark:bg-brand-500/20 dark:text-brand-200 px-2 py-0.5 rounded">
                  {r.version}
                </span>
                <span className="font-semibold text-zinc-900 dark:text-zinc-50">{r.title}</span>
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-800 dark:text-emerald-200">
                  <CheckCircle2 size={12} /> Published
                </span>
              </div>
              <p className="text-sm text-zinc-600 dark:text-zinc-300 mt-2 whitespace-pre-wrap">
                {recoverNotes(r) || r.notes}
              </p>
              <div className="text-xs text-zinc-400 mt-2">
                {r.released_at ? new Date(r.released_at).toLocaleString() : ''}
              </div>
            </div>
            <button
              type="button"
              onClick={() => deleteRelease(r.id)}
              className="text-zinc-400 hover:text-rose-600 shrink-0"
              title="Unpublish / delete"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
