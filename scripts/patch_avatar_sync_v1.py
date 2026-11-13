#!/usr/bin/env python3
"""AVATAR_SYNC_V2: persist avatars to customers; force select cols; Users + LiveChat display."""
from pathlib import Path
import re

tc = Path("src/context/TicketContext.tsx")
if tc.exists() and tc.stat().st_size > 3000:
    s = tc.read_text()
    s2 = re.sub(
        r"const CUSTOMER_COLS = '[^']*';[^\n]*",
        "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at, avatar_url'; // AVATAR_SYNC_V2",
        s,
        count=1,
    )
    if "AVATAR_SYNC_SOFT_LOAD" not in s2 and "from('customers').select(CUSTOMER_COLS)" in s2:
        s2 = s2.replace(
            "withTimeout(supabase.from('customers').select(CUSTOMER_COLS).limit(200), 4000)",
            """withTimeout((async () => {
          // AVATAR_SYNC_SOFT_LOAD
          const full = await supabase.from('customers').select(CUSTOMER_COLS).limit(200);
          if (!full.error) return full;
          return await supabase.from('customers').select('id, name, email, role, branch, status, created_at').limit(200);
        })(), 4000)""",
        )
        print("soft load")
    tc.write_text(s2)
    print("CUSTOMER_COLS", next(ln for ln in s2.splitlines() if "CUSTOMER_COLS" in ln))

tp = Path("src/types.ts")
if tp.exists():
    t = tp.read_text()
    if "export interface Customer" in t:
        start = t.find("export interface Customer")
        end = t.find("}", start)
        block = t[start:end]
        if "avatar_url" not in block:
            t = t[:end] + "\n  avatar_url?: string | null;" + t[end:]
            tp.write_text(t)
            print("types ok")
        else:
            print("types has avatar")

ac = Path("src/context/AuthContext.tsx")
if ac.exists() and ac.stat().st_size > 3000:
    a = ac.read_text()
    if "AVATAR_SYNC_V2" in a:
        print("Auth already V2")
    else:
        new_fn = r'''  const updateProfile = async (data: Record<string, unknown>) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload = { ...data };
    if (typeof payload.branch === 'string') {
      let b = payload.branch.trim().toUpperCase();
      if (b.endsWith(' BRANCH')) b = b.slice(0, -7).trim();
      payload.branch = b;
    }
    // AVATAR_SYNC_V2
    const avatarRaw = typeof payload.avatar_url === 'string' ? (payload.avatar_url as string) : null;
    const metaPayload: Record<string, unknown> = { ...payload };
    if (avatarRaw && avatarRaw.length > 6000) {
      metaPayload.avatar_url = 'stored';
    }
    const { error: authErr } = await supabase.auth.updateUser({ data: metaPayload });
    if (authErr) {
      console.warn('updateUser metadata', authErr.message);
      if (!avatarRaw) throw friendlyAuthError(authErr);
    }
    const { data: sess } = await supabase.auth.getSession();
    const nextUser = sess.session?.user ?? null;
    setUser(nextUser);
    setSession(sess.session);
    try {
      const em = (nextUser?.email || user?.email || '').trim().toLowerCase();
      if (!em) return;
      const name =
        String(payload.full_name || payload.name || nextUser?.user_metadata?.full_name || '').trim() ||
        em.split('@')[0];
      let branchVal: string | null | undefined =
        payload.branch !== undefined ? String(payload.branch || '').trim().toUpperCase() || null : undefined;
      if (branchVal && branchVal.endsWith(' BRANCH')) {
        branchVal = branchVal.slice(0, -7).trim() || null;
      }
      const customerPatch: Record<string, unknown> = { name, email: em };
      if (branchVal !== undefined) customerPatch.branch = branchVal;
      if (avatarRaw) customerPatch.avatar_url = avatarRaw;
      const { data: existing } = await supabase.from('customers').select('id').ilike('email', em).maybeSingle();
      if (existing?.id) {
        let { error: upErr } = await supabase.from('customers').update(customerPatch).eq('id', existing.id);
        if (upErr && avatarRaw) {
          const { avatar_url: _drop, ...rest } = customerPatch;
          const r2 = await supabase.from('customers').update(rest).eq('id', existing.id);
          upErr = r2.error;
          console.warn('customer avatar update fallback', upErr?.message);
        }
        if (upErr) console.warn('customer update', upErr.message);
        else console.info('customer avatar synced', em);
      } else {
        const { error: insErr } = await supabase.from('customers').insert(customerPatch);
        if (insErr && avatarRaw) {
          const { avatar_url: _drop, ...rest } = customerPatch;
          await supabase.from('customers').upsert(rest, { onConflict: 'email' });
        }
      }
      try {
        if (avatarRaw) {
          const uid = nextUser?.id || user?.id;
          if (uid) await supabase.from('profiles').update({ avatar_url: avatarRaw }).eq('id', uid);
          await supabase.from('profiles').update({ avatar_url: avatarRaw }).ilike('email', em);
        }
      } catch {
        /* profiles optional */
      }
    } catch (e) {
      console.warn('customer profile sync', e);
    }
  };'''
        m = re.search(
            r"  const updateProfile = async \(data: Record<string, unknown>\) => \{[\s\S]*?\n  \};(?=\n\n  const updatePassword)",
            a,
        )
        if m:
            a = a[: m.start()] + new_fn + a[m.end() :]
            ac.write_text(a)
            print("AuthContext updateProfile V2", a.count("{") - a.count("}"))
        else:
            print("AuthContext updateProfile regex miss")
