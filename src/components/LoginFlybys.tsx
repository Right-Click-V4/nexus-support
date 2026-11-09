import { useEffect, useRef, useState } from 'react';
import { publishSkyCraft } from '../lib/skyTraffic';
import { SatelliteCraft } from './SatelliteCraft';

type FlybyKind = 'ufo' | 'rocket' | 'satellite';

type Flyby = {
  id: number;
  kind: FlybyKind;
  variant: number;
  top: number;
  duration: number;
  dir: 'ltr' | 'rtl';
  chat?: string;
};

const CHATS = [
  'WOAH COOL',
  'Need backup?',
  'Branch online',
  'Tickets clear!',
  'Zoom zoom',
  'Nice UI!',
  'Hold my coffee',
  'Deployed!',
];

function Flame({ eid, tone }: { eid: string; tone: 'fire' | 'violet' | 'cyan' | 'gold' }) {
  const stops =
    tone === 'violet'
      ? ['#6d28d9', '#c026d3', '#f9a8d4', '#fff']
      : tone === 'cyan'
        ? ['#0369a1', '#a78bfa', '#a5f3fc', '#fff']
        : tone === 'gold'
          ? ['#b45309', '#f59e0b', '#e9d5ff', '#fff']
          : ['#4c1d95', '#a78bfa', '#fbbf24', '#fff7ed'];
  return (
    <g>
      <defs>
        <linearGradient id={eid} x1="34" y1="18" x2="2" y2="18" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor={stops[0]} />
          <stop offset="35%" stopColor={stops[1]} />
          <stop offset="72%" stopColor={stops[2]} />
          <stop offset="100%" stopColor={stops[3]} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path className="login-ship-flame-core" d="M34 10 C22 2 8 6 1 18 C8 30 22 34 34 26 Z" fill={`url(#${eid})`} />
      <path className="login-ship-flame-mid" d="M34 13 C24 8 14 11 8 18 C14 25 24 28 34 23 Z" fill={stops[2]} opacity="0.9" />
      <path className="login-ship-flame-hot" d="M34 15.2 C27 13 20 14.5 16 18 C20 21.5 27 23 34 20.8 Z" fill="#fff" />
    </g>
  );
}

function RocketClassic({ eid }: { eid: string }) {
  return (
    <svg className="login-ship-svg" width="86" height="40" viewBox="0 0 96 40" fill="none" aria-hidden>
      <Flame eid={eid} tone="fire" />
      <path d="M36 12 L42 20 L36 28 Z" fill="#6d28d9" />
      <path d="M38 15 L41 20 L38 25 Z" fill="#ddd6fe" />
      <path d="M42 11.5 C58 10 72 10 74 20 C72 30 58 30 42 28.5 Z" fill="#f8fafc" stroke="#e9d5ff" strokeWidth="0.6" />
      <path d="M46 13.2 C58 12.2 68 12.4 70 18" stroke="#fff" strokeWidth="1.4" strokeLinecap="round" opacity="0.7" />
      <path d="M74 11.5 C90 14 94 20 90 20 C94 20 90 26 74 28.5 Z" fill="#7c3aed" />
      <path d="M78 15 C86 17 88 20 86 20 C88 20 86 23 78 25 Z" fill="#e9d5ff" opacity="0.85" />
      <circle cx="58" cy="20" r="4.2" fill="#0ea5e9" stroke="#0369a1" strokeWidth="1.1" />
      <circle cx="58" cy="20" r="2.4" fill="#7dd3fc" />
      <ellipse cx="56.6" cy="18.6" rx="1.1" ry="0.8" fill="#fff" opacity="0.95" />
      <path d="M46 11.5 L52 4.5 L58 12 Z" fill="#a78bfa" />
      <path d="M46 28.5 L52 35.5 L58 28 Z" fill="#a78bfa" />
      <path d="M48 11.8 L52 7 L55 12" stroke="#ddd6fe" strokeWidth="0.8" fill="none" />
    </svg>
  );
}

