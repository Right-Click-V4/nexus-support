import { useEffect, useMemo, useState } from 'react';
import {
  Search,
  RefreshCw,
  Check,
  X,
  Clock,
  Shield,
  UserRound,
  Building2,
  KeyRound,
  Save,
} from 'lucide-react';
import clsx from 'clsx';
import { useTickets } from '../context/TicketContext';
import { supabase } from '../lib/supabase';
import type { Agent, Customer, Branch } from '../types';
import { normalizeBranchName } from '../lib/branches';
import { INITIAL_BRANCHES } from '../data';

const BRANCH_LS = 'nexus-branches-v1';

function loadBranchNames(): string[] {
  try {
    const raw = localStorage.getItem(BRANCH_LS);
    if (raw) {
      const list = JSON.parse(raw) as Branch[];
      return list.map((b) => normalizeBranchName(b.name)).filter(Boolean);
    }
  } catch {}
  return INITIAL_BRANCHES.map((b) => normalizeBranchName(b.name)).filter(Boolean);
}

type UserKind = 'agent' | 'customer';

interface UnifiedUser {
  key: string;
  kind: UserKind;
  id: string;
  name: string;
  email: string;
  role: string;
  is_admin: boolean;
  branch: string;
  status: string;
  agent?: Agent;
  customer?: Customer;
}

