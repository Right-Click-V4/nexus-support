"""Dish satellite, accurate maintenance/404 modes, more login features, remove chips."""
from pathlib import Path
import re

fly = Path('src/components/LoginFlybys.tsx')
if fly.exists():
    s = fly.read_text()
    dish = r'''
function SatelliteCraft({ uid }: { uid: string }) {
  /* DISH_SAT_V1 — classic satellite with solar panels + dish antenna */
  return (
    <svg className="login-ship-svg login-sat-svg" width="88" height="56" viewBox="0 0 120 72" fill="none" aria-hidden>
      <defs>
        <linearGradient id={`${uid}-panel`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#dbeafe" />
          <stop offset="100%" stopColor="#3b82f6" />
        </linearGradient>
        <linearGradient id={`${uid}-body`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f8fafc" />
          <stop offset="100%" stopColor="#94a3b8" />
        </linearGradient>
        <linearGradient id={`${uid}-dish`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fbbf24" />
          <stop offset="55%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
        <radialGradient id={`${uid}-dish-inner`} cx="50%" cy="45%" r="55%">
          <stop offset="0%" stopColor="#fef3c7" />
          <stop offset="70%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#b45309" />
        </radialGradient>
      </defs>
      <g transform="translate(2 22)">
        <rect x="0" y="0" width="28" height="20" rx="2" fill={`url(#${uid}-panel)`} stroke="#1e40af" strokeWidth="1" />
        <line x1="7" y1="1" x2="7" y2="19" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="14" y1="1" x2="14" y2="19" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="21" y1="1" x2="21" y2="19" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="1" y1="7" x2="27" y2="7" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.45" />
        <line x1="1" y1="13" x2="27" y2="13" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.45" />
      </g>
      <g transform="translate(90 22)">
        <rect x="0" y="0" width="28" height="20" rx="2" fill={`url(#${uid}-panel)`} stroke="#1e40af" strokeWidth="1" />
        <line x1="7" y1="1" x2="7" y2="19" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="14" y1="1" x2="14" y2="19" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="21" y1="1" x2="21" y2="19" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="1" y1="7" x2="27" y2="7" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.45" />
        <line x1="1" y1="13" x2="27" y2="13" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.45" />
      </g>
      <rect x="30" y="30" width="12" height="4" rx="1" fill="#cbd5e1" />
      <rect x="78" y="30" width="12" height="4" rx="1" fill="#cbd5e1" />
      <rect x="42" y="24" width="20" height="18" rx="3" fill={`url(#${uid}-body)`} stroke="#e2e8f0" strokeWidth="1" />
      <rect x="46" y="28" width="12" height="4" rx="1" fill="#64748b" opacity="0.5" />
      <rect x="49" y="12" width="6" height="14" rx="1.5" fill="#94a3b8" />
      <ellipse cx="52" cy="14" rx="16" ry="12" fill={`url(#${uid}-dish)`} stroke="#b45309" strokeWidth="1.2" />
      <ellipse cx="52" cy="14" rx="11" ry="8" fill={`url(#${uid}-dish-inner)`} opacity="0.95" />
      <path d="M52 14 L46 20 L58 20 Z" fill="#fde68a" stroke="#d97706" strokeWidth="0.8" />
      <circle cx="52" cy="14" r="2.2" fill="#fff7ed" className="login-sat-blink" />
      <line x1="52" y1="2" x2="52" y2="8" stroke="#fcd34d" strokeWidth="1.4" />
      <circle cx="52" cy="2" r="2" fill="#fef3c7" className="login-sat-blink" />
    </svg>
  );
}
'''
    if 'function SatelliteCraft' in s:
        s2 = re.sub(
            r'function SatelliteCraft\(\{ uid \}: \{ uid: string \}\) \{.*?\n\}',
            dish.strip(),
            s,
            count=1,
            flags=re.S,
        )
        if s2 != s:
            s = s2
            print('replaced SatelliteCraft with dish')
        else:
            print('sat replace failed')
    elif 'const ROCKETS' in s:
        s = s.replace(
            'const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];',
            dish + 'const ROCKETS = [RocketClassic, RocketViolet, RocketOrange, RocketTeal, RocketBullet];',
            1,
        )
        print('inserted dish sat')
    if "type FlybyKind = 'ufo' | 'rocket';" in s:
        s = s.replace("type FlybyKind = 'ufo' | 'rocket';", "type FlybyKind = 'ufo' | 'rocket' | 'satellite'", 1)
    fly.write_text(s)
    print('flybys sat ok')
