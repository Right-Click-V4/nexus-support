import { useMemo, useState } from 'react';
import { Megaphone, Pause, Play } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import type { Announcement } from '../types';

function severityClass(severity?: Announcement['severity']) {
  if (severity === 'critical') return 'portal-marquee--critical';
  if (severity === 'warning') return 'portal-marquee--warning';
  return 'portal-marquee--info';
}

export default function PortalAnnouncementMarquee() {
  const { announcements } = usePlatform();
  const [paused, setPaused] = useState(false);

  const active = useMemo(
    () => (announcements || []).filter((a) => a.active !== false),
    [announcements],
  );

  if (active.length === 0) return null;

  const text = active
    .map((a) => {
      const body = (a.body || '').trim();
      return body ? `${a.title}: ${body}` : a.title;
    })
    .join('   ·   ');

  const track = `${text}   ·   ${text}`;
  const topSeverity = active.some((a) => a.severity === 'critical')
    ? 'critical'
    : active.some((a) => a.severity === 'warning')
      ? 'warning'
      : 'info';

  return (
    <div
      className={`portal-marquee shrink-0 relative z-20 ${severityClass(topSeverity)}`}
      role="region"
      aria-label="Announcements"
    >
      <div className="portal-marquee-icon" aria-hidden>
        <Megaphone size={14} />
      </div>
      <div className="portal-marquee-viewport">
        <div
          className={`portal-marquee-track ${paused ? 'is-paused' : ''}`}
          style={{ animationDuration: `${Math.max(18, text.length * 0.18)}s` }}
        >
          <span className="portal-marquee-text">{track}</span>
        </div>
      </div>
      <button
        type="button"
        className="portal-marquee-toggle"
        onClick={() => setPaused((p) => !p)}
        aria-label={paused ? 'Resume announcement scroll' : 'Pause announcement scroll'}
        title={paused ? 'Resume' : 'Pause'}
      >
        {paused ? <Play size={13} /> : <Pause size={13} />}
      </button>
    </div>
  );
}