export default function UsersAdminPage() {
  const { agents, customers, currentAgent, setAgentAdmin, refresh, usingSupabase } = useTickets();
  const [q, setQ] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'admin' | 'agent' | 'customer'>('all');
  const [branchNames, setBranchNames] = useState<string[]>(loadBranchNames);
  const [editing, setEditing] = useState<UnifiedUser | null>(null);
  const [editName, setEditName] = useState('');
  const [editRole, setEditRole] = useState('');
  const [editAdmin, setEditAdmin] = useState(false);
  const [editBranch, setEditBranch] = useState('');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  useEffect(() => {
    setBranchNames(loadBranchNames());
  }, []);

  const rows: UnifiedUser[] = useMemo(() => {
    const agentRows: UnifiedUser[] = agents.map((a) => ({
      key: `agent-${a.id}`,
      kind: 'agent' as const,
      id: a.id,
      name: a.name,
      email: a.email || '',
      role: a.is_admin ? 'Admin' : a.role || 'Agent',
      is_admin: !!a.is_admin,
      branch: normalizeBranchName(a.branch) || '',
      status: a.approval_status || 'approved',
      agent: a,
    }));
    const branchNameSet = new Set(branchNames.map((b) => b.trim().toUpperCase()));
    const customerRows: UnifiedUser[] = customers
      .filter((c) => {
        const n = (c.name || '').trim().toUpperCase();
        if (n.endsWith(' BRANCH')) return false;
        if (branchNameSet.has(n)) return false;
        if (branchNameSet.has(normalizeBranchName(n))) return false;
        return true;
      })
      .map((c) => ({
        key: `customer-${c.id}`,
        kind: 'customer' as const,
        id: c.id,
        name: c.name,
        email: c.email || '',
        role: c.role || 'Customer',
        is_admin: false,
        branch: normalizeBranchName(c.branch) || '',
        status: c.status || 'approved',
        customer: c,
      }));
    return [...agentRows, ...customerRows].sort((a, b) => {
      const ap = a.status === 'pending' ? 0 : 1;
      const bp = b.status === 'pending' ? 0 : 1;
      if (ap !== bp) return ap - bp;
      return a.name.localeCompare(b.name);
    });
  }, [agents, customers, branchNames]);

  const pendingCount = rows.filter((r) => r.status === 'pending').length;

  const filtered = rows.filter((r) => {
    if (filter === 'pending' && r.status !== 'pending') return false;
    if (filter === 'admin' && !r.is_admin) return false;
    if (filter === 'agent' && r.kind !== 'agent') return false;
    if (filter === 'customer' && r.kind !== 'customer') return false;
    if (!q.trim()) return true;
    const qq = q.trim().toLowerCase();
    return (
      r.name.toLowerCase().includes(qq) ||
      r.email.toLowerCase().includes(qq) ||
      r.role.toLowerCase().includes(qq) ||
      r.branch.toLowerCase().includes(qq)
    );
  });

  const setCustomerStatus = async (id: string, status: 'approved' | 'rejected' | 'pending') => {
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
  };

  const setAgentApproval = async (id: string, approval_status: 'approved' | 'rejected' | 'pending') => {
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
  };

  const openEdit = (u: UnifiedUser) => {
    setEditing(u);
    setEditName(u.name);
    setEditRole(u.role === 'Admin' ? 'Agent' : u.role);
    setEditAdmin(u.is_admin);
    setEditBranch(u.branch);
    setMsg('');
    setErr('');
  };

  const saveEdit = async () => {
    if (!editing) return;
    setSaving(true);
    setMsg('');
    setErr('');
    try {
      const branchVal = normalizeBranchName(editBranch) || null;
      if (editing.kind === 'agent') {
        const roleLabel = editAdmin ? 'Admin' : editRole.trim() || 'Agent';
        if (supabase) {
          const payload: Record<string, unknown> = {
            name: editName.trim(),
            role: roleLabel,
            is_admin: editAdmin,
            branch: branchVal,
          };
          const { error } = await supabase.from('agents').update(payload).eq('id', editing.id);
          if (error) {
            if (String(error.message).toLowerCase().includes('branch')) {
              const { error: e2 } = await supabase
                .from('agents')
                .update({ name: editName.trim(), role: roleLabel, is_admin: editAdmin })
                .eq('id', editing.id);
              if (e2) throw e2;
            } else throw error;
          }
        }
        if (editAdmin !== editing.is_admin && setAgentAdmin) {
          await setAgentAdmin(editing.id, editAdmin);
        }
        setMsg('Agent updated.');
      } else {
        if (supabase) {
          const payload: Record<string, unknown> = {
            name: editName.trim(),
            branch: branchVal,
          };
          const { error } = await supabase.from('customers').update(payload).eq('id', editing.id);
          if (error) {
            const { error: e2 } = await supabase
              .from('customers')
              .update({ name: editName.trim() })
              .eq('id', editing.id);
            if (e2) throw e2;
            if (String(error.message).toLowerCase().includes('branch')) {
              setErr("Branch column missing — ran name update only. Add customers.branch if needed.");
            } else throw error;
          }
        }
        setMsg('Customer updated.');
      }
      setEditing(null);
      await refresh?.();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const filters: { id: typeof filter; label: string }[] = [
    { id: 'all', label: 'All' },
    { id: 'pending', label: `Pending (${pendingCount})` },
    { id: 'admin', label: 'Admin' },
    { id: 'agent', label: 'Agent' },
    { id: 'customer', label: 'Customer' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-zinc-100">All users</h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Approve new customer accounts here — no need to open Supabase for approval.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void refresh?.()}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-white/15 bg-white dark:bg-white/5 text-slate-700 dark:text-zinc-200 hover:bg-slate-50 dark:hover:bg-white/10"
        >
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {pendingCount > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-sm text-amber-900 dark:text-amber-100">
            <Clock size={16} className="shrink-0 text-amber-600 dark:text-amber-300" />
            <div>
              <span className="font-semibold">{pendingCount} account{pendingCount === 1 ? '' : 's'} waiting for approval</span>
              <span className="block text-xs text-amber-800/80 dark:text-amber-200/80">
                New Agent and Customer signups appear here. Approve to grant workspace or portal access.
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setFilter('pending')}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-500 text-white hover:bg-amber-600"
          >
            Review pending
          </button>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search name, email, role, branch"
            className="w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-black/30 text-slate-900 dark:text-zinc-100"
          />
        </div>
        {filters.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setFilter(f.id)}
            className={clsx(
              'px-3 py-1.5 text-xs font-medium rounded-full border transition',
              filter === f.id
                ? 'bg-violet-600 border-violet-600 text-white'
                : 'bg-white dark:bg-white/5 border-slate-200 dark:border-white/15 text-slate-600 dark:text-zinc-300',
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {(msg || err) && (
        <div
          className={clsx(
            'text-sm px-3 py-2 rounded-xl border',
            err
              ? 'text-rose-700 dark:text-rose-300 bg-rose-500/10 border-rose-500/25'
              : 'text-emerald-700 dark:text-emerald-300 bg-emerald-500/10 border-emerald-500/25',
          )}
        >
          {err || msg}
        </div>
      )}

      <div className="rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden bg-white dark:bg-zinc-900/40">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-white/5 text-left text-xs text-slate-500 dark:text-zinc-400 uppercase tracking-wide">
              <tr>
                <th className="px-4 py-3 font-medium">User</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Branch workplace</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/5">
              {filtered.map((u) => (
                <tr key={u.key} className="hover:bg-slate-50/80 dark:hover:bg-white/[0.03]">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white text-[11px] font-semibold flex items-center justify-center shrink-0">
                        {(u.name || '?').slice(0, 2).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-slate-900 dark:text-zinc-100 truncate flex items-center gap-1.5">
                          {u.name}
                          {u.id === currentAgent?.id && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-violet-500/15 text-violet-600 dark:text-violet-300">
                              You
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-zinc-400 truncate">{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={clsx(
                        'inline-flex px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wide',
                        u.is_admin
                          ? 'bg-violet-500/15 text-violet-700 dark:text-violet-300'
                          : u.kind === 'agent'
                            ? 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300'
                            : 'bg-sky-500/15 text-sky-700 dark:text-sky-300',
                      )}
                    >
                      {u.is_admin ? 'Admin' : u.kind === 'agent' ? 'Agent' : 'Customer'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={clsx(
                        'inline-flex px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase',
                        u.status === 'pending'
                          ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300'
                          : u.status === 'rejected'
                            ? 'bg-rose-500/15 text-rose-700 dark:text-rose-300'
                            : 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300',
                      )}
                    >
                      {u.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600 dark:text-zinc-300">{normalizeBranchName(u.branch) || '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap items-center gap-1.5">
                      {u.status === 'pending' && (
                        <>
                          <button
                            type="button"
                            onClick={() =>
                              void (u.kind === 'customer'
                                ? setCustomerStatus(u.id, 'approved')
                                : setAgentApproval(u.id, 'approved'))
                            }
                            className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-500"
                          >
                            <Check size={12} /> Approve
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              void (u.kind === 'customer'
                                ? setCustomerStatus(u.id, 'rejected')
                                : setAgentApproval(u.id, 'rejected'))
                            }
                            className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-semibold rounded-lg bg-rose-600 text-white hover:bg-rose-500"
                          >
                            <X size={12} /> Reject
                          </button>
                        </>
                      )}
                      {u.kind === 'customer' && u.status === 'approved' && (
                        <button
                          type="button"
                          onClick={() => void setCustomerStatus(u.id, 'pending')}
                          className="px-2 py-1 text-[11px] font-medium rounded-lg border border-slate-200 dark:border-white/15 text-slate-600 dark:text-zinc-300"
                        >
                          Unapprove
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => openEdit(u)}
                        className="px-2 py-1 text-[11px] font-medium rounded-lg border border-slate-200 dark:border-white/15 text-slate-600 dark:text-zinc-300"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        disabled
                        title="Password reset from admin coming soon"
                        className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium rounded-lg border border-slate-200 dark:border-white/10 text-slate-400 dark:text-zinc-500 opacity-60 cursor-not-allowed"
                      >
                        <KeyRound size={12} /> Reset
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-400">
                    No users match this filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-xs text-slate-400">
        {pendingCount} pending · Showing {filtered.length} of {rows.length} people
      </p>

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="w-full max-w-md rounded-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-white/10 shadow-xl p-5 space-y-3">
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">Edit user</h3>
            <div>
              <label className="block text-xs font-medium text-slate-600 dark:text-zinc-400 mb-1">Name</label>
              <input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-black/30"
              />
            </div>
            {editing.kind === 'agent' && (
              <>
                <div>
                  <label className="block text-xs font-medium text-slate-600 dark:text-zinc-400 mb-1">Role label</label>
                  <input
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-white/15 bg-white dark:bg-black/30"
                  />
                </div>
                <label className="inline-flex items-center gap-2 text-sm text-slate-700 dark:text-zinc-300">
                  <input type="checkbox" checked={editAdmin} onChange={(e) => setEditAdmin(e.target.checked)} />
                  <Shield size={14} /> Admin access
                </label>
              </>
            )}
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
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEditing(null)}
                className="px-3 py-1.5 text-sm rounded-lg border border-slate-200 dark:border-white/15"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={() => void saveEdit()}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold rounded-lg bg-violet-600 text-white hover:bg-violet-500 disabled:opacity-50"
              >
                <Save size={14} /> {saving ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {!usingSupabase && (
        <p className="text-xs text-amber-600 dark:text-amber-300">
          Offline demo mode — edits and approvals need a live backend.
        </p>
      )}
    </div>
  );
}
