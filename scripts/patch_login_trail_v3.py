#!/usr/bin/env python3
"""LoginPilot trail v3: thick energy-comet wake (theme colors); shrink on warp, grow after."""
from pathlib import Path
import re

p = Path("src/components/LoginScene.tsx")
if not p.exists() or p.stat().st_size < 3000:
    print("skip")
    raise SystemExit(0)

s = p.read_text()
if "TRAIL_ENERGY_V3" in s:
    print("already v3")
    raise SystemExit(0)

m = re.search(
    r"function trailPathD\(points: TrailPoint\[\]\): string \{[\s\S]*?\n\}\n\nfunction trimTrail\(list: TrailPoint\[\], maxDist: number\): TrailPoint\[\] \{[\s\S]*?\n\}\n",
    s,
)
if m:
    old_helpers = m.group(0)
else:
    old_helpers = None
    print("helpers miss")

new_helpers = r'''function trailPathD(points: TrailPoint[]): string {
  if (points.length < 2) return '';
  const pts = [...points].reverse();
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const c = pts[i];
    const n = pts[i + 1];
    d += ` Q ${c.x.toFixed(1)} ${c.y.toFixed(1)} ${((c.x + n.x) / 2).toFixed(1)} ${((c.y + n.y) / 2).toFixed(1)}`;
  }
  const last = pts[pts.length - 1];
  d += ` L ${last.x.toFixed(1)} ${last.y.toFixed(1)}`;
  return d;
}

/** Wavy energy ribbon — offset perpendicular to path (comet / energy-blast look). */
function trailPathWavy(points: TrailPoint[], amp: number, waves: number, phase: number): string {
  if (points.length < 2) return '';
  const pts = [...points].reverse();
  const out: TrailPoint[] = [];
  let dist = 0;
  out.push(pts[0]);
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1];
    const b = pts[i];
    const seg = Math.hypot(b.x - a.x, b.y - a.y) || 1;
    dist += seg;
    const t = dist / Math.max(1, TRAIL_MAX_DIST);
    const nx = -(b.y - a.y) / seg;
    const ny = (b.x - a.x) / seg;
    const aMul = 0.25 + 0.75 * (1 - t);
    const off = Math.sin(t * Math.PI * waves + phase) * amp * aMul;
    out.push({ x: b.x + nx * off, y: b.y + ny * off });
  }
  return trailPathD(out);
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

'''

if old_helpers:
    s = s.replace(old_helpers, new_helpers)
    print("helpers upgraded")

if "TRAIL_MAX_DIST = 280" in s:
    s = s.replace(
        "const TRAIL_MAX_DIST = 280;\nconst TRAIL_DRIFT = 0.085; // px per ms — wake keeps streaming when pilot pauses",
        "const TRAIL_MAX_DIST = 320;\nconst TRAIL_DRIFT = 0.09; // px per ms — wake keeps streaming when pilot pauses\n// TRAIL_ENERGY_V3",
    )
elif "TRAIL_MAX_DIST = 220" in s:
    s = s.replace(
        "const TRAIL_MAX_DIST = 220;",
        "const TRAIL_MAX_DIST = 320;\nconst TRAIL_DRIFT = 0.09;\n// TRAIL_ENERGY_V3",
    )
elif "TRAIL_ENERGY_V3" not in s:
    s = s.replace("const TRAIL_MAX_DIST", "// TRAIL_ENERGY_V3\nconst TRAIL_MAX_DIST", 1)

if "pathWaveRef" not in s and "pathWaveARef" not in s:
    s = s.replace(
        "const pathGlowRef = useRef<SVGPathElement>(null);",
        "const pathGlowRef = useRef<SVGPathElement>(null);\n  const pathWaveARef = useRef<SVGPathElement>(null);\n  const pathWaveBRef = useRef<SVGPathElement>(null);\n  const pathCoreRef = useRef<SVGPathElement>(null);",
    )
    print("wave refs")

