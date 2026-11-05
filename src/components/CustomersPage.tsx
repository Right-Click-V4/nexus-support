/* dark-cards-v1 */
import { useMemo, useState } from 'react';
import {
  Search, Building2, Mail, Users, UserCog, X, Ticket as TicketIcon, UserPlus,
  Pencil, Trash2, Check,
} from 'lucide-react';
import { useTickets } from '../context/TicketContext';
import { INITIAL_BRANCHES } from '../data';
import { ticketBranch } from '../types';
import type { Ticket, Branch, BranchMember } from '../types';

const BRANCH_LS = 'nexus-branches-v1';

function loadBranches(): Branch[] {
  try {
    const raw = localStorage.getItem(BRANCH_LS);
    if (raw) return JSON.parse(raw) as Branch[];
  } catch {}
  return INITIAL_BRANCHES;
}

function saveBranches(list: Branch[]) {
  try {
    localStorage.setItem(BRANCH_LS, JSON.stringify(list));
  } catch {}
}

export default function CustomersPage() {
  const { tickets, agents, customers, updateTicket } = useTickets();
  const [search, setSearch] = useState('');
  const [branches, setBranches] = useState<Branch[]>(loadBranches);
  const [selected, setSelected] = useState<string | null>(null);
  const [newMemberName, setNewMemberName] = useState('');
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState('Staff');
  const [newBranchName, setNewBranchName] = useState('');
  const [newBranchEmail, setNewBranchEmail] = useState('');
  const [showNewBranch, setShowNewBranch] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editMemberId, setEditMemberId] = useState<string | null>(null);
  const [editMemberName, setEditMemberName] = useState('');
  const [editMemberEmail, setEditMemberEmail] = useState('');
  const [editMemberRole, setEditMemberRole] = useState('');

  const allBranches = useMemo(() => {
    const map = new Map<string, Branch>();
    branches.forEach((b) => map.set(b.name.toUpperCase(), { ...b, members: b.members || [] }));
    tickets.forEach((t) => {
      if (!t.branch?.trim()) return;
      const name = t.branch.trim();
      const key = name.toUpperCase();
      if (!map.has(key)) map.set(key, { id: `auto-${key}`, name, members: [] });
    });
    return Array.from(map.values());
  }, [branches, tickets]);

  const statsFixed = useMemo(() => {
    const m = new Map<string, { total: number; open: number; tickets: Ticket[] }>();
    allBranches.forEach((b) => m.set(b.name.toUpperCase(), { total: 0, open: 0, tickets: [] }));
    tickets.forEach((t) => {
      const name = t.branch?.trim() || '';
      if (!name) return;
      const key = name.toUpperCase();
      const row = m.get(key);
      if (!row) return;
      row.total += 1;
      if (t.status !== 'resolved') row.open += 1;
      row.tickets.push(t);
    });
    return m;
  }, [tickets, allBranches]);

  const filtered = allBranches
    .filter(
      (b) =>
        !search ||
        b.name.toLowerCase().includes(search.toLowerCase()) ||
        (b.email || '').toLowerCase().includes(search.toLowerCase()) ||
        b.members.some((m) => m.name.toLowerCase().includes(search.toLowerCase()))
    )
    .sort((a, b) => {
      const oa = statsFixed.get(a.name.toUpperCase())?.open || 0;
      const ob = statsFixed.get(b.name.toUpperCase())?.open || 0;
      return ob - oa;
    });

  const selectedBranch = allBranches.find((b) => b.name === selected) || null;
  const selectedStats = selectedBranch ? statsFixed.get(selectedBranch.name.toUpperCase()) : null;
  const branchKey = selectedBranch?.name.trim().toUpperCase() || '';
  const branchCustomers = customers.filter(
    (c) => (c.branch || '').trim().toUpperCase() === branchKey
  );
  const branchAgents = agents.filter(
    (a) => (a.branch || '').trim().toUpperCase() === branchKey
  );

  const persist = (next: Branch[]) => {
    setBranches(next);
    saveBranches(next);
  };

  const ensureInList = (branch: Branch): Branch[] => {
    if (branches.some((b) => b.name.toUpperCase() === branch.name.toUpperCase())) {
      return branches.map((b) =>
        b.name.toUpperCase() === branch.name.toUpperCase() ? { ...branch, id: b.id } : b
      );
    }
    return [...branches, branch];
  };

  const addBranch = () => {
    const name = newBranchName.trim().toUpperCase();
    if (!name) return;
    if (allBranches.some((b) => b.name.toUpperCase() === name)) {
      setSelected(allBranches.find((b) => b.name.toUpperCase() === name)!.name);
      setShowNewBranch(false);
      setNewBranchName('');
      setNewBranchEmail('');
      return;
    }
    const branch: Branch = {
      id: `b-${Date.now()}`,
      name,
      email: newBranchEmail.trim() || undefined,
      members: [],
    };
    persist([...branches, branch]);
    setSelected(name);
    setShowNewBranch(false);
    setNewBranchName('');
    setNewBranchEmail('');
  };

  const startEdit = () => {
    if (!selectedBranch) return;
    setEditName(selectedBranch.name);
    setEditEmail(selectedBranch.email || '');
    setEditing(true);
  };

  const saveEdit = async () => {
    if (!selectedBranch || !editName.trim()) return;
    const newName = editName.trim().toUpperCase();
    const oldName = selectedBranch.name;
    const oldKey = oldName.toUpperCase();
    if (newName !== oldKey && allBranches.some((b) => b.name.toUpperCase() === newName)) {
      alert('A branch with that name already exists.');
      return;
    }
    const updated: Branch = {
      ...selectedBranch,
      name: newName,
      email: editEmail.trim() || undefined,
    };
    let next = ensureInList(updated);
    if (newName !== oldKey) {
      const map = new Map<string, Branch>();
      next.forEach((b) => {
        if (b.name.toUpperCase() !== oldKey) map.set(b.name.toUpperCase(), b);
      });
      map.set(newName, updated);
      next = Array.from(map.values());
      const toUpdate = tickets.filter(
        (t) =>
          (t.branch || '').toUpperCase() === oldKey ||
          (!t.branch && (t.customer_name || '').toUpperCase() === oldKey)
      );
      for (const t of toUpdate) {
        try {
          await updateTicket(t.id, { branch: newName });
        } catch (e) {
          console.error(e);
        }
      }
    }
    persist(next);
    setSelected(newName);
    setEditing(false);
  };

  const deleteBranch = () => {
    if (!selectedBranch) return;
    const count = selectedStats?.total || 0;
    const msg =
      count > 0
        ? `Delete "${selectedBranch.name}"? ${count} ticket(s) keep their data.`
        : `Delete branch "${selectedBranch.name}"?`;
    if (!confirm(msg)) return;
    persist(branches.filter((b) => b.name.toUpperCase() !== selectedBranch.name.toUpperCase()));
    setSelected(null);
    setEditing(false);
  };

  const addMember = () => {
    if (!selectedBranch || !newMemberName.trim()) return;
    const member: BranchMember = {
      id: `m-${Date.now()}`,
      name: newMemberName.trim(),
      email: newMemberEmail.trim() || undefined,
      role: newMemberRole.trim() || 'Staff',
    };
    persist(
      ensureInList({
        ...selectedBranch,
        members: [...(selectedBranch.members || []), member],
      })
    );
    setNewMemberName('');
    setNewMemberEmail('');
    setNewMemberRole('Staff');
  };

  const removeMember = (memberId: string) => {
    if (!selectedBranch) return;
    persist(
      ensureInList({
        ...selectedBranch,
        members: (selectedBranch.members || []).filter((m) => m.id !== memberId),
      })
    );
  };

  const startEditMember = (m: BranchMember) => {
    setEditMemberId(m.id);
    setEditMemberName(m.name);
    setEditMemberEmail(m.email || '');
    setEditMemberRole(m.role || 'Staff');
  };

  const saveEditMember = () => {
    if (!selectedBranch || !editMemberId || !editMemberName.trim()) return;
    persist(
      ensureInList({
        ...selectedBranch,
        members: (selectedBranch.members || []).map((m) =>
          m.id === editMemberId
            ? {
                ...m,
                name: editMemberName.trim(),
                email: editMemberEmail.trim() || undefined,
                role: editMemberRole.trim() || 'Staff',
              }
            : m
        ),
      })
    );
    setEditMemberId(null);
  };

  void ticketBranch;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search branches or members"
            className="w-full pl-9 pr-3 py-2 text-sm bg-white dark:bg-zinc-900 border border-slate-200 dark:border-white/10 rounded-lg text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
          />
        </div>
        <div className="flex items-center gap-3">
          <div className="text-sm text-slate-500 dark:text-zinc-400">{filtered.length} workplaces</div>
          <button type="button" onClick={() => setShowNewBranch((v) => !v)} className="px-3 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700">
            + Branch
          </button>
        </div>
      </div>

      {showNewBranch && (
        <div className="bg-white dark:bg-zinc-900/90 rounded-xl border border-slate-200 dark:border-white/10 p-4 flex flex-wrap gap-2 items-end shadow-sm">
          <div className="flex-1 min-w-[180px]">
            <label className="text-xs text-slate-500 dark:text-zinc-400">Branch name *</label>
            <input value={newBranchName} onChange={(e) => setNewBranchName(e.target.value)} placeholder="e.g. CIRIAN BRANCH" className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-100 rounded-lg" onKeyDown={(e) => e.key === 'Enter' && addBranch()} />
          </div>
          <div className="flex-1 min-w-[180px]">
            <label className="text-xs text-slate-500 dark:text-zinc-400">Contact email</label>
            <input value={newBranchEmail} onChange={(e) => setNewBranchEmail(e.target.value)} placeholder="branch@company.com" className="w-full px-3 py-2 text-sm border border-slate-200 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-100 rounded-lg" />
          </div>
          <button type="button" onClick={addBranch} className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg">Add</button>
          <button type="button" onClick={() => setShowNewBranch(false)} className="px-4 py-2 text-sm text-slate-600 dark:text-zinc-300">Cancel</button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((b) => {
          const s = statsFixed.get(b.name.toUpperCase()) || { total: 0, open: 0, tickets: [] };
          const key = b.name.toUpperCase();
          const custCount = customers.filter((c) => (c.branch || '').toUpperCase() === key).length;
          return (
            <button
              key={b.id || b.name}
              type="button"
              onClick={() => { setSelected(b.name); setEditing(false); setEditMemberId(null); }}
              className="text-left bg-white dark:bg-zinc-900/90 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm p-5 hover:border-brand-300 dark:hover:border-violet-500/40 hover:shadow-md transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-brand-50 dark:bg-violet-500/20 flex items-center justify-center text-brand-600 dark:text-violet-300 shrink-0">
                  <Building2 size={20} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-slate-900 dark:text-zinc-100 truncate">{b.name}</div>
                  {b.email && (
                    <div className="text-xs text-slate-500 dark:text-zinc-400 flex items-center gap-1 mt-0.5"><Mail size={12} />{b.email}</div>
                  )}
                  <div className="text-xs text-slate-400 dark:text-zinc-500 mt-1 flex items-center gap-1">
                    <Users size={12} />
                    {custCount} customer{custCount !== 1 ? 's' : ''} · {(b.members || []).length} staff
                  </div>
                </div>
              </div>
              <div className="mt-4 flex gap-4 text-sm">
                <div>
                  <div className="text-lg font-bold text-slate-800 dark:text-zinc-100 tabular-nums">{s.total}</div>
                  <div className="text-[11px] text-slate-500 dark:text-zinc-400">Total tickets</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-amber-600 tabular-nums">{s.open}</div>
                  <div className="text-[11px] text-slate-500 dark:text-zinc-400">Open</div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="bg-white dark:bg-zinc-900/90 rounded-xl border border-slate-200 dark:border-white/10 p-12 text-center text-slate-500 dark:text-zinc-400">
          No branches found. Create one with + Branch.
        </div>
      )}

      {selectedBranch && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={() => setSelected(null)}>
          <div className="w-full max-w-lg bg-white dark:bg-zinc-900 h-full shadow-2xl overflow-y-auto text-slate-900 dark:text-zinc-100" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-slate-200 dark:border-white/10 px-5 py-4 z-10">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="text-xs text-slate-400 uppercase tracking-wide">Workplace / Branch</div>
                  {editing ? (
                    <div className="mt-1 space-y-2">
                      <input value={editName} onChange={(e) => setEditName(e.target.value)} className="w-full px-3 py-2 text-sm font-semibold border border-slate-200 dark:border-white/10 dark:bg-zinc-950 rounded-lg" />
                      <input value={editEmail} onChange={(e) => setEditEmail(e.target.value)} className="w-full px-3 py-1.5 text-xs border border-slate-200 dark:border-white/10 dark:bg-zinc-950 rounded-lg" placeholder="Contact email" />
                    </div>
                  ) : (
                    <>
                      <h2 className="text-lg font-semibold text-slate-900 dark:text-zinc-100">{selectedBranch.name}</h2>
                      {selectedBranch.email && <div className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">{selectedBranch.email}</div>}
                    </>
                  )}
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {editing ? (
                    <>
                      <button type="button" onClick={() => void saveEdit()} className="p-1.5 rounded-lg hover:bg-emerald-50 text-emerald-600"><Check size={18} /></button>
                      <button type="button" onClick={() => setEditing(false)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500"><X size={18} /></button>
                    </>
                  ) : (
                    <>
                      <button type="button" onClick={startEdit} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500"><Pencil size={16} /></button>
                      <button type="button" onClick={deleteBranch} className="p-1.5 rounded-lg hover:bg-rose-50 text-slate-400 hover:text-rose-600"><Trash2 size={16} /></button>
                      <button type="button" onClick={() => setSelected(null)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500"><X size={20} /></button>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="p-5 space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Users size={16} className="text-slate-400" />
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200">Customers at this branch ({branchCustomers.length})</h3>
                </div>
                {branchCustomers.length === 0 && (
                  <p className="text-xs text-slate-400 mb-2">No customers assigned. Use Manage - Users to set their branch.</p>
                )}
                <div className="space-y-2">
                  {branchCustomers.map((c) => (
                    <div key={c.id} className="border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2.5 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 text-[10px] font-bold flex items-center justify-center">
                        {(c.name || '?').slice(0, 2).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate">{c.name}</div>
                        <div className="text-xs text-slate-400 truncate">{c.email || 'No email'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <UserCog size={16} className="text-slate-400" />
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200">Agents covering this branch ({branchAgents.length})</h3>
                </div>
                {branchAgents.length === 0 && (
                  <p className="text-xs text-slate-400 mb-2">No agents assigned. Set branch on an agent from Users.</p>
                )}
                <div className="space-y-2">
                  {branchAgents.map((a) => (
                    <div key={a.id} className="border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2.5 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-violet-100 text-violet-700 text-[10px] font-bold flex items-center justify-center">
                        {a.initials || a.name.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate">{a.name}{a.is_admin ? ' · Admin' : ''}</div>
                        <div className="text-xs text-slate-400 truncate">{a.role} · {a.status}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <UserPlus size={16} className="text-slate-400" />
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200">Branch staff ({(selectedBranch.members || []).length})</h3>
                </div>
                {(selectedBranch.members || []).length === 0 && (
                  <p className="text-xs text-slate-400">No staff listed yet.</p>
                )}
                <div className="space-y-2 mb-3">
                  {(selectedBranch.members || []).map((m) => (
                    <div key={m.id} className="border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2.5 flex items-center justify-between gap-2">
                      {editMemberId === m.id ? (
                        <div className="flex-1 space-y-1">
                          <input value={editMemberName} onChange={(e) => setEditMemberName(e.target.value)} className="w-full px-2 py-1 text-sm border rounded dark:bg-zinc-950 dark:border-white/10" />
                          <input value={editMemberEmail} onChange={(e) => setEditMemberEmail(e.target.value)} className="w-full px-2 py-1 text-xs border rounded dark:bg-zinc-950 dark:border-white/10" placeholder="Email" />
                          <input value={editMemberRole} onChange={(e) => setEditMemberRole(e.target.value)} className="w-full px-2 py-1 text-xs border rounded dark:bg-zinc-950 dark:border-white/10" placeholder="Role" />
                          <div className="flex gap-2 pt-1">
                            <button type="button" onClick={saveEditMember} className="text-xs text-emerald-600">Save</button>
                            <button type="button" onClick={() => setEditMemberId(null)} className="text-xs text-slate-500">Cancel</button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-slate-800 dark:text-zinc-100">{m.name}</div>
                            <div className="text-xs text-slate-400">{m.role}{m.email ? ` · ${m.email}` : ''}</div>
                          </div>
                          <div className="flex gap-1">
                            <button type="button" onClick={() => startEditMember(m)} className="p-1 text-slate-400 hover:text-slate-600"><Pencil size={14} /></button>
                            <button type="button" onClick={() => removeMember(m.id)} className="p-1 text-slate-400 hover:text-rose-600"><Trash2 size={14} /></button>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2 items-end border-t border-slate-100 dark:border-white/10 pt-3">
                  <input value={newMemberName} onChange={(e) => setNewMemberName(e.target.value)} placeholder="Name" className="flex-1 min-w-[100px] px-2 py-1.5 text-sm border border-slate-200 dark:border-white/10 dark:bg-zinc-950 rounded-lg" />
                  <input value={newMemberEmail} onChange={(e) => setNewMemberEmail(e.target.value)} placeholder="Email" className="flex-1 min-w-[100px] px-2 py-1.5 text-sm border border-slate-200 dark:border-white/10 dark:bg-zinc-950 rounded-lg" />
                  <input value={newMemberRole} onChange={(e) => setNewMemberRole(e.target.value)} placeholder="Role" className="w-24 px-2 py-1.5 text-sm border border-slate-200 dark:border-white/10 dark:bg-zinc-950 rounded-lg" />
                  <button type="button" onClick={addMember} className="px-3 py-1.5 text-sm text-white bg-brand-600 rounded-lg">Add</button>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <TicketIcon size={16} className="text-slate-400" />
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-zinc-200">Tickets ({selectedStats?.total || 0})</h3>
                </div>
                {(selectedStats?.tickets || []).length === 0 && (
                  <p className="text-xs text-slate-400">No tickets for this branch.</p>
                )}
                <div className="space-y-2">
                  {(selectedStats?.tickets || []).slice(0, 20).map((t) => (
                    <div key={t.id} className="border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2">
                      <div className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate">{t.title}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{t.id} · {t.status} · {t.priority}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
