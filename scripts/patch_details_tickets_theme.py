#!/usr/bin/env python3
"""Sentence-case Details; theme-aware agent Tickets table; bold capitalized Subject."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "details-tickets-theme-v1" not in c:
    if "function capitalizeSentences" not in c:
        marker = "type PortalView ="
        if marker in c:
            helper = '''function capitalizeSentences(text: string): string {
  if (!text) return text;
  return text.replace(/(^|[.!?\\s]+)([a-z])/g, (_m, lead: string, ch: string) => lead + ch.toUpperCase());
}

'''
            # fix: use proper regex in output file
            helper = (
                "function capitalizeSentences(text: string): string {\n"
                "  if (!text) return text;\n"
                "  return text.replace(/(^[.!?\\n]\\s*)|([.!?\\n]\\s+)([a-z])/g, (m, a, b, ch) => {\n"
                "    // handled below\n"
                "    return m;\n"
                "  });\n"
                "}\n\n"
            )
            helper = (
                "function capitalizeSentences(text: string): string {\n"
                "  if (!text) return text;\n"
                "  return text.replace(/(^|[.!?\\n]\\s+)([a-z])/g, (_m, lead: string, ch: string) => lead + ch.toUpperCase());\n"
                "}\n\n"
            )
            c = c.replace(marker, helper + marker, 1)
            print("helper ok")
        else:
            print("helper marker miss")

    old_ta = """                      <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={4}
                        placeholder="Describe what happened, steps to reproduce, and any error messages…"
                        className={field}
                      />"""
    new_ta = """                      <textarea
                        value={description}
                        onChange={(e) => setDescription(capitalizeSentences(e.target.value))}
                        onBlur={(e) => setDescription(capitalizeSentences(e.target.value))}
                        rows={4}
                        placeholder="Describe what happened, steps to reproduce, and any error messages…"
                        className={field}
                      />"""
    if old_ta in c:
        c = c.replace(old_ta, new_ta, 1)
        print("textarea ok")
    else:
        print("textarea miss")

    c = c.replace(
        "description: description.trim(),",
        "description: capitalizeSentences(description.trim()),",
        1,
    )

    if "details-tickets-theme-v1" not in c:
        c = c.replace("/* modal-glow-v2 */", "/* modal-glow-v2 */ /* details-tickets-theme-v1 */", 1)
        if "details-tickets-theme-v1" not in c:
            c = "/* details-tickets-theme-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

tp = Path("src/components/TicketsPage.tsx")
t = tp.read_text()
if "details-tickets-theme-v1" in t:
    print("tp already")
else:
    t = t.replace(
        '<div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">',
        '<div className="tickets-table-panel rounded-xl border shadow-sm overflow-hidden">',
        1,
    )
    t = t.replace(
        '<thead className="bg-slate-50 border-b border-slate-200">\n              <tr className="text-left text-slate-500">',
        '<thead className="tickets-table-head border-b">\n              <tr className="text-left">',
        1,
    )

    t2, n = re.subn(
        r'<td className="px-4 py-3 font-medium text-slate-800 max-w-\[240px\]">\s*'
        r'<div className="truncate" title=\{t\.title\}>\{t\.title\}</div>\s*'
        r'\{t\.description \? \(\s*'
        r'<div className="text-\[11px\] text-slate-400 truncate mt-0\.5 font-normal" title=\{t\.description\}>\s*'
        r'\{t\.description\}\s*'
        r'</div>\s*'
        r'\) : null\}',
        '''<td className="px-4 py-3 max-w-[240px]">
                      <div className="tickets-subject truncate font-bold tracking-wide" title={t.title}>
                        {t.title}
                      </div>
                      {t.description ? (
                        <div className="tickets-desc text-[11px] truncate mt-0.5 font-normal" title={t.description}>
                          {t.description}
                        </div>
                      ) : null}''',
        t,
        count=1,
    )
    if n:
        t = t2
        print("subject cell ok")
    else:
        if 'title={t.title}>{t.title}</div>' in t:
            t = t.replace(
                '<div className="truncate" title={t.title}>{t.title}</div>',
                '<div className="tickets-subject truncate font-bold tracking-wide" title={t.title}>{t.title}</div>',
                1,
            )
            t = t.replace(
                'className="text-[11px] text-slate-400 truncate mt-0.5 font-normal"',
                'className="tickets-desc text-[11px] truncate mt-0.5 font-normal"',
                1,
            )
            t = t.replace(
                'className="px-4 py-3 font-medium text-slate-800 max-w-[240px]"',
                'className="px-4 py-3 max-w-[240px]"',
                1,
            )
            print("subject cell simple ok")
        else:
            print("subject cell miss")

    t = t.replace(
        """className={clsx(
                      'border-b border-slate-100 hover:bg-brand-50/50 cursor-pointer transition-colors',
                      t.status === 'new' && t.channel === 'portal' && 'bg-violet-50/80 ring-1 ring-inset ring-violet-200/60',
                      t.status === 'new' && t.channel !== 'portal' && 'bg-brand-50/40'
                    )}""",
        """className={clsx(
                      'tickets-row border-b cursor-pointer transition-colors',
                      t.status === 'new' && t.channel === 'portal' && 'tickets-row-new-portal',
                      t.status === 'new' && t.channel !== 'portal' && 'tickets-row-new'
                    )}""",
        1,
    )

    replacements = [
        ('className="px-4 py-3 font-mono text-xs text-slate-500"', 'className="px-4 py-3 font-mono text-xs tickets-muted"'),
        ('className="px-4 py-3 text-slate-600 text-xs max-w-[120px] truncate"', 'className="px-4 py-3 tickets-cell text-xs max-w-[120px] truncate"'),
        ('className="px-4 py-3 text-[11px] text-slate-500 whitespace-nowrap tabular-nums"', 'className="px-4 py-3 text-[11px] tickets-muted whitespace-nowrap tabular-nums"'),
        ('className="px-4 py-3 text-slate-600"', 'className="px-4 py-3 tickets-cell"'),
        ('className="text-slate-800 font-medium"', 'className="tickets-cell font-medium"'),
        ('className="text-[11px] text-slate-400 truncate max-w-[140px]"', 'className="text-[11px] tickets-muted truncate max-w-[140px]"'),
        ('className="p-10 text-center text-slate-400 text-sm"', 'className="p-10 text-center tickets-muted text-sm"'),
        ('className="px-4 py-6 text-center text-slate-400"', 'className="px-4 py-6 text-center tickets-muted"'),
    ]
    for a, b in replacements:
        if a in t:
            t = t.replace(a, b)
    print("cell classes updated")

    if "details-tickets-theme-v1" not in t:
        t = "/* details-tickets-theme-v1 */\n" + t
    tp.write_text(t)
    print("tp done")

css = """

