#!/usr/bin/env python3
"""Login: pure slow top→bottom stars; continuous pilot trail (keeps flowing when paused); no planets."""
from pathlib import Path
import re

p = Path("src/components/LoginScene.tsx")
if not p.exists() or p.stat().st_size < 2000:
    print("LoginScene skip")
    raise SystemExit(0)

s = p.read_text()
# Fix accidental literal \\n from prior bad edit
s = s.replace("phase: (i * 0.41) % (Math.PI * 2),\\n          speed:", "phase: (i * 0.41) % (Math.PI * 2),\n          speed:")
s = s.replace("phase: (i * 0.41) % (Math.PI * 2),\\n", "phase: (i * 0.41) % (Math.PI * 2),\n")

# --- Remove planets from CosmicFallBackground ---
s = re.sub(
    r'\s*<DistantPlanet className="login-planet login-planet-[abc]"[^/]*/>\s*',
    "\n",
    s,
)

# --- StarCanvas: slower pure vertical fall ---
s = s.replace(
    "speed: layer <= 1 ? 0.012 : layer === 2 ? 0.02 : 0.035,",
    "speed: layer <= 1 ? 0.004 : layer === 2 ? 0.007 : layer === 3 ? 0.011 : 0.016,",
)
s = s.replace(
    "speed: layer <= 1 ? 0.007 : layer === 2 ? 0.012 : 0.02,",
    "speed: layer <= 1 ? 0.004 : layer === 2 ? 0.007 : layer === 3 ? 0.011 : 0.016,",
)
for old_mul in ("0.06", "0.035", "0.04", "0.05"):
    s = s.replace(
        f"s.y += s.speed * dt * {old_mul};",
        "s.y += s.speed * dt * 0.022; // pure top\u2192bottom, slow drift",
    )
s = re.sub(r"\s*s\.x \+= [^;]+;\n", "\n", s)

# --- Trail: continuous flow even when pilot pauses ---
if "TRAIL_DRIFT" not in s:
    s = s.replace(
        "const TRAIL_MAX_DIST = 220;",
        "const TRAIL_MAX_DIST = 280;\nconst TRAIL_DRIFT = 0.085; // px per ms — wake keeps streaming when pilot pauses",
    )
if "SAMPLE_MS = 32" in s:
    s = s.replace("const SAMPLE_MS = 32;", "const SAMPLE_MS = 24;")

old_trail_path = '''function trailPathD(points: TrailPoint[]): string {
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
}'''

new_trail_path = '''function trailPathD(points: TrailPoint[]): string {
  if (points.length < 2) return '';
  // points[0] is pilot (head); draw from tail → head so gradient reads as a comet
  const pts = [...points].reverse();
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const c = pts[i];
    const n = pts[i + 1];
    const mx = (c.x + n.x) / 2;
    const my = (c.y + n.y) / 2;
    d += ` Q ${c.x.toFixed(1)} ${c.y.toFixed(1)} ${mx.toFixed(1)} ${my.toFixed(1)}`;
  }
  const last = pts[pts.length - 1];
  d += ` L ${last.x.toFixed(1)} ${last.y.toFixed(1)}`;
  return d;
}'''

if old_trail_path in s:
    s = s.replace(old_trail_path, new_trail_path)
    print("trailPathD upgraded")
else:
    print("trailPathD pattern miss — keep existing")

old_trail_block = '''      if (now - lastSample >= SAMPLE_MS && mode !== 'portal') {
        lastSample = now;
        trail = trimTrail([{ x, y }, ...trail], TRAIL_MAX_DIST);
        const d = trailPathD(trail);
        if (pathMainRef.current) pathMainRef.current.setAttribute('d', d);
        if (pathSoftRef.current) pathSoftRef.current.setAttribute('d', d);
        if (pathGlowRef.current) pathGlowRef.current.setAttribute('d', d);
      }'''

new_trail_block = '''      // Continuous wake: drift old points away from pilot so trail keeps flowing when paused
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
      }'''

if old_trail_block in s:
    s = s.replace(old_trail_block, new_trail_block)
    print("trail continuous flow")
else:
    print("trail block miss")

old_defs = '''        <defs>
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
        <path ref={pathMainRef} d="" fill="none" stroke="url(#loginWakeMain)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" opacity="0.95" className="login-light-trail" />'''

new_defs = '''        <defs>
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
        <path ref={pathMainRef} d="" fill="none" stroke="#f5d0fe" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" filter="url(#loginTrailBloom)" opacity="0.95" className="login-light-trail" />'''

if old_defs in s:
    s = s.replace(old_defs, new_defs)
    print("trail style upgraded")
else:
    print("trail defs miss")

p.write_text(s)
print("done LoginScene", len(s), "planets", "login-planet-a" in s, "TRAIL_DRIFT", "TRAIL_DRIFT" in s)
print("braces", s.count("{") - s.count("}"), "parens", s.count("(") - s.count(")"))
