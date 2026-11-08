import { useState, useEffect, useRef, type FormEvent } from 'react';
import {
  Camera,
  Phone,
  Briefcase,
  KeyRound,
  Eye,
  EyeOff,
  Check,
  User,
  Mail,
  Shield,
  AtSign,
  LogOut,
} from 'lucide-react';

/** Resize image to max edge px as JPEG data-URL (keeps Supabase metadata small). */
function compressAvatar(dataUrl: string, maxEdge = 128, quality = 0.82): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      try {
        const scale = Math.min(1, maxEdge / Math.max(img.width, img.height));
        const w = Math.max(1, Math.round(img.width * scale));
        const h = Math.max(1, Math.round(img.height * scale));
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          resolve(dataUrl);
          return;
        }
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL('image/jpeg', quality));
      } catch {
        resolve(dataUrl);
      }
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

/** Avatar cache must be per-account (email), never a shared browser key. */
function avatarCacheKey(email: string) {
  const e = (email || '').trim().toLowerCase();
  return e ? `nexus-portal-avatar:${e}` : '';
}
function writeAvatarCache(email: string, dataUrl: string) {
  try {
    const k = avatarCacheKey(email);
    if (!k) return;
    localStorage.setItem(k, dataUrl);
    localStorage.removeItem('nexus-portal-avatar');
  } catch {
    /* ignore */
  }
}
function readAvatarCache(email: string): string {
  try {
    const k = avatarCacheKey(email);
    if (!k) return '';
    return localStorage.getItem(k) || '';
  } catch {
    return '';
  }
}

export type AccountProfilePanelProps = {
  legalName: string;
  email: string;
  initials: string;
  avatarUrl: string;
  nickname: string;
  phone: string;
  jobTitle: string;
  requiresAuth: boolean;
  onSignOut: () => void;
  updateProfile: (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
  }) => Promise<void>;
  updatePassword: (newPassword: string) => Promise<void>;
  updateEmail?: (newEmail: string) => Promise<void>;
};