function RocketViolet({ eid }: { eid: string }) {
  return (
    <svg className="login-ship-svg" width="82" height="40" viewBox="0 0 96 40" fill="none" aria-hidden>
      <Flame eid={eid} tone="violet" />
      <path d="M36 13 L43 20 L36 27 Z" fill="#7e22ce" />
      <path d="M42 12 C60 9 74 11 78 20 C74 29 60 31 42 28 Z" fill="#c4b5fd" />
      <path d="M46 14.5 C58 12.8 68 14 70 18.5" stroke="#ede9fe" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M76 13 C92 16 96 20 92 20 C96 20 92 24 76 27 Z" fill="#7c3aed" />
      <circle cx="60" cy="20" r="4" fill="#a78bfa" stroke="#0891b2" strokeWidth="1" />
      <ellipse cx="58.6" cy="18.7" rx="1.2" ry="0.8" fill="#fff" />
      <path d="M48 12 L54 5 L60 13 Z" fill="#c026d3" />
      <path d="M48 28 L54 35 L60 27 Z" fill="#c026d3" />
    </svg>
  );
}

function RocketOrange({ eid }: { eid: string }) {
  return (
    <svg className="login-ship-svg" width="80" height="42" viewBox="0 0 96 42" fill="none" aria-hidden>
      <g transform="translate(0 1)">
        <Flame eid={eid} tone="gold" />
        <ellipse cx="40" cy="12" rx="5" ry="3.2" fill="#6d28d9" />
        <ellipse cx="40" cy="28" rx="5" ry="3.2" fill="#6d28d9" />
        <path d="M36 13 L30 20 L36 27 Z" fill="#4c1d95" />
        <path d="M42 12 C58 9.5 72 11 76 20 C72 29 58 30.5 42 28 Z" fill="#c4b5fd" />
        <path d="M48 14.2 C60 12.6 68 13.5 70 17.8" stroke="#ede9fe" strokeWidth="1.6" strokeLinecap="round" />
        <path d="M74 13.5 C90 16.5 94 20 90 20 C94 20 90 23.5 74 26.5 Z" fill="#6d28d9" />
        <circle cx="60" cy="20" r="4.1" fill="#38bdf8" stroke="#0369a1" strokeWidth="1" />
        <ellipse cx="58.5" cy="18.6" rx="1.2" ry="0.85" fill="#fff" />
      </g>
    </svg>
  );
}

function RocketTeal({ eid }: { eid: string }) {
  return (
    <svg className="login-ship-svg" width="86" height="36" viewBox="0 0 96 36" fill="none" aria-hidden>
      <g transform="translate(0 -2)">
        <Flame eid={eid} tone="cyan" />
        <path d="M36 14 L42 18 L36 22 Z" fill="#0e7490" />
        <path d="M42 12 C62 9 76 11 80 18 C76 25 62 27 42 24 Z" fill="#a5f3fc" stroke="#67e8f9" strokeWidth="0.5" />
        <path d="M78 13 C92 15 96 18 92 18 C96 18 92 21 78 23 Z" fill="#0891b2" />
        <circle cx="60" cy="18" r="3.6" fill="#22d3ee" stroke="#0e7490" strokeWidth="1" />
        <ellipse cx="58.8" cy="16.8" rx="1" ry="0.7" fill="#fff" />
      </g>
    </svg>
  );
}

function RocketBullet({ eid }: { eid: string }) {
  return (
    <svg className="login-ship-svg" width="78" height="34" viewBox="0 0 96 34" fill="none" aria-hidden>
      <g transform="translate(0 -2)">
        <Flame eid={eid} tone="fire" />
        <path d="M38 12 C58 9 74 11 78 17 C74 23 58 25 38 22 Z" fill="#e9d5ff" />
        <path d="M76 12.5 C90 15 94 17 90 17 C94 17 90 19 76 21.5 Z" fill="#7c3aed" />
        <circle cx="58" cy="17" r="3.4" fill="#38bdf8" stroke="#0369a1" strokeWidth="0.9" />
      </g>
    </svg>
  );
}

