import { useState, useEffect, useRef, type FormEvent } from 'react';
import { Camera, Phone, Briefcase, KeyRound, Eye, EyeOff, Check } from 'lucide-react';

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
}: {
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
}) {
  const [nick, setNick] = useState(initialNick);
  const [phone, setPhone] = useState(initialPhone);
  const [jobTitle, setJobTitle] = useState(initialJob);
  const [avatar, setAvatar] = useState(initialAvatar);
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
  const fileRef = useRef<HTMLInputElement>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setNick(initialNick);
    setPhone(initialPhone);
    setJobTitle(initialJob);
    setAvatar(initialAvatar);
  }, [initialNick, initialPhone, initialJob, initialAvatar]);

  useEffect(() => {
    return () => {
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, []);

  const field =
    'w-full px-3 py-2.5 text-sm rounded-xl border border-white/25 dark:border-white/15 bg-white/40 dark:bg-black/25 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400/50 placeholder:text-zinc-400';
  const fieldLocked =
    'w-full px-3 py-2.5 text-sm rounded-xl border border-white/20 dark:border-white/10 bg-white/20 dark:bg-black/15 text-zinc-700 dark:text-zinc-300 cursor-not-allowed opacity-90';

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
        localStorage.setItem('nexus-portal-avatar', dataUrl);
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
        nickname: nick.trim() || '',
        phone: phone.trim() || '',
        job_title: jobTitle.trim() || '',
        avatar_url: avatarToSave,
      });
      if (avatarToSave) {
        try {
          localStorage.setItem('nexus-portal-avatar', avatarToSave);
        } catch {
          /* ignore */
        }
        setAvatar(avatarToSave);
      }
      try {
        window.dispatchEvent(
          new CustomEvent('nexus-profile-updated', {
            detail: { avatar_url: avatarToSave, nickname: nick.trim() || '' },
          })
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

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4 pb-2 relative">
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

      <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-5">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-pink-600 dark:text-pink-300/90">Your profile</p>
        <h1 className="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">Account</h1>
        <p className="mt-1.5 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
          Name and email are locked to your registered account. Add a nickname, contact number, and job title so agents can identify you faster.
        </p>
      </section>

      <section className="portal-overview-glass rounded-2xl p-5 sm:p-6">
        <form onSubmit={saveProfile} className="space-y-5">
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <div className="relative shrink-0">
              {avatar ? (
                <img src={avatar} alt="" className="w-20 h-20 rounded-full object-cover ring-2 ring-white/30 shadow-lg" />
              ) : (
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-xl font-semibold shadow-lg shadow-violet-500/25">
                  {initials}
                </div>
              )}
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-violet-600 text-white flex items-center justify-center shadow-md hover:bg-violet-500"
                title="Change avatar"
              >
                <Camera size={14} />
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
              <div className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 truncate">
                {nick.trim() ? `${legalName} (${nick.trim()})` : legalName}
              </div>
              <div className="text-sm text-zinc-600 dark:text-zinc-400 truncate">{email}</div>
              <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Tickets & Live Chat show Name (Nickname).</p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Full name</label>
              <input value={legalName} readOnly className={fieldLocked} title="Locked to registered name" />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Email</label>
              <input value={email} readOnly className={fieldLocked} title="Locked to registered email" />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Nickname</label>
              <input
                value={nick}
                onChange={(e) => setNick(e.target.value)}
                placeholder="Optional display nickname"
                maxLength={40}
                className={field}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
                <span className="inline-flex items-center gap-1"><Phone size={12} /> Contact number</span>
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
              <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">
                <span className="inline-flex items-center gap-1"><Briefcase size={12} /> Job title</span>
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
            <div className="text-sm text-rose-600 dark:text-rose-400 bg-rose-50/80 dark:bg-rose-950/40 border border-rose-200/60 dark:border-rose-500/30 px-3 py-2 rounded-xl">{err}</div>
          )}
          {msg && !toast && (
            <div className="text-sm text-emerald-700 dark:text-emerald-300 bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-200/60 dark:border-emerald-500/30 px-3 py-2 rounded-xl">{msg}</div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/20 disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save profile'}
          </button>
        </form>
      </section>

      <section className="portal-overview-glass rounded-2xl p-5 sm:p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-amber-500/15 text-amber-600 dark:text-amber-300 flex items-center justify-center">
            <KeyRound size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Change password</h2>
            <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Update your sign-in password anytime.</p>
          </div>
        </div>
        <form onSubmit={changePw} className="space-y-3 max-w-md">
          <div>
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">New password</label>
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
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded-md text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
                title={showPw ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Confirm password</label>
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
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded-md text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
                title={showPw2 ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showPw2 ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          {pwErr && <div className="text-sm text-rose-600 dark:text-rose-400">{pwErr}</div>}
          {pwMsg && <div className="text-sm text-emerald-700 dark:text-emerald-300">{pwMsg}</div>}
          <button type="submit" disabled={pwBusy} className="px-4 py-2 rounded-xl text-sm font-semibold border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-900 dark:text-zinc-50 hover:bg-white/40 disabled:opacity-50">
            {pwBusy ? 'Updating…' : 'Update password'}
          </button>
        </form>
      </section>
    </div>
  );
}

export default AccountProfilePanel;
