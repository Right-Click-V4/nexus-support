#!/usr/bin/env python3
"""Profile: resilient save, Contact No., no Timezone, password merged into profile card."""
from pathlib import Path
import re

p = Path("src/components/ProfilePage.tsx")
t = p.read_text()

# Always repair known bad escape if present
if "characters');\\n" in t:
    t = t.replace("characters');\\n", "characters');\n")
    print("repaired escaped newline")

if "profile-rework-v1" in t and "Optional" in t and "Contact No." in t:
    p.write_text(t)
    print("profile already (repaired if needed)")
    raise SystemExit(0)

if "profile-rework-v1" in t:
    t = t.replace("/* profile-rework-v1 */\n", "", 1)

old_save_start = "  const saveProfile = async (e: React.FormEvent) => {"
old_save_end = "  const changePassword = async (e: React.FormEvent) => {"
i = t.find(old_save_start)
j = t.find(old_save_end)
if i >= 0 and j > i:
    new_save = (
        "  const saveProfile = async (e: React.FormEvent) => {\n"
        "    e.preventDefault();\n"
        "    setMsg('');\n"
        "    setErr('');\n"
        "    setSaving(true);\n"
        "    try {\n"
        "      if (supabase && user) {\n"
        "        try {\n"
        "          await supabase.auth.updateUser({\n"
        "            data: { full_name: name.trim(), avatar_url: avatarUrl || null },\n"
        "          });\n"
        "        } catch {\n"
        "          /* auth metadata optional */\n"
        "        }\n"
        "        if (currentAgent) {\n"
        "          const parts = name.trim().split(/\\s+/);\n"
        "          const initials = parts.map((p) => p[0]).join('').slice(0, 2).toUpperCase() || 'AG';\n"
        "          const base: Record<string, unknown> = {\n"
        "            name: name.trim(),\n"
        "            initials,\n"
        "            phone: phone.trim() || null,\n"
        "            bio: bio.trim() || null,\n"
        "          };\n"
        "          let lastErr: { message?: string } | null = null;\n"
        "          const attempts: Record<string, unknown>[] = [\n"
        "            { ...base, avatar_url: avatarUrl || null },\n"
        "            { ...base },\n"
        "            { name: name.trim(), initials, phone: phone.trim() || null },\n"
        "            { name: name.trim(), initials },\n"
        "          ];\n"
        "          let ok = false;\n"
        "          for (const patch of attempts) {\n"
        "            const { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);\n"
        "            if (!error) {\n"
        "              ok = true;\n"
        "              break;\n"
        "            }\n"
        "            lastErr = error;\n"
        "          }\n"
        "          if (!ok && lastErr) {\n"
        "            throw new Error(lastErr.message || 'Could not save profile');\n"
        "          }\n"
        "        }\n"
        "        try {\n"
        "          await refresh();\n"
        "        } catch {\n"
        "          /* ignore */\n"
        "        }\n"
        "      }\n"
        "      if (currentAgent) {\n"
        "        try {\n"
        "          if (avatarUrl) localStorage.setItem(`nexus-avatar-${currentAgent.id}`, avatarUrl);\n"
        "          else localStorage.removeItem(`nexus-avatar-${currentAgent.id}`);\n"
        "        } catch {}\n"
        "      }\n"
        "      try {\n"
        "        await updateAgentStatus(\n"
        "          status === 'offline' ? 'online' : status,\n"
        "          status === 'custom' ? statusMessage.trim() || null : null,\n"
        "          status === 'custom' ? statusEmoji || null : null,\n"
        "        );\n"
        "      } catch {\n"
        "        /* optional */\n"
        "      }\n"
        "      if (password.trim()) {\n"
        "        if (password.trim().length < 6) throw new Error('Password must be at least 6 characters');\n"
        "        if (!supabase) throw new Error('Cloud auth required to change password');\n"
        "        const { error: pwErr } = await supabase.auth.updateUser({ password: password.trim() });\n"
        "        if (pwErr) throw pwErr;\n"
        "        setPassword('');\n"
        "        setMsg('Profile and password saved.');\n"
        "      } else {\n"
        "        setMsg('Profile saved.');\n"
        "      }\n"
        "    } catch (e: unknown) {\n"
        "      setErr(e instanceof Error ? e.message : 'Could not save profile');\n"
        "    } finally {\n"
        "      setSaving(false);\n"
        "    }\n"
        "  };\n\n"
    )
    rest = t[j:]
    k = rest.find("\n  return (")
    if k > 0 and "changePassword" in rest[: min(k, 800)]:
        t = t[:i] + new_save + rest[k:]
        print("save replaced, changePassword removed")
    else:
        t = t[:i] + new_save + t[j:]
        print("save replaced")

t = t.replace(">Phone</label>", ">Contact No.</label>", 1)
t = t.replace('placeholder="+1 555 000 0000"', 'placeholder="e.g. 09XX XXX XXXX"', 1)
t2, n = re.subn(r'\s*<div>\s*<label[^>]*>Timezone</label>[\s\S]*?</select>\s*</div>', '', t, count=1)
if n:
    t = t2
    print("timezone removed")
t2, n = re.subn(
    r'\s*<div className="bg-white rounded-2xl border border-zinc-200 shadow-card p-8">\s*<h2[^>]*>Change password</h2>[\s\S]*?Update password[\s\S]*?</form>\s*</div>',
    '', t, count=1)
if n:
    t = t2
    print("pw card removed")
save_btn = (
    "          <button\n"
    "            type=\"submit\"\n"
    "            disabled={saving || uploading}\n"
    "            className=\"w-full py-3 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 disabled:opacity-50 transition-colors\"\n"
    "          >\n"
    "            {saving ? 'Saving...' : 'Save profile'}\n"
    "          </button>"
)
pw_fields = (
    "          <div className=\"pt-2 border-t border-zinc-200 dark:border-white/10\">\n"
    "            <label className=\"block text-sm font-medium text-zinc-700 dark:text-zinc-200 mb-1\">Change password</label>\n"
    "            <p className=\"text-xs text-zinc-500 mb-2\">Optional — leave blank to keep your current password.</p>\n"
    "            <input\n"
    "              type=\"password\"\n"
    "              value={password}\n"
    "              onChange={(e) => setPassword(e.target.value)}\n"
    "              minLength={6}\n"
    "              placeholder=\"New password (min 6 characters)\"\n"
    "              className=\"w-full px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400\"\n"
    "              autoComplete=\"new-password\"\n"
    "            />\n"
    "          </div>\n\n"
) + save_btn
if save_btn in t and "Optional — leave blank" not in t:
    t = t.replace(save_btn, pw_fields, 1)
    print("pw merged")
if "profile-rework-v1" not in t:
    t = "/* profile-rework-v1 */\n" + t
p.write_text(t)
print("done", len(t.splitlines()))
