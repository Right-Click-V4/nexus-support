/* login-speed-v1 */
/* postlogin-force-exit-v1 */
/* postlogin-auto-clear-v1 */
/* postlogin-timing-v2 */
/* postlogin-no-boot-flash-v1 */
import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';

const MIN_MS = 1600;
const FADE_MS = 500;
const POST_LOGIN_KEY = 'nexus_post_login';

export function markJustLoggedIn() {
  try {
    sessionStorage.setItem(POST_LOGIN_KEY, String(Date.now()));
  } catch {
    /* ignore */
  }
}

export function hasJustLoggedIn(): boolean {
  try {
    const v = sessionStorage.getItem(POST_LOGIN_KEY);
    if (!v) return false;
    return Date.now() - Number(v) < 90_000;
  } catch {
    return false;
  }
}

export function clearJustLoggedIn() {
  try {
    sessionStorage.removeItem(POST_LOGIN_KEY);
  } catch {
    /* ignore */
  }
}

/** Compact star-X logo for boot. */
function LogoMark({ spinning }: { spinning: boolean }) {
  return (
    <div
      className="w-14 h-14 rounded-2xl bg-white/[0.08] border border-white/20 flex items-center justify-center shadow-[0_0_36px_rgba(167,139,250,0.35)] backdrop-blur-md"
      style={{ animation: spinning ? 'pl-spin-ring 2.2s linear infinite' : 'none' }}
    >
      <svg viewBox="0 0 48 48" width={30} height={30} fill="none" aria-hidden>
        <path d="M10 10 L38 38 M38 10 L10 38" stroke="#ffffff" strokeWidth="7" strokeLinecap="round" />
        <path d="M24 6 L27.2 20.8 L42 24 L27.2 27.2 L24 42 L20.8 27.2 L6 24 L20.8 20.8 Z" fill="#ffffff" />
        <circle cx="24" cy="24" r="3" fill="#ffffff" />
      </svg>
    </div>
  );
}