if "trailLenScale" not in s:
    s = s.replace(
        "let trail: TrailPoint[] = [];",
        "let trail: TrailPoint[] = [];\n    let trailLenScale = 1; // 1 full, 0 collapsed (warp)",
    )
    print("trailLenScale")

old_portal_clear = """        if (portalPhase === 'enter' && now >= modeUntil) {
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
        }"""

new_portal_clear = """        if (portalPhase === 'enter' && now >= modeUntil) {
          x = portalExit.x;
          y = portalExit.y;
          // keep a short stub trail at exit so it can grow back
          trail = [{ x, y }, { x: x - Math.cos(heading) * 12, y: y - Math.sin(heading) * 12 }];
          trailLenScale = 0.08;
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
          trailLenScale = 1; // full length again after warp
          pickTarget(sr.width, sr.height);
          exitPortalRef.current?.classList.remove('is-active');
        }"""

if old_portal_clear in s:
    s = s.replace(old_portal_clear, new_portal_clear)
    print("portal shrink/grow")
else:
    print("portal block miss")

old_start = """    const startPortal = (now: number, w: number, h: number) => {
      mode = 'portal';
      portalPhase = 'enter';
      modeUntil = now + 700;
      modeSpeed = 0.2;
      opacityGoal = 0;
      scaleGoal = 0.35;
      lastPortalAt = now;"""

new_start = """    const startPortal = (now: number, w: number, h: number) => {
      mode = 'portal';
      portalPhase = 'enter';
      modeUntil = now + 700;
      modeSpeed = 0.2;
      opacityGoal = 0;
      scaleGoal = 0.35;
      trailLenScale = 0.12; // trail collapses into the warp
      lastPortalAt = now;"""

if old_start in s:
    s = s.replace(old_start, new_start)
    print("startPortal shrink")
else:
    print("startPortal miss")

old_trail_upd = """      // Continuous wake: drift old points away from pilot so trail keeps flowing when paused
      if (mode !== 'portal' && trail.length) {
        const drift = TRAIL_DRIFT * dt;
        const bx = -Math.cos(heading) * drift;
        const by = -Math.sin(heading) * drift;
        for (let i = 0; i < trail.length; i++) {
          trail[i] = { x: trail[i].x + bx, y: trail[i].y + by };
        }
      }
      if (now - lastSample >= SAMPLE_MS && mode !== 'portal') {
        lastSample = now;
        trail = trimTrail([{ x, y }, ...trail], TRAIL_MAX_DIST);
      } else if (mode !== 'portal' && trail.length) {
        // Keep head pinned to pilot every frame while drifting the tail
        trail[0] = { x, y };
      }
      if (mode !== 'portal') {
        const d = trailPathD(trail);
        if (pathMainRef.current) pathMainRef.current.setAttribute('d', d);
        if (pathSoftRef.current) pathSoftRef.current.setAttribute('d', d);
        if (pathGlowRef.current) pathGlowRef.current.setAttribute('d', d);
      }"""

