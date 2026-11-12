#!/usr/bin/env python3
"""When approving/rejecting agents or customers, also sync profiles.status + approved
so login assertApproved does not still see pending."""
from pathlib import Path

p = Path("src/components/UsersAdminPage.tsx")
if not p.exists() or p.stat().st_size < 3000:
    print("skip UsersAdminPage")
    raise SystemExit(0)

t = p.read_text()
if "APPROVE_SYNC_PROFILES_V1" in t:
    print("already patched")
    raise SystemExit(0)

old_agent = """  const setAgentApproval = async (id: string, approval_status: 'approved' | 'rejected' | 'pending') => {
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

new_agent = """  const setAgentApproval = async (id: string, approval_status: 'approved' | 'rejected' | 'pending') => {
    if (!supabase) return;
    setErr('');
    setMsg('');
    try {
      // APPROVE_SYNC_PROFILES_V1
      const { error } = await supabase.from('agents').update({ approval_status }).eq('id', id);
      if (error) {
        setErr(error.message);
        return;
      }
      try {
        const agent = agents.find((a) => a.id === id);
        const profileStatus = approval_status === 'approved' ? 'approved' : approval_status === 'rejected' ? 'rejected' : 'pending';
        const approvedFlag = approval_status === 'approved';
        if (agent?.user_id) {
          await supabase.from('profiles').update({ status: profileStatus, approved: approvedFlag, role: agent.is_admin ? 'admin' : 'agent' }).eq('id', agent.user_id);
        }
        if (agent?.email) {
          await supabase.from('profiles').update({ status: profileStatus, approved: approvedFlag }).ilike('email', agent.email);
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

old_cust = """  const setCustomerStatus = async (id: string, status: 'approved' | 'rejected' | 'pending') => {
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

new_cust = """  const setCustomerStatus = async (id: string, status: 'approved' | 'rejected' | 'pending') => {
    if (!supabase) return;
    setErr('');
    setMsg('');
    try {
      // APPROVE_SYNC_PROFILES_V1
      const { error } = await supabase.from('customers').update({ status }).eq('id', id);
      if (error) {
        if (String(error.message).toLowerCase().includes('status')) {
          setErr("Add column: alter table public.customers add column if not exists status text default 'approved';");
        } else setErr(error.message);
        return;
      }
      try {
        const cust = customers.find((c) => c.id === id);
        const approvedFlag = status === 'approved';
        if (cust?.email) {
          await supabase.from('profiles').update({ status, approved: approvedFlag, role: 'customer' }).ilike('email', cust.email);
        }
        if ((cust as { user_id?: string } | undefined)?.user_id) {
          await supabase.from('profiles').update({ status, approved: approvedFlag, role: 'customer' }).eq('id', (cust as { user_id?: string }).user_id!);
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

changed = False
if old_agent in t:
    t = t.replace(old_agent, new_agent)
    print("setAgentApproval synced")
    changed = True
else:
    print("setAgentApproval pattern miss")

if old_cust in t:
    t = t.replace(old_cust, new_cust)
    print("setCustomerStatus synced")
    changed = True
else:
    print("setCustomerStatus pattern miss")

if changed:
    p.write_text(t)
print("done", len(t), "APPROVE_SYNC", "APPROVE_SYNC_PROFILES_V1" in t)
