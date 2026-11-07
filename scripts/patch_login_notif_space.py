"""Solid notif panel + richer login + calmer flybys (1 every 10-15s) + satellite."""
from pathlib import Path
import re

core = Path('src/SystemAppCore.tsx')
if core.exists():
    s = core.read_text()
    if 'NOTIF_SOLID_V1' not in s:
        s = s.replace(
            'className="absolute right-0 top-full mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-white/15 bg-zinc-950 shadow-2xl z-[90] overflow-hidden"',
            'className="absolute right-0 top-full mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-600/80 bg-[#0c0a14] shadow-2xl shadow-black/60 z-[90] overflow-hidden /* NOTIF_SOLID_V1 */"',
            1,
        )
        s = s.replace('bg-zinc-950 shadow-2xl z-[90]', 'bg-[#0c0a14] shadow-2xl shadow-black/70 z-[90] /* NOTIF_SOLID_V1 */', 1)
        s = s.replace(
            'className="flex items-center justify-between px-3 py-2.5 border-b border-white/10"',
            'className="flex items-center justify-between px-3 py-2.5 border-b border-white/15 bg-[#14101f]"',
            1,
        )
        s = s.replace('text-sm font-medium text-zinc-100 truncate', 'text-sm font-semibold text-white truncate')
        s = s.replace('text-[11px] text-zinc-400 line-clamp-2 mt-0.5', 'text-[11px] text-zinc-300 line-clamp-2 mt-0.5')
        s = s.replace('px-3 py-6 text-center text-xs text-zinc-500', 'px-3 py-6 text-center text-xs text-zinc-400')
        core.write_text(s)
        print('notif solid')
    else:
        print('notif already')

fly = Path('src/components/LoginFlybys.tsx')
if fly.exists():
    s = fly.read_text()
    if 'FLYBY_CALM_V1' in s:
        print('flyby already')
    else:
        s = s.replace("type FlybyKind = 'ufo' | 'rocket';", "type FlybyKind = 'ufo' | 'rocket' | 'satellite'; // FLYBY_CALM_V1", 1)
        sat = r'''
function SatelliteCraft({ uid }: { uid: string }) {
  return (
    <svg className="login-ship-svg login-sat-svg" width="72" height="36" viewBox="0 0 96 40" fill="none" aria-hidden>
      <defs>
        <linearGradient id={`${uid}-panel`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#e0e7ff" />
          <stop offset="100%" stopColor="#818cf8" />
        </linearGradient>
        <linearGradient id={`${uid}-body`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f5f3ff" />
          <stop offset="100%" stopColor="#a5b4fc" />
        </linearGradient>
      </defs>
      <rect x="4" y="14" width="22" height="12" rx="1.5" fill={`url(#${uid}-panel)`} stroke="#c7d2fe" strokeWidth="0.8" />
      <rect x="70" y="14" width="22" height="12" rx="1.5" fill={`url(#${uid}-panel)`} stroke="#c7d2fe" strokeWidth="0.8" />
      <rect x="26" y="18.5" width="12" height="3" rx="1" fill="#a5b4fc" />
      <rect x="58" y="18.5" width="12" height="3" rx="1" fill="#a5b4fc" />
      <rect x="38" y="12" width="20" height="16" rx="3" fill={`url(#${uid}-body)`} stroke="#e0e7ff" strokeWidth="0.9" />
      <circle cx="48" cy="20" r="4" fill="#22d3ee" stroke="#0891b2" strokeWidth="0.8" />
      <circle cx="48" cy="20" r="1.6" fill="#ecfeff" className="login-sat-blink" />
      <line x1="48" y1="12" x2="48" y2="4" stroke="#c4b5fd" strokeWidth="1.2" />
      <circle cx="48" cy="3" r="2" fill="#f0abfc" className="login-sat-blink" />
    </svg>
  );
}

'''
        if 'function SatelliteCraft' not in s:
            s = s.replace(
                'const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];',
                sat + 'const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];',
                1,
            )
        old_sched = '''    const schedule = () => {
      if (cancelled) return;
      const id = ++idRef.current;
      const isUfo = Math.random() < 0.32;
      const kind: FlybyKind = isUfo ? 'ufo' : 'rocket';
      const variant = isUfo ? (Math.random() < 0.55 ? 0 : 1) : Math.floor(Math.random() * ROCKETS.length);
      const top = 5 + Math.random() * 42;
      const duration = 16 + Math.random() * 10;
      const dir: 'ltr' | 'rtl' = Math.random() < 0.5 ? 'ltr' : 'rtl';
      const chat = Math.random() < 0.28 ? CHATS[Math.floor(Math.random() * CHATS.length)] : undefined;
      // Keep at most 3 craft on screen so the sky stays calm
      setFlybys((prev) => [...prev.slice(-2), { id, kind, variant, top, duration, dir, chat }]);
      // Longer gaps = fewer flybys
      const gaps = [16, 22, 28, 34, 42];
      timer = setTimeout(schedule, gaps[Math.floor(Math.random() * gaps.length)] * 1000);
    };

    timer = setTimeout(schedule, 2200 + Math.random() * 1800);'''
        new_sched = '''    const schedule = () => {
      if (cancelled) return;
      const id = ++idRef.current;
      // FLYBY_CALM_V1 — one craft at a time
      const roll = Math.random();
      const kind: FlybyKind = roll < 0.22 ? 'satellite' : roll < 0.48 ? 'ufo' : 'rocket';
      const variant =
        kind === 'ufo' ? (Math.random() < 0.55 ? 0 : 1)
        : kind === 'satellite' ? 0
        : Math.floor(Math.random() * ROCKETS.length);
      const top = 8 + Math.random() * 36;
      const duration = kind === 'satellite' ? 22 + Math.random() * 8 : 14 + Math.random() * 8;
      const dir: 'ltr' | 'rtl' = Math.random() < 0.5 ? 'ltr' : 'rtl';
      const chat = kind !== 'satellite' && Math.random() < 0.22
        ? CHATS[Math.floor(Math.random() * CHATS.length)]
        : undefined;
      setFlybys([{ id, kind, variant, top, duration, dir, chat }]);
      const gaps = [10, 11, 12, 13, 14, 15];
      timer = setTimeout(schedule, gaps[Math.floor(Math.random() * gaps.length)] * 1000);
    };

    timer = setTimeout(schedule, 3500 + Math.random() * 2500);'''
        if old_sched in s:
            s = s.replace(old_sched, new_sched, 1)
        else:
            s = s.replace(
                'setFlybys((prev) => [...prev.slice(-2), { id, kind, variant, top, duration, dir, chat }]);',
                'setFlybys([{ id, kind, variant, top, duration, dir, chat }]); // FLYBY_CALM_V1',
                1,
            )
            s = s.replace('const gaps = [16, 22, 28, 34, 42];', 'const gaps = [10, 11, 12, 13, 14, 15]; // FLYBY_CALM_V1', 1)
        old_r = '''                {f.kind === 'ufo'
                  ? f.variant === 1
                    ? <UfoIon uid={`ufo-${f.id}`} />
                    : <UfoClassic uid={`ufo-${f.id}`} />
                  : <Rocket eid={`rocketFlame-${f.id}`} />}'''
        new_r = '''                {f.kind === 'satellite'
                  ? <SatelliteCraft uid={`sat-${f.id}`} />
                  : f.kind === 'ufo'
                    ? f.variant === 1
                      ? <UfoIon uid={`ufo-${f.id}`} />
                      : <UfoClassic uid={`ufo-${f.id}`} />
                    : <Rocket eid={`rocketFlame-${f.id}`} />}'''
        if old_r in s:
            s = s.replace(old_r, new_r, 1)
        fly.write_text(s)
        print('flybys updated')