function UfoClassic({ uid }: { uid: string }) {
  return (
    <svg className="login-ship-svg login-flyby-ufo" width="86" height="64" viewBox="0 0 90 72" fill="none" aria-hidden>
      <ellipse className="login-ufo-glow" cx="45" cy="42" rx="30" ry="10" fill="#67e8f9" opacity="0.25" />
      <path className="login-ufo-beam" d="M32 40 L28 68 L34 68 Z" fill="#22d3ee" opacity="0.4" />
      <path className="login-ufo-beam login-ufo-beam-mid" d="M45 40 L42 70 L48 70 Z" fill="#a5f3fc" opacity="0.45" />
      <path className="login-ufo-beam" d="M58 40 L56 68 L62 68 Z" fill="#22d3ee" opacity="0.4" />
      <ellipse cx="45" cy="36" rx="32" ry="10" fill="#0e7490" opacity="0.5" />
      <ellipse cx="45" cy="34" rx="30" ry="9" fill="#67e8f9" stroke="#a5f3fc" strokeWidth="1.2" />
      <ellipse cx="45" cy="28" rx="16" ry="12" fill="#67e8f9" opacity="0.95" />
      <ellipse cx="45" cy="26" rx="12" ry="9" fill="#a5f3fc" opacity="0.9" />
      <g className="login-ufo-eye">
        <circle cx="45" cy="26" r="6.5" fill="#0369a1" />
        <circle className="login-ufo-pupil" cx="45" cy="26" r="3.5" fill="#0c4a6e" />
        <ellipse className="login-ufo-shine" cx="43" cy="24" rx="1.8" ry="1.2" fill="#fff" opacity="0.95" />
      </g>
      <circle className="login-ufo-light" cx="24" cy="34" r="1.5" fill="#e0f2fe" />
      <circle className="login-ufo-light login-ufo-light-delay" cx="45" cy="37" r="1.5" fill="#fff" />
      <circle className="login-ufo-light" cx="66" cy="34" r="1.5" fill="#e0f2fe" />
    </svg>
  );
}

function UfoIon({ uid }: { uid: string }) {
  return (
    <svg className="login-ship-svg login-flyby-ufo" width="84" height="60" viewBox="0 0 90 68" fill="none" aria-hidden>
      <ellipse className="login-ufo-glow" cx="45" cy="40" rx="28" ry="9" fill="#38bdf8" opacity="0.3" />
      <path className="login-ufo-beam" d="M34 38 L30 64 L36 64 Z" fill="#22d3ee" opacity="0.4" />
      <path className="login-ufo-beam login-ufo-beam-mid" d="M45 38 L43 66 L47 66 Z" fill="#67e8f9" opacity="0.5" />
      <path className="login-ufo-beam" d="M56 38 L54 64 L60 64 Z" fill="#22d3ee" opacity="0.4" />
      <ellipse cx="45" cy="34" rx="30" ry="9" fill="#0e7490" />
      <ellipse cx="45" cy="32" rx="28" ry="8" fill="#38bdf8" stroke="#7dd3fc" strokeWidth="1.1" />
      <ellipse cx="45" cy="26" rx="14" ry="10" fill="#7dd3fc" opacity="0.95" />
      <ellipse cx="45" cy="24" rx="10" ry="7" fill="#a5f3fc" />
      <g className="login-ufo-eye">
        <circle cx="45" cy="24" r="5.5" fill="#075985" />
        <circle className="login-ufo-pupil" cx="45" cy="24" r="3" fill="#0c4a6e" />
        <ellipse className="login-ufo-shine" cx="43.5" cy="22.5" rx="1.5" ry="1" fill="#fff" opacity="0.95" />
      </g>
      <circle className="login-ufo-light" cx="26" cy="32" r="1.4" fill="#e0f2fe" />
      <circle className="login-ufo-light login-ufo-light-delay" cx="45" cy="35" r="1.4" fill="#fff" />
      <circle className="login-ufo-light" cx="64" cy="32" r="1.4" fill="#e0f2fe" />
    </svg>
  );
}

