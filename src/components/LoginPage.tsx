/* login: autofill off, forgot password, signup placeholders */
/* signup-branch-showhide-v1 */
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

const BRANCH_OPTIONS = [
  'Abucay', 'Abuyog', 'Avenida', 'Baybay', 'Burauen', 'Calbayog', 'Carigara',
  'Catarman', 'Catbalogan', 'Kananga', 'Maasin', 'Ormoc', 'Palo-Naga',
  'Palo-Pawing', 'Palo-Schisto', 'Sogod',
] as const;

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
  const [showConfirm, setShowConfirm] = useState(false);
  const [branch, setBranch] = useState('');
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
      if (!branch.trim()) {
        setLocalError('Please select your branch');
        return;
      }
      try {
        await signUp(email, password, name, role, branch);
      } catch (err) {
        setLocalError(err instanceof Error ? err.message : 'Could not create account');
      }
      return;
    }
    markJustLoggedIn(role === 'agent' ? 'agent' : 'customer');
    try {
      await signIn(email, password, role);
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Sign in failed');
    }
  };

  const err = localError || error;

  return (
    <div className="login-screen-fit relative min-h-screen w-full overflow-hidden text-violet-50">
      <CosmicFallBackground />
      <div className="relative z-10 flex min-h-[100dvh] w-full items-center justify-between gap-10 px-12 sm:px-16 xl:px-24 2xl:px-32">
        <div className="hidden lg:flex flex-col max-w-md xl:max-w-lg shrink-0">
          <div className="flex items-center gap-3 mb-6">
            <div className="login-brand-badge">
              <NexusLogoMark size={22} />
            </div>
            <div>
              <NexusWordmark className="text-lg font-semibold tracking-tight text-white" />
              <p className="text-[10px] uppercase tracking-[0.18em] text-violet-300/70">Support operations platform</p>
            </div>
          </div>
          <p className="login-eyebrow text-[9px] sm:text-[10px] font-semibold uppercase tracking-[0.24em] text-violet-300/85 mb-2.5">
            Built for agent teams
          </p>
          <h1 className="login-hero-title text-[1.55rem] sm:text-[1.85rem] xl:text-[2.15rem] font-semibold leading-[1.15] tracking-[-0.025em]">
            {leftTitle}
            <span className="login-hero-sub block font-medium mt-1">{leftSub}</span>
          </h1>
          <p className="login-hero-blurb mt-3 text-[12px] sm:text-[13px] text-violet-100/65 leading-[1.6] max-w-sm">
            {leftBlurb}
          </p>
          <div className="login-hero-chips mt-4 flex flex-wrap gap-1.5">
            {(isAgent
              ? ['Omnichannel inbox', 'SLA tracking', 'Branch routing']
              : ['Submit ticket', 'Live chat', 'Track status']
            ).map((tag) => (
              <span key={tag} className="login-chip">
                {tag}
              </span>
            ))}
          </div>
          <ul className="mt-6 space-y-2.5">
            {caps.map((c, i) => (
              <li key={c.title} className="login-cap group">
                <span className="login-cap-index">{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <div className="text-sm font-semibold text-violet-50">{c.title}</div>
                  <p className="text-[11px] text-violet-200/55 mt-0.5">{c.blurb}</p>
                </div>
              </li>
            ))}
          </ul>
          <div className="login-left-footer mt-5 pt-1 text-[10px] text-violet-300/40 tracking-wide">
            NexusOps Agent Workspace · © 2026 Lizer &amp; Kirzhian
          </div>
        </div>

        <div className="flex-1 flex justify-center lg:justify-end">
          {mode === 'signin' && (
            <form
              onSubmit={onSubmit}
              className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 space-y-4"
              autoComplete="off"
            >
              <div className="flex flex-col items-center text-center gap-2 mb-1">
                <div className="login-card-logo">
                  <NexusLogoMark size={26} />
                </div>
                <div>
                  <NexusWordmark className="text-xl font-semibold text-white" />
                  <p className="text-xs text-violet-200/70 mt-0.5">
                    Sign in to {isAgent ? 'Agent Workspace' : 'Customer Portal'}
                  </p>
                </div>
              </div>

              <div className="flex gap-2 p-1 rounded-xl bg-black/20 border border-white/10">
                <button
                  type="button"
                  className={`login-tab ${!isAgent ? 'login-tab-on' : ''}`}
                  onClick={() => {
                    setRole('customer');
                    setLocalError(null);
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
                    setLocalError(null);
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
                  autoComplete="username"
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
                    className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-14"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    name="nexus-password"
                    readOnly
                    onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-violet-200/80 hover:text-white px-2 py-1"
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
                    setBranch('');
                    setShowPassword(false);
                    setShowConfirm(false);
                    setLocalError(null);
                    clearError?.();
                  }}
                >
                  {isAgent ? 'Create an agent account' : 'Create a customer account'}
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
                  Forgot password?
                </button>
              </p>
            </form>
          )}

          {mode === 'forgot' && (
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                setLocalError(null);
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
            >
              <div className="flex flex-col items-center text-center gap-2 mb-1">
                <div className="login-card-logo">
                  <NexusLogoMark size={26} />
                </div>
                <div>
                  <NexusWordmark className="text-xl font-semibold text-white" />
                  <p className="text-xs text-violet-200/70 mt-0.5">Reset your password</p>
                </div>
              </div>
              {forgotSent ? (
                <p className="text-sm text-emerald-300/90 text-center">
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
                      name="nexus-forgot-email"
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
                <button type="button" onClick={() => setMode('signin')} className="text-white font-semibold">
                  Back to sign in
                </button>
              </p>
            </form>
          )}

          {mode === 'signup' && (
            <form
              onSubmit={onSubmit}
              className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 space-y-3.5"
              autoComplete="off"
            >
              <div className="flex flex-col items-center text-center gap-2 mb-1">
                <div className="login-card-logo">
                  <NexusLogoMark size={26} />
                </div>
                <div>
                  <NexusWordmark className="text-xl font-semibold text-white" />
                  <p className="text-xs text-violet-200/70 mt-0.5">
                    {isAgent ? 'Create your agent account' : 'Create your customer account'}
                  </p>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Full name</label>
                <input
                  required
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  name="nexus-signup-name"
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
                  autoComplete="username"
                  autoCorrect="off"
                  autoCapitalize="none"
                  spellCheck={false}
                  name="nexus-signup-email"
                  readOnly
                  onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Branch</label>
                <select
                  required
                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  name="nexus-signup-branch"
                >
                  <option value="" disabled>
                    Select your branch
                  </option>
                  {BRANCH_OPTIONS.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-14"
                    placeholder="At least 6 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    name="nexus-signup-password"
                    readOnly
                    onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-violet-200/80 hover:text-white px-2 py-1"
                    onClick={() => setShowPassword((v) => !v)}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Confirm password</label>
                <div className="relative">
                  <input
                    type={showConfirm ? 'text' : 'password'}
                    required
                    minLength={6}
                    className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none pr-14"
                    placeholder="Re-enter password"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    autoComplete="new-password"
                    name="nexus-signup-confirm"
                    readOnly
                    onFocus={(e) => e.currentTarget.removeAttribute('readOnly')}
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-violet-200/80 hover:text-white px-2 py-1"
                    onClick={() => setShowConfirm((v) => !v)}
                  >
                    {showConfirm ? 'Hide' : 'Show'}
                  </button>
                </div>
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
