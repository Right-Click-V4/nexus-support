import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react';
import { SpaceFlybys } from './LoginFlybys';
import { subscribeSkyCraft, type SkyCraft } from '../lib/skyTraffic';
import { NexusLogoMark, NexusWordmark } from './NexusBrand';
export { NexusLogoMark, NexusWordmark };

function useStarField(count: number) {
  return useMemo(
    () =>
      Array.from({ length: count }, (_, i) => {
        const layer = i % 5;
        const size =
          layer === 0
            ? 0.6 + (i % 3) * 0.15
            : layer === 1
              ? 0.9 + (i % 3) * 0.2
              : layer === 2
                ? 1.3 + (i % 4) * 0.25
                : layer === 3
                  ? 1.8 + (i % 3) * 0.3
                  : 2.4 + (i % 4) * 0.4;
        const duration =
          layer <= 1 ? 28 + (i % 10) * 2.5 : layer === 2 ? 18 + (i % 8) * 1.8 : 11 + (i % 7) * 1.4;
        const palette = ['#a78bfa', '#c4b5fd', '#67e8f9', '#e9d5ff', '#f9a8d4', '#ffffff', '#f0abfc', '#a5f3fc'];
        return {
          id: i,
          left: `${(i * 41 + 9 + layer * 13) % 100}%`,
          top: `${(i * 59 + 7 + layer * 19) % 100}%`,
          size,
          delay: -((i * 0.41 + layer * 1.3) % 26),
          duration,
          color: palette[i % palette.length],
          opacity: 0.15 + layer * 0.12 + (i % 4) * 0.04,
          twinkle: 2.4 + (i % 7) * 0.55,
        };
      }),
    [count],
  );
}

type TrailPoint = { x: number; y: number };
const TRAIL_MAX_DIST = 220;
const SAMPLE_MS = 32;
const BASE_SPEED = 0.26;
const TURN_RATE = 0.0048;
const PORTAL_EVERY_MS = 20000;

type PilotMode = 'cruise' | 'pause' | 'dash' | 'bob_v' | 'bob_h' | 'portal' | 'curious';

function randomIn(min: number, max: number) {
  return min + Math.random() * (max - min);
}

function trailPathD(points: TrailPoint[]): string {
  if (points.length < 2) return '';
  const pts = [...points].reverse();
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1];
    const b = pts[i];
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    d += ` Q ${a.x.toFixed(1)} ${a.y.toFixed(1)} ${mx.toFixed(1)} ${my.toFixed(1)}`;
  }
  return d;
}

function trimTrail(list: TrailPoint[], maxDist: number): TrailPoint[] {
  if (list.length < 2) return list;
  let dist = 0;
  const kept: TrailPoint[] = [list[0]];
  for (let i = 1; i < list.length; i++) {
    const step = Math.hypot(list[i].x - list[i - 1].x, list[i].y - list[i - 1].y);
    dist += step;
    kept.push(list[i]);
    if (dist >= maxDist) break;
  }
  return kept;
}

const HERO_CHATS = ['Hold my coffee', 'Copy that', 'Nice ship!', 'After you', 'Zoom!', 'I got this'];

