#!/usr/bin/env python3
"""Remove Groups + button; add clearance between chat/content and portal footer."""
from pathlib import Path
import re

# --- PortalCommunityChat: remove header + button ---
pcc = Path("src/components/PortalCommunityChat.tsx")
t = pcc.read_text()
changed = False

old_groups = """        <div className="px-3 py-3 border-b border-zinc-200 flex items-center justify-between gap-2">
          <div className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Groups</div>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="p-1.5 rounded-lg text-violet-600 hover:bg-violet-50"
            title="Create group"
          >
            <Plus size={16} />
          </button>
        </div>"""
new_groups = """        <div className="px-3 py-3 border-b border-zinc-200 dark:border-white/10">
          <div className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Groups</div>
        </div>"""
if old_groups in t:
    t = t.replace(old_groups, new_groups, 1)
    changed = True
    print("pcc: removed Groups +")
else:
    t2, n = re.subn(
        r'<div className="px-3 py-3 border-b border-zinc-200 flex items-center justify-between gap-2">\s*'
        r'<div className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Groups</div>\s*'
        r'<button[\s\S]*?</button>\s*</div>',
        new_groups,
        t,
        count=1,
    )
    if n:
        t = t2
        changed = True
        print("pcc: removed Groups + (loose)")
    else:
        print("pcc: Groups + already gone or miss")

if changed:
    pcc.write_text(t)

# --- CustomerPortal: footer clearance for all tabs ---
cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
c_changed = False

old_wrap = """          <div
            className={`w-full mx-auto flex flex-col flex-1 min-h-0 ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={`flex-1 min-h-0 ${view === 'community' ? 'flex flex-col' : ''}`}>"""

new_wrap = """          <div
            className={`w-full mx-auto flex flex-col flex-1 min-h-0 gap-5 ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={`flex-1 min-h-0 ${view === 'community' ? 'flex flex-col' : 'pb-2'}`}>"""

if old_wrap in c:
    c = c.replace(old_wrap, new_wrap, 1)
    c_changed = True
    print("cp: gap on content wrapper")
else:
    t2, n = re.subn(
        r'className=\{`w-full mx-auto flex flex-col flex-1 min-h-0 \$\{',
        'className={`w-full mx-auto flex flex-col flex-1 min-h-0 gap-5 ${',
        c,
        count=1,
    )
    if n:
        c = t2
        c_changed = True
        print("cp: gap-5 injected")
    else:
        print("cp: wrap miss")

old_ft = 'className="portal-footer relative z-10 mt-auto shrink-0 mb-1 px-2 py-3.5 rounded-xl"'
new_ft = 'className="portal-footer relative z-10 mt-6 shrink-0 mb-3 px-2 py-4 rounded-xl"'
if old_ft in c:
    c = c.replace(old_ft, new_ft, 1)
    c_changed = True
    print("cp: footer spacing")
elif 'portal-footer relative z-10 mt-auto' in c:
    c = c.replace(
        'portal-footer relative z-10 mt-auto shrink-0 mb-1 px-2 py-3.5 rounded-xl',
        'portal-footer relative z-10 mt-6 shrink-0 mb-3 px-2 py-4 rounded-xl',
        1,
    )
    c_changed = True
    print("cp: footer spacing alt")
elif 'portal-footer' in c and 'mt-6' in c:
    print("cp: footer already spaced")
else:
    print("cp: footer miss")

if c_changed:
    cp.write_text(c)

css_paths = [Path("src/index.css"), Path("src/portal-lounge.css")]
for css_path in css_paths:
    if not css_path.exists():
        continue
    css = css_path.read_text()
    if "portal-footer-clearance" in css:
        print(f"{css_path}: clearance already")
        continue
    if ".portal-footer {" in css:
        css = css.replace(
            ".portal-footer {",
            """.portal-footer {
  /* portal-footer-clearance */
  margin-top: 1.5rem;
  position: relative;
  clear: both;
""",
            1,
        )
        css_path.write_text(css)
        print(f"{css_path}: clearance CSS")

print("done")
