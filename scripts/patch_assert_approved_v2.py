#!/usr/bin/env python3
"""ASSERT_APPROVED_V2: agents/customers table is source of truth; profiles is fallback only."""
from pathlib import Path

p = Path("src/context/AuthContext.tsx")
if not p.exists() or p.stat().st_size < 5000:
    print("skip AuthContext")
    raise SystemExit(0)

t = p.read_text()
if "ASSERT_APPROVED_V2" in t:
    print("already ASSERT_APPROVED_V2")
    raise SystemExit(0)

old = """async function assertApproved(user: User, role: AccountRole): Promise<void> {
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
    if (e instanceof Error and /pending|rejected/i.test(e.message)) throw e;
  }

  if (kind === 'agent') {
    try {
      let row: { approval_status?: string | null } | null = null;
      const byId = await supabase
        .from('agents')
        .select('approval_status')
        .eq('user_id', user.id)
        .maybeSingle();
      row = byId.data as typeof row;
      if (!row && email) {
        const byEmail = await supabase
          .from('agents')
          .select('approval_status')
          .eq('email', email)
          .maybeSingle();
        row = byEmail.data as typeof row;
      }
      const st = (row?.approval_status || '').toLowerCase();
      if (st === 'pending') {
        throw new Error('Your agent account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your agent account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error and /pending|rejected/i.test(e.message)) throw e;
    }
  }

  if (kind === 'customer' && email) {
    try {
      const { data: cust } = await supabase
        .from('customers')
        .select('status')
        .ilike('email', email)
        .maybeSingle();
      const st = String((cust as { status?: string } | null)?.status || '').toLowerCase();
      if (st === 'pending') {
        throw new Error('Your customer account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your customer account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error and /pending|rejected/i.test(e.message)) throw e;
    }
  }
}"""

# Fix accidental Python and -> && in the old pattern string above
old = old.replace("and /pending", "and /pending")  # noop placeholder
# Rebuild with correct JS regex in the search string
old = r'''async function assertApproved(user: User, role: AccountRole): Promise<void> {
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
  }

  if (kind === 'agent') {
    try {
      let row: { approval_status?: string | null } | null = null;
      const byId = await supabase
        .from('agents')
        .select('approval_status')
        .eq('user_id', user.id)
        .maybeSingle();
      row = byId.data as typeof row;
      if (!row && email) {
        const byEmail = await supabase
          .from('agents')
          .select('approval_status')
          .eq('email', email)
          .maybeSingle();
        row = byEmail.data as typeof row;
      }
      const st = (row?.approval_status || '').toLowerCase();
      if (st === 'pending') {
        throw new Error('Your agent account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your agent account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
  }

  if (kind === 'customer' && email) {
    try {
      const { data: cust } = await supabase
        .from('customers')
        .select('status')
        .ilike('email', email)
        .maybeSingle();
      const st = String((cust as { status?: string } | null)?.status || '').toLowerCase();
      if (st === 'pending') {
        throw new Error('Your customer account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your customer account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
  }
}'''

new = r'''async function assertApproved(user: User, role: AccountRole): Promise<void> {
  if (!supabase) return;
  const email = (user.email || '').trim().toLowerCase();
  const kind = role === 'customer' ? 'customer' : 'agent';

  // ASSERT_APPROVED_V2: agents/customers table is source of truth; profiles is fallback.
  if (kind === 'agent') {
    try {
      let row: { approval_status?: string | null } | null = null;
      const byId = await supabase
        .from('agents')
        .select('approval_status')
        .eq('user_id', user.id)
        .maybeSingle();
      row = byId.data as typeof row;
      if (!row && email) {
        const byEmail = await supabase
          .from('agents')
          .select('approval_status')
          .eq('email', email)
          .maybeSingle();
        row = byEmail.data as typeof row;
      }
      const st = (row?.approval_status || '').toLowerCase();
      if (st === 'approved') return;
      if (st === 'pending') {
        throw new Error('Your agent account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your agent account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
  }

  if (kind === 'customer' && email) {
    try {
      const { data: cust } = await supabase
        .from('customers')
        .select('status')
        .ilike('email', email)
        .maybeSingle();
      const st = String((cust as { status?: string } | null)?.status || '').toLowerCase();
      if (st === 'approved') return;
      if (st === 'pending') {
        throw new Error('Your customer account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your customer account was rejected. Contact support.');
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
      if (data.status === 'rejected') {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account was rejected. Contact support.'
            : 'Your agent account was rejected. Contact support.',
        );
      }
      if (data.status === 'pending' || data.approved === false) {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account is pending approval. Please wait for an admin.'
            : 'Your agent account is pending approval. Please wait for an admin.',
        );
      }
    }
  } catch (e) {
    if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
  }
}'''

if old in t:
    t = t.replace(old, new)
    p.write_text(t)
    print("assertApproved V2 applied", len(t))
else:
    print("pattern miss")
    i = t.find('async function assertApproved')
    print(repr(t[i:i+120]) if i>=0 else 'not found')
