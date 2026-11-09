import { useEffect, useMemo, useRef, useState } from 'react';
import { SpaceFlybys } from './LoginFlybys';
import { subscribeSkyCraft, type SkyCraft } from '../lib/skyTraffic';
import { NexusLogoMark, NexusWordmark } from './NexusBrand';
export { NexusLogoMark, NexusWordmark };

function useFallingStars(count: number) {
  return useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        id: i,
        left: `${(i * 37 + 7) % 100}%`,
        top: `${(i * 53 + 11) % 100}%`,
        size: i % 7 === 0 ? 2.4 : i % 3 === 0 ? 1.6 : 1,
        delay: -((i * 0.47) % 18),
        duration: 14 + (i % 9) * 2.2,
        twinkle: 2.4 + (i % 5) * 0.7,
        color: i % 5 === 0 ? '#f9a8d4' : i % 4 === 0 ? '#67e8f9' : i % 3 === 0 ? '#ffffff' : '#c4b5fd',
        opacity: 0.25 + (i % 5) * 0.12,
      })),
    [count],
  );
}

type TrailPoint = { x: number; y: number; t: number };
const TRAIL_MAX_DIST = 160;
const SAMPLE_MS = 14;
const BASE_SPEED = 0.24;
const TURN_RATE = 0.0045;

type PilotMode = 'cruise' | 'pause' | 'dash' | 'bob_v' | 'bob_h' | 'portal' | 'curious';

function randomIn(min: number, max: number) {
  return min + Math.random() * (max - min);
}

