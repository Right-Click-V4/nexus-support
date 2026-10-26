import { useMemo, useState } from 'react';
import { Megaphone, Plus, Trash2, Sparkles, Radio, LayoutDashboard } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import type { Announcement } from '../types';

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
    if (!title.trim() || !body.trim() || busy) return;
    setBusy(true);
    setStatusMsg(null);
    try {
      await saveAnnouncement({
        title: title.trim(),
        body: body.trim(),
        severity,
        active: true,
        channel,
      });
      setTitle('');
      setBody('');
      setSeverity('info');
      setChannel('both');
      setStatusMsg('Announcement published — visible on the Customer Portal now.');
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
      await saveRelease({
        version: version.trim(),
        title: relTitle.trim(),
        notes: notes.trim(),
      });
      setVersion('');
      setRelTitle('');
      setNotes('');
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
              <div className="font-semibold text-slate-900">{a.title}</div>
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
            <p className="text-sm text-slate-600 mt-1 whitespace-pre-wrap">{a.body}</p>
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
            placeholder="Title"
            className="w-full px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            required
          />
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Message"
            rows={3}
            className="w-full px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            required
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
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="What changed in this release…"
            rows={3}
            required
            className="w-full px-3 py-2 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30"
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
                <p className="text-sm text-slate-600 mt-1.5 whitespace-pre-wrap">{r.notes}</p>
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
