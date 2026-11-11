#!/usr/bin/env python3
"""Ensure LoginScene StarCanvas has fall/drift/sparkle motion."""
from pathlib import Path
import re

p = Path("src/components/LoginScene.tsx")
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
if "mode === 'fall'" in s and "pickMode" in s and "StarCanvas" in s:
    print("star motion already present")
    raise SystemExit(0)

new_star = r'''/** Single canvas starfield — 320 stars, mixed fall / drift / sparkle (GPU-friendly). */
function StarCanvas({ count = 320 }: { count?: number }) {
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

    type Mode = 'fall' | 'drift' | 'sparkle' | 'slow';
    type Star = {
      x: number;
      y: number;
      r: number;
      base: number;
      tw: number;
      phase: number;
      vx: number;
      vy: number;
      mode: Mode;
      color: string;
      glow: boolean;
    };

    const palette = ['#a78bfa', '#c4b5fd', '#67e8f9', '#e9d5ff', '#f9a8d4', '#ffffff', '#f0abfc', '#a5f3fc', '#ddd6fe'];
    let stars: Star[] = [];

    const pickMode = (i: number): Mode => {
      const m = i % 10;
      if (m <= 3) return 'fall';
      if (m <= 6) return 'drift';
      if (m <= 8) return 'slow';
      return 'sparkle';
    };

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
        const layer = i % 5;
        const mode = pickMode(i);
        const r =
          layer === 0
            ? 0.45 + (i % 3) * 0.1
            : layer === 1
              ? 0.7 + (i % 3) * 0.14
              : layer === 2
                ? 1.05 + (i % 4) * 0.18
                : layer === 3
                  ? 1.45 + (i % 3) * 0.22
                  : 1.9 + (i % 4) * 0.28;

        let vx = 0;
        let vy = 0;
        if (mode === 'fall') {
          vx = ((i % 7) - 3) * 0.004;
          vy = 0.035 + (layer + 1) * 0.018 + (i % 5) * 0.006;
        } else if (mode === 'drift') {
          vx = (((i * 17) % 11) - 5) * 0.012;
          vy = (((i * 13) % 9) - 4) * 0.01;
        } else if (mode === 'slow') {
          vx = (((i * 3) % 5) - 2) * 0.003;
          vy = 0.008 + (i % 4) * 0.003;
        }

        return {
          x: (((i * 41 + 9 + layer * 13) % 1000) / 1000) * w,
          y: (((i * 59 + 7 + layer * 19) % 1000) / 1000) * h,
          r,
          base: 0.18 + layer * 0.11 + (i % 4) * 0.04,
          tw: 1.8 + (i % 9) * 0.45,
          phase: (i * 0.41) % (Math.PI * 2),
          vx,
          vy,
          mode,
          color: palette[i % palette.length],
          glow: layer >= 3 || mode === 'sparkle',
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
      const t = dt * 0.06;

      ctx.clearRect(0, 0, w, h);

      for (const s of stars) {
        if (s.mode === 'drift') {
          s.vx += Math.sin(now * 0.0007 + s.phase) * 0.002 * t;
          s.vy += Math.cos(now * 0.0009 + s.phase * 1.3) * 0.002 * t;
          const sp = Math.hypot(s.vx, s.vy);
          if (sp > 0.12) {
            s.vx = (s.vx / sp) * 0.12;
            s.vy = (s.vy / sp) * 0.12;
          }
        }

        s.x += s.vx * dt;
        s.y += s.vy * dt;

        if (s.mode === 'fall' || s.mode === 'slow') {
          if (s.y > h + 6) {
            s.y = -6;
            s.x = Math.random() * w;
          }
          if (s.x < -8) s.x = w + 6;
          if (s.x > w + 8) s.x = -6;
        } else if (s.mode === 'drift') {
          if (s.x < -10) s.x = w + 8;
          if (s.x > w + 10) s.x = -8;
          if (s.y < -10) s.y = h + 8;
          if (s.y > h + 10) s.y = -8;
        }

        const pulse =
          s.mode === 'sparkle'
            ? 0.25 + 0.75 * Math.abs(Math.sin(now * 0.004 * (1 / s.tw) + s.phase))
            : 0.5 + 0.5 * Math.sin(now * 0.0012 * (1 / s.tw) * 5 + s.phase);
        const alpha = Math.max(0.06, Math.min(1, s.base * pulse));

        if (s.glow && s.r > 1.2) {
          ctx.beginPath();
          ctx.fillStyle = s.color;
          ctx.globalAlpha = alpha * 0.25;
          ctx.arc(s.x, s.y, s.r * 2.4, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.beginPath();
        ctx.fillStyle = s.color;
        ctx.globalAlpha = alpha;
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
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
    r'(?:/\*\* Single canvas starfield[\s\S]*?\*/\n)?function StarCanvas[\s\S]*?\n(?=export function CosmicFallBackground)',
    s,
)
if not m:
    print("StarCanvas block not found")
    raise SystemExit(0)
s = s[: m.start()] + new_star + s[m.end() :]
p.write_text(s)
print("star motion patched", p.stat().st_size)
