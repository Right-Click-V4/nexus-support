"""Fix branch delete, MetricBar light mode, dark-mode Off button contrast."""
from pathlib import Path

cp = Path('src/components/CustomersPage.tsx')
if cp.exists():
    s = cp.read_text()
    if 'DELETED_BRANCHES_V1' not in s:
        if "const BRANCH_LS = 'nexus-branches-v1';" in s:
            s = s.replace(
                "const BRANCH_LS = 'nexus-branches-v1';",
                '''const BRANCH_LS = 'nexus-branches-v1';
const DELETED_BRANCH_LS = 'nexus-deleted-branches-v1'; // DELETED_BRANCHES_V1

function loadDeletedBranches(): Set<string> {
  try {
    const raw = localStorage.getItem(DELETED_BRANCH_LS);
    if (raw) return new Set((JSON.parse(raw) as string[]).map((x) => x.toUpperCase()));
  } catch {}
  return new Set();
}
function saveDeletedBranches(set: Set<string>) {
  try {
    localStorage.setItem(DELETED_BRANCH_LS, JSON.stringify([...set]));
  } catch {}
}
''',
                1,
            )
        if 'const [branches, setBranches] = useState' in s and 'deletedBranches' not in s:
            s = s.replace(
                'const [branches, setBranches] = useState<Branch[]>(loadBranches);',
                '''const [branches, setBranches] = useState<Branch[]>(loadBranches);
  const [deletedBranches, setDeletedBranches] = useState<Set<string>>(() => loadDeletedBranches());''',
                1,
            )
        old_ab = '''  const allBranches = useMemo(() => {
    const map = new Map<string, Branch>();
    branches.forEach((b) => map.set(b.name.toUpperCase(), { ...b, members: b.members || [] }));
    tickets.forEach((t) => {
      if (!t.branch?.trim()) return;
      const name = t.branch.trim();
      const key = name.toUpperCase();
      if (!map.has(key)) map.set(key, { id: `auto-${key}`, name, members: [] });
    });
    return Array.from(map.values());
  }, [branches, tickets]);'''
        new_ab = '''  const allBranches = useMemo(() => {
    const map = new Map<string, Branch>();
    branches.forEach((b) => {
      const key = b.name.toUpperCase();
      if (deletedBranches.has(key)) return;
      map.set(key, { ...b, members: b.members || [] });
    });
    tickets.forEach((t) => {
      if (!t.branch?.trim()) return;
      const name = t.branch.trim();
      const key = name.toUpperCase();
      if (deletedBranches.has(key)) return;
      if (!map.has(key)) map.set(key, { id: `auto-${key}`, name, members: [] });
    });
    return Array.from(map.values());
  }, [branches, tickets, deletedBranches]);'''
        if old_ab in s:
            s = s.replace(old_ab, new_ab, 1)
        old_del = '''  const deleteBranch = () => {
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
  };'''
        new_del = '''  const deleteBranch = () => {
    if (!selectedBranch) return;
    const count = selectedStats?.total || 0;
    const msg =
      count > 0
        ? `Delete "${selectedBranch.name}"? ${count} ticket(s) keep their data.`
        : `Delete branch "${selectedBranch.name}"?`;
    if (!confirm(msg)) return;
    const key = selectedBranch.name.toUpperCase();
    const nextDeleted = new Set(deletedBranches);
    nextDeleted.add(key);
    setDeletedBranches(nextDeleted);
    saveDeletedBranches(nextDeleted);
    persist(branches.filter((b) => b.name.toUpperCase() !== key));
    setSelected(null);
    setEditing(false);
  };'''
        if old_del in s:
            s = s.replace(old_del, new_del, 1)
        if 'const addBranch = () => {' in s and 'nextDeleted.delete' not in s:
            s = s.replace(
                '''    persist([...branches, branch]);
    setSelected(name);''',
                '''    if (deletedBranches.has(name)) {
      const nextDeleted = new Set(deletedBranches);
      nextDeleted.delete(name);
      setDeletedBranches(nextDeleted);
      saveDeletedBranches(nextDeleted);
    }
    persist([...branches, branch]);
    setSelected(name);''',
                1,
            )
        cp.write_text(s)
        print('CustomersPage written')
    else:
        print('branch delete already')