function trailPath(points: TrailPoint[], amp = 0, phase = 0, freq = 0.22): string {
  if (points.length < 2) return '';
  const pts = [...points].reverse();
  const out: { x: number; y: number }[] = [];
  let dist = 0;
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    if (i === 0) {
      out.push({ x: p.x, y: p.y });
      continue;
    }
    const prev = pts[i - 1];
    const dx = p.x - prev.x;
    const dy = p.y - prev.y;
    const len = Math.hypot(dx, dy) || 1;
    dist += len;
    const nx = -dy / len;
    const ny = dx / len;
    const wave = amp === 0 ? 0 : Math.sin(dist * freq + phase) * amp * (i / pts.length);
    out.push({ x: p.x + nx * wave, y: p.y + ny * wave });
  }
  let d = `M ${out[0].x.toFixed(1)} ${out[0].y.toFixed(1)}`;
  for (let i = 1; i < out.length; i++) {
    const a = out[i - 1];
    const b = out[i];
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

const HERO_CHATS = [
  'Hold my coffee',
  'Copy that',
  'Nice ship!',
  'After you',
  'Zoom!',
  'I got this',
];

const PORTAL_EVERY_MS = 28000;

function LogoPilotStage() {
  const stageRef = useRef<HTMLDivElement>(null);
  const pilotRef = useRef<HTMLDivElement>(null);
  const enterPortalRef = useRef<HTMLDivElement>(null);
  const exitPortalRef = useRef<HTMLDivElement>(null);
  const craftRef = useRef<SkyCraft | null>(null);
  const [sparks, setSparks] = useState<TrailPoint[]>([]);
  const [heroChat, setHeroChat] = useState<string | null>(null);
  const stageSizeRef = useRef({ w: 1200, h: 800 });

  useEffect(() => subscribeSkyCraft((c) => { craftRef.current = c; }), []);

  useEffect(() => {
    const stage = stageRef.current;
    const pilot = pilotRef.current;
    if (!stage || !pilot) return;

    let raf = 0;
    let x = 120;
    let y = 160;
    let heading = 0.2;
    let targetX = 400;
    let targetY = 220;
    let mode: PilotMode = 'cruise';
    let modeUntil = 0;
    let modeSpeed = 1;
    let scale = 0.95;
    let scaleGoal = 0.95;
    let opacity = 1;
    let opacityGoal = 1;
    let lastSample = 0;
    let lastTick = performance.now();
    let trail: TrailPoint[] = [];
    let lastCuriousAt = 0;
    let curiousUntil = 0;
    let lastPortalAt = performance.now() - PORTAL_EVERY_MS + 4000;
    let lastChatCraftId: number | null = null;
    let chatUntil = 0;
    let portalPhase: null | 'enter' | 'exit' = null;

    const pickTarget = (w: number, h: number, near = false) => {
      if (near) {
        targetX = Math.max(40, Math.min(w - 40, x + randomIn(-180, 180)));
        targetY = Math.max(40, Math.min(h * 0.55, y + randomIn(-100, 100)));
      } else {
        targetX = randomIn(60, Math.max(120, w - 60));
        targetY = randomIn(50, Math.max(100, h * 0.55));
      }
    };

    const pickMode = (now: number) => {
      const roll = Math.random();
      if (roll < 0.18) {
        mode = 'pause';
        modeUntil = now + randomIn(600, 1400);
        modeSpeed = 0.15;
      } else if (roll < 0.34) {
        mode = 'dash';
        modeUntil = now + randomIn(900, 1600);
        modeSpeed = randomIn(1.8, 2.6);
        pickTarget(stageSizeRef.current.w, stageSizeRef.current.h);
      } else if (roll < 0.5) {
        mode = 'bob_v';
        modeUntil = now + randomIn(1400, 2400);
        modeSpeed = randomIn(0.7, 1.1);
      } else if (roll < 0.66) {
        mode = 'bob_h';
        modeUntil = now + randomIn(1400, 2400);
        modeSpeed = randomIn(0.7, 1.1);
      } else {
        mode = 'cruise';
        modeUntil = now + randomIn(1800, 3200);
        modeSpeed = randomIn(0.85, 1.35);
        pickTarget(stageSizeRef.current.w, stageSizeRef.current.h);
      }
    };

    const startPortal = (now: number, w: number, h: number) => {
      mode = 'portal';
      portalPhase = 'enter';
      lastPortalAt = now;
      const ex = randomIn(80, w - 80);
      const ey = randomIn(60, h * 0.5);
      const entr = enterPortalRef.current;
      const exit = exitPortalRef.current;
      if (entr) {
        entr.style.left = `${x}px`;
        entr.style.top = `${y}px`;
        entr.classList.add('is-active');
      }
      if (exit) {
        exit.style.left = `${ex}px`;
        exit.style.top = `${ey}px`;
      }
      opacityGoal = 0;
      scaleGoal = 0.55;
      targetX = x;
      targetY = y;
      modeUntil = now + 700;
      ;(window as any).__portalExit = { x: ex, y: ey };
    };

    const sr0 = stage.getBoundingClientRect();
    stageSizeRef.current = { w: sr0.width, h: sr0.height };
    pickTarget(sr0.width, sr0.height);
    modeUntil = performance.now() + 1200;

    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      const sr = stage.getBoundingClientRect();
      if (Math.abs(sr.width - stageSizeRef.current.w) > 12 || Math.abs(sr.height - stageSizeRef.current.h) > 12) {
        stageSizeRef.current = { w: sr.width, h: sr.height };
      }
      const dt = Math.min(32, Math.max(0, now - lastTick));
      lastTick = now;

      const craft = craftRef.current;
      // HERO_ESCORT_V2
      // HERO_ESCORT_SPARSE — only occasionally follow a chatty craft
      if (
        mode !== 'portal' &&
        mode !== 'curious' &&
        craft &&
        craft.label &&
        now - lastCuriousAt > 16000 &&
        Math.random() < 0.004
      ) {
        mode = 'curious';
        curiousUntil = now + randomIn(2800, 4800);
        lastCuriousAt = now;
        modeSpeed = randomIn(1.2, 1.8);
        targetX = craft.x;
        targetY = craft.y;
        scaleGoal = randomIn(0.9, 1.08);
        if (craft.id !== lastChatCraftId && Math.random() < 0.55) {
          lastChatCraftId = craft.id;
          setHeroChat(HERO_CHATS[Math.floor(Math.random() * HERO_CHATS.length)]);
          chatUntil = now + 2000;
        }
      }
      if (mode === 'curious') {
        if (craft) {
          targetX = craft.x + (craft.dir === 'ltr' ? 28 : -28);
          targetY = craft.y + Math.sin(now * 0.004) * 10;
        }
        if (now >= curiousUntil || !craft) {
          mode = 'cruise';
          modeUntil = now + randomIn(1200, 2400);
          modeSpeed = randomIn(0.9, 1.3);
          pickTarget(sr.width, sr.height);
        }
      }
      if (chatUntil && now >= chatUntil) {
        chatUntil = 0;
        setHeroChat(null);
      }

      if (mode !== 'portal' && now - lastPortalAt >= PORTAL_EVERY_MS) {
        startPortal(now, sr.width, sr.height);
      }

      if (mode === 'portal') {
        if (portalPhase === 'enter' && now >= modeUntil) {
          const exit = (window as any).__portalExit as { x: number; y: number } | undefined;
          x = exit?.x ?? randomIn(80, sr.width - 80);
          y = exit?.y ?? randomIn(60, sr.height * 0.5);
          trail = [];
          opacityGoal = 1;
          scaleGoal = 0.95;
          portalPhase = 'exit';
          modeUntil = now + 650;
          const entr = enterPortalRef.current;
          const exitEl = exitPortalRef.current;
          if (entr) entr.classList.remove('is-active');
          if (exitEl) exitEl.classList.add('is-active');
        } else if (portalPhase === 'exit' && now >= modeUntil) {
          portalPhase = null;
          mode = 'cruise';
          modeUntil = now + randomIn(1600, 2600);
          modeSpeed = 1;
          pickTarget(sr.width, sr.height);
          const exitEl = exitPortalRef.current;
          if (exitEl) exitEl.classList.remove('is-active');
        }
      } else if (mode !== 'curious' && now >= modeUntil) {
        pickMode(now);
      }

      if (mode === 'bob_v') targetY = y + Math.sin(now * 0.006) * 28;
      if (mode === 'bob_h') targetX = x + Math.sin(now * 0.005) * 40;

      const dx = targetX - x;
      const dy = targetY - y;
      const desired = Math.atan2(dy, dx);
      let turn = desired - heading;
      while (turn > Math.PI) turn -= Math.PI * 2;
      while (turn < -Math.PI) turn += Math.PI * 2;
      const turnBoost = mode === 'dash' || mode === 'curious' ? 1.8 : 1;
      const maxTurn = TURN_RATE * turnBoost * dt;
      heading += Math.max(-maxTurn, Math.min(maxTurn, turn));

      const speed = BASE_SPEED * modeSpeed * (mode === 'pause' || mode === 'portal' ? 0.2 : 1);
      x += Math.cos(heading) * speed * dt;
      y += Math.sin(heading) * speed * dt;
      x = Math.max(24, Math.min(sr.width - 24, x));
      y = Math.max(24, Math.min(sr.height - 24, y));

      scale += (scaleGoal - scale) * Math.min(1, dt * 0.006);
      opacity += (opacityGoal - opacity) * Math.min(1, dt * 0.004);

      pilot.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px) scale(${scale})`;
      pilot.style.opacity = String(Math.max(0, Math.min(1, opacity)));

      if (now - lastSample >= SAMPLE_MS) {
        lastSample = now;
        trail = trimTrail([{ x, y, t: now }, ...trail], TRAIL_MAX_DIST);
        if (trail.length % 3 === 0) setSparks(trail.slice(0, 12));
      }
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div ref={stageRef} className="login-pilot-stage absolute inset-0 pointer-events-none overflow-visible" aria-hidden>
      <svg className="absolute inset-0 w-full h-full overflow-visible" aria-hidden>
        <defs>
          <linearGradient id="loginWake" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#c4b5fd" stopOpacity="0" />
            <stop offset="55%" stopColor="#a78bfa" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#f5d0fe" stopOpacity="0.85" />
          </linearGradient>
        </defs>
      </svg>
      {sparks.map((p, i) => {
        const fade = 1 - i / 12;
        return (
          <span
            key={`${p.t}-${i}`}
            className={`login-trail-spark ${i % 3 === 1 ? 'login-trail-spark-1' : i % 3 === 2 ? 'login-trail-spark-2' : ''}`}
            style={{
              left: p.x,
              top: p.y,
              width: 1.4 + fade * 2.2,
              height: 1.4 + fade * 2.2,
              opacity: 0.12 + fade * 0.35,
              transform: 'translate(-50%, -50%)',
            }}
          />
        );
      })}
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
      <div ref={pilotRef} className="login-pilot login-pilot-js" style={{ left: 0, top: 0, transform: 'translate(-50%, -50%) scale(0.95)' }}>
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

export function CosmicFallBackground() {
  const stars = useFallingStars(48);
  return (
    <div className="login-cosmos absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      <div className="login-cosmos-sky absolute inset-0" />
      <div className="login-galaxy-band" />
      <div className="login-nebula login-nebula-a" />
      <div className="login-dust" />
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
            animationDuration: `${s.duration}s`,
            animationDelay: `${s.delay}s`,
            boxShadow: `0 0 ${s.size * 2}px ${s.color}`,
          }}
        />
      ))}
      <LogoPilotStage />
      <SpaceFlybys />
    </div>
  );
}