new_trail_upd = """      // TRAIL_ENERGY_V3 — continuous energy wake; shrink/grow with trailLenScale on warp
      if (portalPhase === 'enter') {
        trailLenScale = Math.max(0.05, trailLenScale - dt * 0.0022);
      } else if (portalPhase === 'exit') {
        trailLenScale = Math.min(1, trailLenScale + dt * 0.0018);
      } else if (mode !== 'portal') {
        trailLenScale = Math.min(1, trailLenScale + dt * 0.0025);
      }

      // Drift wake away from pilot (even while paused / during exit grow)
      if (trail.length) {
        const drift = TRAIL_DRIFT * dt * (portalPhase === 'enter' ? 1.6 : 1);
        const bx = -Math.cos(heading) * drift;
        const by = -Math.sin(heading) * drift;
        for (let i = 0; i < trail.length; i++) {
          trail[i] = { x: trail[i].x + bx, y: trail[i].y + by };
        }
      }
      if (now - lastSample >= SAMPLE_MS) {
        lastSample = now;
        const maxD = TRAIL_MAX_DIST * Math.max(0.06, trailLenScale);
        trail = trimTrail([{ x, y }, ...trail], maxD);
      } else if (trail.length) {
        trail[0] = { x, y };
      }

      {
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

if old_trail_upd in s:
    s = s.replace(old_trail_upd, new_trail_upd)
    print("trail update energy")
else:
    print("trail update miss")

old_svg = """        <defs>
          <linearGradient id="loginWakeMain" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#7c3aed" stopOpacity="0" />
            <stop offset="35%" stopColor="#a78bfa" stopOpacity="0.45" />
            <stop offset="75%" stopColor="#e9d5ff" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#faf5ff" stopOpacity="1" />
          </linearGradient>
          <linearGradient id="loginWakeSoft" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#4c1d95" stopOpacity="0" />
            <stop offset="40%" stopColor="#8b5cf6" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#c4b5fd" stopOpacity="0.55" />
          </linearGradient>
          <filter id="loginTrailBlur" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="3.4" />
          </filter>
          <filter id="loginTrailBloom" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path ref={pathGlowRef} d="" fill="none" stroke="#a78bfa" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailBlur)" opacity="0.35" className="login-light-trail" />
        <path ref={pathSoftRef} d="" fill="none" stroke="#c4b5fd" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" className="login-light-trail" />
        <path ref={pathMainRef} d="" fill="none" stroke="#f5d0fe" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailBloom)" opacity="0.95" className="login-light-trail" />
      </svg>"""

old_svg_v1 = """        <defs>
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
        <path ref={pathGlowRef} d="" fill="none" stroke="url(#loginWakeSoft)" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailBlur)" opacity="0.55" className="login-light-trail" />
        <path ref={pathSoftRef} d="" fill="none" stroke="url(#loginWakeSoft)" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.7" className="login-light-trail" />
        <path ref={pathMainRef} d="" fill="none" stroke="url(#loginWakeMain)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" opacity="0.95" className="login-light-trail" />
      </svg>"""

new_svg = """        <defs>
          <filter id="loginTrailBlur" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="6" />
          </filter>
          <filter id="loginTrailBloom" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="4.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="loginTrailSoft" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2.2" />
          </filter>
        </defs>
        {/* Energy comet layers — violet/fuchsia theme (ref: glowing energy trails) */}
        <path ref={pathGlowRef} d="" fill="none" stroke="#7c3aed" strokeWidth="22" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailBlur)" opacity="0.4" className="login-light-trail" />
        <path ref={pathSoftRef} d="" fill="none" stroke="#a78bfa" strokeWidth="11" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailSoft)" opacity="0.55" className="login-light-trail" />
        <path ref={pathWaveARef} d="" fill="none" stroke="#e879f9" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" className="login-light-trail" />
        <path ref={pathWaveBRef} d="" fill="none" stroke="#c4b5fd" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" opacity="0.45" className="login-light-trail" />
        <path ref={pathMainRef} d="" fill="none" stroke="#f5d0fe" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailBloom)" opacity="0.9" className="login-light-trail" />
        <path ref={pathCoreRef} d="" fill="none" stroke="#ffffff" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" opacity="0.95" className="login-light-trail" />
      </svg>"""

if old_svg in s:
    s = s.replace(old_svg, new_svg)
    print("svg energy layers")
elif old_svg_v1 in s:
    s = s.replace(old_svg_v1, new_svg)
    print("svg energy layers from v1")
else:
    print("svg miss")

p.write_text(s)
print("done", len(s), "braces", s.count("{") - s.count("}"), "parens", s.count("(") - s.count(")"))
print("V3", "TRAIL_ENERGY_V3" in s, "pathWaveARef", "pathWaveARef" in s, "trailLenScale", "trailLenScale" in s)
