#!/usr/bin/env python3
"""Sync customer/agent avatars to DB so Users tab + Live Chat see the same image."""
from pathlib import Path
import re

tp = Path("src/types.ts")
if tp.exists():
    t = tp.read_text()
    chunk = t[t.find("export interface Customer"):t.find("export interface Customer")+500] if "export interface Customer" in t else ""
    if "export interface Customer" in t and "avatar_url" not in chunk:
        t = t.replace(
            """export interface Customer {
  id: string;
  name: string;
  email?: string;
  company?: string;
  role?: string;
  branch?: string | null;
  status?: 'pending' | 'approved' | 'rejected' | null;
  created_at?: string;
}""",
            """export interface Customer {
  id: string;
  name: string;
  email?: string;
  company?: string;
  role?: string;
  branch?: string | null;
  status?: 'pending' | 'approved' | 'rejected' | null;
  created_at?: string;
  avatar_url?: string | null;
}""",
        )
        tp.write_text(t)
        print("types Customer.avatar_url")
    else:
        print("types ok/skip")

tc = Path("src/context/TicketContext.tsx")
if tc.exists() and tc.stat().st_size > 5000:
    s = tc.read_text()
    s = re.sub(
        r"const CUSTOMER_COLS = '[^']*';[^\n]*",
        "const CUSTOMER_COLS = 'id, name, email, role, branch, status, created_at, avatar_url'; // AVATAR_SYNC_V1",
        s,
        count=1,
    )
    if "AVATAR_SYNC_SOFT_LOAD" not in s and "from('customers').select(CUSTOMER_COLS)" in s:
        s = s.replace(
            "withTimeout(supabase.from('customers').select(CUSTOMER_COLS).limit(200), 4000)",
            """withTimeout((async () => {
          // AVATAR_SYNC_SOFT_LOAD
          const full = await supabase.from('customers').select(CUSTOMER_COLS).limit(200);
          if (!full.error) return full;
          const safe = await supabase
            .from('customers')
            .select('id, name, email, role, branch, status, created_at')
            .limit(200);
          return safe;
        })(), 4000)""",
        )
        print("soft load customers")
    tc.write_text(s)
    print("TicketContext cols")
else:
    print("TicketContext skip")

