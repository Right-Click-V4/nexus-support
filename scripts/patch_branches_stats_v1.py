#!/usr/bin/env python3
"""Sync Branches tab names with Live Chat dropdown + period ticket filters."""
from pathlib import Path
import re

CANONICAL = [
    "Abucay", "Abuyog", "Avenida", "Baybay", "Burauen", "Calbayog", "Carigara",
    "Catarman", "Catbalogan", "Kananga", "Maasin", "Ormoc", "Palo-Naga",
    "Palo-Pawing", "Palo-Schisto", "Sogod",
]

data = Path('src/data.ts')
if data.exists() and data.stat().st_size > 500:
    t = data.read_text()
    if 'BRANCHES_CANON_V1' not in t:
        block_lines = ['/** BRANCHES_CANON_V1 — matches Live Chat branch dropdown */', 'export const INITIAL_BRANCHES: Branch[] = [']
        for i, name in enumerate(CANONICAL, 1):
            slug = name.lower().replace(' ', '-')
            block_lines.append(f"  {{ id: 'b{i}', name: '{name}', email: '{slug}@company.com', members: [] }},")
        block_lines.append('];')
        new_block = '\n'.join(block_lines)
        m = re.search(r'export const INITIAL_BRANCHES: Branch\[\] = \[[\s\S]*?\];', t)
        if m:
            t = t[:m.start()] + new_block + t[m.end():]
            data.write_text(t)
            print('data.ts INITIAL_BRANCHES')
        else:
            print('data.ts INITIAL_BRANCHES miss')
    else:
        print('data.ts already')
else:
    print('data.ts skip')

br = Path('src/lib/branches.ts')
if br.exists():
    t = br.read_text()
    if 'BRANCHES_CANON_V1' not in t:
        defaults = ", ".join(f"'{n.upper()}'" for n in CANONICAL)
        t = t.replace(
            "for (const n of ['MAASIN', 'KANANGA', 'AVENIDA', 'CIRIAN', 'SOGOD', 'ORMOC', 'ABUCAY', 'CATARMAN']) {",
            f"// BRANCHES_CANON_V1\n    for (const n of [{defaults}]) {{",
            1,
        )
        br.write_text(t)
        print('branches.ts defaults')
    else:
        print('branches.ts already')

cp = Path('src/components/CustomersPage.tsx')
if not cp.exists() or cp.stat().st_size < 3000:
    print('CustomersPage skip')
