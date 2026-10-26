import { useEffect, useMemo, useRef, useState } from 'react';
import { SpaceFlybys } from './LoginFlybys';

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

export function NexusLogoMark({ size = 56 }: { size?: number }) {
  return (
    <div className="login-logo-mark" style={{ width: size, height: size }}>
      <svg viewBox="0 0 48 48" width={size} height={size} fill="none" aria-hidden>
        <circle cx="24" cy="24" r="5.2" fill="#e9d5ff" className="login-logo-core" />
        <g className="login-logo-arcs">
          <path d="M24 7a17 17 0 0 1 17 17" stroke="#c4b5fd" strokeWidth="3" strokeLinecap="round" />
          <path d="M24 41a17 17 0 0 1-17-17" stroke="#a78bfa" strokeWidth="3" strokeLinecap="round" opacity="0.7" />
        </g>
        <g className="login-logo-arcs-rev">
          <path d="M10 30a16 16 0 0 1 4-14" stroke="#f0abfc" strokeWidth="1.6" strokeLinecap="round" opacity="0.8" />
        </g>
      </svg>
    </div>
  );
}

type TrailPoint = { x: number; y: number };
const TRAIL_LEN = 32;
function easeInOut(t: number) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
function randomIn(min: number, max: number) { return min + Math.random() * (max - min); }

function LogoPilotStage() {
  const pilotRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const history = useRef<TrailPoint[]>([]);
  const [trail, setTrail] = useState<TrailPoint[]>([]);
  const [stageSize, setStageSize] = useState({ w: 1, h: 1 });
  useEffect(() => {
    let raf = 0;
    let lastSample = 0;
    let x = 0, y = 0, fromX = 0, fromY = 0, toX = 0, toY = 0, toScale = 1, fromScale = 1, scale = 1, startT = 0, duration = 2500, ready = false;
    const pickTarget = (w: number, h: number) => {
      const marginX = w * 0.12, marginY = h * 0.1;
      let nx = randomIn(marginX, w - marginX);
      let ny = randomIn(marginY, h - marginY);
      if (Math.random() < 0.25) ny = randomIn(h * 0.55, h * 0.88);
      if (Math.random() < 0.25) ny = randomIn(h * 0.08, h * 0.28);
      if (Math.random() < 0.2) nx = randomIn(marginX, w * 0.35);
      if (Math.random() < 0.2) nx = randomIn(w * 0.55, w - marginX);
      fromX = x; fromY = y; fromScale = scale; toX = nx; toY = ny; toScale = randomIn(0.88, 1.14);
      startT = performance.now();
      const dist = Math.hypot(toX - fromX, toY - fromY);
      const travel = dist * 2.2 + randomIn(200, 800);
      duration = Math.min(4200, Math.max(1400, travel));
    };
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      const stage = stageRef.current, pilot = pilotRef.current;
      if (!stage || !pilot) return;
      const sr = stage.getBoundingClientRect();
      if (sr.width < 10 || sr.height < 10) return;
      if (!ready) {
        x = sr.width * 0.5; y = sr.height * 0.35; fromX = x; fromY = y; toX = x; toY = y; ready = true;
        pickTarget(sr.width, sr.height);
        setStageSize({ w: sr.width, h: sr.height });
      }
      if (Math.abs(sr.width - stageSize.w) > 8 || Math.abs(sr.height - stageSize.h) > 8) setStageSize({ w: sr.width, h: sr.height });
      const t = Math.min(1, (now - startT) / duration);
      const e = easeInOut(t);
      x = fromX + (toX - fromX) * e; y = fromY + (toY - fromY) * e; scale = fromScale + (toScale - fromScale) * e;
      pilot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${scale})`;
      if (t >= 1) pickTarget(sr.width, sr.height);
      if (now - lastSample >= 24) {
        lastSample = now;
        const prev = history.current[0];
        if (!prev || Math.hypot(prev.x - x, prev.y - y) >= 2.5) {
          history.current = [{ x, y }, ...history.current].slice(0, TRAIL_LEN);
          setTrail([...history.current]);
        } else if (history.current.length > 4) {
          history.current = history.current.slice(0, -1);
          setTrail([...history.current]);
        }
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [stageSize.w, stageSize.h]);

  return (
    <div ref={stageRef} className="login-pilot-stage absolute inset-0 overflow-hidden pointer-events-none">
      {trail.map((p, i) => {
        const t = i / Math.max(1, trail.length - 1);
        return <span key={`spark-${i}-${Math.round(p.x)}`} className="login-trail-spark" style={{ left: p.x + ((i % 3) - 1) * 5, top: p.y + ((i % 2) * 3 - 1), opacity: Math.max(0, 0.55 * (1 - t)), width: 2 + (1 - t) * 3, height: 2 + (1 - t) * 3 }} />;
      })}
      <div ref={pilotRef} className="login-pilot login-pilot-js" style={{ left: 0, top: 0, transform: 'translate(-50%, -50%)' }}>
        <NexusLogoMark size={48} />
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
      <div className="login-nebula login-nebula-b" />
      <div className="login-dust" />
      <div className="absolute inset-0">
        {twinkles.map((s) => (
          <span key={`t-${s.id}`} className="absolute rounded-full" style={{ left: s.left, top: s.top, width: s.size, height: s.size, background: s.color, boxShadow: `0 0 ${s.size * 4}px ${s.color}`, animation: `login-twinkle ${s.twinkle}s ease-in-out ${s.delay}s infinite` }} />
        ))}
      </div>
      <div className="absolute inset-0 overflow-hidden">
        {stars.map((s) => (
          <span key={s.id} className="login-star absolute rounded-full" style={{ left: s.left, width: s.size, height: s.size, background: s.color, opacity: s.opacity, boxShadow: `0 0 ${s.size * 4}px ${s.color}`, animationDelay: `${s.delay}s`, animationDuration: `${s.duration}s` }} />
        ))}
      </div>
      <LogoPilotStage />
      <SpaceFlybys />
    </div>
  );
}
