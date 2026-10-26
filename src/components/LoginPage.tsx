import { useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { markJustLoggedIn } from './PostLoginLoader';
import { CosmicFallBackground, NexusLogoMark } from './LoginScene';

interface Props {
  audience?: 'customer' | 'agent';
  onOpenPortal?: () => void;
  onOpenAgent?: () => void;
}

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

  const cardSub = isAgent ? 'Sign in to Agent Workspace' : 'Sign in to Customer Portal';

  return (
    <div className="relative min-h-screen overflow-hidden">
      <CosmicFallBackground />
      <div className="relative z-10 min-h-screen flex items-center justify-center px-5 sm:px-8 py-10">
          <div className="flex items-center justify-center w-full">
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
  );
}
