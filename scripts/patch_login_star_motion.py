#!/usr/bin/env python3
"""Login StarCanvas: slow but VISIBLE pure top\u2192bottom stars only. No sideways drift."""
from pathlib import Path
import re

p = Path("src/components/LoginScene.tsx")
if not p.exists() or p.stat().st_size < 2000:
    raise SystemExit(0)

s = p.read_text()

new_star = r'''/** Single canvas starfield \u2014 slow pure top\u2192bottom (visible drift, no sideways). */
function StarCanvas({ count = 220 }: { count?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    let raf = 0;
    let w = 0;
    let h = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    type Star = {
      x: number;
      y: number;
      r: number;
      base: number;
      tw: number;
      phase: number;
      speed: number;
      color: string;
    };

    const palette = ['#a78bfa', '#c4b5fd', '#e9d5ff', '#ffffff', '#f0abfc', '#ddd6fe', '#f5d0fe', '#a5b4fc'];
    let stars: Star[] = [];

    const resize = () => {
      const parent = canvas.parentElement;
      w = parent?.clientWidth || window.innerWidth;
      h = parent?.clientHeight || window.innerHeight;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      stars = Array.from({ length: count }, (_, i) => {
        const layer = i % 4;
        const r =
          layer === 0
            ? 0.45 + (i % 3) * 0.12
            : layer === 1
              ? 0.7 + (i % 3) * 0.15
              : layer === 2
                ? 1.05 + (i % 4) * 0.18
                : 1.5 + (i % 3) * 0.25;
        // px per ms \u2014 crosses ~1080px screen in ~25\u201355s (slow but obvious)
        const speed =
          layer === 0 ? 0.014 : layer === 1 ? 0.022 : layer === 2 ? 0.032 : 0.045;
        return {
          x: (((i * 47 + 13 + layer * 19) % 1000) / 1000) * w,
          y: (((i * 59 + 7 + layer * 23) % 1000) / 1000) * h,
          r,
          base: 0.25 + layer * 0.12 + (i % 4) * 0.05,
          tw: 3.2 + (i % 7) * 0.7,
          phase: (i * 0.41) % (Math.PI * 2),
          speed,
          color: palette[i % palette.length],
        };
      });
    };

    resize();
    const onResize = () => resize();
    window.addEventListener('resize', onResize);

    let last = performance.now();
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      if (document.visibilityState === 'hidden') return;
      const dt = Math.min(40, now - last);
      last = now;
      ctx.clearRect(0, 0, w, h);
      for (const st of stars) {
        // Pure vertical only
        st.y += st.speed * dt;
        if (st.y > h + 4) {
          st.y = -4;
          st.x = Math.random() * w;
        }
        const pulse = 0.55 + 0.45 * Math.sin(now * 0.001 * (1 / st.tw) * 5 + st.phase);
        const alpha = Math.max(0.1, Math.min(1, st.base * pulse));
        ctx.beginPath();
        ctx.fillStyle = st.color;
        ctx.globalAlpha = alpha;
        ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    };

    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
    };
  }, [count]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      aria-hidden
    />
  );
}

'''

m = re.search(
    r'(?:/\*\*[^*]*\*/\n)?(?:// STARS_V5_PURE\n)?function StarCanvas[\s\S]*?\n(?=export function CosmicFallBackground)',
    s,
)
if not m:
    print("StarCanvas block not found")
    raise SystemExit(0)
s = s[: m.start()] + new_star + s[m.end() :]

s = re.sub(r'\s*<div className="login-dust[^"]*"\s*/>\s*', "\n", s)

s = s.replace('<StarCanvas count={320} />', '<StarCanvas count={220} />')
s = s.replace('<StarCanvas count={280} />', '<StarCanvas count={220} />')
s = s.replace('<StarCanvas count={180} />', '<StarCanvas count={220} />')

p.write_text(s)
print("visible slow stars", len(s), "braces", s.count("{") - s.count("}"))
