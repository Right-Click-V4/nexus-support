#!/usr/bin/env python3
"""Users dedupe by email; approve syncs profiles; signup upsert; login trusts customers/agents."""
from pathlib import Path

u = Path("src/components/UsersAdminPage.tsx")
if u.exists() and u.stat().st_size > 2000:
    s = u.read_text()
    if "APPROVE_SYNC_V2" not in s:
        old_c = """  const setCustomerStatus = async (id: string, status: 'approved' | 'rejected' | 'pending') => {
    if (!supabase) return;
    setErr('');
    setMsg('');
    try {
      const { error } = await supabase.from('customers').update({ status }).eq('id', id);
      if (error) {
        if (String(error.message).toLowerCase().includes('status')) {
          setErr("Add column: alter table public.customers add column if not exists status text default 'approved';");
        } else setErr(error.message);
        return;
      }
      setMsg(status === 'approved' ? 'Customer approved.' : status === 'rejected' ? 'Customer rejected.' : 'Set to pending.');
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Update failed');
    }
  };"""
        new_c = """  const setCustomerStatus = async (id: string, status: 'approved' | 'rejected' | 'pending') => {
    if (!supabase) return;
    setErr('');
    setMsg('');
    try {
      // APPROVE_SYNC_V2
      const { error } = await supabase.from('customers').update({ status }).eq('id', id);
      if (error) {
        if (String(error.message).toLowerCase().includes('status')) {
          setErr("Add column: alter table public.customers add column if not exists status text default 'approved';");
        } else setErr(error.message);
        return;
      }
      try {
        const cust = customers.find((c) => c.id === id);
        const email = (cust?.email || '').trim();
        if (email) {
          const approvedFlag = status === 'approved';
          await supabase
            .from('profiles')
            .update({ status, approved: approvedFlag, role: 'customer' })
            .ilike('email', email);
          await supabase.from('customers').update({ status }).ilike('email', email);
        }
      } catch {
        /* profiles sync non-fatal */
      }
      setMsg(status === 'approved' ? 'Customer approved.' : status === 'rejected' ? 'Customer rejected.' : 'Set to pending.');
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Update failed');
    }
  };"""
        if old_c in s:
            s = s.replace(old_c, new_c)
            print("customer approve sync")
        else:
            print("customer approve miss")

        old_a = """  const setAgentApproval = async (id: string, approval_status: 'approved' | 'rejected' | 'pending') => {
    if (!supabase) return;
    setErr('');
    setMsg('');
    try {
      const { error } = await supabase.from('agents').update({ approval_status }).eq('id', id);
      if (error) {
        setErr(error.message);
        return;
      }
      setMsg(`Agent ${approval_status}.`);
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Update failed');
    }
  };"""
        new_a = """  const setAgentApproval = async (id: string, approval_status: 'approved' | 'rejected' | 'pending') => {
    if (!supabase) return;
    setErr('');
    setMsg('');
    try {
      // APPROVE_SYNC_V2
      const { error } = await supabase.from('agents').update({ approval_status }).eq('id', id);
      if (error) {
        setErr(error.message);
        return;
      }
      try {
        const agent = agents.find((a) => a.id === id);
        const profileStatus =
          approval_status === 'approved' ? 'approved' : approval_status === 'rejected' ? 'rejected' : 'pending';
        const approvedFlag = approval_status === 'approved';
        if (agent?.user_id) {
          await supabase
            .from('profiles')
            .update({ status: profileStatus, approved: approvedFlag, role: agent.is_admin ? 'admin' : 'agent' })
            .eq('id', agent.user_id);
        }
        if (agent?.email) {
          await supabase
            .from('profiles')
            .update({ status: profileStatus, approved: approvedFlag })
            .ilike('email', agent.email);
          await supabase.from('agents').update({ approval_status }).ilike('email', agent.email);
        }
      } catch {
        /* profiles sync non-fatal */
      }
      setMsg(`Agent ${approval_status}.`);
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Update failed');
    }
  };"""
        if old_a in s:
            s = s.replace(old_a, new_a)
            print("agent approve sync")
        else:
            print("agent approve miss")

        old_merge = """    return [...agentRows, ...customerRows].sort((a, b) => {
      const ap = a.status === 'pending' ? 0 : 1;
      const bp = b.status === 'pending' ? 0 : 1;
      if (ap !== bp) return ap - bp;
      return a.name.localeCompare(b.name);
    });
  }, [agents, customers, branchNames]);"""
        new_merge = """    // DEDUPE_EMAIL_V1 \u2014 one row per email; prefer entry that has a branch
    const merged = [...agentRows, ...customerRows];
    const byEmail = new Map<string, (typeof merged)[0]>();
    for (const row of merged) {
      const key = (row.email || '').trim().toLowerCase();
      if (!key) {
        byEmail.set(`id:${row.id}`, row);
        continue;
      }
      const prev = byEmail.get(key);
      if (!prev) {
        byEmail.set(key, row);
        continue;
      }
      const prevHas = !!(prev.branch && prev.branch !== '\u2014');
      const rowHas = !!(row.branch && row.branch !== '\u2014');
      if (rowHas && !prevHas) byEmail.set(key, row);
      else if (rowHas === prevHas) {
        if (row.status === 'pending' && prev.status !== 'pending') byEmail.set(key, row);
      }
    }
    return Array.from(byEmail.values()).sort((a, b) => {
      const ap = a.status === 'pending' ? 0 : 1;
      const bp = b.status === 'pending' ? 0 : 1;
      if (ap !== bp) return ap - bp;
      return a.name.localeCompare(b.name);
    });
  }, [agents, customers, branchNames]);"""
        if old_merge in s:
            s = s.replace(old_merge, new_merge)
            print("dedupe merge")
        else:
            print("dedupe miss")
        u.write_text(s)
        print("UsersAdmin", len(s), "braces", s.count("{") - s.count("}"))
    else:
        print("UsersAdmin already")
