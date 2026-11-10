import { useMemo, useRef, useState } from 'react';
import { Megaphone, Plus, Trash2, Sparkles, Radio, LayoutDashboard } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import type { Announcement } from '../types';

const EMOJIS = ['😀','😁','😂','🥳','😍','😎','👋','👍','👏','🔥','✨','🎉','✅','⚠️','❌','💡','📢','🚀','💜','⭐','🙌','💬','🛠️','📌'];
const COLORS = [
  { name: 'Default', value: '' },
  { name: 'Rose', value: '#e11d48' },
  { name: 'Orange', value: '#ea580c' },
  { name: 'Amber', value: '#d97706' },
  { name: 'Green', value: '#16a34a' },
  { name: 'Teal', value: '#0d9488' },
  { name: 'Blue', value: '#2563eb' },
  { name: 'Indigo', value: '#4f46e5' },
  { name: 'Violet', value: '#7c3aed' },
  { name: 'Fuchsia', value: '#c026d3' },
  { name: 'White', value: '#f8fafc' },
];

function channelOf(a: Announcement) {
  const meta = (a.body || '').match(/^<!--nexus:channel=(\w+)-->/);
  if (meta) return meta[1];
  return a.channel || 'both';
}

function stripMeta(body?: string) {
  return (body || '').replace(/^<!--nexus:[^>]*-->\n?/, '').trim();
}

