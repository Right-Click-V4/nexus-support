/* login: autofill off, forgot password, signup placeholders */
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
  const { signIn, signUp, loading, error, clearError, resetPassword } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup' | 'forgot'>('signin');
  const [forgotSent, setForgotSent] = useState(false);
  const [role, setRole] = useState<'customer' | 'agent'>(audience === 'agent' ? 'agent' : 'customer');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const isAgent = role === 'agent';
  const caps = isAgent ? AGENT_CAPS : CUSTOMER_CAPS;
  const leftTitle = isAgent ? 'Resolve faster.' : 'Get help, fast.';
  const leftSub = isAgent
    ? 'Stay organized across every branch.'
    : 'Submit requests, chat live, and track every ticket.';
  const leftBlurb = isAgent
    ? 'Nexus Ops connects your customer portal, live chat, and agent desk. Route by branch, track SLA, and keep every conversation in one place.'
    : 'Open a request, talk to an agent in real time, or check the status of an existing ticket — all from one place.';

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError?.();
    if (mode === 'signup') {
      if (password !== confirm) {
        setLocalError('Passwords do not match');
        return;
      }
      markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');
      await signUp(email, password, name, role);
      return;
    }
    markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');
    await signIn(email, password);
  };

  const err = localError || error;

  return (
    <div className="login-screen-fit relative min-h-screen w-full overflow-hidden text-violet-50">
      <CosmicFallBackground />
      <div className="relative z-10 flex min-h-[100dvh] w-full items-center justify-between gap-10 px-12 sm:px-16 xl:px-24 2xl:px-32">
        <div className="hidden lg:flex flex-col justify-center shrink-0 py-10 pl-2 xl:pl-4 max-w-[340px] xl:max-w-[380px]">
          <div className="flex items-center gap-2.5 mb-5">
            <div className="login-brand-badge">
              <NexusLogoMark size={22} />
            </div>
            <div>
              <NexusWordmark className="text-base font-semibold tracking-tight text-white" />
              <div className="text-[10px] text-violet-300/70">
                {isAgent ? 'Support operations platform' : 'Customer support portal'}
              </div>
            </div>
          </div>

          <p className="login-eyebrow text-[9px] sm:text-[10px] font-semibold uppercase tracking-[0.24em] text-violet-300/85 mb-2.5">
            {isAgent ? 'Built for agent teams' : 'Built for customers'}
          </p>
          <h1 className="login-hero-title text-[1.55rem] sm:text-[1.85rem] xl:text-[2.15rem] font-semibold leading-[1.15] tracking-[-0.025em]">
            {leftTitle}
            <span className="login-hero-sub block font-medium mt-1">
              {leftSub}
            </span>
          </h1>
          <p className="login-hero-blurb mt-3 text-[12px] sm:text-[13px] text-violet-100/65 leading-[1.6] max-w-sm">
            {leftBlurb}
          </p>

          <div className="login-hero-chips mt-4 flex flex-wrap gap-1.5">
            {(isAgent
              ? ['Omnichannel inbox', 'SLA tracking', 'Branch routing']
              : ['Live status', 'Secure portal', '24/7 desk']
            ).map((tag) => (
              <span key={tag} className="login-chip">
                {tag}
              </span>
            ))}
          </div>

          <ul className="mt-5 space-y-2 max-w-sm">
            {caps.map((c, i) => (
              <li key={c.title} className="login-cap group">
                <span className="login-cap-index">{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <div className="text-[12px] sm:text-[13px] font-semibold text-violet-50 tracking-tight">{c.title}</div>
                  <div className="text-[11px] text-violet-200/50 mt-0.5 leading-snug">{c.blurb}</div>
                </div>
              </li>
            ))}
          </ul>

          <div className="login-left-footer mt-5 pt-1 text-[10px] text-violet-300/40 tracking-wide">
            {isAgent
              ? 'NexusOps Agent Workspace · © 2026 Lizer & Kirzhian'
              : 'NexusOps Customer Portal · © 2026 Lizer & Kirzhian'}
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center lg:justify-end py-8 min-w-0 pr-2 xl:pr-6">
          {mode === 'signin' ? (
            <form
              onSubmit={onSubmit}
              className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 space-y-4"
              autoComplete="off"
            >
              <div className="flex flex-col items-center gap-2 mb-1">
                <div className="login-card-logo">
                  <NexusLogoMark size={28} />
                </div>
                <div className="text-center">
                  <NexusWordmark className="text-xl font-semibold text-white" />
                  <p className="text-xs text-violet-200/70 mt-0.5">
                    {isAgent ? 'Sign in to Agent Workspace' : 'Sign in to Customer Portal'}
                  </p>
                </div>
              </div>

              <div className="flex gap-2 p-1 rounded-xl bg-black/20 border border-white/10">
                <button
                  type="button"
                  className={`login-tab ${!isAgent ? 'login-tab-on' : ''}`}
                  onClick={() => {
                    setRole('customer');
                    clearError?.();
                  }}
                >
                  Customer
                </button>
                <button
                  type="button"
                  className={`login-tab ${isAgent ? 'login-tab-on' : ''}`}
                  onClick={() => {
                    setRole('agent');
                    clearError?.();
                  }}
                >
                  Agent
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label>
                <input
                  type="email"
                  required
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="none"
                  spellCheck={false}
                  name="nexus-email"
                  readOnly
                  onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-14"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    name="nexus-password"
                    readOnly
                    onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-[11px] font-semibold text-violet-200/80 px-2 py-1 rounded-lg hover:bg-white/5"
                    onClick={() => setShowPassword((v) => !v)}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              {err && <p className="text-sm text-rose-300">{err}</p>}

              <button
                type="submit"
                disabled={loading}
                className="login-submit-btn w-full rounded-xl text-white font-semibold text-sm py-2.5 disabled:opacity-60"
              >
                {loading ? 'Signing in…' : 'Sign in'}
              </button>

              <p className="text-center text-xs text-violet-200/70">
                New here?{' '}
                <button
                  type="button"
                  className="text-white font-semibold hover:underline"
                  onClick={() => {
                    setMode('signup');
                    setPassword('');
                    setConfirm('');
                    setName('');
                    setLocalError(null);
                    clearError?.();
                  }}
                >
                  Create a customer account
                </button>
              </p>
              <p className="text-center text-xs text-violet-300/50">
                <button
                  type="button"
                  className="hover:text-violet-100 hover:underline"
                  onClick={() => {
                    setMode('forgot');
                    setForgotSent(false);
                    setLocalError(null);
                    clearError?.();
                  }}
                >
                  Forgot Password?
                </button>
              </p>
            </form>
          ) : mode === 'forgot' ? (
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                setLocalError(null);
                clearError?.();
                if (!email.trim()) {
                  setLocalError('Enter your email to reset password');
                  return;
                }
                try {
                  await resetPassword?.(email.trim());
                  setForgotSent(true);
                } catch (err: any) {
                  setLocalError(err?.message || 'Could not send reset email');
                }
              }}
              className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 space-y-4"
              autoComplete="off"
            >
              <div className="flex flex-col items-center gap-2 mb-1">
                <div className="login-card-logo">
                  <NexusLogoMark size={28} />
                </div>
                <div className="text-center">
                  <NexusWordmark className="text-xl font-semibold text-white" />
                  <p className="text-xs text-violet-200/70 mt-0.5">Reset your password</p>
                </div>
              </div>
              {forgotSent ? (
                <p className="text-sm text-emerald-300/90 text-center leading-relaxed">
                  If an account exists for that email, a reset link has been sent. Check your inbox.
                </p>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label>
                    <input
                      type="email"
                      required
                      className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                      placeholder="you@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      autoComplete="off"
                      name="nexus-forgot-email"
                      readOnly
                      onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                    />
                  </div>
                  {err && <p className="text-sm text-rose-300">{err}</p>}
                  <button
                    type="submit"
                    disabled={loading}
                    className="login-submit-btn w-full rounded-xl text-white font-semibold text-sm py-2.5 disabled:opacity-60"
                  >
                    {loading ? 'Sending…' : 'Send reset link'}
                  </button>
                </>
              )}
              <p className="text-center text-xs text-violet-200/70 pt-1">
                <button type="button" onClick={() => { setMode('signin'); setForgotSent(false); }} className="text-white font-semibold hover:underline">
                  Back to sign in
                </button>
              </p>
            </form>
          ) : (
            <form
              onSubmit={onSubmit}
              className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 space-y-3.5"
              autoComplete="off"
            >
              <div className="flex flex-col items-center gap-2 mb-1">
                <div className="login-card-logo">
                  <NexusLogoMark size={28} />
                </div>
                <div className="text-center">
                  <NexusWordmark className="text-xl font-semibold text-white" />
                  <p className="text-xs text-violet-200/70 mt-0.5">Create your customer account</p>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Full name</label>
                <input
                  required
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  placeholder="Your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoComplete="off"
                  name="nexus-fullname"
                  readOnly
                  onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label>
                <input
                  type="email"
                  required
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="none"
                  spellCheck={false}
                  name="nexus-signup-email"
                  readOnly
                  onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label>
                <input
                  type="password"
                  required
                  minLength={6}
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                  name="nexus-signup-password"
                  readOnly
                  onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Confirm password</label>
                <input
                  type="password"
                  required
                  minLength={6}
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  placeholder="Re-enter password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  autoComplete="new-password"
                  name="nexus-signup-confirm"
                  readOnly
                  onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                />
              </div>
              {err && <p className="text-sm text-rose-300">{err}</p>}
              <button
                type="submit"
                disabled={loading}
                className="login-submit-btn w-full rounded-xl text-white font-semibold text-sm py-2.5 disabled:opacity-60"
              >
                {loading ? 'Creating…' : 'Create account'}
              </button>
              <p className="text-center text-xs text-violet-200/70 pt-1">
                Already have an account?{' '}
                <button type="button" onClick={() => setMode('signin')} className="text-white font-semibold">
                  Sign in
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