else:
    print('LoginFlybys missing')

core = Path('src/SystemAppCore.tsx')
if core.exists():
    s = core.read_text()
    if "type ReactNode" not in s and "from 'react'" in s:
        s = s.replace(
            "import { useEffect, useRef, useState } from 'react';",
            "import { useEffect, useRef, useState, type ReactNode } from 'react';",
            1,
        )
        s = s.replace('React.ReactNode', 'ReactNode')
    if 'MODE_GATES_V1' not in s:
        if 'MaintenanceScreen' not in s:
            s = s.replace(
                "import NotFoundScreen from './components/NotFoundScreen';",
                "import NotFoundScreen from './components/NotFoundScreen';\nimport MaintenanceScreen from './components/MaintenanceScreen';",
                1,
            )
        old_root = '''export function Root() {
  const [mode, setMode] = useState(() => getModeFromHash());
  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  return (
    <TicketProvider>
      <PlatformProvider>
        {mode === 'portal' ? <PortalShell /> : mode === 'notfound' ? <NotFoundScreen /> : <AgentShell />}
      </PlatformProvider>
    </TicketProvider>
  );
}'''
        new_root = '''export function Root() {
  // MODE_GATES_V1 — maintenance / 404 apply to everyone except admins
  const [mode, setMode] = useState(() => getModeFromHash());
  const { enabled: maintenanceOn, ready: maintenanceReady } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const { user, loading: authLoading } = useAuth();

  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const goAdminLogin = () => {
    window.location.hash = '';
  };

  const modesReady = maintenanceReady && site404Ready && (adminReady || !user);
  const blockPublic = modesReady && !isAdmin;

  let locked: ReactNode | null = null;
  if (blockPublic && site404On) {
    locked = <NotFoundScreen onAdminSignIn={goAdminLogin} />;
  } else if (blockPublic && maintenanceOn) {
    locked = <MaintenanceScreen onAdminSignIn={goAdminLogin} />;
  }

  return (
    <TicketProvider>
      <PlatformProvider>
        {locked
          ? locked
          : mode === 'portal'
            ? <PortalShell />
            : mode === 'notfound'
              ? <NotFoundScreen onAdminSignIn={goAdminLogin} />
              : <AgentShell />}
      </PlatformProvider>
    </TicketProvider>
  );
}'''
        if old_root in s:
            s = s.replace(old_root, new_root, 1)
            print('Root mode gates')
        else:
            print('Root block not exact')

        s = s.replace(
            '''  if (maintenanceReady && maintenanceOn && !isAdmin) {
    return <BootLoader label="Maintenance" />;
  }''',
            '''  if (maintenanceReady && maintenanceOn && !isAdmin) {
    return <MaintenanceScreen onAdminSignIn={() => { window.location.hash = ''; }} />;
  }
  if (site404Ready && site404On && !isAdmin) {
    return <NotFoundScreen onAdminSignIn={() => { window.location.hash = ''; }} />;
  }''',
            1,
        )
        core.write_text(s)
        print('SystemAppCore modes written')
    else:
        print('mode gates already')
else:
    print('SystemAppCore missing')

