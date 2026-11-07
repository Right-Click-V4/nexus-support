/* login-customer-first-v1 + screen-fit */
import { useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { markJustLoggedIn } from './PostLoginLoader';
import { CosmicFallBackground, NexusLogoMark } from './LoginScene';
import { NexusWordmark } from './NexusBrand';

interface Props {
  audience?: 'customer' | 'agent';
  onOpenPortal?: () => void;
  onOpenAgent?: () => void;
}

const AGENT_CAPS = [
  { title: 'Omnichannel inbox', blurb: 'Portal, chat, and email land in one queue.' },
  { title: 'Branch-aware routing', blurb: 'Tickets stay with the right team automatically.' },
  { title: 'SLA + automations', blurb: 'Rules fire on create, priority, and breach.' },
];

const CUSTOMER_CAPS = [
  { title: 'Submit & track', blurb: 'Open a request and follow status anytime.' },
  { title: 'Live chat', blurb: 'Reach an agent when you need a quick answer.' },
  { title: 'Community', blurb: 'Ask other customers before opening a ticket.' },
];

export default function LoginPage({ audience = 'customer', onOpenPortal, onOpenAgent }: Props) {
  const { signIn, signUp, resetPassword, configError } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [audienceTab, setAudienceTab] = useState<'agent' | 'customer'>('customer');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState('');
  const isAgent = audienceTab === 'agent';

  const submit = async (e: FormEvent) => {
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
      } else {
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
  const caps = isAgent ? AGENT_CAPS : CUSTOMER_CAPS;
  const cardSub = isAgent ? 'Sign in to Agent Workspace' : 'Sign in to Customer Portal';
  const footerCredit = isAgent
    ? 'NexusOps Agent Workspace · © 2026 Lizer & Kirzhian'
    : 'NexusOps Customer Portal · © 2026 Lizer & Kirzhian';

  return (
    <div className="relative login-screen-fit overflow-hidden">
      <CosmicFallBackground />
      <div className="relative z-10 h-full max-h-full flex items-center overflow-hidden">
        <div className="w-full max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(320px,400px)] gap-6 lg:gap-10 xl:gap-14 px-5 sm:px-8 lg:px-12 xl:px-16 py-5 lg:py-6 items-center max-h-full">
          <div className="flex flex-col relative z-10 order-2 lg:order-1 lg:pr-4 xl:pr-8 min-w-0">
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2.5">
                <div className="login-brand-badge">
                  <NexusLogoMark size={22} />
                </div>
                <NexusWordmark height={22} className="text-white" color="currentColor" />
              </div>
              <div className="text-[11px] text-fuchsia-200/70 pl-[34px]">
                {isAgent ? 'Support operations platform' : 'Customer support portal'}
              </div>
            </div>
            <div className="mt-5 lg:mt-6 max-w-lg xl:max-w-xl relative">
              <div
                aria-hidden
                className="pointer-events-none absolute -left-16 -top-10 w-64 h-64 rounded-full opacity-40 blur-3xl"
                style={{ background: 'radial-gradient(circle, rgba(168,85,247,0.45) 0%, transparent 70%)' }}
              />
              <div className="relative">
              <div className="login-status-pill mb-4 inline-flex items-center gap-2">
                <span className="login-status-dot" />
                <span>Desk online</span>
                <span className="mx-1 text-fuchsia-300/30">·</span>
                <span className="text-fuchsia-200/70">Avg reply under 5 min</span>
              </div>
              <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-fuchsia-300/80 mb-3">
                {isAgent ? 'Built for agent teams' : 'Built for customers'}
              </p>
              <h1 className="login-hero-title text-3xl sm:text-4xl xl:text-[2.75rem] font-semibold leading-[1.08] tracking-tight">
                {leftTitle}
                <span
                  className="block font-normal mt-1 bg-clip-text text-transparent"
                  style={{
                    backgroundImage: 'linear-gradient(105deg, #f5d0fe 0%, #e9d5ff 40%, #c4b5fd 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {leftSub}
                </span>
              </h1>
              <p className="mt-4 text-sm sm:text-[15px] text-fuchsia-100/75 leading-relaxed max-w-md">
                {leftBlurb}
              </p>
              <div className="mt-5 flex flex-wrap gap-2">
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
              </div>
              </div>
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
            <div className="mt-6 lg:mt-8 text-[11px] text-fuchsia-200/35 hidden lg:block tracking-wide">
              {footerCredit}
            </div>
          </div>

          <div className="flex items-center justify-center lg:justify-end order-1 lg:order-2 w-full lg:w-auto">
            {mode === 'signin' ? (
              <div className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] lg:max-w-none rounded-[22px] px-6 py-7 sm:px-7">
                <div className="flex flex-col items-center text-center mb-5">
                  <div className="login-card-logo">
                    <NexusLogoMark size={28} />
                  </div>
                  <div className="mt-3 text-white flex justify-center">
                    <NexusWordmark height={26} color="currentColor" />
                  </div>
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
                    <input type="email" required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="off" name="nexus_email_manual" data-lpignore="true" data-1p-ignore="true" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label>
                    <div className="relative">
                      <input type={showPassword ? 'text' : 'password'} required minLength={6} className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-12" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" autoComplete="new-password" name="nexus_password_manual" data-lpignore="true" data-1p-ignore="true" />
                      <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-fuchsia-100/90 hover:text-white px-2 py-1 rounded-md hover:bg-white/10 transition" onClick={() => setShowPassword((v) => !v)}>{showPassword ? 'Hide' : 'Show'}</button>
                    </div>
                  </div>
                  <button type="submit" disabled={loading} className="login-submit-btn w-full rounded-xl bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500 text-white font-semibold text-sm py-2.5 shadow-lg shadow-fuchsia-600/30">{loading ? 'Signing in…' : 'Sign in'}</button>
                  <p className="text-center text-xs text-violet-200/70 pt-1">New here?{' '}<button type="button" onClick={() => { setMode('signup'); setError(''); setInfo(''); }} className="text-white font-semibold hover:text-fuchsia-100">{isAgent ? 'Create an agent account' : 'Create a customer account'}</button></p>
                  <div className="text-center"><button type="button" onClick={() => void handleForgotPassword()} className="text-xs font-medium text-violet-100/80 hover:text-white">Forgot Password?</button></div>
                </form>
              </div>
            ) : (
              <div className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] lg:max-w-none rounded-[22px] px-6 py-7 sm:px-7">
                <div className="flex flex-col items-center text-center mb-4">
                  <div className="login-card-logo"><NexusLogoMark size={28} /></div>
                  <div className="mt-3 text-[22px] font-semibold text-white tracking-tight">Create your account</div>
                  <div className="text-[13px] text-violet-200/75 mt-1">{isAgent ? 'Register for Agent Workspace' : 'Register for Customer Portal'}</div>
                </div>
                {error && <div className="mb-3 text-sm text-rose-200 bg-rose-500/10 border border-rose-400/30 rounded-lg px-3 py-2">{error}</div>}
                <form onSubmit={submit} className="space-y-3.5">
                  <div><label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Full name</label><input required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" /></div>
                  <div><label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label><input type="email" required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" /></div>
                  <div><label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label><input type="password" required minLength={6} className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 6 characters" /></div>
                  <div><label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Confirm password</label><input type="password" required minLength={6} className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Re-enter password" /></div>
                  <button type="submit" disabled={loading} className="login-submit-btn w-full rounded-xl bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500 text-white font-semibold text-sm py-2.5">{loading ? 'Creating account…' : 'Create account'}</button>
                  <p className="text-center text-xs text-violet-200/70 pt-1">Already have an account?{' '}<button type="button" onClick={() => setMode('signin')} className="text-white font-semibold">Sign in</button></p>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