/* details-tickets-theme-v1 — agent Tickets table readable in light/dark */
.tickets-table-panel {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #0f172a;
}
html.nexus-dark .tickets-table-panel,
.dark .tickets-table-panel {
  background: rgba(24, 20, 42, 0.92);
  border-color: rgba(167, 139, 250, 0.22);
  color: #f1f5f9;
}
.tickets-table-head {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #64748b;
}
html.nexus-dark .tickets-table-head,
.dark .tickets-table-head {
  background: rgba(15, 12, 30, 0.95);
  border-color: rgba(167, 139, 250, 0.18);
  color: #c4b5fd;
}
.tickets-table-head th {
  font-weight: 600;
  color: inherit;
}
.tickets-row {
  border-color: #f1f5f9;
  background: transparent;
}
.tickets-row:hover {
  background: rgba(99, 102, 241, 0.06);
}
html.nexus-dark .tickets-row,
.dark .tickets-row {
  border-color: rgba(255, 255, 255, 0.06);
}
html.nexus-dark .tickets-row:hover,
.dark .tickets-row:hover {
  background: rgba(139, 92, 246, 0.12);
}
.tickets-row-new-portal {
  background: rgba(139, 92, 246, 0.08);
  box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.25);
}
html.nexus-dark .tickets-row-new-portal,
.dark .tickets-row-new-portal {
  background: rgba(139, 92, 246, 0.16);
  box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.35);
}
.tickets-row-new {
  background: rgba(99, 102, 241, 0.05);
}
html.nexus-dark .tickets-row-new,
.dark .tickets-row-new {
  background: rgba(99, 102, 241, 0.1);
}
.tickets-subject {
  color: #1e293b;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}
html.nexus-dark .tickets-subject,
.dark .tickets-subject {
  color: #f8fafc;
}
.tickets-desc {
  color: #64748b;
  text-transform: none;
  letter-spacing: normal;
  font-weight: 400;
}
html.nexus-dark .tickets-desc,
.dark .tickets-desc {
  color: #94a3b8;
}
.tickets-cell {
  color: #334155;
}
html.nexus-dark .tickets-cell,
.dark .tickets-cell {
  color: #e2e8f0;
}
.tickets-muted {
  color: #64748b;
}
html.nexus-dark .tickets-muted,
.dark .tickets-muted {
  color: #94a3b8;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "details-tickets-theme-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
