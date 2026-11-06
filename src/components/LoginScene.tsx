import { useEffect, useMemo, useRef, useState } from 'react';
import { SpaceFlybys } from './LoginFlybys';
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
    [count]
  );
}

type TrailPoint = { x: number; y: number; t: number };
const TRAIL_MAX_DIST = 280;
const SAMPLE_MS = 14;
const BASE_SPEED = 0.24;
const TURN_RATE = 0.0045;

type PilotMode = 'cruise' | 'pause' | 'dash' | 'bob_v' | 'bob_h';

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
    if (dist > maxDist) break;
    kept.push(list[i]);
  }
  return kept;
}

function LogoPilotStage() {
  const pilotRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const history = useRef<TrailPoint[]>([]);
  const stageSizeRef = useRef({ w: 1, h: 1 });
  const [trail, setTrail] = useState<TrailPoint[]>([]);
  const [paths, setPaths] = useState({ core: '', waveA: '', waveB: '' });
  const [grad, setGrad] = useState({ x1: 0, y1: 0, x2: 1, y2: 0 });

  useEffect(() => {
    let raf = 0;
    let lastSample = 0;
    let lastTick = 0;
    let x = 0;
    let y = 0;
    let angle = -Math.PI / 2;
    let scale = 1;
    let scaleGoal = 1;
    let targetX = 0;
    let targetY = 0;
    let ready = false;
    let prevX = 0;
    let prevY = 0;
    let turnBoost = 1;
    let mode: PilotMode = 'cruise';
    let modeUntil = 0;
    let modeSpeed = 1;
    let lastWeaveAt = 0;
    let bobPhase = 0;
    let bobAmp = 16;

    const pickMode = (now: number) => {
      const weaveReady = now - lastWeaveAt >= 30000;
      const r = Math.random();
      modeSpeed = randomIn(0.75, 1.45);

      if (weaveReady && r < 0.12) {
        mode = 'bob_v';
        bobAmp = randomIn(12, 22);
        bobPhase = 0;
        modeSpeed = randomIn(0.5, 0.8);
        modeUntil = now + randomIn(520, 780);
        lastWeaveAt = now;
      } else if (weaveReady && r < 0.24) {
        mode = 'bob_h';
        bobAmp = randomIn(14, 26);
        bobPhase = 0;
        modeSpeed = randomIn(0.5, 0.8);
        modeUntil = now + randomIn(520, 800);
        lastWeaveAt = now;
      } else if (r < 0.12) {
        mode = 'pause';
        modeUntil = now + randomIn(300, 700);
      } else if (r < 0.28) {
        mode = 'dash';
        modeSpeed = randomIn(1.7, 2.5);
        modeUntil = now + randomIn(400, 1000);
      } else {
        mode = 'cruise';
        modeSpeed = randomIn(0.85, 1.35);
        modeUntil = now + randomIn(1600, 3800);
      }
    };

    const pickTarget = (w: number, h: number, preferAwayFromEdge = false) => {
      const marginX = w * 0.12;
      const marginY = h * 0.1;
      const allowSharp = Math.random() < 0.35;
      const verticalBias = Math.random() < 0.22;
      const horizontalBias = Math.random() < 0.22;
      let bestX = randomIn(marginX, w - marginX);
      let bestY = randomIn(marginY, h - marginY);
      let bestScore = -Infinity;
      for (let tries = 0; tries < 12; tries++) {
        let nx = randomIn(marginX, w - marginX);
        let ny = randomIn(marginY, h - marginY);
        if (preferAwayFromEdge) {
          nx = randomIn(w * 0.25, w * 0.75);
          ny = randomIn(h * 0.25, h * 0.75);
        } else if (verticalBias) {
          nx = x + randomIn(-36, 36);
          nx = Math.max(marginX, Math.min(w - marginX, nx));
          ny = randomIn(marginY, h - marginY);
        } else if (horizontalBias) {
          ny = y + randomIn(-36, 36);
          ny = Math.max(marginY, Math.min(h - marginY, ny));
          nx = randomIn(marginX, w - marginX);
        }
        const desired = Math.atan2(ny - y, nx - x);
        let delta = desired - angle;
        while (delta > Math.PI) delta -= Math.PI * 2;
        while (delta < -Math.PI) delta += Math.PI * 2;
        const dist = Math.hypot(nx - x, ny - y);
        const score = allowSharp
          ? dist * 0.3 + Math.abs(delta) * 55
          : dist * 0.45 - Math.abs(delta) * 90;
        if (score > bestScore && dist > 70) {
          bestScore = score;
          bestX = nx;
          bestY = ny;
        }
      }
      targetX = bestX;
      targetY = bestY;
      scaleGoal = randomIn(0.94, 1.08);
      turnBoost = allowSharp ? 2.6 : 1;
    };

    const publishTrail = (list: TrailPoint[]) => {
      const fixed = trimTrail(list, TRAIL_MAX_DIST);
      setTrail(fixed);
      setPaths({
        core: trailPath(fixed, 0, 0, 0),
        waveA: trailPath(fixed, 5, 0, 0.32),
        waveB: trailPath(fixed, 4, Math.PI * 0.9, 0.38),
      });
      const oldest = fixed[fixed.length - 1];
      const newest = fixed[0];
      if (oldest && newest) setGrad({ x1: oldest.x, y1: oldest.y, x2: newest.x, y2: newest.y });
    };

    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      const stage = stageRef.current;
      const pilot = pilotRef.current;
      if (!stage || !pilot) return;
      const sr = stage.getBoundingClientRect();
      if (sr.width < 10 || sr.height < 10) return;

      if (!ready) {
        x = sr.width * 0.5;
        y = sr.height * 0.38;
        prevX = x;
        prevY = y;
        targetX = x;
        targetY = y;
        ready = true;
        lastTick = now;
        stageSizeRef.current = { w: sr.width, h: sr.height };
        pickTarget(sr.width, sr.height);
        lastWeaveAt = now;
        pickMode(now);
      }

      if (
        Math.abs(sr.width - stageSizeRef.current.w) > 12 ||
        Math.abs(sr.height - stageSizeRef.current.h) > 12
      ) {
        stageSizeRef.current = { w: sr.width, h: sr.height };
      }

      const dt = Math.min(32, Math.max(0, now - lastTick));
      lastTick = now;

      if (now >= modeUntil) pickMode(now);

      let speedMul = modeSpeed;
      if (mode === 'pause') speedMul = 0;

      if (mode !== 'pause') {
        const targetAngle = Math.atan2(targetY - y, targetX - x);
        let delta = targetAngle - angle;
        while (delta > Math.PI) delta -= Math.PI * 2;
        while (delta < -Math.PI) delta += Math.PI * 2;
        const maxTurn = TURN_RATE * turnBoost * (mode === 'dash' ? 1.5 : 1) * dt;
        if (delta > maxTurn) delta = maxTurn;
        if (delta < -maxTurn) delta = -maxTurn;
        angle += delta;

        const step = BASE_SPEED * speedMul * dt;
        x += Math.cos(angle) * step;
        y += Math.sin(angle) * step;

        if (mode === 'bob_v' || mode === 'bob_h') {
          bobPhase += dt * 0.012;
          const wiggle = Math.sin(bobPhase) * bobAmp * (dt / 16) * 0.55;
          if (mode === 'bob_v') y += wiggle;
          else x += wiggle;
        }
      }

      scale += (scaleGoal - scale) * Math.min(1, dt * 0.002);

      const mX = sr.width * 0.06;
      const mY = sr.height * 0.06;
      let bounced = false;
      if (x < mX) {
        x = mX;
        angle = Math.PI - angle;
        bounced = true;
      } else if (x > sr.width - mX) {
        x = sr.width - mX;
        angle = Math.PI - angle;
        bounced = true;
      }
      if (y < mY) {
        y = mY;
        angle = -angle;
        bounced = true;
      } else if (y > sr.height - mY) {
        y = sr.height - mY;
        angle = -angle;
        bounced = true;
      }
      if (bounced) {
        while (angle > Math.PI) angle -= Math.PI * 2;
        while (angle < -Math.PI) angle += Math.PI * 2;
        pickTarget(sr.width, sr.height, true);
        if (mode === 'pause') {
          mode = 'cruise';
          modeSpeed = randomIn(1.0, 1.6);
          modeUntil = now + randomIn(600, 1400);
        }
      }

      pilot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${scale})`;

      if (mode !== 'pause' && Math.hypot(targetX - x, targetY - y) < 56) {
        pickTarget(sr.width, sr.height);
      }

      const moved = Math.hypot(x - prevX, y - prevY);
      if (now - lastSample >= SAMPLE_MS && moved >= 0.8) {
        lastSample = now;
        prevX = x;
        prevY = y;
        history.current = [{ x, y, t: now }, ...history.current];
        history.current = trimTrail(history.current, TRAIL_MAX_DIST + 30);
        publishTrail([...history.current]);
      } else if (mode === 'pause' && now - lastSample >= 80) {
        lastSample = now;
        if (history.current.length > 12) {
          history.current = history.current.slice(0, -3);
          publishTrail([...history.current]);
        }
      }
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div ref={stageRef} className="login-pilot-stage absolute inset-0 overflow-hidden pointer-events-none">
      <svg className="login-trail-svg" width="100%" height="100%" aria-hidden>
        <defs>
          <linearGradient id="loginTrailViolet" gradientUnits="userSpaceOnUse" x1={grad.x1} y1={grad.y1} x2={grad.x2} y2={grad.y2}>
            <stop offset="0%" stopColor="#4c1d95" stopOpacity="0" />
            <stop offset="20%" stopColor="#8b5cf6" stopOpacity="0.35" />
            <stop offset="55%" stopColor="#e879f9" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#fce7f3" stopOpacity="1" />
          </linearGradient>
          <linearGradient id="loginTrailCyan" gradientUnits="userSpaceOnUse" x1={grad.x1} y1={grad.y1} x2={grad.x2} y2={grad.y2}>
            <stop offset="0%" stopColor="#0e7490" stopOpacity="0" />
            <stop offset="35%" stopColor="#22d3ee" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#a5f3fc" stopOpacity="0.9" />
          </linearGradient>
          <linearGradient id="loginTrailCore" gradientUnits="userSpaceOnUse" x1={grad.x1} y1={grad.y1} x2={grad.x2} y2={grad.y2}>
            <stop offset="0%" stopColor="#a78bfa" stopOpacity="0" />
            <stop offset="45%" stopColor="#f0abfc" stopOpacity="0.65" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="1" />
          </linearGradient>
          <filter id="loginTrailGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="loginTrailSoft" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {paths.waveA && (
          <path className="login-trail-wave login-trail-wave-a" d={paths.waveA} fill="none" stroke="url(#loginTrailCyan)" filter="url(#loginTrailSoft)" />
        )}
        {paths.waveB && (
          <path className="login-trail-wave login-trail-wave-b" d={paths.waveB} fill="none" stroke="url(#loginTrailViolet)" filter="url(#loginTrailSoft)" />
        )}
        {paths.core && (
          <>
            <path className="login-trail-ribbon-glow" d={paths.core} fill="none" stroke="url(#loginTrailViolet)" />
            <path className="login-trail-ribbon" d={paths.core} fill="none" stroke="url(#loginTrailViolet)" filter="url(#loginTrailGlow)" />
            <path className="login-trail-ribbon-core" d={paths.core} fill="none" stroke="url(#loginTrailCore)" />
          </>
        )}
      </svg>
      {trail.map((p, i) => {
        const fade = 1 - i / Math.max(1, trail.length - 1);
        if (fade < 0.08) return null;
        const kind = i % 3;
        const size = kind === 0 ? 2.5 + fade * 5.5 : kind === 1 ? 1.8 + fade * 4 : 1.2 + fade * 3;
        return (
          <span
            key={`spark-${i}-${Math.round(p.x)}-${Math.round(p.y)}`}
            className={`login-trail-spark login-trail-spark-${kind}`}
            style={{
              left: p.x + ((i % 5) - 2) * 3.5 * fade,
              top: p.y + ((i % 3) - 1) * 3 * fade,
              opacity: 0.3 + fade * 0.7,
              width: size,
              height: size,
              transform: 'translate(-50%, -50%)',
            }}
          />
        );
      })}
      <div
        ref={pilotRef}
        className="login-pilot login-pilot-js"
        style={{ left: 0, top: 0, transform: 'translate(-50%, -50%)' }}
      >
        <span className="login-pilot-halo" />
        <span className="login-pilot-orbit" />
        <NexusLogoMark size={52} />
      </div>
    </div>
  );
}

export function CosmicFallBackground() {
  const stars = useFallingStars(48);
  const twinkles = useFallingStars(22);
  return (
    <div className="login-cosmos-sky absolute inset-0 overflow-hidden" aria-hidden>
      <div className="login-galaxy-band" />
      <div className="login-nebula login-nebula-a" />
      <div className="login-dust" />
      <div className="absolute inset-0">
        {twinkles.map((s) => (
          <span
            key={`t-${s.id}`}
            className="absolute rounded-full"
            style={{
              left: s.left,
              top: s.top,
              width: s.size,
              height: s.size,
              background: s.color,
              boxShadow: `0 0 ${s.size * 4}px ${s.color}`,
              animation: `login-twinkle ${s.twinkle}s ease-in-out ${s.delay}s infinite`,
            }}
          />
        ))}
      </div>
      <div className="absolute inset-0 overflow-hidden">
        {stars.map((s) => (
          <span
            key={s.id}
            className="login-star absolute rounded-full"
            style={{
              left: s.left,
              width: s.size,
              height: s.size,
              background: s.color,
              opacity: s.opacity,
              boxShadow: `0 0 ${s.size * 4}px ${s.color}`,
              animationDelay: `${s.delay}s`,
              animationDuration: `${s.duration}s`,
            }}
          />
        ))}
      </div>
      <LogoPilotStage />
      <SpaceFlybys />
    </div>
  );
}