else:
    print('CustomersPage missing')

mb = Path('src/components/MetricBar.tsx')
if mb.exists():
    s = mb.read_text()
    if 'METRIC_LIGHT_V1' not in s:
        old = '    <div className="bg-gradient-to-r from-zinc-950 via-brand-950 to-zinc-900 text-white rounded-2xl px-5 py-4 flex flex-wrap items-center gap-6 lg:gap-8 shadow-lg border border-white/5">'
        new = '    <div className="/* METRIC_LIGHT_V1 */ bg-gradient-to-r from-white via-violet-50 to-white dark:from-zinc-950 dark:via-brand-950 dark:to-zinc-900 text-zinc-900 dark:text-white rounded-2xl px-5 py-4 flex flex-wrap items-center gap-6 lg:gap-8 shadow-lg border border-zinc-200/80 dark:border-white/5">'
        if old in s:
            s = s.replace(old, new, 1)
        s = s.replace(
            'text-xs text-zinc-400 flex items-center gap-1',
            'text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1',
        )
        s = s.replace(
            'text-[11px] uppercase tracking-wider text-zinc-400 font-medium',
            'text-[11px] uppercase tracking-wider text-zinc-500 dark:text-zinc-400 font-medium',
        )
        s = s.replace(
            'className="ml-1 p-1.5 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/5"',
            'className="ml-1 p-1.5 rounded-lg text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-white/5"',
        )
        s = s.replace(
            'className="h-8 w-px bg-white/10 hidden sm:block"',
            'className="h-8 w-px bg-zinc-200 dark:bg-white/10 hidden sm:block"',
        )
        s = s.replace('text-zinc-400', 'text-zinc-500 dark:text-zinc-400')
        mb.write_text(s)
        print('MetricBar written')
    else:
        print('metric already')
else:
    print('MetricBar missing')

af = Path('src/components/AdminFeaturesPage.tsx')
if af.exists():
    s = af.read_text()
    if 'OFF_BTN_DARK_V1' not in s:
        s = s.replace(
            "maintOn ? 'bg-amber-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'",
            "maintOn ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-800 hover:bg-slate-300 dark:bg-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-600' /* OFF_BTN_DARK_V1 */",
        )
        s = s.replace(
            "site404On ? 'bg-rose-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'",
            "site404On ? 'bg-rose-500 text-white' : 'bg-slate-200 text-slate-800 hover:bg-slate-300 dark:bg-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-600'",
        )
        s = s.replace(
            'bg-slate-100 text-slate-700',
            'bg-slate-200 text-slate-800 dark:bg-zinc-700 dark:text-zinc-100',
        )
        s = s.replace(
            'bg-white rounded-xl border border-slate-200',
            'bg-white dark:bg-zinc-900/80 rounded-xl border border-slate-200 dark:border-white/10',
        )
        s = s.replace('text-slate-900', 'text-slate-900 dark:text-zinc-50')
        s = s.replace('text-slate-500', 'text-slate-500 dark:text-zinc-400')
        af.write_text(s)
        print('AdminFeatures contrast')
    else:
        print('admin off already')
else:
    print('AdminFeatures missing')

for css_path in ['src/theme-modes.css', 'src/index.css']:
    p = Path(css_path)
    if not p.exists():
        continue
    c = p.read_text()
    if 'METRIC_LIGHT_CSS_V1' in c:
        continue
    p.write_text(c.rstrip() + '''

/* METRIC_LIGHT_CSS_V1 */
html:not(.dark):not(.nexus-dark) [class*="from-zinc-950"][class*="via-brand-950"],
html:not(.dark):not(.nexus-dark) .metric-bar-force-light {
  background: linear-gradient(90deg, #ffffff, #f5f3ff, #ffffff) !important;
  color: #18181b !important;
  border-color: rgba(113, 113, 122, 0.25) !important;
}
html.dark button[aria-pressed="false"],
html.nexus-dark button[aria-pressed="false"] {
  background: #3f3f46 !important;
  color: #f4f4f5 !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
}
''')
    print('css', css_path)

print('DONE')
