"""v4: opaque notifs, flybys complete full pass, login text design."""
from pathlib import Path
import re

fly = Path('src/components/LoginFlybys.tsx')
if fly.exists():
    s = fly.read_text()
    if 'FLYBY_FULLPASS_V4' in s:
        print('flyby fullpass already')
    else:
        m = re.search(
            r"  useEffect\(\(\) => \{\n    let cancelled = false;\n    let timer: ReturnType<typeof setTimeout>;\n\n    const schedule = \(\) => \{.*?\n    timer = setTimeout\(schedule, [^\n]+\);\n    return \(\) => \{\n      cancelled = true;\n      clearTimeout\(timer\);\n    \};\n  \}, \[\]\);",
            s,
            re.S,
        )
        if m:
            new_block = '''  useEffect(() => {
    // FLYBY_FULLPASS_V4 — spawn only when sky is empty; full screen pass
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const spawn = () => {
      if (cancelled) return;
      const id = ++idRef.current;
      const roll = Math.random();
      const kind = (roll < 0.22 ? 'satellite' : roll < 0.5 ? 'ufo' : 'rocket') as FlybyKind;
      const variant =
        kind === 'ufo' ? (Math.random() < 0.55 ? 0 : 1)
        : kind === 'satellite' ? 0
        : Math.floor(Math.random() * ROCKETS.length);
      const top = 10 + Math.random() * 32;
      const duration = kind === 'satellite' ? 28 + Math.random() * 6 : 20 + Math.random() * 6;
      const dir: 'ltr' | 'rtl' = Math.random() < 0.5 ? 'ltr' : 'rtl';
      const chat =
        kind !== 'satellite' && Math.random() < 0.2
          ? CHATS[Math.floor(Math.random() * CHATS.length)]
          : undefined;
      setFlybys([{ id, kind, variant, top, duration, dir, chat }]);
    };

    (window as any).__nexusSpawnFlyby = () => {
      clearTimeout(timer);
      timer = setTimeout(spawn, (10 + Math.random() * 5) * 1000);
    };

    timer = setTimeout(spawn, 3000 + Math.random() * 2000);
    return () => {
      cancelled = true;
      clearTimeout(timer);
      delete (window as any).__nexusSpawnFlyby;
    };
  }, []);'''
            s = s[: m.start()] + new_block + s[m.end() :]
            print('replaced schedule effect')
        else:
            print('schedule effect not matched')

        if 'onAnimEnd' in s and 'FLYBY_FULLPASS_V4_END' not in s:
            s = s.replace(
                '''  const onAnimEnd = (id: number) => {
    setFlybys((prev) => prev.filter((f) => f.id !== id));
    nodeRefs.current.delete(id);
  };''',
                '''  const onAnimEnd = (id: number) => {
    // FLYBY_FULLPASS_V4_END — only remove after full pass, then wait 10–15s
    setFlybys((prev) => prev.filter((f) => f.id !== id));
    nodeRefs.current.delete(id);
    try {
      const spawnNext = (window as any).__nexusSpawnFlyby;
      if (typeof spawnNext === 'function') spawnNext();
    } catch {}
  };''',
                1,
            )
            print('onAnimEnd chains next')

        if "type FlybyKind = 'ufo' | 'rocket';" in s:
            s = s.replace(
                "type FlybyKind = 'ufo' | 'rocket';",
                "type FlybyKind = 'ufo' | 'rocket' | 'satellite'",
                1,
            )
        if 'function SatelliteCraft' not in s and 'const ROCKETS' in s:
            sat = r'''
function SatelliteCraft({ uid }: { uid: string }) {
  return (
    <svg className="login-ship-svg login-sat-svg" width="72" height="36" viewBox="0 0 96 40" fill="none" aria-hidden>
      <defs>
        <linearGradient id={`${uid}-panel`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#e0e7ff" /><stop offset="100%" stopColor="#818cf8" />
        </linearGradient>
        <linearGradient id={`${uid}-body`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f5f3ff" /><stop offset="100%" stopColor="#a5b4fc" />
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
            s = s.replace(
                'const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];',
                sat + 'const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];',
                1,
            )
            print('sat added')
        if "f.kind === 'satellite'" not in s and "f.kind === 'ufo'" in s:
            s = s.replace(
                '''                {f.kind === 'ufo'
                  ? f.variant === 1
                    ? <UfoIon uid={`ufo-${f.id}`} />
                    : <UfoClassic uid={`ufo-${f.id}`} />
                  : <Rocket eid={`rocketFlame-${f.id}`} />}''',
                '''                {f.kind === 'satellite'
                  ? <SatelliteCraft uid={`sat-${f.id}`} />
                  : f.kind === 'ufo'
                    ? f.variant === 1
                      ? <UfoIon uid={`ufo-${f.id}`} />
                      : <UfoClassic uid={`ufo-${f.id}`} />
                    : <Rocket eid={`rocketFlame-${f.id}`} />}''',
                1,
            )
            print('sat render')

        fly.write_text(s)
        print('flybys written')
else:
    print('LoginFlybys missing')

css = Path('src/login-glass.css')
if css.exists():
    t = css.read_text()
    if 'FLYBY_CSS_V4' not in t:
        t = t.rstrip() + '''

