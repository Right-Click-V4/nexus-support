/* profile-rework-v1 */
/* status-active-labels-v1 */
/* emoji-beside-custom-field-v1 */
/* emoji-custom-only-v1 */
/* status-emoji-profile-v1 */
/* agent-presence-profile-v1 */
import { useState, useEffect, useRef } from 'react';
import { Camera, Trash2, ZoomIn, ZoomOut, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTickets } from '../context/TicketContext';
import { supabase } from '../lib/supabase';
import type { AgentStatus } from '../types';

const MAX_AVATAR_BYTES = 350_000;
const OUTPUT_SIZE = 256;

function cropToDataUrl(
  img: HTMLImageElement,
  crop: { x: number; y: number; size: number }
): string {
  const canvas = document.createElement('canvas');
  canvas.width = OUTPUT_SIZE;
  canvas.height = OUTPUT_SIZE;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Could not process image');
  const sx = Math.max(0, Math.min(crop.x, img.naturalWidth - 1));
  const sy = Math.max(0, Math.min(crop.y, img.naturalHeight - 1));
  const s = Math.min(crop.size, img.naturalWidth - sx, img.naturalHeight - sy);
  ctx.drawImage(img, sx, sy, s, s, 0, 0, OUTPUT_SIZE, OUTPUT_SIZE);
  let quality = 0.85;
  let dataUrl = canvas.toDataURL('image/jpeg', quality);
  while (dataUrl.length > MAX_AVATAR_BYTES && quality > 0.4) {
    quality -= 0.1;
    dataUrl = canvas.toDataURL('image/jpeg', quality);
  }
  if (dataUrl.length > MAX_AVATAR_BYTES) {
    throw new Error('Could not compress image enough. Try a simpler photo.');
  }
  return dataUrl;
}

