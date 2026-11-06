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
const TRAIL_LEN = 64;
const SAMPLE_MS = 14;

function easeInOut(t: number) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}
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
    let x = 0;
    let y = 0;
    let fromX = 0;
    let fromY = 0;
    let toX = 0;
    let toY = 0;
    let toScale = 1;
    let fromScale = 1;
    let scale = 1;
    let startT = 0;
    let duration = 2500;
    let ready = false;
    let prevX = 0;
    let prevY = 0;

    const pickTarget = (w: number, h: number) => {
      const marginX = w * 0.12;
      const marginY = h * 0.1;
      let nx = randomIn(marginX, w - marginX);
      let ny = randomIn(marginY, h - marginY);
      if (Math.random() < 0.25) ny = randomIn(h * 0.55, h * 0.88);
      if (Math.random() < 0.25) ny = randomIn(h * 0.08, h * 0.28);
      if (Math.random() < 0.2) nx = randomIn(marginX, w * 0.35);
      if (Math.random() < 0.2) nx = randomIn(w * 0.55, w - marginX);
      fromX = x;
      fromY = y;
      fromScale = scale;
      toX = nx;
      toY = ny;
      toScale = randomIn(0.9, 1.12);
      startT = performance.now();
      const dist = Math.hypot(toX - fromX, toY - fromY);
      const travel = dist * 2.4 + randomIn(280, 900);
      duration = Math.min(4800, Math.max(1600, travel));
    };

    const publishTrail = (list: TrailPoint[]) => {
      setTrail(list);
      setPaths({
        core: trailPath(list, 0, 0, 0),
        waveA: trailPath(list, 8, 0, 0.3),
        waveB: trailPath(list, 6, Math.PI * 0.9, 0.36),
      });
      const oldest = list[list.length - 1];
      const newest = list[0];
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
        y = sr.height * 0.35;
        prevX = x;
        prevY = y;
        fromX = x;
        fromY = y;
        toX = x;
        toY = y;
        ready = true;
        stageSizeRef.current = { w: sr.width, h: sr.height };
        pickTarget(sr.width, sr.height);
      }

      if (
        Math.abs(sr.width - stageSizeRef.current.w) > 12 ||
        Math.abs(sr.height - stageSizeRef.current.h) > 12
      ) {
        stageSizeRef.current = { w: sr.width, h: sr.height };
      }

      const t = Math.min(1, (now - startT) / duration);
      const e = easeInOut(t);
      x = fromX + (toX - fromX) * e;
      y = fromY + (toY - fromY) * e;
      scale = fromScale + (toScale - fromScale) * e;
      pilot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${scale})`;

      if (t >= 1) pickTarget(sr.width, sr.height);

      const moved = Math.hypot(x - prevX, y - prevY);
      if (now - lastSample >= SAMPLE_MS && moved >= 0.9) {
        lastSample = now;
        prevX = x;
        prevY = y;
        history.current = [{ x, y, t: now }, ...history.current].slice(0, TRAIL_LEN);
        publishTrail([...history.current]);
      } else if (now - lastSample >= 90 && history.current.length > 10) {
        lastSample = now;
        history.current = history.current.slice(0, -2);
        publishTrail([...history.current]);
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
