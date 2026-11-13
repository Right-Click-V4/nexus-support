#!/usr/bin/env python3
"""Users: delete + clean duplicates; Edit branch only for customers; ensure customer branch required."""
from pathlib import Path
import re

u = Path("src/components/UsersAdminPage.tsx")
if not u.exists() or u.stat().st_size < 2000:
    print("UsersAdmin skip")
    raise SystemExit(0)

s = u.read_text()
if "USERS_DELETE_V1" in s:
    print("already")
    raise SystemExit(0)

if "Trash2" not in s:
    s = s.replace(
        """  KeyRound,
  Save,
} from 'lucide-react';""",
        """  KeyRound,
  Save,
  Trash2,
} from 'lucide-react';""",
    )
    print("Trash2 import")

delete_fn = '''
  // USERS_DELETE_V1
  const deleteUser = async (u: UnifiedUser) => {
    if (!supabase) return;
    const label = u.email || u.name || u.id;
    if (!window.confirm(`Remove ${label} from Users? This cannot be undone.`)) return;
    setErr('');
    setMsg('');
    try {
      if (u.kind === 'customer') {
        const { error } = await supabase.from('customers').delete().eq('id', u.id);
        if (error) throw error;
        if (u.email) {
          await supabase.from('customers').delete().ilike('email', u.email);
        }
      } else {
        const { error } = await supabase.from('agents').delete().eq('id', u.id);
        if (error) throw error;
        if (u.email) {
          await supabase.from('agents').delete().ilike('email', u.email);
        }
      }
      setMsg(`Removed ${label}.`);
      if (editing?.id === u.id) setEditing(null);
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Delete failed');
    }
  };

  const cleanDuplicateCustomers = async () => {
    if (!supabase) return;
    if (!window.confirm('Remove duplicate customer rows that have no branch (keep the row with a branch)?')) return;
    setErr('');
    setMsg('');
    try {
      const { data, error } = await supabase.from('customers').select('id, email, branch');
      if (error) throw error;
      const rows = (data || []) as { id: string; email?: string; branch?: string }[];
      const byEmail = new Map<string, typeof rows>();
      for (const r of rows) {
        const key = (r.email || '').trim().toLowerCase();
        if (!key) continue;
        const list = byEmail.get(key) || [];
        list.push(r);
        byEmail.set(key, list);
      }
      let removed = 0;
      for (const [, list] of byEmail) {
        if (list.length < 2) continue;
        const withBranch = list.filter((r) => !!(r.branch && String(r.branch).trim() && r.branch !== '\u2014'));
        const keepIds = new Set<string>();
        if (withBranch.length) keepIds.add(withBranch[0].id);
        else keepIds.add(list[0].id);
        for (const r of list) {
          if (keepIds.has(r.id)) continue;
          const { error: delErr } = await supabase.from('customers').delete().eq('id', r.id);
          if (!delErr) removed += 1;
        }
      }
      setMsg(removed ? `Removed ${removed} duplicate customer row(s).` : 'No customer duplicates to remove.');
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Cleanup failed');
    }
  };

'''

marker = "  const openEdit = (u: UnifiedUser) => {"
if marker in s and "USERS_DELETE_V1" not in s:
    s = s.replace(marker, delete_fn + marker)
    print("delete fns")
else:
    print("openEdit marker miss")

old_agent_payload = """        if (supabase) {
          const payload: Record<string, unknown> = {
            name: editName.trim(),
            role: roleLabel,
            is_admin: editAdmin,
            branch: branchVal,
          };"""
new_agent_payload = """        if (supabase) {
          const payload: Record<string, unknown> = {
            name: editName.trim(),
            role: roleLabel,
            is_admin: editAdmin,
          };"""
if old_agent_payload in s:
    s = s.replace(old_agent_payload, new_agent_payload)
    print("agent save no branch")

old_branch_block = """            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-zinc-400 mb-1 inline-flex items-center gap-1">
                <Building2 size={12} /> Branch workplace
              </label>
              <select
                value={editBranch}
                onChange={(e) => setEditBranch(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-black/30"
              >
                <option value="">\u2014</option>
                {branchNames.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>"""
# Use both em-dash and regular dash option variants
if old_branch_block not in s:
    old_branch_block = """            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-zinc-400 mb-1 inline-flex items-center gap-1">
                <Building2 size={12} /> Branch workplace
              </label>
              <select
                value={editBranch}
                onChange={(e) => setEditBranch(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-black/30"
              >
                <option value="">—</option>
                {branchNames.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>"""

new_branch_block = """            {editing.kind === 'customer' && (
              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-zinc-400 mb-1 inline-flex items-center gap-1">
                  <Building2 size={12} /> Branch workplace
                </label>
                <select
                  value={editBranch}
                  onChange={(e) => setEditBranch(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-black/30"
                >
                  <option value="">—</option>
                  {branchNames.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>
            )}"""
if old_branch_block in s:
    s = s.replace(old_branch_block, new_branch_block)
    print("branch modal customer-only")
else:
    print("branch modal miss")

if "deleteUser(u)" not in s:
    m = re.search(
        r'(onClick=\{\(\) => openEdit\(u\)\}[^>]*>[\s\S]*?</button>)',
        s,
    )
    if m:
        insert = m.group(1) + """
                <button
                  type="button"
                  title="Remove"
                  onClick={() => void deleteUser(u)}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-lg border border-rose-200/80 dark:border-rose-500/30 text-rose-600 dark:text-rose-300 hover:bg-rose-50 dark:hover:bg-rose-500/10"
                >
                  <Trash2 size={12} /> Remove
                </button>"""
        s = s.replace(m.group(1), insert, 1)
        print("row remove button")
    else:
        print("row remove miss")

if "Clean duplicates" not in s:
    if "Approve to grant workspace" in s:
        s = s.replace(
            "Approve to grant workspace or portal access.",
            """Approve to grant workspace or portal access.{" "}
              <button
                type="button"
                onClick={() => void cleanDuplicateCustomers()}
                className="text-rose-500 hover:text-rose-400 underline-offset-2 hover:underline font-medium"
              >
                Clean duplicates
              </button>""",
        )
        print("clean duplicates link")
    else:
        print("clean link miss")

u.write_text(s)
print("UsersAdmin", len(s), "braces", s.count("{") - s.count("}"))

lp = Path("src/components/LoginPage.tsx")
if lp.exists() and lp.stat().st_size > 3000:
    t = lp.read_text()
    if "if (!branch.trim())" in t and "if (!isAgent && !branch.trim())" not in t:
        t = t.replace(
            """      if (!branch.trim()) {
        setLocalError('Please select your branch');
        return;
      }""",
            """      if (!isAgent && !branch.trim()) {
        setLocalError('Please select your branch');
        return;
      }""",
        )
        print("LoginPage branch required customer-only")
    if 'name="nexus-signup-branch"' in t and "{!isAgent &&" not in t:
        t2, n = re.subn(
            r'(<div>\s*<label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Branch</label>[\s\S]*?name="nexus-signup-branch"[\s\S]*?</select>\s*</div>)',
            r"{!isAgent && (\1)}",
            t,
            count=1,
        )
        if n:
            t = t2
            print("LoginPage hide branch for agent")
    lp.write_text(t)
    print("LoginPage", len(t), "braces", t.count("{") - t.count("}"))
else:
    print("LoginPage skip")

print("patch_users_delete_branch done")