function AccountProfilePanel({
  legalName,
  email,
  initials,
  avatarUrl: initialAvatar,
  nickname: initialNick,
  phone: initialPhone,
  jobTitle: initialJob,
  requiresAuth,
  onSignOut,
  updateProfile,
  updatePassword,
  updateEmail,
}: AccountProfilePanelProps) {
  const [username, setUsername] = useState(initialNick);
  const [phone, setPhone] = useState(initialPhone);
  const [jobTitle, setJobTitle] = useState(initialJob);
  const [avatar, setAvatar] = useState(initialAvatar || readAvatarCache(email));
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  const [newEmail, setNewEmail] = useState('');
  const [emailBusy, setEmailBusy] = useState(false);
  const [emailMsg, setEmailMsg] = useState('');
  const [emailErr, setEmailErr] = useState('');

  const [pw, setPw] = useState('');
  const [pw2, setPw2] = useState('');
  const [pwBusy, setPwBusy] = useState(false);
  const [pwMsg, setPwMsg] = useState('');
  const [pwErr, setPwErr] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [showPw2, setShowPw2] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setUsername(initialNick);
    setPhone(initialPhone);
    setJobTitle(initialJob);
    const next = initialAvatar || readAvatarCache(email);
    setAvatar(next);
  }, [initialNick, initialPhone, initialJob, initialAvatar, email]);

  const field =
    'w-full px-3.5 py-2.5 text-sm rounded-xl border border-white/20 bg-black/30 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/35 focus:border-fuchsia-400/40 transition';
  const fieldLocked =
    'w-full px-3.5 py-2.5 text-sm rounded-xl border border-white/10 bg-black/20 text-zinc-400 cursor-not-allowed';
  const label = 'block text-xs font-medium text-zinc-300 mb-1.5';
  const card =
    'rounded-2xl border border-white/10 bg-white/[0.06] backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.25)]';

  const onAvatar = async (file: File | null) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setErr('Please choose an image file.');
      return;
    }
    if (file.size > 2_000_000) {
      setErr('Avatar must be under 2 MB.');
      return;
    }
    setErr('');
    const reader = new FileReader();
    reader.onload = async () => {
      const raw = String(reader.result || '');
      const compressed = await compressAvatar(raw);
      setAvatar(compressed);
      writeAvatarCache(email, compressed);
    };
    reader.readAsDataURL(file);
  };

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setErr('');
    setMsg('');
    try {
      let avatarToSave: string | null = avatar || null;
      if (avatarToSave && avatarToSave.startsWith('data:') && avatarToSave.length > 40_000) {
        avatarToSave = await compressAvatar(avatarToSave, 128, 0.78);
        setAvatar(avatarToSave);
      }
      await updateProfile({
        nickname: username.trim() || '',
        phone: phone.trim() || '',
        job_title: jobTitle.trim() || '',
        avatar_url: avatarToSave,
      });
      if (avatarToSave) writeAvatarCache(email, avatarToSave);
      setMsg('Updated Profile');
      try {
        window.dispatchEvent(new CustomEvent('nexus-profile-updated'));
      } catch {
        /* ignore */
      }
    } catch (ex: unknown) {
      setErr(ex instanceof Error ? ex.message : 'Could not save profile');
    } finally {
      setSaving(false);
    }
  };

  const changeEmail = async (e: FormEvent) => {
    e.preventDefault();
    setEmailErr('');
    setEmailMsg('');
    if (!updateEmail) {
      setEmailErr('Email change is not available right now.');
      return;
    }
    const next = newEmail.trim().toLowerCase();
    if (!next || !next.includes('@')) {
      setEmailErr('Enter a valid email address.');
      return;
    }
    if (next === (email || '').trim().toLowerCase()) {
      setEmailErr('That is already your current email.');
      return;
    }
    setEmailBusy(true);
    try {
      await updateEmail(next);
      setEmailMsg('Check your inbox — confirm the new email to finish the change.');
      setNewEmail('');
    } catch (ex: unknown) {
      setEmailErr(ex instanceof Error ? ex.message : 'Could not update email');
    } finally {
      setEmailBusy(false);
    }
  };

  const changePw = async (e: FormEvent) => {
    e.preventDefault();
    setPwErr('');
    setPwMsg('');
    if (pw.length < 6) {
      setPwErr('Password must be at least 6 characters.');
      return;
    }
    if (pw !== pw2) {
      setPwErr('Passwords do not match.');
      return;
    }
    setPwBusy(true);
    try {
      await updatePassword(pw);
      setPw('');
      setPw2('');
      setPwMsg('Password updated.');
    } catch (ex: unknown) {
      setPwErr(ex instanceof Error ? ex.message : 'Could not update password');
    } finally {
      setPwBusy(false);
    }
  };

  const displayLine = username.trim()
    ? `${legalName} (${username.trim()})`
    : legalName;

  return (
    <div className="w-full max-w-3xl mx-auto space-y-4 pb-4">
      {/* Hero */}
      <section className={`${card} overflow-hidden`}>
        <div className="relative px-5 py-6 sm:px-8 sm:py-7">
          <div
            className="pointer-events-none absolute inset-0 opacity-60"
            style={{
              background:
                'radial-gradient(ellipse 80% 60% at 15% 20%, rgba(192,38,211,0.22), transparent 55%), radial-gradient(ellipse 70% 50% at 85% 80%, rgba(99,102,241,0.18), transparent 50%)',
            }}
          />
          <div className="relative flex flex-col sm:flex-row items-center gap-5">
            <div className="relative shrink-0">
              {avatar ? (
                <img
                  src={avatar}
                  alt=""
                  className="w-24 h-24 sm:w-28 sm:h-28 rounded-full object-cover ring-2 ring-fuchsia-400/40 shadow-xl shadow-fuchsia-900/30"
                />
              ) : (
                <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-gradient-to-br from-fuchsia-500 via-violet-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-semibold shadow-xl shadow-violet-900/40 ring-2 ring-white/20">
                  {initials}
                </div>
              )}
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="absolute -bottom-1 -right-1 w-9 h-9 rounded-full bg-gradient-to-br from-fuchsia-500 to-violet-600 text-white flex items-center justify-center shadow-lg hover:brightness-110 border border-white/20"
                title="Change avatar"
              >
                <Camera size={15} />
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => void onAvatar(e.target.files?.[0] || null)}
              />
            </div>
            <div className="text-center sm:text-left min-w-0 flex-1">
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-fuchsia-300/90">
                Your profile
              </p>
              <h1 className="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-white truncate">
                {displayLine}
              </h1>
              <p className="mt-1 text-sm text-zinc-400 truncate flex items-center justify-center sm:justify-start gap-1.5">
                <Mail size={13} className="opacity-70 shrink-0" />
                {email}
              </p>
              <p className="mt-2 text-[12px] text-zinc-500 leading-relaxed max-w-md">
                Update your display name, contact details, and security settings. Full name stays locked to your registered account.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Profile details */}
      <section className={`${card} p-5 sm:p-6`}>
        <div className="flex items-center gap-2.5 mb-5">
          <div className="w-9 h-9 rounded-xl bg-fuchsia-500/15 text-fuchsia-300 flex items-center justify-center">
            <User size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Personal information</h2>
            <p className="text-[11px] text-zinc-400">Nickname appears on tickets and Live Chat.</p>
          </div>
        </div>

        <form onSubmit={saveProfile} className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-3.5">
            <div>
              <label className={label}>Full name</label>
              <input value={legalName} readOnly className={fieldLocked} title="Locked to registered name" />
            </div>
            <div>
              <label className={label}>Current email</label>
              <input value={email} readOnly className={fieldLocked} title="Change email in the section below" />
            </div>
            <div>
              <label className={label}>
                <span className="inline-flex items-center gap-1.5">
                  <AtSign size={12} /> Username / nickname
                </span>
              </label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="How agents should see you"
                maxLength={40}
                className={field}
              />
            </div>
            <div>
              <label className={label}>
                <span className="inline-flex items-center gap-1.5">
                  <Phone size={12} /> Contact number
                </span>
              </label>
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="e.g. +63 9xx xxx xxxx"
                maxLength={30}
                className={field}
              />
            </div>
            <div className="sm:col-span-2">
              <label className={label}>
                <span className="inline-flex items-center gap-1.5">
                  <Briefcase size={12} /> Job title
                </span>
              </label>
              <input
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Branch cashier, Store manager"
                maxLength={60}
                className={field}
              />
            </div>
          </div>

          {err && (
            <div className="text-sm text-rose-300 bg-rose-500/10 border border-rose-500/25 px-3 py-2 rounded-xl">
              {err}
            </div>
          )}
          {msg && (
            <div className="text-sm text-emerald-300 bg-emerald-500/10 border border-emerald-500/25 px-3 py-2 rounded-xl inline-flex items-center gap-2">
              <Check size={15} className="shrink-0" />
              {msg}
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-fuchsia-600 to-violet-600 hover:from-fuchsia-500 hover:to-violet-500 shadow-lg shadow-fuchsia-900/30 disabled:opacity-50 transition"
          >
            {saving ? 'Saving…' : 'Save profile'}
          </button>
        </form>
      </section>

      {/* Email change */}
      <section className={`${card} p-5 sm:p-6`}>
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-9 h-9 rounded-xl bg-sky-500/15 text-sky-300 flex items-center justify-center">
            <Mail size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Change email</h2>
            <p className="text-[11px] text-zinc-400">
              We will send a confirmation link to the new address.
            </p>
          </div>
        </div>
        <form onSubmit={changeEmail} className="space-y-3 max-w-md">
          <div>
            <label className={label}>New email address</label>
            <input
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="you@example.com"
              className={field}
              autoComplete="email"
            />
          </div>
          {emailErr && <div className="text-sm text-rose-300">{emailErr}</div>}
          {emailMsg && <div className="text-sm text-emerald-300">{emailMsg}</div>}
          <button
            type="submit"
            disabled={emailBusy || !updateEmail}
            className="px-4 py-2 rounded-xl text-sm font-semibold border border-white/15 bg-white/10 text-white hover:bg-white/15 disabled:opacity-50 transition"
          >
            {emailBusy ? 'Sending…' : 'Update email'}
          </button>
        </form>
      </section>

      {/* Password */}
      <section className={`${card} p-5 sm:p-6`}>
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-9 h-9 rounded-xl bg-amber-500/15 text-amber-300 flex items-center justify-center">
            <KeyRound size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Change password</h2>
            <p className="text-[11px] text-zinc-400">Use at least 6 characters.</p>
          </div>
        </div>
        <form onSubmit={changePw} className="space-y-3 max-w-md">
          <div>
            <label className={label}>New password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                value={pw}
                onChange={(e) => setPw(e.target.value)}
                className={field + ' pr-10'}
                autoComplete="new-password"
                minLength={6}
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded-md text-zinc-400 hover:text-white"
                title={showPw ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div>
            <label className={label}>Confirm password</label>
            <div className="relative">
              <input
                type={showPw2 ? 'text' : 'password'}
                value={pw2}
                onChange={(e) => setPw2(e.target.value)}
                className={field + ' pr-10'}
                autoComplete="new-password"
                minLength={6}
              />
              <button
                type="button"
                onClick={() => setShowPw2((v) => !v)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded-md text-zinc-400 hover:text-white"
                title={showPw2 ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showPw2 ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          {pwErr && <div className="text-sm text-rose-300">{pwErr}</div>}
          {pwMsg && <div className="text-sm text-emerald-300">{pwMsg}</div>}
          <button
            type="submit"
            disabled={pwBusy}
            className="px-4 py-2 rounded-xl text-sm font-semibold border border-white/15 bg-white/10 text-white hover:bg-white/15 disabled:opacity-50 transition"
          >
            {pwBusy ? 'Updating…' : 'Update password'}
          </button>
        </form>
      </section>

      {/* Session */}
      {requiresAuth && (
        <section className={`${card} p-5 sm:p-6`}>
          <div className="flex flex-col sm:flex-row sm:items-center gap-4 justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-zinc-500/20 text-zinc-300 flex items-center justify-center">
                <Shield size={16} />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white">Session</h2>
                <p className="text-[11px] text-zinc-400">Sign out on shared devices when you are done.</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onSignOut}
              className="inline-flex items-center justify-center gap-2 w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold border border-white/15 bg-white/5 text-zinc-100 hover:bg-white/10 transition"
            >
              <LogOut size={15} />
              Sign out
            </button>
          </div>
        </section>
      )}
    </div>
  );
}

export default AccountProfilePanel;
