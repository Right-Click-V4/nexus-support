#!/usr/bin/env python3
"""Add updateProfile + updatePassword to AuthContext."""
from pathlib import Path

p = Path("src/context/AuthContext.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
if "auth-profile-update-v1" in t and "updateProfile" in t:
    print("auth already")
    raise SystemExit(0)

old_iface = """  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}"""
new_iface = """  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updateProfile: (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
  }) => Promise<void>;
  updatePassword: (newPassword: string) => Promise<void>;
}"""
if old_iface not in t:
    print("FAIL iface")
    raise SystemExit(1)
t = t.replace(old_iface, new_iface, 1)

fn = """
  const updateProfile = async (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
  }) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload: Record<string, unknown> = {};
    if (data.nickname !== undefined) payload.nickname = data.nickname;
    if (data.phone !== undefined) payload.phone = data.phone;
    if (data.job_title !== undefined) payload.job_title = data.job_title;
    if (data.avatar_url !== undefined) payload.avatar_url = data.avatar_url;
    const { data: res, error } = await supabase.auth.updateUser({ data: payload });
    if (error) throw friendlyAuthError(error);
    if (res.user) setUser(res.user);
    if (res.session) setSession(res.session);
  };

  const updatePassword = async (newPassword: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    if (!newPassword || newPassword.length < 6) {
      throw new Error('Password must be at least 6 characters');
    }
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (error) throw friendlyAuthError(error);
  };

"""
if "const updateProfile = async" not in t:
    t = t.replace("  const signOut = async () => {", fn + "  const signOut = async () => {", 1)

t = t.replace(
    """        signOut,
        resetPassword,
      }}""",
    """        signOut,
        resetPassword,
        updateProfile,
        updatePassword,
      }}""",
    1,
)

if "auth-profile-update-v1" not in t:
    t = "/* auth-profile-update-v1 */\n" + t
p.write_text(t)
print("auth done", t.count("{") - t.count("}"))
