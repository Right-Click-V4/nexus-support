import { useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { markJustLoggedIn } from './PostLoginLoader';
import { SpaceFlybys } from './LoginFlybys';

interface Props {
  audience?: 'customer' | 'agent';
  onOpenPortal?: () => void;
  onOpenAgent?: () => void;
}

function useFallingStars(count: number) {
  return useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        id: i,
        left: `${(i * 37 + 7) % 100}%`,
        top: `${(i * 53 + 11) % 100}%`,
        size: i % 7 === 0 ? 2.4 : i % 3 === 0 ? 1.6 : 1,
        delay: -((i * 0.47) % 18),
        duration: 14 + (i % 9) * 2.2,
        twinkle: 2.4 + (i % 5) * 0.7,
        color: i % 5 === 0 ? '#f9a8d4' : i % 4 === 0 ? '#67e8f9' : i % 3 === 0 ? '#ffffff' : '#c4b5fd',
        opacity: 0.25 + (i % 5) * 0.12,
      })),
    [count]
  );
}

function NexusLogoMark({ size = 56 }: { size?: number }) {
  return (
    <div className="login-logo-mark" style={{ width: size, height: size }}>
      <svg viewBox="0 0 48 48" width={size} height={size} fill="none" aria-hidden>
        <circle cx="24" cy="24" r="5.2" fill="#e9d5ff" className="login-logo-core" />
        <g className="login-logo-arcs">
          <path d="M24 7a17 17 0 0 1 17 17" stroke="#c4b5fd" strokeWidth="3" strokeLinecap="round" />
          <path d="M24 41a17 17 0 0 1-17-17" stroke="#a78bfa" strokeWidth="3" strokeLinecap="round" opacity="0.7" />
        </g>
        <g className="login-logo-arcs-rev">
          <path d="M10 30a16 16 0 0 1 4-14" stroke="#f0abfc" strokeWidth="1.6" strokeLinecap="round" opacity="0.8" />
        </g>
      </svg>
    </div>
  );
}

type TrailPoint = { x: number; y: number };
const TRAIL_LEN = 32;
function easeInOut(t: number) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
function randomIn(min: number, max: number) { return min + Math.random() * (max - min); }

