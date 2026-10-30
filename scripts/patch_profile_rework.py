#!/usr/bin/env python3
"""Profile: resilient save, Contact No., no Timezone, password merged into profile card."""
from pathlib import Path
import re

p = Path("src/components/ProfilePage.tsx")
t = p.read_text()
if "profile-rework-v1" in t:
    print("profile already")
    raise SystemExit(0)

old_save_start = "  const saveProfile = async (e: React.FormEvent) => {"
old_save_end = "  const changePassword = async (e: React.FormEvent) => {"
i = t.find(old_save_start)
j = t.find(old_save_end)
if i < 0 or j < 0:
    print("save block miss", i, j)
else:
    new_save = r"""  const saveProfile = async (e: React.FormEvent) => {
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

"""
    t = t[:i] + new_save + t[j:]
    print("save replaced")

t = t.replace(">Phone</label>", ">Contact No.</label>", 1)
t = t.replace('placeholder="+1 555 000 0000"', 'placeholder="e.g. 09XX XXX XXXX"', 1)

t2, n = re.subn(
    r'\s*<div>\s*<label[^>]*>Timezone</label>[\s\S]*?</select>\s*</div>',
    '',
    t,
    count=1,
)
if n:
    t = t2
    print("timezone removed")

t2, n = re.subn(
    r'\s*<div className="bg-white rounded-2xl border border-zinc-200 shadow-card p-8">\s*<h2[^>]*>Change password</h2>[\s\S]*?Update password[\s\S]*?</form>\s*</div>',
    '',
    t,
    count=1,
)
if n:
    t = t2
    print("pw card removed")

save_btn = """          <button
            type="submit"
            disabled={saving || uploading}
            className="w-full py-3 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 disabled:opacity-50 transition-colors"
          >
            {saving ? 'Saving...' : 'Save profile'}
          </button>"""
pw_fields = """          <div className="pt-2 border-t border-zinc-200 dark:border-white/10">
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

""" + save_btn
if save_btn in t and "Optional — leave blank" not in t:
    t = t.replace(save_btn, pw_fields, 1)
    print("pw merged")

t = "/* profile-rework-v1 */\n" + t
p.write_text(t)
print("done", len(t.splitlines()))