else:
    print('LoginFlybys missing')

css = Path('src/login-glass.css')
if css.exists():
    t = css.read_text()
    if 'LOGIN_DESIGN_V2' not in t:
        t = t.replace(
            '''.login-glass-card {
  position: relative; z-index: 30 !important;
  background: linear-gradient(160deg, rgba(28, 14, 55, 0.28) 0%, rgba(18, 8, 40, 0.32) 100%) !important;
  border: 1px solid rgba(196, 181, 253, 0.22) !important;
  box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.08), 0 20px 40px -14px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(18px) saturate(1.2) !important;
  -webkit-backdrop-filter: blur(18px) saturate(1.2) !important;
  animation: login-card-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}''',
            '''.login-glass-card {
  /* LOGIN_DESIGN_V2 */
  position: relative; z-index: 30 !important;
  background:
    radial-gradient(120% 80% at 10% -10%, rgba(167, 139, 250, 0.22), transparent 55%),
    radial-gradient(90% 70% at 110% 20%, rgba(236, 72, 153, 0.14), transparent 50%),
    linear-gradient(165deg, rgba(32, 16, 62, 0.82) 0%, rgba(14, 8, 32, 0.88) 100%) !important;
  border: 1px solid rgba(196, 181, 253, 0.32) !important;
  box-shadow:
    0 0 0 1px rgba(139, 92, 246, 0.12),
    0 24px 48px -12px rgba(0, 0, 0, 0.55),
    0 0 60px -20px rgba(124, 58, 237, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(22px) saturate(1.35) !important;
  -webkit-backdrop-filter: blur(22px) saturate(1.35) !important;
  animation: login-card-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.login-glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 40%, transparent 60%, rgba(167,139,250,0.06) 100%);
}''',
            1,
        )
        t = t.rstrip() + '''

/* LOGIN_DESIGN_V2 extras */
.login-sat-blink { animation: login-sat-pulse 2.4s ease-in-out infinite; }
@keyframes login-sat-pulse { 0%, 100% { opacity: 0.55; } 50% { opacity: 1; } }
.login-sat-svg { filter: drop-shadow(0 0 8px rgba(34, 211, 238, 0.35)); }
.login-hero-title { text-shadow: 0 0 40px rgba(167, 139, 250, 0.25); }
.login-brand-badge { box-shadow: 0 0 24px rgba(167, 139, 250, 0.35); }
.login-submit-btn { position: relative; overflow: hidden; }
.login-submit-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.18) 50%, transparent 60%);
  transform: translateX(-120%);
  animation: login-btn-sheen 4.5s ease-in-out infinite;
}
@keyframes login-btn-sheen {
  0%, 55% { transform: translateX(-120%); }
  75%, 100% { transform: translateX(120%); }
}
.login-glass-input {
  background: rgba(10, 6, 24, 0.65) !important;
  border: 1px solid rgba(196, 181, 253, 0.22) !important;
  color: #f5f3ff !important;
}
.login-glass-input:focus {
  border-color: rgba(167, 139, 250, 0.55) !important;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.22) !important;
}
'''
        css.write_text(t)
        print('login design')
    else:
        print('login design already')
else:
    print('login-glass missing')

tm = Path('src/theme-modes.css')
if tm.exists() and 'NOTIF_SOLID_CSS_V1' not in tm.read_text():
    tm.write_text(tm.read_text().rstrip() + '''

/* NOTIF_SOLID_CSS_V1 */
.app-cosmos .nexus-topbar [class*="w-80"] {
  background: #0c0a14 !important;
  border: 1px solid rgba(113,113,122,0.75) !important;
  box-shadow: 0 16px 40px rgba(0,0,0,0.6) !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
}
''')
    print('theme notif css')

print('DONE')
