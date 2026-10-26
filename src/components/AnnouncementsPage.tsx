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
  { name: 'Violet', value: '#7c3aed' },
  { name: 'Fuchsia', value: '#c026d3' },
  { name: 'White', value: '#f8fafc' },
];

function MessageEditor({
  value,
  onChange,
  color,
  onColorChange,
  placeholder,
  rows = 3,
}: {
  value: string;
  onChange: (v: string) => void;
  color: string;
  onColorChange: (c: string) => void;
  placeholder?: string;
  rows?: number;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [showEmoji, setShowEmoji] = useState(false);

  const insertEmoji = (emoji: string) => {
    const el = ref.current;
    if (!el) {
      onChange(value + emoji);
      return;
    }
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    const next = value.slice(0, start) + emoji + value.slice(end);
    onChange(next);
    requestAnimationFrame(() => {
      el.focus();
      const pos = start + emoji.length;
      el.setSelectionRange(pos, pos);
    });
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-1.5">
        <button
          type="button"
          onClick={() => setShowEmoji((s) => !s)}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-lg border border-zinc-200 bg-white hover:bg-zinc-50 text-zinc-700"
          title="Insert emoji"
        >
          😀 Emoji
        </button>
        <span className="text-[11px] text-slate-400 px-1">Color</span>
        {COLORS.map((c) => (
          <button
            key={c.name}
            type="button"
            title={c.name}
            onClick={() => onColorChange(c.value)}
            className={`h-6 w-6 rounded-full border-2 transition ${
              color === c.value ? 'border-zinc-900 scale-110' : 'border-zinc-200'
            }`}
            style={{ background: c.value || 'linear-gradient(135deg,#e2e8f0,#94a3b8)' }}
          />
        ))}
      </div>
      {showEmoji && (
        <div className="flex flex-wrap gap-1 p-2 rounded-xl border border-zinc-200 bg-zinc-50 max-h-28 overflow-y-auto">
          {EMOJIS.map((e) => (
            <button
              key={e}
              type="button"
              className="h-8 w-8 text-lg leading-none rounded-lg hover:bg-white"
              onClick={() => insertEmoji(e)}
            >
              {e}
            </button>
          ))}
        </div>
      )}
      <textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        required
        className="w-full px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
        style={color ? { color } : undefined}
      />
    </div>
  );
}

type Channel = 'marquee' | 'portal' | 'both';

function channelLabel(c?: string) {
  if (c === 'marquee') return 'Marquee only';
  if (c === 'portal') return 'Portal Overview only';
  return 'Marquee + Portal';
}

function matchesChannel(a: Announcement, want: 'marquee' | 'portal') {
  const c = a.channel || 'both';
  return c === 'both' || c === want;
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
  const [channel, setChannel] = useState<Channel>('both');
  const [msgColor, setMsgColor] = useState('');
  const [notesColor, setNotesColor] = useState('');

  const [version, setVersion] = useState('');
  const [relTitle, setRelTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const marqueeList = useMemo(
    () => (announcements || []).filter((a) => matchesChannel(a, 'marquee')),
    [announcements],
  );
  const portalList = useMemo(
    () => (announcements || []).filter((a) => matchesChannel(a, 'portal')),
    [announcements],
  );

  const submitAnnouncement = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim() || busy) return;
    setBusy(true);
    setStatusMsg(null);
    try {
      let msg = body.trim();
      if (msgColor) msg = `<!--nexus:color=${msgColor}-->\n${msg}`;
      await saveAnnouncement({
        title: title.trim(),
        body: msg,
        severity,
        active: true,
        channel,
      });
      setTitle('');
      setBody('');
      setSeverity('info');
      setChannel('both');
      setMsgColor('');
      setStatusMsg('Published — Customer Portal updates within about a second (no refresh needed).');
    } catch (err) {
      console.error(err);
      setStatusMsg('Could not publish. Check the console or try again.');
    } finally {
      setBusy(false);
    }
  };

  const submitRelease = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!version.trim() || !relTitle.trim() || !notes.trim() || busy) return;
    setBusy(true);
    setStatusMsg(null);
    try {
      let n = notes.trim();
      if (notesColor) n = `<!--nexus:color=${notesColor}-->\n${n}`;
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

  const renderAnnouncementList = (list: Announcement[], empty: string) => (
    <div className="space-y-2.5">
      {list.length === 0 && (
        <p className="text-sm text-slate-500 text-center py-5">{empty}</p>
      )}
      {list.map((a) => (
        <div
          key={a.id || a.title}
          className="bg-white rounded-xl border border-zinc-200 p-4 shadow-sm flex justify-between gap-3"
        >
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <div className="font-semibold text-slate-900">{a.title?.trim() || '(No title)'}</div>
              <span className="text-[10px] uppercase tracking-wide font-semibold px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-600">
                {a.severity || 'info'}
              </span>
              <span className="text-[10px] uppercase tracking-wide font-semibold px-1.5 py-0.5 rounded bg-violet-50 text-violet-700">
                {channelLabel(a.channel)}
              </span>
              <span className="text-[10px] text-slate-400">
                {a.active === false ? 'Off' : 'Active'}
              </span>
            </div>
            <p
              className="text-sm text-slate-600 mt-1 whitespace-pre-wrap"
              style={
                (a.body || '').match(/<!--nexus:color=([^>]+)-->/)
                  ? { color: (a.body || '').match(/<!--nexus:color=([^>]+)-->/)![1] }
                  : undefined
              }
            >
              {(a.body || '')
                .replace(/^<!--nexus:channel=\w+-->\n?/, '')
                .replace(/^<!--nexus:color=[^>]+-->\n?/, '')
                .trim()}
            </p>
            {a.created_at && (
              <div className="text-[11px] text-slate-400 mt-1.5">
                {new Date(a.created_at).toLocaleString()}
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={() => a.id && deleteAnnouncement(a.id)}
            className="text-slate-400 hover:text-rose-600 shrink-0"
            title="Delete"
          >
            <Trash2 size={16} />
          </button>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 max-w-3xl">
      {statusMsg && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-800 text-sm px-4 py-2.5">
          {statusMsg}
        </div>
      )}
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-card p-6">
        <div className="flex items-center gap-2 mb-1">
          <Megaphone className="text-brand-600" size={20} />
          <h2 className="text-lg font-semibold text-zinc-900">Publish announcement</h2>
        </div>
        <p className="text-sm text-slate-500 mb-4">
          Choose where it appears: the sliding text marquee under the portal top bar, the Overview
          Announcements card, or both.
        </p>
        <form onSubmit={submitAnnouncement} className="space-y-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title (optional — leave blank for marquee-only)"
            className="w-full px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
          />
          <MessageEditor
            value={body}
            onChange={setBody}
            color={msgColor}
            onColorChange={setMsgColor}
            placeholder="Message (required) — use emoji & color tools above"
            rows={3}
          />
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as 'info' | 'warning' | 'critical')}
              className="px-3 py-2 text-sm border border-zinc-200 rounded-xl bg-white"
            >
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value as Channel)}
              className="px-3 py-2 text-sm border border-zinc-200 rounded-xl bg-white"
            >
              <option value="both">Marquee + Portal Overview</option>
              <option value="marquee">Marquee only</option>
              <option value="portal">Portal Overview only</option>
            </select>
            <button
              type="submit"
              disabled={busy}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-xl hover:bg-brand-700 disabled:opacity-60"
            >
              <Plus size={16} /> {busy ? 'Publishing…' : 'Publish'}
            </button>
          </div>
        </form>
      </div>

      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <Radio size={16} className="text-violet-600" />
          <h3 className="text-sm font-semibold text-zinc-900">Marquee announcements</h3>
          <span className="text-xs text-slate-400">({marqueeList.length})</span>
        </div>
        <p className="text-xs text-slate-500 -mt-1">
          Shown in the scrolling banner under the Customer Portal top bar.
        </p>
        {renderAnnouncementList(marqueeList, 'No marquee announcements yet.')}
      </section>

      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <LayoutDashboard size={16} className="text-violet-600" />
          <h3 className="text-sm font-semibold text-zinc-900">Portal Overview announcements</h3>
          <span className="text-xs text-slate-400">({portalList.length})</span>
        </div>
        <p className="text-xs text-slate-500 -mt-1">
          Shown in the Announcements card on the Customer Portal Overview tab.
        </p>
        {renderAnnouncementList(portalList, 'No portal announcements yet.')}
      </section>

      <div className="bg-white rounded-2xl border border-zinc-200 shadow-card p-6">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="text-fuchsia-600" size={20} />
          <h2 className="text-lg font-semibold text-zinc-900">Patch notes</h2>
        </div>
        <p className="text-sm text-slate-500 mb-4">
          Publish release notes here — they appear automatically in the Customer Portal Overview
          Patch notes card.
        </p>
        <form onSubmit={submitRelease} className="space-y-3">
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              placeholder="Version e.g. 1.4.0"
              required
              className="px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            />
            <input
              value={relTitle}
              onChange={(e) => setRelTitle(e.target.value)}
              placeholder="Title"
              required
              className="px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            />
          </div>
          <MessageEditor
            value={notes}
            onChange={setNotes}
            color={notesColor}
            onColorChange={setNotesColor}
            placeholder="What changed in this release… — emoji & color supported"
            rows={3}
          />
          <button
            type="submit"
            disabled={busy}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-xl hover:bg-brand-700 disabled:opacity-60"
          >
            <Plus size={16} /> {busy ? 'Publishing…' : 'Publish patch notes'}
          </button>
        </form>
      </div>

      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-fuchsia-600" />
          <h3 className="text-sm font-semibold text-zinc-900">Published patch notes</h3>
          <span className="text-xs text-slate-400">({releases.length})</span>
        </div>
        <div className="space-y-2.5">
          {releases.length === 0 && (
            <p className="text-sm text-slate-500 text-center py-5">No patch notes yet.</p>
          )}
          {releases.map((r) => (
            <div
              key={r.id}
              className="bg-white rounded-xl border border-zinc-200 p-4 shadow-sm flex justify-between gap-3"
            >
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
                    {r.version}
                  </span>
                  <span className="font-semibold text-slate-900">{r.title}</span>
                </div>
                <p
                  className="text-sm text-slate-600 mt-1.5 whitespace-pre-wrap"
                  style={
                    (r.notes || '').match(/<!--nexus:color=([^>]+)-->/)
                      ? { color: (r.notes || '').match(/<!--nexus:color=([^>]+)-->/)![1] }
                      : undefined
                  }
                >
                  {(r.notes || '').replace(/^<!--nexus:color=[^>]+-->\n?/, '').trim()}
                </p>
                <div className="text-[11px] text-slate-400 mt-1.5">
                  {new Date(r.released_at).toLocaleString()}
                </div>
              </div>
              <button
                type="button"
                onClick={() => deleteRelease(r.id)}
                className="text-slate-400 hover:text-rose-600 shrink-0"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