function LogoPilotStage() {
  const pilotRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const history = useRef<TrailPoint[]>([]);
  const [trail, setTrail] = useState<TrailPoint[]>([]);
  const [stageSize, setStageSize] = useState({ w: 1, h: 1 });
  useEffect(() => {
    let raf = 0;
    let lastSample = 0;
    let x = 0, y = 0, fromX = 0, fromY = 0, toX = 0, toY = 0, toScale = 1, fromScale = 1, scale = 1, startT = 0, duration = 2500, ready = false;
    const pickTarget = (w: number, h: number) => {
      const marginX = w * 0.12, marginY = h * 0.1;
      let nx = randomIn(marginX, w - marginX);
      let ny = randomIn(marginY, h - marginY);
      if (Math.random() < 0.25) ny = randomIn(h * 0.55, h * 0.88);
      if (Math.random() < 0.25) ny = randomIn(h * 0.08, h * 0.28);
      if (Math.random() < 0.2) nx = randomIn(marginX, w * 0.35);
      if (Math.random() < 0.2) nx = randomIn(w * 0.55, w - marginX);
      fromX = x; fromY = y; fromScale = scale; toX = nx; toY = ny; toScale = randomIn(0.88, 1.14);
      startT = performance.now();
      const dist = Math.hypot(toX - fromX, toY - fromY);
      const travel = dist * 2.2 + randomIn(200, 800);
      duration = Math.min(4200, Math.max(1400, travel));
    };
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      const stage = stageRef.current, pilot = pilotRef.current;
      if (!stage || !pilot) return;
      const sr = stage.getBoundingClientRect();
      if (sr.width < 10 || sr.height < 10) return;
      if (!ready) {
        x = sr.width * 0.5; y = sr.height * 0.35; fromX = x; fromY = y; toX = x; toY = y; ready = true;
        pickTarget(sr.width, sr.height);
        setStageSize({ w: sr.width, h: sr.height });
      }
      if (Math.abs(sr.width - stageSize.w) > 8 || Math.abs(sr.height - stageSize.h) > 8) setStageSize({ w: sr.width, h: sr.height });
      const t = Math.min(1, (now - startT) / duration);
      const e = easeInOut(t);
      x = fromX + (toX - fromX) * e; y = fromY + (toY - fromY) * e; scale = fromScale + (toScale - fromScale) * e;
      pilot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) scale(${scale})`;
      if (t >= 1) pickTarget(sr.width, sr.height);
      if (now - lastSample >= 24) {
        lastSample = now;
        const prev = history.current[0];
        if (!prev || Math.hypot(prev.x - x, prev.y - y) >= 2.5) {
          history.current = [{ x, y }, ...history.current].slice(0, TRAIL_LEN);
          setTrail([...history.current]);
        } else if (history.current.length > 4) {
          history.current = history.current.slice(0, -1);
          setTrail([...history.current]);
        }
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);
  const pathD = useMemo(() => {
    if (trail.length < 2) return '';
    let d = `M ${trail[0].x.toFixed(1)} ${trail[0].y.toFixed(1)}`;
    for (let i = 1; i < trail.length - 1; i++) {
      const midX = (trail[i].x + trail[i + 1].x) / 2;
      const midY = (trail[i].y + trail[i + 1].y) / 2;
      d += ` Q ${trail[i].x.toFixed(1)} ${trail[i].y.toFixed(1)} ${midX.toFixed(1)} ${midY.toFixed(1)}`;
    }
    const last = trail[trail.length - 1];
    d += ` L ${last.x.toFixed(1)} ${last.y.toFixed(1)}`;
    return d;
  }, [trail]);
  return (
    <div ref={stageRef} className="login-pilot-stage absolute inset-0 pointer-events-none z-[5] hidden lg:block" aria-hidden>
      {pathD && (
        <svg className="login-light-trail absolute inset-0 w-full h-full overflow-visible" width={stageSize.w} height={stageSize.h} viewBox={`0 0 ${stageSize.w} ${stageSize.h}`}>
          <defs>
            <linearGradient id="starTrailGrad" gradientUnits="userSpaceOnUse" x1={trail[0]?.x ?? 0} y1={trail[0]?.y ?? 0} x2={trail[trail.length - 1]?.x ?? 0} y2={trail[trail.length - 1]?.y ?? 0}>
              <stop offset="0%" stopColor="#f0abfc" stopOpacity="0.9" />
              <stop offset="25%" stopColor="#e879f9" stopOpacity="0.55" />
              <stop offset="55%" stopColor="#c026d3" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#86198f" stopOpacity="0" />
            </linearGradient>
            <filter id="starGlow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur stdDeviation="4" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <filter id="starBloom" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="10" /></filter>
          </defs>
          <path d={pathD} fill="none" stroke="url(#starTrailGrad)" strokeWidth={22} strokeLinecap="round" strokeLinejoin="round" filter="url(#starBloom)" opacity={0.4} />
          <path d={pathD} fill="none" stroke="url(#starTrailGrad)" strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" filter="url(#starGlow)" opacity={0.8} />
        </svg>
      )}
      {trail.slice(2, 12).map((p, i) => {
        const t = i / 10;
        return <span key={`spark-${i}-${Math.round(p.x)}`} className="login-trail-spark" style={{ left: p.x + ((i % 3) - 1) * 5, top: p.y + ((i % 2) * 3 - 1), opacity: Math.max(0, 0.55 * (1 - t)), width: 2 + (1 - t) * 3, height: 2 + (1 - t) * 3 }} />;
      })}
      <div ref={pilotRef} className="login-pilot login-pilot-js" style={{ left: 0, top: 0, transform: 'translate(-50%, -50%)' }}>
        <div className="login-pilot-glow" /><NexusLogoMark size={40} />
      </div>
    </div>
  );
}

function CosmicFallBackground() {
  const stars = useFallingStars(70);
  const field = useFallingStars(48);
  return (
    <div className="login-cosmos absolute inset-0 overflow-hidden" aria-hidden>
      <div className="login-cosmos-sky absolute inset-0" />
      <div className="login-galaxy-band" />
      <div className="login-nebula login-nebula-a absolute inset-0" />
      <div className="login-nebula login-nebula-b absolute inset-0" />
      <div className="login-dust absolute inset-0" />
      <div className="absolute inset-0">
        {field.map((s) => (
          <span key={`t-${s.id}`} className="absolute rounded-full" style={{ left: s.left, top: s.top, width: s.size, height: s.size, background: s.color, boxShadow: `0 0 ${s.size * 4}px ${s.color}`, animation: `login-twinkle ${s.twinkle}s ease-in-out ${s.delay}s infinite` }} />
        ))}
      </div>
      <div className="login-starfield absolute inset-0">
        {stars.map((s) => (
          <span key={s.id} className="login-star absolute rounded-full" style={{ left: s.left, width: s.size, height: s.size, background: s.color, opacity: s.opacity, boxShadow: `0 0 ${s.size * 4}px ${s.color}`, animationDelay: `${s.delay}s`, animationDuration: `${s.duration}s` }} />
        ))}
      </div>
      <LogoPilotStage />
      <SpaceFlybys />
      <div className="login-cosmos-vignette absolute inset-0 pointer-events-none" />
    </div>
  );
}

const CAPABILITIES = [
  { title: 'Omnichannel inbox', blurb: 'Portal, chat, and email land in one queue.' },
  { title: 'Branch-aware routing', blurb: 'Tickets stay with the right team automatically.' },
  { title: 'SLA + automations', blurb: 'Rules fire on create, priority, and breach.' },
];

export default function LoginPage({ audience = 'customer', onOpenPortal, onOpenAgent }: Props) {
  const { signIn, signUp, resetPassword, configError } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [audienceTab, setAudienceTab] = useState<'agent' | 'customer'>(audience === 'agent' ? 'agent' : 'customer');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState('');
  const isAgent = audienceTab === 'agent';

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setInfo('');
    if (mode === 'signup') {
      if (!name.trim()) { setError('Please enter your full name.'); return; }
      if (password.length < 6) { setError('Password must be at least 6 characters.'); return; }
      if (password !== confirmPassword) { setError('Passwords do not match.'); return; }
    }
    setLoading(true);
    try {
      if (mode === 'signin') {
        markJustLoggedIn();
        await signIn(email.trim(), password, isAgent ? 'agent' : 'customer');
        window.location.hash = isAgent ? '' : 'portal';
      }
      else {
        await signUp(email.trim(), password, name.trim() || undefined, isAgent ? 'agent' : 'customer');
        setInfo('Account created. You can sign in now.');
        setMode('signin');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Authentication failed';
      if (/pending admin approval|must approve|Account created/i.test(msg)) {
        setInfo(msg);
        setMode('signin');
      } else setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    setError('');
    setInfo('');
    const em = email.trim();
    if (!em) {
      setError('Enter your email above, then click Forgot Password?');
      return;
    }
    setLoading(true);
    try {
      if (!resetPassword) throw new Error('Password reset is not available.');
      await resetPassword(em);
      setInfo('Password reset email sent. Check your inbox (and spam folder).');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not send reset email');
    } finally {
      setLoading(false);
    }
  };

  const leftTitle = isAgent ? 'Resolve faster.' : 'Get help, fast.';
  const leftSub = isAgent ? 'Stay organized across every branch.' : 'Submit requests, chat live, and track every ticket.';
  const leftBlurb = isAgent
    ? 'Nexus Ops connects your customer portal, live chat, and agent desk. Route by branch, track SLA, and keep every conversation in one place.'
    : 'Open a request, talk to an agent in real time, or check the status of an existing ticket — all from one place.';
  const caps = isAgent
    ? CAPABILITIES
    : [
        { title: 'Submit & track', blurb: 'Open a request and follow status anytime.' },
        { title: 'Live chat', blurb: 'Reach an agent when you need a quick answer.' },
        { title: 'Community', blurb: 'Ask other customers before opening a ticket.' },
      ];
  const cardSub = isAgent ? 'Sign in to Agent Workspace' : 'Sign in to Customer Portal';
  const footerCredit = isAgent
    ? 'NexusOps Agent Workspace · © 2026 Lizer & Kirzhian'
    : 'NexusOps Customer Portal · © 2026 Lizer & Kirzhian';

  return (
    <div className="relative min-h-screen overflow-hidden">
      <CosmicFallBackground />
      <div className="relative z-10 min-h-screen flex items-center justify-center">
        <div className="w-full max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(300px,380px)] gap-10 lg:gap-14 xl:gap-20 2xl:gap-28 px-5 sm:px-8 lg:px-12 xl:px-16 2xl:px-24 py-8 lg:py-12 items-center">
          <div className="login-copy flex flex-col relative z-10 order-2 lg:order-1">
            <div className="flex items-center gap-3">
              <div className="login-brand-badge">
                <NexusLogoMark size={20} />
              </div>
              <div>
                <div className="text-sm font-semibold text-white tracking-tight">Nexus Ops</div>
                <div className="text-[11px] text-fuchsia-200/70">{isAgent ? 'Support operations platform' : 'Customer support portal'}</div>
              </div>
            </div>
            <div className="mt-8 lg:mt-10 max-w-lg">
              <div className="login-status-pill mb-4"><span className="login-status-dot" /> Desk online</div>
              <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-fuchsia-300/80 mb-3">{isAgent ? 'Built for agent teams' : 'Built for customers'}</p>
              <h1 className="login-hero-title text-3xl sm:text-4xl xl:text-[2.75rem] font-semibold leading-[1.08] tracking-tight">
                {leftTitle}<span className="block text-fuchsia-200/90 font-normal mt-1" style={{ WebkitTextFillColor: 'rgba(245, 208, 254, 0.92)', background: 'none' }}>{leftSub}</span>
              </h1>
              <p className="mt-4 text-sm sm:text-[15px] text-fuchsia-100/75 leading-relaxed max-w-md">{leftBlurb}</p>
              <ul className="mt-6 space-y-2.5 max-w-md">
                {caps.map((c, i) => (
                  <li key={c.title} className="login-cap">
                    <span className="login-cap-index">{String(i + 1).padStart(2, '0')}</span>
                    <div>
                      <div className="text-sm font-medium text-white">{c.title}</div>
                      <div className="text-xs text-fuchsia-100/65 mt-0.5">{c.blurb}</div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="mt-10 lg:mt-14 text-[11px] text-fuchsia-200/35 hidden lg:block tracking-wide">{footerCredit}</div>
          </div>

          <div className="flex items-center justify-center lg:justify-end order-1 lg:order-2 w-full lg:w-auto">
            {mode === 'signin' ? (
            <div className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 sm:px-7">
              <div className="flex flex-col items-center text-center mb-5">
                <div className="login-card-logo"><NexusLogoMark size={28} /></div>
                <div className="mt-3 text-[22px] font-semibold text-white tracking-tight">Nexus Ops</div>
                <div className="text-[13px] text-violet-200/75 mt-1">{cardSub}</div>
              </div>
              <div className="flex gap-2 mb-4 text-sm">
                <button type="button" onClick={() => setAudienceTab('customer')} className={`login-tab ${audienceTab === 'customer' ? 'login-tab-on' : ''}`}>Customer</button>
                <button type="button" onClick={() => setAudienceTab('agent')} className={`login-tab ${audienceTab === 'agent' ? 'login-tab-on' : ''}`}>Agent</button>
              </div>
              {configError && <div className="mb-3 text-sm text-amber-200 bg-amber-500/10 border border-amber-400/30 rounded-lg px-3 py-2">{configError}</div>}
              {error && <div className="mb-3 text-sm text-rose-200 bg-rose-500/10 border border-rose-400/30 rounded-lg px-3 py-2">{error}</div>}
              {info && <div className="mb-3 text-sm text-emerald-200 bg-emerald-500/10 border border-emerald-400/30 rounded-lg px-3 py-2">{info}</div>}
              <form onSubmit={submit} className="space-y-3.5">
                <div>
                  <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label>
                  <input type="email" required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="off" autoCapitalize="none" autoCorrect="off" spellCheck={false} name="nexus_email_manual" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" data-form-type="other" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label>
                  <div className="relative">
                    <input type={showPassword ? 'text' : 'password'} required minLength={6} className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-12" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" autoComplete="new-password" name="nexus_password_manual" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" data-form-type="other" />
                    <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-fuchsia-100/90 hover:text-white px-2 py-1 rounded-md hover:bg-white/10 transition" onClick={() => setShowPassword((v) => !v)}>{showPassword ? 'Hide' : 'Show'}</button>
                  </div>
                </div>
                <button type="submit" disabled={loading} className="login-submit-btn w-full rounded-xl bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500 hover:from-violet-400 hover:via-fuchsia-400 hover:to-violet-400 disabled:opacity-60 text-white font-semibold text-sm py-2.5 shadow-lg shadow-fuchsia-600/30">
                  {loading ? 'Signing in…' : 'Sign in'}
                </button>
                <p className="text-center text-xs text-violet-200/70 pt-1">
                  New here?{' '}
                  <button type="button" onClick={() => { setMode('signup'); setError(''); setInfo(''); }} className="text-white font-semibold hover:text-fuchsia-100">{isAgent ? 'Create an agent account' : 'Create a customer account'}</button>
                </p>
                <div className="text-center">
                  <button type="button" onClick={() => void handleForgotPassword()} className="text-xs font-medium text-violet-100/80 hover:text-white">Forgot Password?</button>
                </div>
              </form>
            </div>
            ) : (
            <div className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 sm:px-7">
              <div className="flex flex-col items-center text-center mb-4">
                <div className="login-card-logo"><NexusLogoMark size={28} /></div>
                <div className="mt-3 text-[22px] font-semibold text-white tracking-tight">Create your account</div>
                <div className="text-[13px] text-violet-200/75 mt-1">{isAgent ? 'Register for Agent Workspace' : 'Register for Customer Portal'}</div>
                <div className="login-role-chip mt-3"><span className="login-status-dot" style={{ width: 6, height: 6 }} />{isAgent ? 'Agent registration' : 'Customer registration'}</div>
              </div>
              {configError && <div className="mb-3 text-sm text-amber-200 bg-amber-500/10 border border-amber-400/30 rounded-lg px-3 py-2">{configError}</div>}
              {error && <div className="mb-3 text-sm text-rose-200 bg-rose-500/10 border border-rose-400/30 rounded-lg px-3 py-2">{error}</div>}
              {info && <div className="mb-3 text-sm text-emerald-200 bg-emerald-500/10 border border-emerald-400/30 rounded-lg px-3 py-2">{info}</div>}
              <form onSubmit={submit} className="space-y-3.5">
                <div>
                  <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Full name</label>
                  <input required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" autoComplete="off" name="nexus_name_manual" data-lpignore="true" data-1p-ignore="true" data-form-type="other" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label>
                  <input type="email" required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="off" autoCapitalize="none" autoCorrect="off" spellCheck={false} name="nexus_email_manual" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" data-form-type="other" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label>
                  <div className="relative">
                    <input type={showPassword ? 'text' : 'password'} required minLength={6} className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-12" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 6 characters" autoComplete="new-password" name="nexus_password_manual" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" data-form-type="other" />
                    <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-fuchsia-100/90 hover:text-white px-2 py-1 rounded-md hover:bg-white/10 transition" onClick={() => setShowPassword((v) => !v)}>{showPassword ? 'Hide' : 'Show'}</button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Confirm password</label>
                  <div className="relative">
                    <input type={showConfirm ? 'text' : 'password'} required minLength={6} className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-12" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Re-enter password" autoComplete="new-password" name="nexus_confirm_manual" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" data-form-type="other" />
                    <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-fuchsia-100/90 hover:text-white px-2 py-1 rounded-md hover:bg-white/10 transition" onClick={() => setShowConfirm((v) => !v)}>{showConfirm ? 'Hide' : 'Show'}</button>
                  </div>
                </div>
                <button type="submit" disabled={loading} className="login-submit-btn w-full rounded-xl bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 bg-[length:160%_100%] hover:from-violet-500 hover:via-fuchsia-500 hover:to-violet-500 disabled:opacity-60 text-white font-medium text-sm py-2.5 shadow-lg shadow-violet-600/40 mt-1">
                  {loading ? 'Creating account…' : 'Create account'}
                </button>
                <p className="text-center text-xs text-fuchsia-200/70 pt-1">
                  Already have an account?{' '}
                  <button type="button" onClick={() => { setMode('signin'); setError(''); setInfo(''); setConfirmPassword(''); }} className="text-fuchsia-100 hover:text-white font-semibold underline-offset-2 hover:underline">{isAgent ? 'Back to agent sign in' : 'Back to customer sign in'}</button>
                </p>
              </form>
            </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