export default function AnnouncementsPage() {
  const {
    announcements,
    releases,
    saveAnnouncement,
    deleteAnnouncement,
    saveRelease,
    deleteRelease,
  } = usePlatform();

  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [severity, setSeverity] = useState<'info' | 'warning' | 'critical'>('info');
  const [channel, setChannel] = useState<'portal' | 'agent' | 'both' | 'marquee'>('both');
  const [color, setColor] = useState('');
  const [busy, setBusy] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const [version, setVersion] = useState('');
  const [relTitle, setRelTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [notesColor, setNotesColor] = useState('');
  const emojiRef = useRef<HTMLTextAreaElement | null>(null);

  const publishAnnouncement = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || busy) return;
    setBusy(true);
    setStatusMsg(null);
    try {
      let b = body.trim();
      if (channel) b = `<!--nexus:channel=${channel}-->\n${b}`;
      if (color) b = `<!--nexus:color=${color}-->\n${b}`;
      await saveAnnouncement({
        title: title.trim(),
        body: b,
        severity,
        active: true,
        channel,
      } as any);
      setTitle('');
      setBody('');
      setStatusMsg('Announcement published.');
    } catch (err) {
      console.error(err);
      setStatusMsg('Could not publish announcement.');
    } finally {
      setBusy(false);
    }
  };

  const publishPatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!version.trim() || !relTitle.trim() || busy) return;
    setBusy(true);
    setStatusMsg(null);
    try {
      let n = notes.trim();
      if (notesColor) n = `<!--nexus:color=${notesColor}-->\n${n}`;
      if (releases?.length) {
        for (const r of [...releases]) {
          try { await deleteRelease(r.id); } catch { /* ignore */ }
        }
      }
      await saveRelease({
        version: version.trim(),
        title: relTitle.trim(),
        notes: n,
      });
      setVersion('');
      setRelTitle('');
      setNotes('');
      setNotesColor('');
      setStatusMsg('Patch notes published — visible on the Customer Portal Overview.');
    } catch (err) {
      console.error(err);
      setStatusMsg('Could not publish patch notes. Try again.');
    } finally {
      setBusy(false);
    }
  };

  const insertEmoji = (em: string) => {
    setNotes((prev) => prev + em);
    emojiRef.current?.focus();
  };

  const portalList = useMemo(
    () => (announcements || []).filter((a) => {
      const ch = channelOf(a);
      return ch === 'portal' || ch === 'both';
    }),
    [announcements],
  );
  const marqueeList = useMemo(
    () => (announcements || []).filter((a) => channelOf(a) === 'marquee'),
    [announcements],
  );

  return (
    <div className="space-y-6">
      {statusMsg && (
        <div className="text-sm rounded-lg px-3 py-2 bg-violet-500/15 text-violet-200 border border-violet-400/30">
          {statusMsg}
        </div>
      )}

      <section className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/50 p-5 space-y-3">
        <div className="flex items-center gap-2">
          <Megaphone size={18} className="text-violet-500" />
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Announcements</h2>
            <p className="text-xs text-zinc-500">Shown on portal / agent / marquee depending on channel.</p>
          </div>
        </div>
        <form onSubmit={publishAnnouncement} className="space-y-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title"
            required
            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950"
          />
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Message body"
            rows={3}
            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950"
          />
          <div className="flex flex-wrap gap-2 items-center">
            <select value={severity} onChange={(e) => setSeverity(e.target.value as any)} className="px-2 py-1.5 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950">
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
            <select value={channel} onChange={(e) => setChannel(e.target.value as any)} className="px-2 py-1.5 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950">
              <option value="both">Portal + Agent</option>
              <option value="portal">Portal only</option>
              <option value="agent">Agent only</option>
              <option value="marquee">Marquee only</option>
            </select>
            <button type="submit" disabled={busy} className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-brand-600 hover:bg-brand-500 rounded-lg disabled:opacity-60">
              <Plus size={16} /> Publish announcement
            </button>
          </div>
        </form>

        <div className="space-y-2 pt-2">
          {(announcements || []).map((a) => (
            <div key={a.id || a.title} className="flex justify-between gap-3 rounded-lg border border-zinc-200 dark:border-white/10 px-3 py-2">
              <div>
                <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{a.title}</div>
                <div className="text-xs text-zinc-500">{stripMeta(a.body)}</div>
                <div className="text-[10px] text-zinc-400 mt-0.5">channel: {channelOf(a)}</div>
              </div>
              <button type="button" onClick={() => deleteAnnouncement(a.id)} className="text-zinc-400 hover:text-rose-600">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900/50 p-5 space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-fuchsia-500" />
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Patch notes</h2>
            <p className="text-xs text-zinc-500">Publish release notes here — they appear automatically in the Customer Portal Overview Patch notes card.</p>
          </div>
        </div>
        <form onSubmit={publishPatch} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input value={version} onChange={(e) => setVersion(e.target.value)} placeholder="Version e.g. 1.4.0" required className="px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950" />
            <input value={relTitle} onChange={(e) => setRelTitle(e.target.value)} placeholder="Title" required className="px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950" />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex flex-wrap gap-1">
              {EMOJIS.map((em) => (
                <button key={em} type="button" onClick={() => insertEmoji(em)} className="text-base leading-none px-1 py-0.5 rounded hover:bg-zinc-100 dark:hover:bg-white/10">{em}</button>
              ))}
            </div>
            <div className="flex items-center gap-1.5 text-xs text-zinc-500">
              Color
              {COLORS.map((c) => (
                <button
                  key={c.name}
                  type="button"
                  title={c.name}
                  onClick={() => setNotesColor(c.value)}
                  className="w-4 h-4 rounded-full border border-zinc-300 dark:border-white/20"
                  style={{ background: c.value || '#64748b' }}
                />
              ))}
            </div>
          </div>
          <textarea
            ref={emojiRef}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="What changed in this release… — emoji & color supported"
            rows={3}
            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-950"
          />
          <button type="submit" disabled={busy} className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-brand-600 hover:bg-brand-500 rounded-lg disabled:opacity-60">
            <Plus size={16} /> {busy ? 'Publishing…' : 'Publish patch notes'}
          </button>
        </form>

        <div className="pt-2">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500 mb-2">Published patch notes ({(releases || []).length})</h3>
          <div className="space-y-2">
            {(releases || []).map((r) => (
              <div key={r.id} className="flex justify-between gap-3 rounded-lg border border-zinc-200 dark:border-white/10 px-3 py-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-violet-500/15 text-violet-700 dark:text-violet-200">{r.version}</span>
                    <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{r.title}</span>
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-300 mt-0.5">{r.notes}</p>
                  <div className="text-[10px] text-zinc-400 mt-0.5">{r.released_at ? new Date(r.released_at).toLocaleString() : ''}</div>
                </div>
                <button type="button" onClick={() => deleteRelease(r.id)} className="text-zinc-400 hover:text-rose-600">
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