else:
    print("UsersAdmin skip")

acp = Path("src/context/AuthContext.tsx")
if acp.exists() and acp.stat().st_size > 3000:
    ac = acp.read_text()
    changed = False
    if "SIGNUP_UPSERT_V1" not in ac:
        old_ins = """      } else {
        try {
          await supabase.from('customers').insert({
            name: displayName,
            email: emailNorm,
            status: 'pending',
            branch: branchNorm || null,
          });
        } catch {
          try {
            await supabase.from('customers').upsert(
              {
                name: displayName,
                email: emailNorm,
                status: 'pending',
                branch: branchNorm || null,
              },
              { onConflict: 'email' },
            );
          } catch {
            /* non-fatal */
          }
        }
      }"""
        new_ins = """      } else {
        // SIGNUP_UPSERT_V1 \u2014 never create a second customer row for the same email
        try {
          await supabase.from('customers').upsert(
            {
              name: displayName,
              email: emailNorm,
              status: 'pending',
              branch: branchNorm || null,
            },
            { onConflict: 'email' },
          );
        } catch {
          try {
            const { data: existing } = await supabase
              .from('customers')
              .select('id')
              .ilike('email', emailNorm)
              .limit(1)
              .maybeSingle();
            if (existing?.id) {
              await supabase
                .from('customers')
                .update({
                  name: displayName,
                  status: 'pending',
                  branch: branchNorm || null,
                })
                .eq('id', existing.id);
            } else {
              await supabase.from('customers').insert({
                name: displayName,
                email: emailNorm,
                status: 'pending',
                branch: branchNorm || null,
              });
            }
          } catch {
            /* non-fatal */
          }
        }
      }"""
        if old_ins in ac:
            ac = ac.replace(old_ins, new_ins)
            changed = True
            print("signup upsert")
        else:
            print("signup miss")
    if "ASSERT_ROLE_TABLE_FIRST_V1" not in ac:
        old_assert = """async function assertApproved(user: User, role: AccountRole): Promise<void> {
  if (!supabase) return;
  const email = (user.email || '').trim().toLowerCase();
  const kind = role === 'customer' ? 'customer' : 'agent';

  try {
    const { data } = await supabase
      .from('profiles')
      .select('status, approved, role')
      .eq('id', user.id)
      .maybeSingle();
    if (data) {
      if (data.status === 'pending' || data.approved === false) {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account is pending approval. Please wait for an admin.'
            : 'Your agent account is pending approval. Please wait for an admin.',
        );
      }
      if (data.status === 'rejected') {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account was rejected. Contact support.'
            : 'Your agent account was rejected. Contact support.',
        );
      }
    }
  } catch (e) {
    if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
  }"""
        new_assert = """async function assertApproved(user: User, role: AccountRole): Promise<void> {
  if (!supabase) return;
  const email = (user.email || '').trim().toLowerCase();
  const kind = role === 'customer' ? 'customer' : 'agent';

  // ASSERT_ROLE_TABLE_FIRST_V1 \u2014 customers/agents row is source of truth for approval
  if (kind === 'customer' && email) {
    try {
      const { data: cust } = await supabase
        .from('customers')
        .select('status')
        .ilike('email', email)
        .limit(5);
      const rows = (cust || []) as { status?: string }[];
      const statuses = rows.map((r) => String(r.status || '').toLowerCase());
      if (statuses.some((st) => st === 'approved')) {
        try {
          await supabase
            .from('profiles')
            .update({ status: 'approved', approved: true, role: 'customer' })
            .eq('id', user.id);
        } catch {
          /* ignore */
        }
        return;
      }
      if (statuses.includes('rejected') && !statuses.includes('approved') && !statuses.includes('pending')) {
        throw new Error('Your customer account was rejected. Contact support.');
      }
      if (statuses.includes('pending') || (rows.length > 0 && !statuses.includes('approved'))) {
        throw new Error('Your customer account is pending approval. Please wait for an admin.');
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
  }

  try {
    const { data } = await supabase
      .from('profiles')
      .select('status, approved, role')
      .eq('id', user.id)
      .maybeSingle();
    if (data) {
      if (data.status === 'pending' || data.approved === false) {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account is pending approval. Please wait for an admin.'
            : 'Your agent account is pending approval. Please wait for an admin.',
        );
      }
      if (data.status === 'rejected') {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account was rejected. Contact support.'
            : 'Your agent account was rejected. Contact support.',
        );
      }
    }
  } catch (e) {
    if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
  }"""
        if old_assert in ac:
            ac = ac.replace(old_assert, new_assert)
            changed = True
            print("assert role-first")
        else:
            print("assert miss")
    if changed:
        acp.write_text(ac)
        print("AuthContext", len(ac), "braces", ac.count("{") - ac.count("}"))
    else:
        print("AuthContext no change or already")
else:
    print("AuthContext skip")

print("patch_users_dedupe_approve done")
