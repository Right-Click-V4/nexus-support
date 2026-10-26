import { useEffect, useMemo, useRef, useState } from 'react';
import { Megaphone, Pause, Play } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import type { Announcement } from '../types';

/** Pixels per second — higher = faster across the full bar */
const MARQUEE_PX_PER_SEC = 110;

function severityClass(severity?: Announcement['severity']) {
  if (severity === 'critical') return 'portal-marquee--critical';
  if (severity === 'warning') return 'portal-marquee--warning';
  return 'portal-marquee--info';
}

export default function PortalAnnouncementMarquee() {
  const { announcements } = usePlatform();
  const [paused, setPaused] = useState(false);
  const [shiftPx, setShiftPx] = useState(0);
  const segmentRef = useRef<HTMLSpanElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const active = useMemo(
    () =>
      (announcements || []).filter(
        (a) =>
          a.active !== false &&
          (a.channel === 'marquee' || a.channel === 'both' || !a.channel),
      ),
    [announcements],
  );

  const text = useMemo(
    () =>
      active
        .map((a) => {
          const body = (a.body || '').trim();
          return body ? `${a.title}: ${body}` : a.title;
        })
        .join('   ·   '),
    [active],
  );

  // Measure one segment; ensure at least viewport width so travel spans full bar (1 → 2)
  useEffect(() => {
    const measure = () => {
      const seg = segmentRef.current;
      const vp = viewportRef.current;
      if (!seg || !vp) return;
      const segW = Math.ceil(seg.getBoundingClientRect().width);
      const vpW = Math.ceil(vp.getBoundingClientRect().width);
      // One loop distance = one full segment (min viewport so short text still crosses the bar)
      setShiftPx(Math.max(segW, vpW));
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (segmentRef.current) ro.observe(segmentRef.current);
    if (viewportRef.current) ro.observe(viewportRef.current);
    window.addEventListener('resize', measure);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', measure);
    };
  }, [text]);

  if (active.length === 0) return null;

  const topSeverity = active.some((a) => a.severity === 'critical')
    ? 'critical'
    : active.some((a) => a.severity === 'warning')
      ? 'warning'
      : 'info';

  const durationSec = shiftPx > 0 ? Math.max(4, shiftPx / MARQUEE_PX_PER_SEC) : 8;

  // Pad short text so each segment is at least ~viewport wide (smooth full-width travel)
  const pad = '\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0';

  return (
    <div
      className={`portal-marquee shrink-0 relative z-20 ${severityClass(topSeverity)}`}
      role="region"
      aria-label="Announcements"
    >
      <div className="portal-marquee-icon" aria-hidden>
        <Megaphone size={14} />
      </div>
      <div className="portal-marquee-viewport" ref={viewportRef}>
        <div
          className={`portal-marquee-track ${paused ? 'is-paused' : ''}`}
          style={
            {
              animationDuration: `${durationSec}s`,
              ['--marquee-shift' as string]: `${shiftPx}px`,
            } as React.CSSProperties
          }
        >
          <span className="portal-marquee-text" ref={segmentRef}>
            {text}
            {pad}
            <span className="portal-marquee-gap" aria-hidden>
              ·
            </span>
            {pad}
          </span>
          <span className="portal-marquee-text" aria-hidden>
            {text}
            {pad}
            <span className="portal-marquee-gap" aria-hidden>
              ·
            </span>
            {pad}
          </span>
          {/* Third copy so LTR always covers the full strip while looping */}
          <span className="portal-marquee-text" aria-hidden>
            {text}
            {pad}
            <span className="portal-marquee-gap" aria-hidden>
              ·
            </span>
            {pad}
          </span>
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
