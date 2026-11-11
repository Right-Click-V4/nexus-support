/* release-notes-bullets-v2 */
import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, GitBranch, Plus, Sparkles, Trash2 } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

type DraftItem = {
  id?: string;
  version?: string;
  title?: string;
  notes?: string;
  customer_lines?: string[];
  date?: string;
  head?: string;
  commit_count?: number;
};

type DraftPayload = {
  generated_at?: string;
  branch?: string;
  head?: string;
  suggested?: DraftItem;
  history?: DraftItem[];
  customer_lines?: string[];
};

function noteLines(notes?: string): string[] {
  if (!notes) return [];
  return notes
    .split(/\n|•/)
    .map((x) => x.replace(/^[\-\*\u2022]\s*/, '').trim())
    .filter(Boolean);
}

function loadNotesBackup(): Record<string, string> {
  try {
    const raw = localStorage.getItem('nexus-release-notes-by-id-v1');
    const obj = raw ? JSON.parse(raw) : {};
    return obj && typeof obj === 'object' ? obj : {};
  } catch {
    return {};
  }
}

function rememberNotesBackup(entry: { version?: string; title?: string; notes?: string }) {
  try {
    const map = loadNotesBackup();
    if (entry.version) map[`v:${entry.version}`] = entry.notes || '';
    if (entry.title) map[`t:${entry.title}`] = entry.notes || '';
    localStorage.setItem('nexus-release-notes-by-id-v1', JSON.stringify(map));
    localStorage.setItem('nexus-last-patch-notes', JSON.stringify(entry));
  } catch {
    /* ignore */
  }
}

function recoverNotes(
  r: { id?: string; version?: string; title?: string; notes?: string },
  draftHints?: DraftItem[],
): string {
  if (r.notes && String(r.notes).trim()) return String(r.notes);
  try {
    const map = loadNotesBackup();
    if (r.version && map[`v:${r.version}`]) return map[`v:${r.version}`];
    if (r.title && map[`t:${r.title}`]) return map[`t:${r.title}`];
  } catch {
    /* ignore */
  }
  try {
    const raw = localStorage.getItem('nexus-last-patch-notes');
    if (raw) {
      const last = JSON.parse(raw) as { version?: string; title?: string; notes?: string };
      if (last?.notes) {
        if (r.version && last.version === r.version) return last.notes;
        if (r.title && last.title && r.title.trim() === last.title.trim()) return last.notes;
      }
    }
  } catch {
    /* ignore */
  }
  if (draftHints?.length) {
    const ver = (r.version || '').trim();
    const title = (r.title || '').trim().toLowerCase();
    for (const h of draftHints) {
      if (!h.notes) continue;
      if (ver && h.version && h.version.trim() === ver) return h.notes;
      if (title && h.title && h.title.trim().toLowerCase() === title) return h.notes;
    }
  }
  return '';
}

function isPublished(item: DraftItem, releases: { version?: string; title?: string }[]) {
  const v = (item.version || '').trim();
  const t = (item.title || '').trim().toLowerCase();
  return releases.some((r) => {
    if (v && r.version && r.version.trim() === v) return true;
    if (t && r.title && r.title.trim().toLowerCase() === t) return true;
    return false;
  });
}

export default function ReleasesPage() {
  const { releases, saveRelease, deleteRelease } = usePlatform();
  const [version, setVersion] = useState('');
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState('');
  const [draft, setDraft] = useState<DraftPayload | null>(null);
  const [replacePortal, setReplacePortal] = useState(false);
  const [publishingId, setPublishingId] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const base = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL || '/';
        const url = `${base}git-changelog-draft.json`.replace(/\/{2,}/g, '/').replace(':/', '://');
        const res = await fetch(url, { cache: 'no-store' });
        if (!res.ok) return;
        const data = (await res.json()) as DraftPayload;
        if (alive) setDraft(data);
      } catch {
        /* optional */
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const patchList: DraftItem[] = useMemo(() => {
    if (!draft) return [];
    const hist = Array.isArray(draft.history) ? draft.history : [];
    if (hist.length) return hist;
    if (draft.suggested) {
      return [
        {
          ...draft.suggested,
          id: draft.suggested.id || `suggested-${draft.head || 'latest'}`,
          customer_lines: draft.customer_lines || draft.suggested.customer_lines,
        },
      ];
    }
    return [];
  }, [draft]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!version.trim() || !title.trim()) {
      setStatus('Version and title are required.');
      return;
    }
    setStatus('');
    try {
      await saveRelease({ version: version.trim(), title: title.trim(), notes: notes.trim() });
      rememberNotesBackup({ version: version.trim(), title: title.trim(), notes: notes.trim() });
      setVersion('');
      setTitle('');
      setNotes('');
      setStatus('Published to Customer Portal Overview.');
    } catch (err: unknown) {
      setStatus(err instanceof Error ? err.message : 'Could not publish.');
    }
  };

  const publishDraft = async (item: DraftItem) => {
    const key = item.id || item.version || item.title || 'draft';
    setPublishingId(key);
    setStatus('');
    try {
      const notesText =
        (item.notes || '').trim() ||
        (item.customer_lines || []).map((x) => `• ${x}`).join('\n');
      if (!notesText.trim()) {
        setStatus('This draft has no lines to publish.');
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
    } catch (err: unknown) {
      setStatus(err instanceof Error ? err.message : 'Could not publish.');
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
              const key = item.id || item.version || item.title || 'x';
              const busy = publishingId === key;
              const lines =
                item.customer_lines && item.customer_lines.length
                  ? item.customer_lines
                  : noteLines(item.notes);
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
                      onClick={() => void publishDraft(item)}
                      className="shrink-0 px-3 py-1.5 text-xs font-medium rounded-lg bg-violet-600 text-white hover:bg-violet-500 disabled:opacity-50"
                    >
                      {published ? 'Published' : busy ? 'Publishing…' : 'Publish'}
                    </button>
                  </div>
                  <ul className="text-xs text-zinc-600 dark:text-zinc-300 space-y-1 max-h-40 overflow-y-auto">
                    {lines.map((line, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-violet-500 shrink-0">•</span>
                        <span>{line}</span>
                      </li>
                    ))}
                  </ul>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <form
        onSubmit={(e) => void onSubmit(e)}
        className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/60 p-5 space-y-3 shadow-sm"
      >
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Manual release notes</h2>
        <div className="flex flex-wrap gap-2">
          <input
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            placeholder="Version e.g. 1.3.0"
            className="px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950 min-w-[10rem]"
          />
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title"
            className="flex-1 min-w-[12rem] px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950"
          />
        </div>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Release notes (one bullet per line)"
          rows={5}
          className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950"
        />
        <label className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-300">
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
        {status ? <p className="text-xs text-zinc-500">{status}</p> : null}
      </form>

      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Published on portal</h2>
        {(releases || []).length === 0 && (
          <p className="text-sm text-zinc-500">No published patch notes yet.</p>
        )}
        {(releases || []).map((r) => {
          const text = recoverNotes(r, patchList) || r.notes || '';
          const lines = noteLines(text);
          return (
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
                {lines.length ? (
                  <ul className="mt-2 space-y-1.5">
                    {lines.map((line, i) => (
                      <li key={i} className="text-sm text-zinc-600 dark:text-zinc-300 flex gap-2">
                        <span className="text-violet-500 shrink-0">•</span>
                        <span>{line}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-2 italic">
                    No detail bullets stored for this release. Re-publish from a git draft to include them.
                  </p>
                )}
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
          );
        })}
      </div>
    </div>
  );
}