const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];

export function SpaceFlybys() {
  const [flybys, setFlybys] = useState<Flyby[]>([]);
  const idRef = useRef(0);
  const layerRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const schedule = () => {
      if (cancelled) return;
      const id = ++idRef.current;
      const roll = Math.random();
      const kind: FlybyKind =
        roll < 0.22 ? 'satellite' : roll < 0.48 ? 'ufo' : 'rocket';
      const variant =
        kind === 'ufo'
          ? Math.random() < 0.55
            ? 0
            : 1
          : kind === 'satellite'
            ? 0
            : Math.floor(Math.random() * ROCKETS.length);
      const top = 5 + Math.random() * 42;
      const duration =
        kind === 'satellite' ? 26 + Math.random() * 8 : 16 + Math.random() * 10;
      const dir: 'ltr' | 'rtl' = Math.random() < 0.5 ? 'ltr' : 'rtl';
      const chat =
        kind !== 'satellite' && Math.random() < 0.28
          ? CHATS[Math.floor(Math.random() * CHATS.length)]
          : undefined;
      setFlybys((prev) => [...prev.slice(-2), { id, kind, variant, top, duration, dir, chat }]);
      const gaps = [16, 22, 28, 34, 42];
      timer = setTimeout(schedule, gaps[Math.floor(Math.random() * gaps.length)] * 1000);
    };

    timer = setTimeout(schedule, 2200 + Math.random() * 1800);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  useEffect(() => {
    let raf = 0;
    const tick = () => {
      raf = requestAnimationFrame(tick);
      const layer = layerRef.current;
      if (!layer) return;
      const lr = layer.getBoundingClientRect();
      let bestScore = -1;
      let bestCraft: Parameters<typeof publishSkyCraft>[0] = null;
      nodeRefs.current.forEach((el, id) => {
        const r = el.getBoundingClientRect();
        if (r.width < 2) return;
        const cx = r.left + r.width / 2 - lr.left;
        const cy = r.top + r.height / 2 - lr.top;
        if (cx < -80 || cx > lr.width + 80) return;
        const mid = lr.width * 0.5;
        const score = 1 / (1 + Math.abs(cx - mid) * 0.008);
        const f = flybys.find((x) => x.id === id);
        if (!f) return;
        if (score > bestScore) {
          bestScore = score;
          bestCraft = { id, x: cx, y: cy, dir: f.dir, kind: f.kind, label: f.chat };
        }
      });
      publishSkyCraft(bestCraft);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      publishSkyCraft(null);
    };
  }, [flybys]);

  const onAnimEnd = (id: number) => {
    setFlybys((prev) => prev.filter((f) => f.id !== id));
    nodeRefs.current.delete(id);
  };

  return (
    <div ref={layerRef} className="login-flybys absolute inset-0 pointer-events-none z-[4] overflow-hidden" aria-hidden>
      {flybys.map((f) => {
        const Rocket = ROCKETS[f.variant] ?? RocketClassic;
        return (
          <div
            key={f.id}
            ref={(el) => {
              if (el) nodeRefs.current.set(f.id, el);
              else nodeRefs.current.delete(f.id);
            }}
            className={`login-flyby login-flyby-${f.dir}`}
            style={{ top: `${f.top}%`, animationDuration: `${f.duration}s` }}
            onAnimationEnd={() => onAnimEnd(f.id)}
          >
            {f.chat && <div className="login-flyby-chat">{f.chat}</div>}
            <div className="login-flyby-craft">
              <div className="login-flyby-ship">
                {f.kind === 'satellite' ? (
                  <SatelliteCraft uid={`sat-${f.id}`} />
                ) : f.kind === 'ufo' ? (
                  f.variant === 1 ? (
                    <UfoIon uid={`ufo-${f.id}`} />
                  ) : (
                    <UfoClassic uid={`ufo-${f.id}`} />
                  )
                ) : (
                  <Rocket eid={`rocketFlame-${f.id}`} />
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