function LogoPilotStage() {
  const stageRef = useRef<HTMLDivElement>(null);
  const pilotRef = useRef<HTMLDivElement>(null);
  const enterPortalRef = useRef<HTMLDivElement>(null);
  const exitPortalRef = useRef<HTMLDivElement>(null);
  const pathMainRef = useRef<SVGPathElement>(null);
  const pathSoftRef = useRef<SVGPathElement>(null);
  const pathGlowRef = useRef<SVGPathElement>(null);
  const craftRef = useRef<SkyCraft | null>(null);
  const [heroChat, setHeroChat] = useState<string | null>(null);

  useEffect(() => subscribeSkyCraft((c) => { craftRef.current = c; }), []);

  useEffect(() => {
    const stage = stageRef.current;
    const pilot = pilotRef.current;
    if (!stage || !pilot) return;

    let raf = 0;
    let x = 140;
    let y = 180;
    let heading = 0.25;
    let targetX = 420;
    let targetY = 240;
    let mode: PilotMode = 'cruise';
    let modeUntil = 0;
    let modeSpeed = 1;
    let scale = 0.92;
    let scaleGoal = 0.92;
    let opacity = 1;
    let opacityGoal = 1;
    let trail: TrailPoint[] = [];
    let lastSample = 0;
    let last = performance.now();
    let lastPortalAt = performance.now();
    let portalPhase: null | 'enter' | 'exit' = null;
    let portalExit = { x: 400, y: 200 };
    let breathT = 0;
    let chatUntil = 0;

    const measure = () => {
      const r = stage.getBoundingClientRect();
      return { width: Math.max(320, r.width), height: Math.max(320, r.height) };
    };

    const pickTarget = (w: number, h: number) => {
      targetX = randomIn(w * 0.12, w * 0.88);
      targetY = randomIn(h * 0.12, h * 0.72);
    };

    const pickMode = (now: number) => {
      const roll = Math.random();
      if (roll < 0.12) {
        mode = 'pause';
        modeUntil = now + randomIn(700, 1400);
        modeSpeed = 0.15;
        scaleGoal = randomIn(0.88, 1.02);
      } else if (roll < 0.28) {
        mode = 'dash';
        modeUntil = now + randomIn(900, 1600);
        modeSpeed = randomIn(1.55, 2.1);
        scaleGoal = randomIn(0.78, 0.9);
        pickTarget(measure().width, measure().height);
      } else if (roll < 0.42) {
        mode = 'bob_v';
        modeUntil = now + randomIn(1400, 2400);
        modeSpeed = 0.55;
        scaleGoal = randomIn(0.95, 1.12);
      } else if (roll < 0.55) {
        mode = 'bob_h';
        modeUntil = now + randomIn(1400, 2400);
        modeSpeed = 0.55;
        scaleGoal = randomIn(0.95, 1.1);
      } else if (roll < 0.68) {
        mode = 'curious';
        modeUntil = now + randomIn(1200, 2000);
        modeSpeed = 0.7;
        scaleGoal = randomIn(1.05, 1.22);
        const craft = craftRef.current;
        if (craft) {
          targetX = craft.x;
          targetY = craft.y;
          if (Math.random() < 0.55) {
            setHeroChat(HERO_CHATS[Math.floor(Math.random() * HERO_CHATS.length)]);
            chatUntil = now + 2200;
          }
        } else {
          pickTarget(measure().width, measure().height);
        }
      } else {
        mode = 'cruise';
        modeUntil = now + randomIn(1800, 3200);
        modeSpeed = randomIn(0.85, 1.15);
        scaleGoal = randomIn(0.72, 1.18);
        pickTarget(measure().width, measure().height);
      }
    };

    const startPortal = (now: number, w: number, h: number) => {
      mode = 'portal';
      portalPhase = 'enter';
      modeUntil = now + 700;
      modeSpeed = 0.2;
      opacityGoal = 0;
      scaleGoal = 0.35;
      lastPortalAt = now;
      const entr = enterPortalRef.current;
      if (entr) {
        entr.style.left = `${x}px`;
        entr.style.top = `${y}px`;
        entr.classList.add('is-active');
      }
      portalExit = {
        x: randomIn(w * 0.15, w * 0.85),
        y: randomIn(h * 0.15, h * 0.65),
      };
      const exitEl = exitPortalRef.current;
      if (exitEl) {
        exitEl.style.left = `${portalExit.x}px`;
        exitEl.style.top = `${portalExit.y}px`;
      }
    };

    pickTarget(measure().width, measure().height);
    modeUntil = performance.now() + 1800;

    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      const dt = Math.min(32, now - last);
      last = now;
      const sr = measure();
      breathT += dt * 0.001;

      if (chatUntil && now >= chatUntil) {
        setHeroChat(null);
        chatUntil = 0;
      }

      if (mode !== 'portal' && now - lastPortalAt >= PORTAL_EVERY_MS) {
        startPortal(now, sr.width, sr.height);
      }

      if (mode === 'portal') {
        if (portalPhase === 'enter' && now >= modeUntil) {
          x = portalExit.x;
          y = portalExit.y;
          trail = [];
          if (pathMainRef.current) pathMainRef.current.setAttribute('d', '');
          if (pathSoftRef.current) pathSoftRef.current.setAttribute('d', '');
          if (pathGlowRef.current) pathGlowRef.current.setAttribute('d', '');
          opacityGoal = 1;
          scaleGoal = 0.95;
          portalPhase = 'exit';
          modeUntil = now + 700;
          enterPortalRef.current?.classList.remove('is-active');
          exitPortalRef.current?.classList.add('is-active');
        } else if (portalPhase === 'exit' && now >= modeUntil) {
          portalPhase = null;
          mode = 'cruise';
          modeUntil = now + randomIn(1600, 2600);
          modeSpeed = 1;
          pickTarget(sr.width, sr.height);
          exitPortalRef.current?.classList.remove('is-active');
        }
      } else if (now >= modeUntil) {
        pickMode(now);
      }

      if (mode === 'bob_v') targetY = y + Math.sin(now * 0.006) * 28;
      if (mode === 'bob_h') targetX = x + Math.sin(now * 0.005) * 40;

      const breath = 1 + Math.sin(breathT * 0.9) * 0.04;

      const dx = targetX - x;
      const dy = targetY - y;
      const desired = Math.atan2(dy, dx);
      let turn = desired - heading;
      while (turn > Math.PI) turn -= Math.PI * 2;
      while (turn < -Math.PI) turn += Math.PI * 2;
      const turnBoost = mode === 'dash' || mode === 'curious' ? 1.85 : 1;
      const maxTurn = TURN_RATE * turnBoost * dt;
      heading += Math.max(-maxTurn, Math.min(maxTurn, turn));

      const speed = BASE_SPEED * modeSpeed * (mode === 'pause' || mode === 'portal' ? 0.18 : 1);
      x += Math.cos(heading) * speed * dt;
      y += Math.sin(heading) * speed * dt;
      x = Math.max(28, Math.min(sr.width - 28, x));
      y = Math.max(28, Math.min(sr.height - 28, y));

      scale += (scaleGoal - scale) * Math.min(1, dt * 0.008);
      opacity += (opacityGoal - opacity) * Math.min(1, dt * 0.007);

      pilot.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px) scale(${scale * breath})`;
      pilot.style.opacity = String(Math.max(0, Math.min(1, opacity)));

      if (now - lastSample >= SAMPLE_MS && mode !== 'portal') {
        lastSample = now;
        trail = trimTrail([{ x, y }, ...trail], TRAIL_MAX_DIST);
        const d = trailPathD(trail);
        if (pathMainRef.current) pathMainRef.current.setAttribute('d', d);
        if (pathSoftRef.current) pathSoftRef.current.setAttribute('d', d);
        if (pathGlowRef.current) pathGlowRef.current.setAttribute('d', d);
      }
    };

    const onVis = () => {
      if (document.visibilityState === 'hidden') {
        cancelAnimationFrame(raf);
        raf = 0;
      } else if (!raf) {
        last = performance.now();
        raf = requestAnimationFrame(tick);
      }
    };
    document.addEventListener('visibilitychange', onVis);
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      document.removeEventListener('visibilitychange', onVis);
    };
  }, []);

  return (
    <div ref={stageRef} className="login-pilot-stage absolute inset-0 pointer-events-none overflow-visible" aria-hidden>
      <svg className="absolute inset-0 w-full h-full overflow-visible" aria-hidden>
        <defs>
          <linearGradient id="loginWakeMain" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#c4b5fd" stopOpacity="0" />
            <stop offset="40%" stopColor="#a78bfa" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#f5d0fe" stopOpacity="0.9" />
          </linearGradient>
          <linearGradient id="loginWakeSoft" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#67e8f9" stopOpacity="0" />
            <stop offset="55%" stopColor="#a5b4fc" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#e9d5ff" stopOpacity="0.45" />
          </linearGradient>
          <filter id="loginTrailBlur" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.2" />
          </filter>
        </defs>
        <path
          ref={pathGlowRef}
          d=""
          fill="none"
          stroke="url(#loginWakeSoft)"
          strokeWidth="7"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#loginTrailBlur)"
          opacity="0.55"
          className="login-light-trail"
        />
        <path
          ref={pathSoftRef}
          d=""
          fill="none"
          stroke="url(#loginWakeSoft)"
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.7"
          className="login-light-trail"
        />
        <path
          ref={pathMainRef}
          d=""
          fill="none"
          stroke="url(#loginWakeMain)"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.95"
          className="login-light-trail"
        />
      </svg>

      <div ref={enterPortalRef} className="login-space-portal" aria-hidden>
        <div className="login-space-portal-ring login-space-portal-ring-a" />
        <div className="login-space-portal-ring login-space-portal-ring-b" />
        <div className="login-space-portal-core" />
      </div>
      <div ref={exitPortalRef} className="login-space-portal" aria-hidden>
        <div className="login-space-portal-ring login-space-portal-ring-a" />
        <div className="login-space-portal-ring login-space-portal-ring-b" />
        <div className="login-space-portal-core" />
      </div>
      <div
        ref={pilotRef}
        className="login-pilot login-pilot-js"
        style={{ left: 0, top: 0, transform: 'translate(-50%, -50%) scale(0.92)' }}
      >
        {heroChat ? <span className="login-pilot-chat">{heroChat}</span> : null}
        <div className="login-pilot-halo" />
        <div className="login-pilot-orbit" />
        <div className="login-pilot-spin">
          <NexusLogoMark size={48} />
        </div>
      </div>
    </div>
  );
}

function DistantPlanet({
  className,
  style,
}: {
  className: string;
  style?: CSSProperties;
}) {
  return <div className={className} style={style} aria-hidden />;
}

export function CosmicFallBackground() {
  const stars = useStarField(90);
  return (
    <div className="login-cosmos absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      <div className="login-cosmos-sky absolute inset-0" />
      <div className="login-galaxy-band" />
      <div className="login-galaxy-band login-galaxy-band-2" />
      <div className="login-nebula login-nebula-a" />
      <div className="login-nebula login-nebula-b" />
      <div className="login-nebula login-nebula-c" />
      <div className="login-nebula login-nebula-d" />
      <div className="login-dust" />
      <div className="login-dust login-dust-fine" />
      <DistantPlanet className="login-planet login-planet-a" />
      <DistantPlanet className="login-planet login-planet-b" />
      <DistantPlanet className="login-planet login-planet-c" />
      {stars.map((s) => (
        <span
          key={s.id}
          className="login-star absolute rounded-full"
          style={{
            left: s.left,
            top: s.top,
            width: s.size,
            height: s.size,
            background: s.color,
            opacity: s.opacity,
            animationDuration: `${s.duration}s, ${s.twinkle}s`,
            animationDelay: `${s.delay}s, ${(s.id % 9) * 0.35}s`,
            boxShadow: s.size > 1.8 ? `0 0 ${s.size * 1.4}px ${s.color}` : undefined,
          }}
        />
      ))}
      <LogoPilotStage />
      <SpaceFlybys />
    </div>
  );
}