else:
    s = cp.read_text()
    if 'BRANCH_PERIOD_FILTER_V1' in s and 'periodFilter' in s and 'Catbalogan' in s:
        print('CustomersPage already')
    else:
        if 'CANONICAL_BRANCH_NAMES' not in s:
            inject = (
                "\nconst CANONICAL_BRANCH_NAMES = [\n"
                + ''.join(f"  '{n}',\n" for n in CANONICAL)
                + "] as const;\n\n"
                "function branchKey(name: string | null | undefined) {\n"
                "  return String(name || '').trim().toUpperCase().replace(/\\s+BRANCH$/, '');\n"
                "}\n\n"
                "type PeriodFilter = 'day' | 'week' | 'month' | 'year' | 'all';\n\n"
                "function inPeriod(iso: string | undefined, period: PeriodFilter, now = Date.now()) {\n"
                "  if (period === 'all') return true;\n"
                "  if (!iso) return false;\n"
                "  const t = new Date(iso).getTime();\n"
                "  if (Number.isNaN(t)) return false;\n"
                "  const d = new Date(now);\n"
                "  if (period === 'day') {\n"
                "    const start = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();\n"
                "    return t >= start;\n"
                "  }\n"
                "  if (period === 'week') {\n"
                "    const day = d.getDay();\n"
                "    const start = new Date(d.getFullYear(), d.getMonth(), d.getDate() - day).getTime();\n"
                "    return t >= start;\n"
                "  }\n"
                "  if (period === 'month') {\n"
                "    const start = new Date(d.getFullYear(), d.getMonth(), 1).getTime();\n"
                "    return t >= start;\n"
                "  }\n"
                "  if (period === 'year') {\n"
                "    const start = new Date(d.getFullYear(), 0, 1).getTime();\n"
                "    return t >= start;\n"
                "  }\n"
                "  return true;\n"
                "}\n"
            )
            s = s.replace(
                "const BRANCH_LS = 'nexus-branches-v1';",
                "const BRANCH_LS = 'nexus-branches-v1';" + inject,
                1,
            )
            print('helpers')

        new_load = (
            "function loadBranches(): Branch[] {\n"
            "  // BRANCH_PERIOD_FILTER_V1 — seed canonical list matching Live Chat dropdown\n"
            "  let list: Branch[] = [];\n"
            "  try {\n"
            "    const raw = localStorage.getItem(BRANCH_LS);\n"
            "    if (raw) list = JSON.parse(raw) as Branch[];\n"
            "  } catch { /* ignore */ }\n"
            "  if (!Array.isArray(list) || list.length === 0) {\n"
            "    list = INITIAL_BRANCHES.map((b) => ({ ...b, members: b.members || [] }));\n"
            "  }\n"
            "  const byKey = new Map<string, Branch>();\n"
            "  for (const b of list) {\n"
            "    const k = branchKey(b.name);\n"
            "    if (!k) continue;\n"
            "    const canon = CANONICAL_BRANCH_NAMES.find((c) => branchKey(c) === k);\n"
            "    byKey.set(k, {\n"
            "      ...b,\n"
            "      name: canon || String(b.name).replace(/\\s+BRANCH$/i, '').trim() || b.name,\n"
            "      members: b.members || [],\n"
            "    });\n"
            "  }\n"
            "  for (const name of CANONICAL_BRANCH_NAMES) {\n"
            "    const k = branchKey(name);\n"
            "    if (!byKey.has(k)) {\n"
            "      byKey.set(k, {\n"
            "        id: `b-${k.toLowerCase()}`,\n"
            "        name,\n"
            "        email: `${name.toLowerCase().replace(/\\s+/g, '-')}@company.com`,\n"
            "        members: [],\n"
            "      });\n"
            "    }\n"
            "  }\n"
            "  const merged = Array.from(byKey.values()).sort((a, b) => a.name.localeCompare(b.name));\n"
            "  try { localStorage.setItem(BRANCH_LS, JSON.stringify(merged)); } catch { /* ignore */ }\n"
            "  return merged;\n"
            "}"
        )
        m_load = re.search(r'function loadBranches\(\): Branch\[] \{[\s\S]*?\n\}', s)
        if m_load:
            s = s[: m_load.start()] + new_load + s[m_load.end() :]
            print('loadBranches')

        if 'periodFilter' not in s:
            s = s.replace(
                "const [search, setSearch] = useState('');",
                "const [search, setSearch] = useState('');\n  const [periodFilter, setPeriodFilter] = useState<PeriodFilter>('all'); // BRANCH_PERIOD_FILTER_V1",
                1,
            )

        s = s.replace(
            "branches.forEach((b) => map.set(b.name.toUpperCase(), { ...b, members: b.members || [] }));\n    tickets.forEach((t) => {\n      if (!t.branch?.trim()) return;\n      const name = t.branch.trim();\n      const key = name.toUpperCase();\n      if (!map.has(key)) map.set(key, { id: `auto-${key}`, name, members: [] });\n    });",
            "branches.forEach((b) => map.set(branchKey(b.name), { ...b, members: b.members || [] }));\n"
            "    tickets.forEach((t) => {\n"
            "      if (!t.branch?.trim()) return;\n"
            "      const name = t.branch.trim();\n"
            "      const key = branchKey(name);\n"
            "      if (!key) return;\n"
            "      if (!map.has(key)) {\n"
            "        const canon = CANONICAL_BRANCH_NAMES.find((c) => branchKey(c) === key);\n"
            "        map.set(key, { id: `auto-${key}`, name: canon || name, members: [] });\n"
            "      }\n"
            "    });",
            1,
        )

        m = re.search(r'  const statsFixed = useMemo\(\(\) => \{[\s\S]*?\}, \[tickets, allBranches\]\);', s)
        if m:
            new_stats = """  const statsFixed = useMemo(() => {
    const m = new Map<string, { total: number; open: number; tickets: Ticket[] }>();
    allBranches.forEach((b) => m.set(branchKey(b.name), { total: 0, open: 0, tickets: [] }));
    tickets.forEach((t) => {
      const key = branchKey(t.branch);
      if (!key) return;
      if (!inPeriod(t.created_at || t.updated_at, periodFilter)) return;
      if (!m.has(key)) m.set(key, { total: 0, open: 0, tickets: [] });
      const row = m.get(key)!;
      row.total += 1;
      const st = String(t.status || '').toLowerCase();
      if (st !== 'resolved' && st !== 'closed') row.open += 1;
      row.tickets.push(t);
    });
    return m;
  }, [tickets, allBranches, periodFilter]);"""
            s = s[: m.start()] + new_stats + s[m.end() :]
            print('stats period')

        s = s.replace(
            "const selectedStats = selectedBranch ? statsFixed.get(selectedBranch.name.toUpperCase()) : null;\n  const branchKey = selectedBranch?.name.trim().toUpperCase() || '';",
            "const selectedStats = selectedBranch ? statsFixed.get(branchKey(selectedBranch.name)) : null;\n  const selectedBranchKey = selectedBranch ? branchKey(selectedBranch.name) : '';",
            1,
        )
        s = s.replace(
            "(c.branch || '').trim().toUpperCase() === branchKey",
            "branchKey(c.branch) === selectedBranchKey",
        )
        s = s.replace(
            "(a.branch || '').trim().toUpperCase() === branchKey",
            "branchKey(a.branch) === selectedBranchKey",
        )

        if 'setPeriodFilter' in s and "['day', 'Day']" not in s:
            ui = (
                "\n        <div className=\"flex items-center gap-1 rounded-lg border border-slate-200 dark:border-white/10 p-0.5 bg-white dark:bg-zinc-900/80\">\n"
                "          {([\n"
                "            ['day', 'Day'],\n"
                "            ['week', 'Week'],\n"
                "            ['month', 'Month'],\n"
                "            ['year', 'Year'],\n"
                "            ['all', 'All'],\n"
                "          ] as const).map(([id, label]) => (\n"
                "            <button\n"
                "              key={id}\n"
                "              type=\"button\"\n"
                "              onClick={() => setPeriodFilter(id)}\n"
                "              className={\n"
                "                periodFilter === id\n"
                "                  ? 'px-2.5 py-1.5 text-xs font-semibold rounded-md bg-violet-600 text-white'\n"
                "                  : 'px-2.5 py-1.5 text-xs font-medium rounded-md text-slate-600 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-white/5'\n"
                "              }\n"
                "            >\n"
                "              {label}\n"
                "            </button>\n"
                "          ))}\n"
                "        </div>\n"
            )
            s = s.replace(
                '<div className="flex items-center gap-3">\n          <div className="text-sm text-slate-500 dark:text-zinc-400">{filtered.length} workplaces</div>',
                '<div className="flex items-center gap-3 flex-wrap">' + ui + '\n          <div className="text-sm text-slate-500 dark:text-zinc-400">{filtered.length} workplaces · tickets: {periodFilter === \'all\' ? \'all time\' : periodFilter}</div>',
                1,
            )
            print('period UI')

        s = s.replace(
            'const oa = statsFixed.get(a.name.toUpperCase())?.open || 0;\n      const ob = statsFixed.get(b.name.toUpperCase())?.open || 0;',
            'const oa = statsFixed.get(branchKey(a.name))?.open || 0;\n      const ob = statsFixed.get(branchKey(b.name))?.open || 0;',
        )
        s = s.replace(
            "const s = statsFixed.get(b.name.toUpperCase()) || { total: 0, open: 0, tickets: [] };\n          const key = b.name.toUpperCase();\n          const custCount = customers.filter((c) => (c.branch || '').toUpperCase() === key).length;",
            "const s = statsFixed.get(branchKey(b.name)) || { total: 0, open: 0, tickets: [] };\n          const key = branchKey(b.name);\n          const custCount = customers.filter((c) => branchKey(c.branch) === key).length;",
        )

        cp.write_text(s)
        print('CustomersPage braces', s.count('{') - s.count('}'))

print('patch_branches_stats_v1 done')
