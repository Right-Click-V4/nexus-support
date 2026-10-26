import { useMemo } from 'react';
import '../portal-lounge.css';

type Star = {
  left: string;
  top: string;
  size: number;
  delay: number;
  dur: number;
  color: string;
  opacity: number;
  glow: number;
};

type Drift = {
  left: string;
  top: string;
  size: number;
  delay: number;
  dur: number;
  dx: string;
  dy: string;
  color: string;
};

function makeStars(count: number, seed: number): Star[] {
  const colors = [
    '#ffffff',
    '#e9d5ff',
    '#c4b5fd',
    '#f0abfc',
    '#a5f3fc',
    '#67e8f9',
    '#ddd6fe',
    '#f5d0fe',
    '#bfdbfe',
  ];
  const stars: Star[] = [];
  let s = seed;
  const rnd = () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
  for (let i = 0; i < count; i++) {
    const bright = i % 8 === 0;
    stars.push({
      left: `${rnd() * 100}%`,
      top: `${rnd() * 100}%`,
      size: bright ? 1.6 + rnd() * 2.2 : 0.4 + rnd() * 1.3,
      delay: rnd() * 12,
      dur: 1.8 + rnd() * 5,
      color: colors[i % colors.length],
      opacity: 0.3 + rnd() * 0.7,
      glow: bright ? 6 + rnd() * 8 : 1.5 + rnd() * 3.5,
    });
  }
  return stars;
}

function makeDrift(count: number, seed: number): Drift[] {
  const colors = ['#ffffff', '#e9d5ff', '#c4b5fd', '#67e8f9', '#a5f3fc', '#f0abfc', '#ddd6fe'];
  const out: Drift[] = [];
  let s = seed;
  const rnd = () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
  for (let i = 0; i < count; i++) {
    const angle = rnd() * Math.PI * 2;
    const dist = 40 + rnd() * 120;
    out.push({
      left: `${rnd() * 100}%`,
      top: `${rnd() * 100}%`,
      size: 0.6 + rnd() * 2.0,
      delay: rnd() * 22,
      dur: 14 + rnd() * 28,
      dx: `${Math.cos(angle) * dist}px`,
      dy: `${Math.sin(angle) * dist}px`,
      color: colors[i % colors.length],
    });
  }
  return out;
}

/** Dense galaxy sky — twinkling stars + random drifting particles (no comets). */
export default function PortalSpaceLoungeBg() {
  const stars = useMemo(() => makeStars(280, 42), []);
  const drifts = useMemo(() => makeDrift(90, 91), []);

  return (
    <div className="portal-cosmic" aria-hidden>
      <div className="portal-cosmic-sky" />

      <div className="portal-nebula-wash portal-nebula-wash-a" />
      <div className="portal-nebula-wash portal-nebula-wash-b" />
      <div className="portal-nebula-wash portal-nebula-wash-c" />

      <div className="portal-cosmic-stars">
        {stars.map((st, i) => (
          <span
            key={`s${i}`}
            className="portal-cosmic-star"
            style={{
              left: st.left,
              top: st.top,
              width: st.size,
              height: st.size,
              background: st.color,
              opacity: st.opacity,
              boxShadow: `0 0 ${st.glow}px ${st.color}`,
              animationDelay: `${st.delay}s`,
              animationDuration: `${st.dur}s`,
            }}
          />
        ))}
      </div>

      <div className="portal-drift-layer">
        {drifts.map((d, i) => (
          <span
            key={`d${i}`}
            className="portal-drift-particle"
            style={{
              left: d.left,
              top: d.top,
              width: d.size,
              height: d.size,
              background: d.color,
              boxShadow: `0 0 ${d.size * 3}px ${d.color}`,
              animationDelay: `${d.delay}s`,
              animationDuration: `${d.dur}s`,
              ['--dx' as string]: d.dx,
              ['--dy' as string]: d.dy,
            }}
          />
        ))}
      </div>

      <div className="portal-cosmic-veil" />
    </div>
  );
}