export function BootLoader({ label = 'Loading…' }: { label?: string }) {
  const stars = useMemo(
    () =>
      Array.from({ length: 48 }, (_, i) => ({
        id: i,
        left: `${(i * 47 + 13) % 100}%`,
        top: `${(i * 31 + 7) % 100}%`,
        size: i % 7 === 0 ? 2.5 : i % 3 === 0 ? 1.8 : 1.2,
        delay: `${(i * 0.27) % 4}s`,
        duration: `${2.4 + (i % 5) * 0.55}s`,
        opacity: 0.25 + (i % 6) * 0.1,
      })),
    [],
  );

  return (
    <div className="relative min-h-screen overflow-hidden flex items-center justify-center bg-[#0b0618]">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 120% 80% at 20% 15%, rgba(120, 40, 180, 0.42), transparent 55%),' +
            'radial-gradient(ellipse 90% 70% at 85% 20%, rgba(60, 20, 140, 0.48), transparent 50%),' +
            'radial-gradient(ellipse 80% 55% at 50% 100%, rgba(30, 10, 80, 0.55), transparent 55%),' +
            'linear-gradient(180deg, #1a0a3a 0%, #0b0618 48%, #05030e 100%)',
        }}
      />

      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute w-72 h-72 rounded-full opacity-30 blur-3xl"
          style={{
            left: '15%',
            top: '20%',
            background: 'radial-gradient(circle, rgba(192,38,211,0.45), transparent 70%)',
            animation: 'pl-boot-drift 12s ease-in-out infinite alternate',
          }}
        />
        <div
          className="absolute w-96 h-96 rounded-full opacity-20 blur-3xl"
          style={{
            right: '10%',
            bottom: '15%',
            background: 'radial-gradient(circle, rgba(99,102,241,0.4), transparent 70%)',
            animation: 'pl-boot-drift 14s ease-in-out infinite alternate-reverse',
          }}
        />
      </div>

      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {stars.map((s) => (
          <span
            key={s.id}
            className="absolute rounded-full bg-white"
            style={{
              left: s.left,
              top: s.top,
              width: s.size,
              height: s.size,
              opacity: s.opacity,
              boxShadow: s.size > 2 ? '0 0 6px rgba(255,255,255,0.55)' : undefined,
              animation: `pl-boot-twinkle ${s.duration} ease-in-out infinite`,
              animationDelay: s.delay,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 flex flex-col items-center gap-6 px-6">
        <div className="relative">
          <div
            className="absolute -inset-4 rounded-3xl opacity-50 blur-xl pointer-events-none"
            style={{ background: 'radial-gradient(circle, rgba(167,139,250,0.45), transparent 70%)' }}
          />
          <LogoMark spinning />
        </div>

        <div className="text-center space-y-2 max-w-xs">
          <p className="text-[15px] font-medium tracking-wide text-fuchsia-50/95">{label}</p>
          <p className="text-[11px] uppercase tracking-[0.22em] text-violet-300/55">NeXus Ops</p>
        </div>

        <div className="w-44 h-[3px] rounded-full bg-white/10 overflow-hidden">
          <div
            className="h-full w-1/3 rounded-full"
            style={{
              background: 'linear-gradient(90deg, transparent, #e879f9, #a78bfa, transparent)',
              animation: 'pl-boot-bar 1.35s ease-in-out infinite',
            }}
          />
        </div>
      </div>

      <style>{`
        @keyframes pl-spin-ring { to { transform: rotate(360deg); } }
        @keyframes pl-boot-twinkle {
          0%, 100% { opacity: 0.2; transform: scale(0.85); }
          50% { opacity: 1; transform: scale(1.15); }
        }
        @keyframes pl-boot-drift {
          from { transform: translate3d(0, 0, 0); }
          to { transform: translate3d(2.5%, 1.5%, 0); }
        }
        @keyframes pl-boot-bar {
          0% { transform: translateX(-120%); }
          100% { transform: translateX(320%); }
        }
      `}</style>
    </div>
  );
}

export default function PostLoginLoader({
  label = 'Opening workspace…',
  fading = false,
  variant = 'agent',
}: {
  label?: string;
  subtitle?: string;
  fading?: boolean;
  variant?: 'agent' | 'customer';
}) {
  const steps =
    variant === 'customer'
      ? ['Verifying account…', 'Loading your tickets…', 'Preparing live chat…', 'Ready']
      : ['Verifying session…', 'Loading your desk…', 'Syncing tickets & chat…', 'Ready'];

  const [stepIdx, setStepIdx] = useState(0);

  useEffect(() => {
    const timers = [
      window.setTimeout(() => setStepIdx(1), 280),
      window.setTimeout(() => setStepIdx(2), 620),
      window.setTimeout(() => setStepIdx(3), 980),
      // do NOT clear post-login flag here — PostLoginShell clears after ceremony
    ];
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, []);

  const status = steps[Math.min(stepIdx, steps.length - 1)];
  const isReady = stepIdx >= steps.length - 1;
  const line = stepIdx === 0 && label ? label : status;
  const progress = Math.min(100, ((stepIdx + 1) / steps.length) * 100);

  return (
    <div
      className={`relative min-h-screen overflow-hidden flex items-center justify-center bg-[#0b0618] ${
        fading ? 'opacity-0 scale-[0.985]' : 'opacity-100 scale-100'
      }`}
      style={{
        transition: `opacity ${FADE_MS}ms cubic-bezier(0.22, 1, 0.36, 1), transform ${FADE_MS}ms cubic-bezier(0.22, 1, 0.36, 1)`,
      }}
    >
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 120% 80% at 20% 10%, rgba(120, 40, 180, 0.45), transparent 55%),' +
            'radial-gradient(ellipse 90% 70% at 85% 25%, rgba(60, 20, 140, 0.5), transparent 50%),' +
            'radial-gradient(ellipse 80% 60% at 50% 95%, rgba(30, 10, 80, 0.6), transparent 55%),' +
            'linear-gradient(180deg, #1a0a3a 0%, #0b0618 45%, #05030e 100%)',
        }}
      />

      <div className="relative z-10 flex flex-col items-center gap-7 px-6">
        <LogoMark spinning />
        <div className="text-center space-y-2 max-w-sm">
          <p className="text-base font-medium tracking-wide text-fuchsia-50/95">{line}</p>
          <p className="text-[11px] uppercase tracking-[0.22em] text-violet-300/55">
            {isReady ? 'Almost there' : 'NeXus Ops'}
          </p>
        </div>
        <div className="relative w-52 h-[3px] rounded-full bg-white/10 overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #a78bfa, #e879f9, #f0abfc)',
            }}
          />
        </div>
      </div>

      <style>{`
        @keyframes pl-spin-ring { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

export function PostLoginShell({
  ready = true,
  label = 'Loading…',
  variant = 'agent',
  children,
}: {
  ready?: boolean;
  label?: string;
  subtitle?: string;
  variant?: 'agent' | 'customer';
  children: ReactNode;
}) {
  const [mode, setMode] = useState<'wait' | 'ceremony' | 'fading' | 'done'>('wait');
  const started = useRef(false);
  const wantCeremony = useRef(false);

  useEffect(() => {
    if (!ready) {
      started.current = false;
      setMode('wait');
      return;
    }

    if (!started.current) {
      started.current = true;
      wantCeremony.current = hasJustLoggedIn();
      if (!wantCeremony.current) {
        setMode('done');
        return;
      }
      // sticky flag so BootLoader paths never win mid-ceremony
      try {
        sessionStorage.setItem(POST_LOGIN_KEY, String(Date.now()));
      } catch {
        /* ignore */
      }
      setMode('ceremony');
      const t = window.setTimeout(() => setMode('fading'), MIN_MS);
      return () => window.clearTimeout(t);
    }
  }, [ready]);

  useEffect(() => {
    if (mode !== 'fading') return;
    const t = window.setTimeout(() => {
      clearJustLoggedIn();
      setMode('done');
    }, FADE_MS);
    return () => window.clearTimeout(t);
  }, [mode]);

  useEffect(() => {
    if (!ready || mode === 'ceremony' || mode === 'fading') return;
    if (!hasJustLoggedIn()) return;
    if (wantCeremony.current && mode === 'done') return;
    wantCeremony.current = true;
    started.current = true;
    setMode('ceremony');
    const t = window.setTimeout(() => setMode('fading'), MIN_MS);
    return () => window.clearTimeout(t);
  }, [ready, mode]);

  // Safety: force-complete if stuck (allow full ceremony + fade)
  useEffect(() => {
    if (!ready) return;
    const t = window.setTimeout(() => {
      setMode((m) => (m === 'wait' || m === 'ceremony' || m === 'fading' ? 'done' : m));
      clearJustLoggedIn();
    }, 4500);
    return () => window.clearTimeout(t);
  }, [ready]);

  if (!ready || mode === 'wait') {
    // Login path: only Post-Login UI. BootLoader is for refresh/session restore.
    if (hasJustLoggedIn() || wantCeremony.current) {
      return <PostLoginLoader label={label} fading={false} variant={variant} />;
    }
    return <BootLoader label={label} />;
  }

  if (mode === 'done') {
    return <>{children}</>;
  }

  const showOverlay = mode === 'ceremony' || mode === 'fading';
  const showPortal = mode === 'fading' || mode === 'done';
  const overlayFading = mode === 'fading';

  return (
    <div className="relative min-h-screen bg-[#0b0618]">
      {showPortal && (
        <div className="relative z-0 min-h-screen">
          {children}
        </div>
      )}

      {showOverlay && (
        <div
          className="fixed inset-0 z-50 pointer-events-none"
          style={{
            opacity: overlayFading ? 0 : 1,
            transition: `opacity ${FADE_MS}ms ease`,
          }}
        >
          <PostLoginLoader label={label} fading={overlayFading} variant={variant} />
        </div>
      )}
    </div>
  );
}