else:
    print("AuthContext skip")

ua = Path("src/components/UsersAdminPage.tsx")
if ua.exists() and ua.stat().st_size > 3000:
    s = ua.read_text()
    if "avatar_url: c.avatar_url" not in s:
        s = s.replace(
            "branch: normalizeBranchName(c.branch) || '',\n        status: c.status",
            "branch: normalizeBranchName(c.branch) || '',\n        avatar_url: c.avatar_url || null,\n        status: c.status",
            1,
        )
        print("customer row avatar")
    if "avatar_url: a.avatar_url" not in s:
        s = s.replace(
            """      branch: normalizeBranchName(a.branch) || '',
      status: a.approval_status || 'approved',
      agent: a,""",
            """      branch: normalizeBranchName(a.branch) || '',
      avatar_url: a.avatar_url || null,
      status: a.approval_status || 'approved',
      agent: a,""",
            1,
        )
        print("agent row avatar")
    if "avatar_url?: string | null;" not in s:
        s = s.replace(
            "  branch: string;\n  status: string;",
            "  branch: string;\n  avatar_url?: string | null;\n  status: string;",
            1,
        )
    if "USERS_AVATAR_V1" not in s:
        m2 = re.search(
            r'(<div className="w-8 h-8 rounded-full[^"]*"[^>]*>)\s*\{[^}]+\}(\s*</div>)',
            s,
        )
        if m2:
            repl = (
                m2.group(1)
                + """
                          {/* USERS_AVATAR_V1 */}
                          {u.avatar_url ? (
                            <img src={u.avatar_url} alt="" className="w-full h-full object-cover rounded-full" />
                          ) : (
                            <span>{u.name.trim().slice(0, 1).toUpperCase() || '?'}</span>
                          )}
                        """
                + m2.group(2)
            )
            s = s[: m2.start()] + repl + s[m2.end() :]
            print("users UI avatar")
    ua.write_text(s)
    print("UsersAdmin", s.count("{") - s.count("}"))

lp = Path("src/components/LiveChatPage.tsx")
if lp.exists() and lp.stat().st_size > 5000:
    t = lp.read_text()
    if "CUSTOMER_AVATAR_CHAT_V1" not in t:
        t2 = re.sub(
            r"const \{([^}]+)\} = useTickets\(\)",
            lambda m: m.group(0) if "customers" in m.group(1) else "const {" + m.group(1) + ", customers } = useTickets()",
            t,
            count=1,
        )
        t = t2
        if "{customerInitials || 'C'}" in t:
            t = t.replace(
                "{customerInitials || 'C'}",
                """{(() => {
                          // CUSTOMER_AVATAR_CHAT_V1
                          const em = (selected.customer_email || '').toLowerCase();
                          const cust = (customers || []).find((c) => (c.email || '').toLowerCase() === em);
                          const src = cust?.avatar_url || '';
                          if (src) return <img src={src} alt="" className="w-full h-full object-cover rounded-full" />;
                          return customerInitials || 'C';
                        })()}""",
                1,
            )
            print("LiveChat avatar")
        lp.write_text(t)
        print("LiveChat braces", t.count("{") - t.count("}"))
    else:
        print("LiveChat already")

print("patch_avatar_sync_v1 done")
