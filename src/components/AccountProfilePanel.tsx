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
  const [avatar, setAvatar] = useState(initialAvatar);
  const [emailEdit, setEmailEdit] = useState(email);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [toast, setToast] = useState(false);
  const [pw, setPw] = useState('');
  const [pw2, setPw2] = useState('');
  const [pwBusy, setPwBusy] = useState(false);
  const [pwMsg, setPwMsg] = useState('');
  const [pwErr, setPwErr] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [showPw2, setShowPw2] = useState(false);
  const [emailBusy, setEmailBusy] = useState(false);
  const [emailMsg, setEmailMsg] = useState('');
  const [emailErr, setEmailErr] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setUsername(initialNick);
    setPhone(initialPhone);
    setJobTitle(initialJob);
    setAvatar(initialAvatar);
    setEmailEdit(email);
  }, [initialNick, initialPhone, initialJob, initialAvatar, email]);

  useEffect(() => {
    return () => {
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, []);

  const field =
    'w-full px-3.5 py-2.5 text-sm rounded-xl border border-white/20 dark:border-white/12 bg-white/10 dark:bg-black/25 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-400/50 transition';
  const fieldLocked =
    'w-full px-3.5 py-2.5 text-sm rounded-xl border border-white/10 bg-white/5 text-zinc-400 cursor-not-allowed';
  const label = 'block text-[11px] font-semibold uppercase tracking-wider text-violet-200/80 mb-1.5';
  const card =
    'rounded-2xl border border-white/15 bg-white/[0.07] backdrop-blur-xl shadow-[0_20px_50px_-20px_rgba(0,0,0,0.55)]';

  const onAvatar = (file: File | null) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setErr('Please choose an image file.');
      return;
    }
    if (file.size > 4_000_000) {
      setErr('Avatar must be under 4 MB.');
      return;
    }
    const reader = new FileReader();
    reader.onload = async () => {
      const raw = String(reader.result || '');
      const dataUrl = await compressAvatar(raw, 128, 0.82);
      setAvatar(dataUrl);
      try {
        writeAvatarCache(email, dataUrl);
      } catch {
        /* ignore */
      }
    };
    reader.readAsDataURL(file);
  };

  const showToast = () => {
    setToast(true);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(false), 2800);
  };

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setErr('');
    setMsg('');
    try {
      let avatarToSave = avatar || null;
      if (avatarToSave && avatarToSave.startsWith('data:') && avatarToSave.length > 80_000) {
        avatarToSave = await compressAvatar(avatarToSave, 96, 0.75);
      }
      await updateProfile({
        nickname: username.trim() || '',
        phone: phone.trim() || '',
        job_title: jobTitle.trim() || '',
        avatar_url: avatarToSave,
      });
      if (avatarToSave) {
        try {
          writeAvatarCache(email, avatarToSave);
        } catch {
          /* ignore */
        }
        setAvatar(avatarToSave);
      }
      try {
        window.dispatchEvent(
          new CustomEvent('nexus-profile-updated', {
            detail: { avatar_url: avatarToSave, nickname: username.trim() || '' },
          }),
        );
      } catch {
        /* ignore */
      }
      setMsg('Profile saved.');
      showToast();
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
    const next = emailEdit.trim().toLowerCase();
    if (!next || !next.includes('@')) {
      setEmailErr('Enter a valid email address.');
      return;
    }
    if (next === (email || '').trim().toLowerCase()) {
      setEmailMsg('That is already your current email.');
      return;
    }
    if (!updateEmail) {
      setEmailErr('Email change is not available right now.');
      return;
    }
    setEmailBusy(true);
    try {
      await updateEmail(next);
      setEmailMsg('Check your inbox to confirm the new email (and the old one if required).');
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

  const displayName = username.trim() ? `${legalName} (${username.trim()})` : legalName;

  return (
    <div className="w-full max-w-3xl mx-auto space-y-5 pb-6 relative">
      {toast && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[80]">
          <div className="flex items-center gap-2.5 px-4 py-3 rounded-2xl shadow-xl border border-emerald-400/40 bg-emerald-50/95 dark:bg-emerald-950/90 backdrop-blur-md">
            <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-500/30">
              <Check size={18} strokeWidth={2.5} />
            </div>
            <div>
              <div className="text-sm font-semibold text-emerald-900 dark:text-emerald-100">Updated Profile</div>
              <div className="text-[11px] text-emerald-700 dark:text-emerald-300/90">Your changes are saved.</div>
            </div>
          </div>
        </div>
      )}

      <section className={`${card} px-5 py-5 sm:px-7 sm:py-6`}>
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-fuchsia-300/90">Your profile</p>
        <h1 className="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-white">Account</h1>
        <p className="mt-1.5 text-sm text-zinc-300/90 leading-relaxed max-w-xl">
          Update your username, avatar, contact details, email, and password. Tickets and Live Chat show{' '}
          <span className="text-violet-200">Name (Username)</span>.
        </p>

        <div className="mt-6 flex flex-col sm:flex-row items-center gap-5">
          <div className="relative shrink-0">
            {avatar ? (
              <img
                src={avatar}
                alt=""
                className="w-24 h-24 rounded-full object-cover ring-2 ring-violet-300/40 shadow-lg shadow-violet-900/40"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-white text-2xl font-semibold shadow-lg shadow-violet-500/30">
                {initials}
              </div>
            )}
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="absolute -bottom-1 -right-1 w-9 h-9 rounded-full bg-violet-600 text-white flex items-center justify-center shadow-md hover:bg-violet-500 ring-2 ring-zinc-950/40"
              title="Change avatar"
            >
              <Camera size={15} />
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => onAvatar(e.target.files?.[0] || null)}
            />
          </div>
          <div className="text-center sm:text-left min-w-0">
            <div className="text-xl font-semibold text-white truncate">{displayName}</div>
            <div className="text-sm text-zinc-400 truncate flex items-center justify-center sm:justify-start gap-1.5 mt-0.5">
              <Mail size={13} className="opacity-70" />
              {email}
            </div>
            <p className="text-[11px] text-zinc-500 mt-2">Click the camera to upload a new profile photo.</p>
          </div>
        </div>
      </section>

      <section className={`${card} p-5 sm:p-6`}>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded-xl bg-violet-500/20 text-violet-200 flex items-center justify-center">
            <User size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Personal information</h2>
            <p className="text-[11px] text-zinc-400">Username and contact details agents will see.</p>
          </div>
        </div>

        <form onSubmit={saveProfile} className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-3.5">
            <div>
              <label className={label}>Full name</label>
              <input value={legalName} readOnly className={fieldLocked} title="Locked to registered name" />
            </div>
            <div>
              <label className={label}>
                <span className="inline-flex items-center gap-1">
                  <AtSign size={11} /> Username
                </span>
              </label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Choose a username"
                maxLength={40}
                className={field}
              />
            </div>
            <div>
              <label className={label}>
                <span className="inline-flex items-center gap-1">
                  <Phone size={11} /> Phone
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
            <div>
              <label className={label}>
                <span className="inline-flex items-center gap-1">
                  <Briefcase size={11} /> Job title
                </span>
              </label>
              <input
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Store manager"
                maxLength={60}
                className={field}
              />
            </div>
          </div>

          {err && (
            <div className="text-sm text-rose-300 bg-rose-500/10 border border-rose-400/25 px-3 py-2 rounded-xl">{err}</div>
          )}
          {msg && !toast && (
            <div className="text-sm text-emerald-300 bg-emerald-500/10 border border-emerald-400/25 px-3 py-2 rounded-xl">{msg}</div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25 disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save profile'}
          </button>
        </form>
      </section>

      <section className={`${card} p-5 sm:p-6`}>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded-xl bg-sky-500/15 text-sky-300 flex items-center justify-center">
            <Mail size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Email address</h2>
            <p className="text-[11px] text-zinc-400">Change the email you use to sign in.</p>
          </div>
        </div>
        <form onSubmit={changeEmail} className="space-y-3 max-w-md">
          <div>
            <label className={label}>Email</label>
            <input
              type="email"
              value={emailEdit}
              onChange={(e) => setEmailEdit(e.target.value)}
              className={field}
              autoComplete="email"
            />
          </div>
          {emailErr && <div className="text-sm text-rose-300">{emailErr}</div>}
          {emailMsg && <div className="text-sm text-emerald-300">{emailMsg}</div>}
          <button
            type="submit"
            disabled={emailBusy || !updateEmail}
            className="px-4 py-2 rounded-xl text-sm font-semibold border border-white/15 bg-white/10 text-white hover:bg-white/15 disabled:opacity-50"
          >
            {emailBusy ? 'Updating…' : 'Update email'}
          </button>
        </form>
      </section>

      <section className={`${card} p-5 sm:p-6`}>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded-xl bg-amber-500/15 text-amber-300 flex items-center justify-center">
            <KeyRound size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Change password</h2>
            <p className="text-[11px] text-zinc-400">Use a strong password you do not reuse elsewhere.</p>
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
            className="px-4 py-2 rounded-xl text-sm font-semibold border border-white/15 bg-white/10 text-white hover:bg-white/15 disabled:opacity-50"
          >
            {pwBusy ? 'Updating…' : 'Update password'}
          </button>
        </form>
      </section>

      {requiresAuth && (
        <section className={`${card} p-5 sm:p-6`}>
          <div className="flex items-center gap-2 mb-3">
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
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold border border-white/15 bg-white/5 text-zinc-100 hover:bg-white/10"
          >
            Sign out
          </button>
        </section>
      )}
    </div>
  );
}

export default AccountProfilePanel;