export default function ProfilePage() {
  const { user } = useAuth();
  const { currentAgent, updateAgentStatus, refresh } = useTickets();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [bio, setBio] = useState('');
  const [timezone, setTimezone] = useState('UTC');
  const [status, setStatus] = useState<AgentStatus>('online');
  const [statusMessage, setStatusMessage] = useState('');
  const [statusEmoji, setStatusEmoji] = useState('');
  const [emojiOpen, setEmojiOpen] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const [cropSrc, setCropSrc] = useState<string | null>(null);
  const [imgNatural, setImgNatural] = useState({ w: 0, h: 0 });
  const [crop, setCrop] = useState({ x: 0, y: 0, size: 100 });
  const [dragging, setDragging] = useState(false);
  const dragStart = useRef({ mx: 0, my: 0, cx: 0, cy: 0 });
  const imgRef = useRef<HTMLImageElement | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (currentAgent) {
      setName(currentAgent.name);
      setPhone(currentAgent.phone || '');
      setBio(currentAgent.bio || '');
      setTimezone(currentAgent.timezone || 'UTC');
      setStatus(
        currentAgent.status === 'offline' || currentAgent.status === 'online'
          ? 'online'
          : currentAgent.status,
      );
      setStatusMessage(currentAgent.status_message || '');
      setStatusEmoji(currentAgent.status_emoji || '');
      setAvatarUrl(currentAgent.avatar_url || null);
      if (!currentAgent.avatar_url) {
        try {
          const local = localStorage.getItem(`nexus-avatar-${currentAgent.id}`);
          if (local) setAvatarUrl(local);
        } catch {}
      }
    } else if (user) {
      setName((user.user_metadata?.full_name as string) || user.email?.split('@')[0] || '');
      const metaAvatar = user.user_metadata?.avatar_url as string | undefined;
      if (metaAvatar) setAvatarUrl(metaAvatar);
    }
  }, [currentAgent, user]);

  const openCropper = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setErr('Please choose an image file (PNG, JPG, WebP).');
      return;
    }
    if (file.size > 8_000_000) {
      setErr('Image is too large (max ~8MB).');
      return;
    }
    setErr('');
    const url = URL.createObjectURL(file);
    setCropSrc(url);
  };

  const onCropImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    imgRef.current = img;
    const w = img.naturalWidth;
    const h = img.naturalHeight;
    setImgNatural({ w, h });
    const size = Math.min(w, h);
    setCrop({ x: (w - size) / 2, y: (h - size) / 2, size });
  };

  const zoomCrop = (factor: number) => {
    setCrop((c) => {
      const minSize = Math.min(imgNatural.w, imgNatural.h) * 0.15;
      const maxSize = Math.min(imgNatural.w, imgNatural.h);
      const size = Math.min(maxSize, Math.max(minSize, c.size * factor));
      const cx = c.x + c.size / 2;
      const cy = c.y + c.size / 2;
      let x = cx - size / 2;
      let y = cy - size / 2;
      x = Math.max(0, Math.min(x, imgNatural.w - size));
      y = Math.max(0, Math.min(y, imgNatural.h - size));
      return { x, y, size };
    });
  };

  const onPointerDown = (e: React.PointerEvent) => {
    e.preventDefault();
    setDragging(true);
    dragStart.current = { mx: e.clientX, my: e.clientY, cx: crop.x, cy: crop.y };
    (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (!dragging || !stageRef.current || !imgNatural.w) return;
    const stage = stageRef.current.getBoundingClientRect();
    const scale = Math.max(stage.width / imgNatural.w, stage.height / imgNatural.h);
    const dx = (e.clientX - dragStart.current.mx) / scale;
    const dy = (e.clientY - dragStart.current.my) / scale;
    let x = dragStart.current.cx - dx;
    let y = dragStart.current.cy - dy;
    x = Math.max(0, Math.min(x, imgNatural.w - crop.size));
    y = Math.max(0, Math.min(y, imgNatural.h - crop.size));
    setCrop((c) => ({ ...c, x, y }));
  };

  const onPointerUp = () => setDragging(false);

  const applyCrop = () => {
    if (!imgRef.current) return;
    setUploading(true);
    try {
      const dataUrl = cropToDataUrl(imgRef.current, crop);
      setAvatarUrl(dataUrl);
      setMsg('Photo ready — click Save profile to apply.');
      if (cropSrc) URL.revokeObjectURL(cropSrc);
      setCropSrc(null);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Could not crop image');
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const cancelCrop = () => {
    if (cropSrc) URL.revokeObjectURL(cropSrc);
    setCropSrc(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const clearPhoto = () => {
    setAvatarUrl(null);
    setMsg('Photo removed — click Save profile to apply.');
  };

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');
    setErr('');
    setSaving(true);
    try {
      if (supabase && user) {
        try {
          await supabase.auth.updateUser({
            data: { full_name: name.trim(), avatar_url: avatarUrl || null },
          });
        } catch {
          /* auth metadata optional */
        }
        if (currentAgent) {
          const parts = name.trim().split(/\s+/);
          const initials = parts.map((p) => p[0]).join('').slice(0, 2).toUpperCase() || 'AG';
          const base: Record<string, unknown> = {
            name: name.trim(),
            initials,
            phone: phone.trim() || null,
            bio: bio.trim() || null,
          };
          let lastErr: { message?: string } | null = null;
          const attempts: Record<string, unknown>[] = [
            { ...base, avatar_url: avatarUrl || null },
            { ...base },
            { name: name.trim(), initials, phone: phone.trim() || null },
            { name: name.trim(), initials },
          ];
          let ok = false;
          for (const patch of attempts) {
            const { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
            if (!error) {
              ok = true;
              break;
            }
            lastErr = error;
          }
          if (!ok && lastErr) {
            throw new Error(lastErr.message || 'Could not save profile');
          }
        }
        try {
          await refresh();
        } catch {
          /* ignore */
        }
      }
      if (currentAgent) {
        try {
          if (avatarUrl) localStorage.setItem(`nexus-avatar-${currentAgent.id}`, avatarUrl);
          else localStorage.removeItem(`nexus-avatar-${currentAgent.id}`);
        } catch {}
      }
      try {
        await updateAgentStatus(
          status === 'offline' ? 'online' : status,
          status === 'custom' ? statusMessage.trim() || null : null,
          status === 'custom' ? statusEmoji || null : null,
        );
      } catch {
        /* optional */
      }
      if (password.trim()) {
        if (password.trim().length < 6) throw new Error('Password must be at least 6 characters');\n        if (!supabase) throw new Error('Cloud auth required to change password');
        const { error: pwErr } = await supabase.auth.updateUser({ password: password.trim() });
        if (pwErr) throw pwErr;
        setPassword('');
        setMsg('Profile and password saved.');
      } else {
        setMsg('Profile saved.');
      }
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Could not save profile');
    } finally {
      setSaving(false);
    }
  };

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');
    setErr('');
    if (password.length < 6) {
      setErr('Password must be at least 6 characters');
      return;
    }
    setSaving(true);
    try {
      if (!supabase) throw new Error('Cloud auth required to change password');
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;
      setPassword('');
      setMsg('Password updated.');
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Could not update password');
    } finally {
      setSaving(false);
    }
  };

  const initials = (name || 'A')
    .split(' ')
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const stageW = 320;
  const stageH = 320;
  const coverScale =
    imgNatural.w > 0 ? Math.max(stageW / imgNatural.w, stageH / imgNatural.h) : 1;
  const dispW = imgNatural.w * coverScale;
  const dispH = imgNatural.h * coverScale;
  const offX = (stageW - dispW) / 2;
  const offY = (stageH - dispH) / 2;
  const frameLeft = offX + crop.x * coverScale;
  const frameTop = offY + crop.y * coverScale;
  const frameSize = crop.size * coverScale;

  return (
    <div className="max-w-2xl mx-auto space-y-8 pb-10">
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-card p-8">
        <div className="flex items-center gap-5 mb-8 pb-6 border-b border-zinc-100">
          <div className="relative group">
            <input
              ref={fileRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) openCropper(f);
              }}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={uploading}
              className="relative w-20 h-20 rounded-2xl overflow-hidden shadow-md shadow-brand-500/20 ring-2 ring-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              title="Change photo"
            >
              {avatarUrl ? (
                <img src={avatarUrl} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center text-white text-xl font-bold">
                  {initials}
                </div>
              )}
              <div className="absolute inset-0 bg-black/45 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white text-[10px] font-medium gap-0.5">
                <Camera size={18} />
                {uploading ? '...' : 'Crop & set'}
              </div>
            </button>
            {avatarUrl && (
              <button
                type="button"
                onClick={clearPhoto}
                className="absolute -bottom-1 -right-1 p-1.5 rounded-full bg-white border border-zinc-200 text-zinc-500 hover:text-rose-600 shadow-sm"
                title="Remove photo"
              >
                <Trash2 size={12} />
              </button>
            )}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xl font-semibold text-zinc-900 tracking-tight truncate">{name || 'Agent'}</div>
            <div className="text-sm text-zinc-500 mt-0.5 truncate">{user?.email}</div>
            {currentAgent && (
              <div className="text-xs text-zinc-400 mt-1.5">
                {currentAgent.role} · <span className="text-brand-600 font-medium capitalize">{
                  currentAgent.status === 'in_call'
                    ? 'In a call'
                    : currentAgent.status === 'custom'
                      ? (currentAgent.status_message || 'Custom')
                      : currentAgent.status
                }</span>
              </div>
            )}
            <p className="text-[11px] text-zinc-400 mt-2">Upload a photo, then drag and zoom to choose the crop area.</p>
          </div>
        </div>

        {msg && (
          <div className="mb-5 text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 px-4 py-3 rounded-xl">{msg}</div>
        )}
        {err && (
          <div className="mb-5 text-sm text-rose-600 bg-rose-50 border border-rose-100 px-4 py-3 rounded-xl">{err}</div>
        )}

        <form onSubmit={saveProfile} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-2">Display name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-4 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-2">Contact No.</label>
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full px-4 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                placeholder="e.g. 09XX XXX XXXX"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-200 mb-2">Status</label>
              <div className="flex gap-2 items-start">
                <select
                  value={status === 'offline' || status === 'online' ? 'online' : status}
                  onChange={(e) => {
                    const v = e.target.value as AgentStatus;
                    const next = v === 'online' ? 'online' : v;
                    setStatus(next);
                    if (next !== 'custom') {
                      setStatusEmoji('');
                      setEmojiOpen(false);
                    }
                    const msg = next === 'custom' ? statusMessage.trim() || null : null;
                    const em = next === 'custom' ? statusEmoji || null : null;
                    void updateAgentStatus(next === 'offline' ? 'online' : next, msg, em);
                  }}
                  className="flex-1 px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                >
                  <option value="online">Available (default)</option>
                  <option value="away">Away</option>
                  <option value="busy">Busy</option>
                  <option value="in_call">In a Call / Meeting</option>
                  <option value="custom">Custom Status</option>
                </select>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1">
                Online/Offline is automatic from your session. Status updates Live Chat Active Now in real time.
              </p>
              {status === 'custom' && (
                <div className="mt-2 flex gap-2 items-start">
                  <input
                    value={statusMessage}
                    onChange={(e) => setStatusMessage(e.target.value)}
                    onBlur={() => {
                      void updateAgentStatus('custom', statusMessage.trim() || null, statusEmoji || null);
                    }}
                    placeholder="Write your custom status…"
                    className="flex-1 px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-white dark:text-white placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                  />
                  <div className="relative">
                    <button
                      type="button"
                      title="Add emoji"
                      onClick={() => setEmojiOpen((o) => !o)}
                      className="h-[42px] min-w-[42px] px-2 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900/60 text-lg hover:bg-zinc-50 dark:hover:bg-white/5"
                    >
                      {statusEmoji || '😊'}
                    </button>
                    {emojiOpen && (
                      <div className="absolute right-0 z-30 mt-1 p-2 w-56 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl grid grid-cols-6 gap-1">
                        {['😊','🙂','😎','🫡','💼','📞','🎧','☕','🍔','🚗','🏠','💤','🔥','⚡','✅','❌','🟢','🟡','🟠','🔵','⚪','🛠️','💬','🚀'].map((em) => (
                          <button
                            key={em}
                            type="button"
                            className="h-8 w-8 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10 text-base"
                            onClick={() => {
                              setStatusEmoji(em);
                              setEmojiOpen(false);
                              void updateAgentStatus('custom', statusMessage.trim() || null, em);
                            }}
                          >
                            {em}
                          </button>
                        ))}
                        <button
                          type="button"
                          className="col-span-6 text-[11px] text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 py-1"
                          onClick={() => {
                            setStatusEmoji('');
                            setEmojiOpen(false);
                            void updateAgentStatus('custom', statusMessage.trim() || null, null);
                          }}
                        >
                          Clear emoji
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-2">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={4}
              className="w-full px-4 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400 resize-y"
              placeholder="Short intro for your team"
            />
          </div>

          <div className="pt-2 border-t border-zinc-200 dark:border-white/10">
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-200 mb-1">Change password</label>
            <p className="text-xs text-zinc-500 mb-2">Optional — leave blank to keep your current password.</p>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={6}
              placeholder="New password (min 6 characters)"
              className="w-full px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
              autoComplete="new-password"
            />
          </div>

          <button
            type="submit"
            disabled={saving || uploading}
            className="w-full py-3 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 disabled:opacity-50 transition-colors"
          >
            {saving ? 'Saving...' : 'Save profile'}
          </button>
        </form>
      </div>

      {cropSrc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-white rounded-2xl shadow-xl border border-zinc-200 w-full max-w-md p-5 space-y-4">
            <div>
              <h3 className="text-base font-semibold text-zinc-900">Crop profile photo</h3>
              <p className="text-xs text-zinc-500 mt-0.5">Drag the image to move. Use zoom to frame the face.</p>
            </div>
            <div
              ref={stageRef}
              className="relative mx-auto overflow-hidden rounded-xl bg-zinc-900 touch-none select-none"
              style={{ width: stageW, height: stageH, cursor: dragging ? 'grabbing' : 'grab' }}
              onPointerDown={onPointerDown}
              onPointerMove={onPointerMove}
              onPointerUp={onPointerUp}
              onPointerCancel={onPointerUp}
            >
              <img
                src={cropSrc}
                alt=""
                onLoad={onCropImageLoad}
                draggable={false}
                className="absolute max-w-none pointer-events-none"
                style={{
                  width: dispW,
                  height: dispH,
                  left: offX,
                  top: offY,
                }}
              />
              <div
                className="absolute border-2 border-white rounded-lg pointer-events-none shadow-[0_0_0_9999px_rgba(0,0,0,0.45)]"
                style={{ left: frameLeft, top: frameTop, width: frameSize, height: frameSize }}
              />
            </div>
            <div className="flex items-center justify-center gap-3">
              <button type="button" onClick={() => zoomCrop(1.15)} className="p-2 rounded-lg border border-zinc-200 hover:bg-zinc-50" title="Zoom in">
                <ZoomIn size={18} />
              </button>
              <button type="button" onClick={() => zoomCrop(1 / 1.15)} className="p-2 rounded-lg border border-zinc-200 hover:bg-zinc-50" title="Zoom out">
                <ZoomOut size={18} />
              </button>
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={cancelCrop} className="px-4 py-2 text-sm text-zinc-600 hover:text-zinc-800">
                Cancel
              </button>
              <button
                type="button"
                onClick={applyCrop}
                disabled={uploading || !imgNatural.w}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50"
              >
                <Check size={16} /> Use this crop
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
