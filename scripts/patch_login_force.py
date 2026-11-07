"""Force visible login redesign + ensure calm flybys if prior patch partially applied."""
from pathlib import Path

css = Path('src/login-glass.css')
if css.exists():
    t = css.read_text()
    if 'LOGIN_FORCE_V3' in t:
        print('force already')
    else:
        block = '''

/* LOGIN_FORCE_V3 — always wins */
.login-glass-card {
  position: relative !important;
  z-index: 30 !important;
  background:
    radial-gradient(120% 90% at 0% 0%, rgba(167, 139, 250, 0.28), transparent 50%),
    radial-gradient(100% 80% at 100% 10%, rgba(236, 72, 153, 0.18), transparent 45%),
    linear-gradient(165deg, rgba(36, 18, 68, 0.92) 0%, rgba(12, 6, 28, 0.94) 100%) !important;
  border: 1px solid rgba(196, 181, 253, 0.4) !important;
  box-shadow:
    0 0 0 1px rgba(139, 92, 246, 0.18),
    0 28px 56px -12px rgba(0, 0, 0, 0.65),
    0 0 80px -16px rgba(124, 58, 237, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(24px) saturate(1.4) !important;
  -webkit-backdrop-filter: blur(24px) saturate(1.4) !important;
}
.login-glass-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(125deg, rgba(255,255,255,0.1) 0%, transparent 35%, transparent 65%, rgba(167,139,250,0.08) 100%);
}
.login-hero-title {
  text-shadow: 0 0 48px rgba(192, 132, 252, 0.35), 0 2px 0 rgba(0,0,0,0.2) !important;
}
.login-brand-badge {
  box-shadow: 0 0 28px rgba(167, 139, 250, 0.45), 0 0 0 1px rgba(196,181,253,0.25) !important;
}
.login-submit-btn {
  position: relative !important;
  overflow: hidden !important;
  box-shadow: 0 8px 28px rgba(124, 58, 237, 0.45) !important;
}
.login-submit-btn::after {
  content: '' !important;
  position: absolute !important;
  inset: 0 !important;
  background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.22) 50%, transparent 65%) !important;
  animation: login-btn-sheen 4.2s ease-in-out infinite !important;
}
@keyframes login-btn-sheen {
  0%, 50% { transform: translateX(-130%); }
  72%, 100% { transform: translateX(130%); }
}
.login-glass-input {
  background: rgba(8, 4, 20, 0.75) !important;
  border: 1px solid rgba(196, 181, 253, 0.28) !important;
  color: #f8f5ff !important;
}
.login-glass-input:focus {
  border-color: rgba(192, 132, 252, 0.65) !important;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.28) !important;
}
.login-tab-on {
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.35) !important;
}
.login-sat-blink { animation: login-sat-pulse 2.2s ease-in-out infinite !important; }
@keyframes login-sat-pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
.login-sat-svg { filter: drop-shadow(0 0 10px rgba(34, 211, 238, 0.45)) !important; }
'''
        css.write_text(t.rstrip() + block)
        print('LOGIN_FORCE_V3 appended')
else:
    print('css missing')

fly = Path('src/components/LoginFlybys.tsx')
if fly.exists():
    s = fly.read_text()
    if 'slice(-2)' in s:
        s = s.replace(
            'setFlybys((prev) => [...prev.slice(-2), { id, kind, variant, top, duration, dir, chat }]);',
            'setFlybys([{ id, kind, variant, top, duration, dir, chat }]); // one craft',
            1,
        )
        print('forced one craft')
    if 'const gaps = [16, 22, 28, 34, 42];' in s:
        s = s.replace('const gaps = [16, 22, 28, 34, 42];', 'const gaps = [10, 11, 12, 13, 14, 15];', 1)
        print('forced 10-15 gaps')
    fly.write_text(s)

tm = Path('src/theme-modes.css')
if tm.exists() and 'NOTIF_FORCE_V3' not in tm.read_text():
    tm.write_text(tm.read_text().rstrip() + '''

/* NOTIF_FORCE_V3 */
.app-cosmos .nexus-topbar [class*="w-80"],
.app-cosmos .nexus-topbar [class*="0c0a14"] {
  background: #0c0a14 !important;
  border: 1px solid rgba(120,120,130,0.85) !important;
  box-shadow: 0 18px 44px rgba(0,0,0,0.65) !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
''')
    print('notif force css')

print('DONE')
