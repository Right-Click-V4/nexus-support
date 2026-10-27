#!/usr/bin/env python3
"""Portal branch dropdown: fixed Leyte/Samar list, alphabetical; placeholder only."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "branch-list-v1" in c:
    print("already")
    raise SystemExit(0)

old_bo = "const BRANCH_OPTIONS = INITIAL_BRANCHES.map((b) => b.name);"
new_bo = """/** Fixed portal branch list (alphabetical) */
const BRANCH_OPTIONS = [
  'Abucay',
  'Abuyog',
  'Avenida',
  'Baybay',
  'Burauen',
  'Calbayog',
  'Carigara',
  'Catarman',
  'Catbalogan',
  'Kananga',
  'Maasin',
  'Ormoc',
  'Palo-Naga',
  'Palo-Pawing',
  'Palo-Schisto',
  'Sogod',
] as const;"""

if old_bo in c:
    c = c.replace(old_bo, new_bo, 1)
    print("BRANCH_OPTIONS ok")
else:
    print("BRANCH_OPTIONS miss")

old_memo = """  const branchOptions = useMemo(() => {
    const set = new Set(BRANCH_OPTIONS);
    tickets.forEach((t) => { if (t.branch) set.add(t.branch); });
    try {
      const raw = localStorage.getItem('nexus-branches-v1');
      if (raw) (JSON.parse(raw) as { name: string }[]).forEach((b) => set.add(b.name));
    } catch {}
    return Array.from(set).sort();
  }, [tickets]);"""

new_memo = """  const branchOptions = useMemo(() => [...BRANCH_OPTIONS], []);"""

if old_memo in c:
    c = c.replace(old_memo, new_memo, 1)
    print("memo ok")
else:
    t2, n = re.subn(
        r"  const branchOptions = useMemo\(\(\) => \{[\s\S]*?\}, \[tickets\]\);",
        "  const branchOptions = useMemo(() => [...BRANCH_OPTIONS], []);",
        c,
        count=1,
    )
    if n:
        c = t2
        print("memo loose ok")
    else:
        print("memo miss")

old_sel = """                    <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                      <option value="">Select branch…</option>
                      {branchOptions.map((b) => <option key={b} value={b}>{b}</option>)}
                    </select>"""

new_sel = """                    <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                      <option value="" disabled>
                        Select branch…
                      </option>
                      {branchOptions.map((b) => (
                        <option key={b} value={b}>{b}</option>
                      ))}
                    </select>"""

if old_sel in c:
    c = c.replace(old_sel, new_sel, 1)
    print("select ok")
else:
    c = c.replace(
        '<option value="">Select branch…</option>',
        '<option value="" disabled>Select branch…</option>',
        1,
    )
    print("select partial")

if "branch-list-v1" not in c:
    c = c.replace("/* submit-layout-v1 */", "/* submit-layout-v1 */ /* branch-list-v1 */", 1)
    if "branch-list-v1" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* branch-list-v1 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("done")