/* FLYBY_CSS_V4 — never clip mid-pass */
.login-flybys {
  overflow: visible !important;
  clip-path: none !important;
}
.login-flyby {
  animation-timing-function: linear !important;
  animation-fill-mode: both !important;
}
@keyframes login-flyby-ltr {
  from { transform: translate3d(-180px, 0, 0); opacity: 0; }
  4% { opacity: 1; }
  96% { opacity: 1; }
  to { transform: translate3d(calc(100vw + 180px), 0, 0); opacity: 0; }
}
@keyframes login-flyby-rtl {
  from { transform: translate3d(calc(100vw + 180px), 0, 0); opacity: 0; }
  4% { opacity: 1; }
  96% { opacity: 1; }
  to { transform: translate3d(-180px, 0, 0); opacity: 0; }
}
'''
        print('flyby css v4')

    if 'LOGIN_TEXT_V4' not in t:
        t = t.rstrip() + '''

/* LOGIN_TEXT_V4 — designed typography */
.login-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #e9d5ff;
  margin-bottom: 0.75rem;
}
.login-eyebrow::before {
  content: '';
  width: 18px;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, #c026d3, #818cf8);
  box-shadow: 0 0 10px rgba(192, 38, 211, 0.6);
}
.login-hero-title {
  font-weight: 700 !important;
  letter-spacing: -0.02em !important;
  color: #faf5ff !important;
  text-shadow: 0 0 40px rgba(167, 139, 250, 0.35), 0 1px 0 rgba(0,0,0,0.25) !important;
}
.login-hero-sub {
  display: block;
  margin-top: 0.35rem;
  font-weight: 500 !important;
  background: linear-gradient(105deg, #f5d0fe 0%, #e9d5ff 35%, #a5b4fc 70%, #67e8f9 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 18px rgba(167, 139, 250, 0.25));
}
.login-blurb {
  color: rgba(237, 233, 254, 0.88) !important;
  line-height: 1.65 !important;
}
.login-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 11px;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  color: #f5e9ff !important;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.35), rgba(192, 38, 211, 0.22)) !important;
  border: 1px solid rgba(196, 181, 253, 0.35) !important;
  box-shadow: 0 0 16px rgba(124, 58, 237, 0.2), inset 0 1px 0 rgba(255,255,255,0.08);
  backdrop-filter: blur(8px);
}
.login-cap {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  padding: 0.7rem 0.85rem;
  border-radius: 0.9rem;
  background: linear-gradient(135deg, rgba(30, 16, 55, 0.55), rgba(18, 8, 36, 0.4));
  border: 1px solid rgba(196, 181, 253, 0.18);
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
  transition: border-color 0.2s ease, transform 0.2s ease;
}
.login-cap:hover {
  border-color: rgba(196, 181, 253, 0.35);
  transform: translateY(-1px);
}
.login-cap-index {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.55rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #ede9fe;
  background: linear-gradient(145deg, rgba(124, 58, 237, 0.7), rgba(192, 38, 211, 0.45));
  border: 1px solid rgba(196, 181, 253, 0.35);
  box-shadow: 0 0 14px rgba(124, 58, 237, 0.35);
}
.login-cap-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #faf5ff !important;
}
.login-cap-blurb {
  font-size: 0.75rem;
  color: rgba(221, 214, 254, 0.75) !important;
  margin-top: 0.15rem;
}
'''
        print('login text v4')
    css.write_text(t)
else:
    print('css missing')

lp = Path('src/components/LoginPage.tsx')
if lp.exists():
    s = lp.read_text()
    if 'LOGIN_TEXT_V4' not in s:
        s = s.replace(
            '''              <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-fuchsia-300/80 mb-3">
                {isAgent ? 'Built for agent teams' : 'Built for customers'}
              </p>''',
            '''              <p className="login-eyebrow /* LOGIN_TEXT_V4 */">
                {isAgent ? 'Built for agent teams' : 'Built for customers'}
              </p>''',
            1,
        )
        s = s.replace(
            '''                <span
                  className="block font-normal mt-1 bg-clip-text text-transparent"
                  style={{
                    backgroundImage: 'linear-gradient(105deg, #f5d0fe 0%, #e9d5ff 40%, #c4b5fd 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {leftSub}
                </span>''',
            '''                <span className="login-hero-sub">
                  {leftSub}
                </span>''',
            1,
        )
        s = s.replace(
            'className="mt-4 text-sm sm:text-[15px] text-fuchsia-100/75 leading-relaxed max-w-md"',
            'className="login-blurb mt-4 text-sm sm:text-[15px] leading-relaxed max-w-md"',
            1,
        )
        s = s.replace(
            'className="text-[11px] font-medium px-2.5 py-1 rounded-full border border-white/10 bg-white/5 text-fuchsia-100/85 backdrop-blur-sm"',
            'className="login-chip"',
            1,
        )
        s = s.replace(
            '<div className="text-sm font-medium text-white">{c.title}</div>\n                      <div className="text-xs text-fuchsia-100/65 mt-0.5">{c.blurb}</div>',
            '<div className="login-cap-title">{c.title}</div>\n                      <div className="login-cap-blurb">{c.blurb}</div>',
            1,
        )
        lp.write_text(s)
        print('LoginPage classes')
else:
    print('LoginPage missing')

core = Path('src/SystemAppCore.tsx')
if core.exists():
    s = core.read_text()
    if 'NOTIF_OPAQUE_V4' not in s:
        for old in [
            'className="absolute right-0 top-full mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-600/80 bg-[#0c0a14] shadow-2xl shadow-black/60 z-[90] overflow-hidden /* NOTIF_SOLID_V1 */"',
            'className="absolute right-0 top-full mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-white/15 bg-zinc-950 shadow-2xl z-[90] overflow-hidden"',
        ]:
            if old in s:
                s = s.replace(
                    old,
                    'className="nexus-notif-panel absolute right-0 top-full mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl z-[90] overflow-hidden /* NOTIF_OPAQUE_V4 */"',
                    1,
                )
                print('notif panel class')
                break
        core.write_text(s)

for tm_path in ['src/theme-modes.css', 'src/index.css']:
    tm = Path(tm_path)
    if not tm.exists():
        continue
    c = tm.read_text()
    if 'NOTIF_OPAQUE_V4' in c:
        continue
    tm.write_text(c.rstrip() + '''

/* NOTIF_OPAQUE_V4 */
.nexus-notif-panel {
  background: #0b0912 !important;
  background-color: #0b0912 !important;
  border: 1px solid #3f3a52 !important;
  box-shadow: 0 20px 50px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.06) !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  color: #f4f4f5 !important;
}
.nexus-notif-panel * {
  opacity: 1 !important;
}
.nexus-notif-panel [class*="font-semibold"],
.nexus-notif-panel [class*="font-medium"] {
  color: #fafafa !important;
}
.nexus-notif-panel [class*="text-zinc-300"],
.nexus-notif-panel [class*="text-zinc-400"] {
  color: #d4d4d8 !important;
}
.nexus-notif-panel [class*="text-zinc-500"] {
  color: #a1a1aa !important;
}
.nexus-notif-panel > div:first-child {
  background: #14101f !important;
  border-bottom: 1px solid #3f3a52 !important;
}
''')
    print('opaque css', tm_path)

print('DONE')
