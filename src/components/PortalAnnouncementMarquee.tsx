import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Megaphone, Pause, Play } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import type { Announcement } from '../types';

const SPEED = 95;

function severityClass(severity?: Announcement['severity']) {
  if (severity === 'critical') return 'portal-marquee--critical';
  if (severity === 'warning') return 'portal-marquee--warning';
  return 'portal-marquee--info';
}

/** Strip every nexus meta comment (channel + color), HTML-escaped or raw */
function stripMeta(s?: string) {
  return (s || '')
    .replace(/&lt;!--\s*nexus:[^&]*--&gt;/gi, '')
    .replace(/<!--\s*nexus:[^>]*-->/gi, '')
    .replace(/\\n/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function parseColor(s?: string): string | undefined {
  if (!s) return undefined;
  const raw = s.match(/<!--\s*nexus:color=([#\w(),.\s%-]+)\s*-->/i);
  if (raw?.[1]) return raw[1].trim();
  const esc = s.match(/&lt;!--\s*nexus:color=([#\w(),.\s%-]+)\s*--&gt;/i);
  if (esc?.[1]) return esc[1].trim();
  return undefined;
}

function formatItem(a: Announcement) {
  const t = stripMeta(a.title);
  const body = stripMeta(a.body);
  if (t && body && t !== body) return `${t}: ${body}`;
  return body || t;
}

function Segment({
  items,
  segRef,
}: {
  items: { text: string; color?: string }[];
  segRef?: React.RefObject<HTMLDivElement | null>;
}) {
  return (
    <div className="portal-marquee-segment" ref={segRef as React.RefObject<HTMLDivElement>}>
      {items.map((item, i) => (
        <span key={i} className="portal-marquee-item">
          <span
            className="portal-marquee-text"
            style={item.color ? { color: item.color } : undefined}
          >
            {item.text}
          </span>
          <span className="portal-marquee-sep" aria-hidden>
            {'\u00A0\u00A0\u00A0\u00A0•\u00A0\u00A0\u00A0\u00A0'}
          </span>
        </span>
      ))}
    </div>
  );
}

export default function PortalAnnouncementMarquee() {
  const { announcements } = usePlatform();
  const [paused, setPaused] = useState(false);
  const [segWidth, setSegWidth] = useState(0);
  const [copies, setCopies] = useState(2);
  const segmentRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const active = useMemo(
    () =>
      (announcements || []).filter((a) => {
        if (a.active === false) return false;
        const meta = (a.body || '').match(/<!--\s*nexus:channel=(\w+)\s*-->/i);
        const ch = a.channel || meta?.[1] || 'both';
        return ch === 'marquee' || ch === 'both';
      }),
    [announcements],
  );

  const items = useMemo(
    () =>
      active
        .map((a) => {
          const color = parseColor(a.body) || parseColor(a.title);
          return { text: formatItem(a), color };
        })
        .filter((x) => x.text),
    [active],
  );

  useLayoutEffect(() => {
    const measure = () => {
      const seg = segmentRef.current;
      const vp = viewportRef.current;
      if (!seg || !vp || items.length === 0) return;
      const w = Math.ceil(seg.getBoundingClientRect().width);
      setSegWidth(w);
      const vpW = vp.clientWidth || 1;
      const need = Math.max(2, Math.ceil(vpW / Math.max(w, 1)) + 1);
      setCopies(need);
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
  }, [items]);

  if (active.length === 0 || items.length === 0) return null;

  const topSeverity = active.some((a) => a.severity === 'critical')
    ? 'critical'
    : active.some((a) => a.severity === 'warning')
      ? 'warning'
      : 'info';

  const durationSec = segWidth > 0 ? Math.max(6, segWidth / SPEED) : 12;

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
          className={`portal-marquee-track ${paused ? 'is-paused' : ''} ${segWidth > 0 ? 'is-ready' : ''}`}
          style={
            {
              animationDuration: `${durationSec}s`,
              ['--marquee-shift' as string]: `${segWidth}px`,
            } as React.CSSProperties
          }
        >
          <Segment items={items} segRef={segmentRef} />
          {Array.from({ length: Math.max(1, copies - 1) }).map((_, i) => (
            <Segment key={i} items={items} />
          ))}
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
