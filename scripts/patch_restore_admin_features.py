#!/usr/bin/env python3
"""Restore Admin Features tab for all Agent Workspace users."""
from pathlib import Path
import re

sb = Path("src/components/Sidebar.tsx")
if sb.exists():
    t = sb.read_text()
    if "admin-features-always-v1" not in t:
        old = """        {isAdmin && (
          <div>
            <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Admin</div>
            <div className="space-y-0.5">
              {renderNav([{ id: 'admin-features', label: 'Admin Features', icon: Shield }])}
            </div>
          </div>
        )}"""
        new = """        <div>
            <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Admin</div>
            <div className="space-y-0.5">
              {renderNav([{ id: 'admin-features', label: 'Admin Features', icon: Shield }])}
            </div>
          </div>"""
        if old in t:
            t = t.replace(old, new, 1)
        else:
            t = re.sub(
                r"\{isAdmin && \(\s*<div>\s*<div className=\"px-3 mb-2 text-\[10px\] font-semibold uppercase tracking-wider text-zinc-600\">Admin</div>[\s\S]*?admin-features[\s\S]*?</div>\s*\)\}",
                new.strip(),
                t,
                count=1,
            )
        t = "/* admin-features-always-v1 */\n" + t
        sb.write_text(t)
        print("sidebar")

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "admin-features-page-always-v1" not in s:
        s = s.replace(
            "{activeNav === 'admin-features' && admin && <AdminFeaturesPage />}",
            "{activeNav === 'admin-features' && <AdminFeaturesPage />}",
            1,
        )
        s = re.sub(
            r"\{activeNav === 'admin-features' && !admin && \([\s\S]*?\)\}",
            "",
            s,
            count=1,
        )
        s = "/* admin-features-page-always-v1 */\n" + s
        sa.write_text(s)
        print("systemapp")
print("done")
