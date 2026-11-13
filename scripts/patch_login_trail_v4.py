#!/usr/bin/env python3
"""LoginPilot trail v4: shorter; taper thick\u2192thin; glow fades to tip; spark particles."""
from pathlib import Path
import re

p = Path("src/components/LoginScene.tsx")
if not p.exists() or p.stat().st_size < 3000:
    print("skip")
    raise SystemExit(0)

s = p.read_text()
if "TRAIL_TAPER_V4" in s:
    print("already v4")
    raise SystemExit(0)

# Shorten trail
s = s.replace("const TRAIL_MAX_DIST = 320;", "const TRAIL_MAX_DIST = 130; // TRAIL_TAPER_V4 short")
s = s.replace("const TRAIL_MAX_DIST = 280;", "const TRAIL_MAX_DIST = 130; // TRAIL_TAPER_V4 short")
s = s.replace("const TRAIL_MAX_DIST = 220;", "const TRAIL_MAX_DIST = 130; // TRAIL_TAPER_V4 short")
if "TRAIL_TAPER_V4" not in s:
    s = s.replace("// TRAIL_ENERGY_V3", "// TRAIL_ENERGY_V3\n// TRAIL_TAPER_V4")

if "trailCanvasRef" not in s:
    s = s.replace(
        "const pathCoreRef = useRef<SVGPathElement>(null);",
        "const pathCoreRef = useRef<SVGPathElement>(null);\n  const trailCanvasRef = useRef<HTMLCanvasElement>(null);",
    )
    print("canvas ref")

old_draw = """      {
        const d = trailPathD(trail);
        const wA = trailPathWavy(trail, 7, 2.2, now * 0.004);
        const wB = trailPathWavy(trail, 5, 3.1, now * 0.004 + 2.1);
        if (pathGlowRef.current) pathGlowRef.current.setAttribute('d', d);
        if (pathSoftRef.current) pathSoftRef.current.setAttribute('d', d);
        if (pathMainRef.current) pathMainRef.current.setAttribute('d', d);
        if (pathWaveARef.current) pathWaveARef.current.setAttribute('d', wA);
        if (pathWaveBRef.current) pathWaveBRef.current.setAttribute('d', wB);
        if (pathCoreRef.current) pathCoreRef.current.setAttribute('d', d);
        const op = 0.35 + 0.65 * trailLenScale;
        if (pathGlowRef.current) pathGlowRef.current.style.opacity = String(0.4 * op);
        if (pathSoftRef.current) pathSoftRef.current.style.opacity = String(0.7 * op);
        if (pathMainRef.current) pathMainRef.current.style.opacity = String(0.95 * op);
        if (pathWaveARef.current) pathWaveARef.current.style.opacity = String(0.55 * op);
        if (pathWaveBRef.current) pathWaveBRef.current.style.opacity = String(0.45 * op);
        if (pathCoreRef.current) pathCoreRef.current.style.opacity = String(op);
      }"""