ac = Path("src/context/AuthContext.tsx")
if ac.exists() and ac.stat().st_size > 3000:
    a = ac.read_text()
    if "AVATAR_SYNC_V1" not in a:
        old = """  const updateProfile = async (data: Record<string, unknown>) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload = { ...data };
    if (typeof payload.branch === 'string') {
      let b = payload.branch.trim().toUpperCase();
      if (b.endsWith(' BRANCH')) b = b.slice(0, -7).trim();
      payload.branch = b;
    }
    const { error: authErr } = await supabase.auth.updateUser({ data: payload });
    if (authErr) throw friendlyAuthError(authErr);
    const { data: sess } = await supabase.auth.getSession();
    const nextUser = sess.session?.user ?? null;
    setUser(nextUser);
    setSession(sess.session);
    try {
      const em = (nextUser?.email || '').trim().toLowerCase();
      if (em && payload.branch !== undefined) {
        const name =
          String(payload.full_name || payload.name || nextUser?.user_metadata?.full_name || '').trim() ||
          em.split('@')[0];
        let branchVal = String(payload.branch || '').trim().toUpperCase() || null;
        if (branchVal && branchVal.endsWith(' BRANCH')) {
          branchVal = branchVal.slice(0, -7).trim() || null;
        }
        const row = { name, email: em, branch: branchVal };
        const { data: existing } = await supabase
          .from('customers')
          .select('id')
          .ilike('email', em)
          .maybeSingle();
        if (existing?.id) {
          const { error: upErr } = await supabase
            .from('customers')
            .update({ name, branch: branchVal })
            .eq('id', existing.id);
          if (upErr) console.warn('customer branch update', upErr.message);
        } else {
          const { error: insErr } = await supabase.from('customers').insert(row);
          if (insErr) {
            const { error: upsErr } = await supabase.from('customers').upsert(row, { onConflict: 'email' });
            if (upsErr) console.warn('customer branch insert', insErr.message, upsErr.message);
          }
        }
      }
    } catch (e) {
      console.warn('customer branch sync', e);
    }
  };"""
        new = """  const updateProfile = async (data: Record<string, unknown>) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload = { ...data };
    if (typeof payload.branch === 'string') {
      let b = payload.branch.trim().toUpperCase();
      if (b.endsWith(' BRANCH')) b = b.slice(0, -7).trim();
      payload.branch = b;
    }
    // AVATAR_SYNC_V1 — large data-URL avatars stay out of auth metadata (size limits)
    const avatarRaw = typeof payload.avatar_url === 'string' ? payload.avatar_url : null;
    const metaPayload = { ...payload };
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
      let branchVal =
        payload.branch !== undefined
          ? String(payload.branch || '').trim().toUpperCase() || null
          : undefined;
      if (branchVal && branchVal.endsWith(' BRANCH')) {
        branchVal = branchVal.slice(0, -7).trim() || null;
      }
      const customerPatch: Record<string, unknown> = { name, email: em };
      if (branchVal !== undefined) customerPatch.branch = branchVal;
      if (avatarRaw) customerPatch.avatar_url = avatarRaw;
      const { data: existing } = await supabase
        .from('customers')
        .select('id')
        .ilike('email', em)
        .maybeSingle();
      if (existing?.id) {
        const { error: upErr } = await supabase.from('customers').update(customerPatch).eq('id', existing.id);
        if (upErr) {
          const { avatar_url: _a, ...rest } = customerPatch;
          await supabase.from('customers').update(rest).eq('id', existing.id);
          console.warn('customer update', upErr.message);
        }
      } else if (payload.branch !== undefined || avatarRaw) {
        const { error: insErr } = await supabase.from('customers').insert(customerPatch);
        if (insErr) {
          const { avatar_url: _a, ...rest } = customerPatch;
          await supabase.from('customers').upsert(rest, { onConflict: 'email' });
        }
      }
      try {
        const prof: Record<string, unknown> = { email: em };
        if (avatarRaw) prof.avatar_url = avatarRaw;
        if (branchVal !== undefined) prof.branch = branchVal;
        await supabase.from('profiles').update(prof).eq('id', nextUser?.id || user?.id || '');
        if (avatarRaw) {
          await supabase.from('profiles').update({ avatar_url: avatarRaw }).ilike('email', em);
        }
      } catch {
        /* profiles optional */
      }
    } catch (e) {
      console.warn('customer profile sync', e);
    }
  };"""
        if old in a:
            a = a.replace(old, new)
            ac.write_text(a)
            print("AuthContext updateProfile avatar sync")
        else:
            print("AuthContext updateProfile pattern miss")
    else:
        print("AuthContext already")
else:
    print("AuthContext skip")

ua = Path("src/components/UsersAdminPage.tsx")
if ua.exists() and ua.stat().st_size > 3000:
    s = ua.read_text()
    if "USERS_AVATAR_V1" not in s:
        if "branch: normalizeBranchName(c.branch) || ''," in s:
            s = s.replace(
                "branch: normalizeBranchName(c.branch) || '',\n        status: c.status",
                "branch: normalizeBranchName(c.branch) || '',\n        avatar_url: c.avatar_url || null,\n        status: c.status",
                1,
            )
        if """      branch: normalizeBranchName(a.branch) || '',
      status: a.approval_status || 'approved',
      agent: a,""" in s:
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
        s = s.replace(
            """  branch: string;
  status: string;""",
            """  branch: string;
  avatar_url?: string | null;
  status: string;""",
            1,
        )
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
            print("users list avatar")
        else:
            print("users avatar UI miss")
        ua.write_text(s)
        print("UsersAdmin avatar fields", len(s), s.count("{") - s.count("}"))
    else:
        print("UsersAdmin already")
else:
    print("UsersAdmin skip")

lp = Path("src/components/LiveChatPage.tsx")
if lp.exists() and lp.stat().st_size > 5000:
    t = lp.read_text()
    if "CUSTOMER_AVATAR_CHAT_V1" not in t:
        t = re.sub(
            r"const \{([^}]+)\} = useTickets\(\)",
            lambda m: m.group(0) if "customers" in m.group(1) else "const {" + m.group(1) + ", customers } = useTickets()",
            t,
            count=1,
        )
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
            print("LiveChat customer avatar bubble")
        else:
            print("LiveChat initials pattern miss")
        lp.write_text(t)
        print("LiveChat", t.count("{") - t.count("}"))
    else:
        print("LiveChat already")
else:
    print("LiveChat skip")

print("patch_avatar_sync_v1 done")
