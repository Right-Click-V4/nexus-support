import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Megaphone, Pause, Play } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import type { Announcement } from '../types';

const SPEED = 95;

/** Wide non-collapsing gaps between distinct announcements */
const SEP =
  '\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0·\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0';

function severityClass(severity?: Announcement['severity']) {
  if (severity === 'critical') return 'portal-marquee--critical';
  if (severity === 'warning') return 'portal-marquee--warning';
  return 'portal-marquee--info';
}

function formatItem(a: Announcement) {
  const t = (a.title || '').trim();
  const body = (a.body || '').replace(/^<!--nexus:channel=\w+-->\n?/, '').trim();
  if (t && body && t !== body) return `${t}: ${body}`;
  return body || t;
}

export default function PortalAnnouncementMarquee() {
  const { announcements } = usePlatform();
  const [paused, setPaused] = useState(false);
  const [segWidth, setSegWidth] = useState(0);
  const [filled, setFilled] = useState('');
  const measureRef = useRef<HTMLSpanElement>(null);
  const segmentRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const active = useMemo(
    () =>
      (announcements || []).filter((a) => {
        if (a.active === false) return false;
        const meta = (a.body || '').match(/^<!--nexus:channel=(\w+)-->/);
        const ch = a.channel || meta?.[1] || 'both';
        return ch === 'marquee' || ch === 'both';
      }),
    [announcements],
  );

  const baseText = useMemo(() => {
    const parts = active.map(formatItem).filter(Boolean);
    return parts.join(SEP);
  }, [active]);

  useLayoutEffect(() => {
    const vp = viewportRef.current;
    const probe = measureRef.current;
    if (!vp || !probe || !baseText) {
      setFilled(baseText);
      return;
    }
    const vpW = vp.clientWidth || 1;
    let built = baseText;
    probe.textContent = built;
    let guard = 0;
    while (probe.getBoundingClientRect().width < vpW && guard < 40) {
      built += SEP + baseText;
      probe.textContent = built;
      guard += 1;
    }
    built += SEP + baseText;
    setFilled(built);
  }, [baseText]);

  useEffect(() => {
    const measure = () => {
      const seg = segmentRef.current;
      if (!seg) return;
      setSegWidth(Math.ceil(seg.getBoundingClientRect().width));
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
  }, [filled]);

  if (active.length === 0) return null;

  const topSeverity = active.some((a) => a.severity === 'critical')
    ? 'critical'
    : active.some((a) => a.severity === 'warning')
      ? 'warning'
      : 'info';

  const durationSec = segWidth > 0 ? Math.max(5, segWidth / SPEED) : 10;

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
        <span ref={measureRef} className="portal-marquee-text portal-marquee-probe" aria-hidden />
        <div
          className={`portal-marquee-track ${paused ? 'is-paused' : ''} ${segWidth > 0 ? 'is-ready' : ''}`}
          style={
            {
              animationDuration: `${durationSec}s`,
              ['--marquee-shift' as string]: `${segWidth}px`,
            } as React.CSSProperties
          }
        >
          <div className="portal-marquee-segment" ref={segmentRef}>
            <span className="portal-marquee-text">{filled || baseText}</span>
          </div>
          <div className="portal-marquee-segment" aria-hidden>
            <span className="portal-marquee-text">{filled || baseText}</span>
          </div>
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