new_draw = """      {
        // Hide legacy constant-width SVG strokes \u2014 canvas draws tapered trail
        for (const ref of [pathGlowRef, pathSoftRef, pathMainRef, pathWaveARef, pathWaveBRef, pathCoreRef]) {
          if (ref.current) ref.current.setAttribute('d', '');
        }
        const cnv = trailCanvasRef.current;
        const stage = stageRef.current;
        if (cnv && stage && trail.length >= 2) {
          const wr = stage.getBoundingClientRect();
          const dpr = Math.min(window.devicePixelRatio || 1, 2);
          const cw = Math.max(1, Math.floor(wr.width));
          const ch = Math.max(1, Math.floor(wr.height));
          if (cnv.width !== Math.floor(cw * dpr) || cnv.height !== Math.floor(ch * dpr)) {
            cnv.width = Math.floor(cw * dpr);
            cnv.height = Math.floor(ch * dpr);
            cnv.style.width = cw + 'px';
            cnv.style.height = ch + 'px';
          }
          const ctx = cnv.getContext('2d');
          if (ctx) {
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            ctx.clearRect(0, 0, cw, ch);
            const pts = trail; // [0]=pilot head \u2192 tip
            const n = pts.length;
            const baseOp = 0.4 + 0.6 * trailLenScale;
            // Tapered segments: thick near pilot (~logo size), thin at tip
            for (let i = 0; i < n - 1; i++) {
              const t = i / Math.max(1, n - 1); // 0 at pilot, 1 at tip
              const a = pts[i];
              const b = pts[i + 1];
              // width: ~20px at pilot \u2192 ~1.4px at tip
              const w = (20 * (1 - t) * (1 - t) + 1.4) * trailLenScale;
              const alpha = baseOp * (1 - t * 0.85);
              // outer glow
              ctx.beginPath();
              ctx.strokeStyle = `rgba(124, 58, 237, ${0.28 * alpha})`;
              ctx.lineWidth = w * 2.4;
              ctx.lineCap = 'round';
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
              // mid body
              ctx.beginPath();
              ctx.strokeStyle = `rgba(167, 139, 250, ${0.55 * alpha})`;
              ctx.lineWidth = w * 1.25;
              ctx.lineCap = 'round';
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
              // bright core
              ctx.beginPath();
              ctx.strokeStyle = `rgba(245, 208, 254, ${0.9 * alpha})`;
              ctx.lineWidth = Math.max(1, w * 0.45);
              ctx.lineCap = 'round';
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
              // white hot core near pilot
              if (t < 0.35) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(255, 255, 255, ${(0.7 - t) * alpha})`;
                ctx.lineWidth = Math.max(0.8, w * 0.22);
                ctx.lineCap = 'round';
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
              }
            }
            // Spark / energy particles along trail
            for (let i = 1; i < n; i++) {
              const t = i / Math.max(1, n - 1);
              const p = pts[i];
              const prev = pts[i - 1];
              const seg = Math.hypot(p.x - prev.x, p.y - prev.y) || 1;
              const nx = -(p.y - prev.y) / seg;
              const ny = (p.x - prev.x) / seg;
              const pulse = 0.6 + 0.4 * Math.sin(now * 0.008 + i * 1.7);
              const pr = (3.2 * (1 - t) + 0.6) * pulse * trailLenScale;
              const off = Math.sin(now * 0.006 + i * 2.3) * (4 * (1 - t));
              const px = p.x + nx * off;
              const py = p.y + ny * off;
              const pa = baseOp * (1 - t * 0.9) * pulse;
              const g = ctx.createRadialGradient(px, py, 0, px, py, pr * 2.5);
              g.addColorStop(0, `rgba(233, 213, 255, ${0.85 * pa})`);
              g.addColorStop(0.4, `rgba(192, 132, 252, ${0.45 * pa})`);
              g.addColorStop(1, `rgba(124, 58, 237, 0)`);
              ctx.beginPath();
              ctx.fillStyle = g;
              ctx.arc(px, py, pr * 2.5, 0, Math.PI * 2);
              ctx.fill();
              ctx.beginPath();
              ctx.fillStyle = `rgba(255, 255, 255, ${0.7 * pa})`;
              ctx.arc(px, py, Math.max(0.5, pr * 0.35), 0, Math.PI * 2);
              ctx.fill();
            }
            // Extra tip sparks
            if (n > 3) {
              const tip = pts[n - 1];
              for (let k = 0; k < 4; k++) {
                const ang = now * 0.003 + k * 1.6;
                const sp = 3 + k * 1.5;
                const sx = tip.x + Math.cos(ang) * sp;
                const sy = tip.y + Math.sin(ang) * sp;
                ctx.beginPath();
                ctx.fillStyle = `rgba(196, 181, 253, ${0.35 * baseOp})`;
                ctx.arc(sx, sy, 1.1, 0, Math.PI * 2);
                ctx.fill();
              }
            }
          }
        } else if (cnv) {
          const ctx = cnv.getContext('2d');
          if (ctx) ctx.clearRect(0, 0, cnv.width, cnv.height);
        }
      }"""

if old_draw in s:
    s = s.replace(old_draw, new_draw)
    print("tapered canvas draw")
else:
    print("draw block miss")

if 'trailCanvasRef' in s and 'ref={trailCanvasRef}' not in s:
    s = s.replace(
        """      </svg>\n\n      <div ref={enterPortalRef}""",
        """      </svg>\n      <canvas\n        ref={trailCanvasRef}\n        className=\"absolute inset-0 w-full h-full pointer-events-none\"\n        aria-hidden\n      />\n\n      <div ref={enterPortalRef}""",
    )
    print("canvas element")

p.write_text(s)
print("done", len(s), "braces", s.count("{") - s.count("}"), "parens", s.count("(") - s.count(")"))
print("V4", "TRAIL_TAPER_V4" in s, "trailCanvas", "trailCanvasRef" in s)