lp = Path('src/components/LoginPage.tsx')
if lp.exists():
    s = lp.read_text()
    if 'LOGIN_FEATURES_V2' not in s:
        old_caps = '''const AGENT_CAPS = [
  { title: 'Omnichannel inbox', blurb: 'Portal, chat, and email land in one queue.' },
  { title: 'Branch-aware routing', blurb: 'Tickets stay with the right team automatically.' },
  { title: 'SLA + automations', blurb: 'Rules fire on create, priority, and breach.' },
];

const CUSTOMER_CAPS = [
  { title: 'Submit & track', blurb: 'Open a request and follow status anytime.' },
  { title: 'Live chat', blurb: 'Reach an agent when you need a quick answer.' },
  { title: 'Community', blurb: 'Ask other customers before opening a ticket.' },
];'''
        new_caps = '''/* LOGIN_FEATURES_V2 */
const AGENT_CAPS = [
  { title: 'Omnichannel inbox', blurb: 'Portal, chat, and email land in one queue.' },
  { title: 'Branch-aware routing', blurb: 'Tickets stay with the right team automatically.' },
  { title: 'SLA + automations', blurb: 'Rules fire on create, priority, and breach.' },
  { title: 'Live chat desk', blurb: 'Claim chats exclusively and reply in real time.' },
  { title: 'Knowledge base', blurb: 'Publish help articles agents and customers share.' },
];

const CUSTOMER_CAPS = [
  { title: 'Submit & track', blurb: 'Open a request and follow status anytime.' },
  { title: 'Live chat', blurb: 'Reach an agent when you need a quick answer.' },
  { title: 'Community', blurb: 'Ask other customers before opening a ticket.' },
  { title: 'Help articles', blurb: 'Self-serve guides filtered by topic when you need them.' },
  { title: 'My Tickets', blurb: 'See updates, reply, and rate resolved work in one place.' },
];'''
        if old_caps in s:
            s = s.replace(old_caps, new_caps, 1)
            print('caps expanded')

        chip_block = '''              <div className="mt-5 flex flex-wrap gap-2">
                {(isAgent
                  ? ['Omnichannel inbox', 'SLA tracking', 'Branch routing']
                  : ['Live status', 'Secure portal', '24/7 desk']
                ).map((tag) => (
                  <span
                    key={tag}
                    className="login-chip"
                  >
                    {tag}
                  </span>
                ))}
              </div>'''
        chip_block2 = '''              <div className="mt-5 flex flex-wrap gap-2">
                {(isAgent
                  ? ['Omnichannel inbox', 'SLA tracking', 'Branch routing']
                  : ['Live status', 'Secure portal', '24/7 desk']
                ).map((tag) => (
                  <span
                    key={tag}
                    className="text-[11px] font-medium px-2.5 py-1 rounded-full border border-white/10 bg-white/5 text-fuchsia-100/85 backdrop-blur-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>'''
        if chip_block in s:
            s = s.replace(chip_block, '              {/* chips removed — redundant with feature list */}', 1)
            print('chips removed v1')
        elif chip_block2 in s:
            s = s.replace(chip_block2, '              {/* chips removed — redundant with feature list */}', 1)
            print('chips removed v2')
        else:
            s2 = re.sub(
                r'\s*<div className="mt-5 flex flex-wrap gap-2">\s*\{\(isAgent\s*\n\s*\? \[\'Omnichannel inbox\'.*?</div>',
                '\n              {/* chips removed */}',
                s,
                count=1,
                flags=re.S,
            )
            if s2 != s:
                s = s2
                print('chips removed regex')

        lp.write_text(s)
        print('LoginPage written')
    else:
        print('features already')
else:
    print('LoginPage missing')

css = Path('src/login-glass.css')
if css.exists():
    t = css.read_text()
    if 'CAPS_SHOW_ALL_V1' not in t:
        t = t.replace(
            '.login-screen-fit .login-cap:nth-child(n+3) { display: none; }',
            '/* CAPS_SHOW_ALL_V1 — keep features visible */\n  .login-screen-fit .login-cap:nth-child(n+6) { display: none; }',
        )
        t = t.replace(
            '.login-screen-fit .login-cap { display: none; }',
            '.login-screen-fit .login-cap:nth-child(n+4) { display: none; }',
        )
        css.write_text(t)
        print('caps visibility css')

print('DONE')
