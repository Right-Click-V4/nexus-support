#!/usr/bin/env python3
"""Widen My Tickets panel; sticky Action column always visible."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-wider-v1" in c:
    print("already")
    raise SystemExit(0)

old_wrap = """            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl min-h-full'
            }`}"""
new_wrap = """            className={`w-full mx-auto flex flex-col ${
              view === 'community'
                ? 'max-w-6xl flex-1 min-h-0'
                : view === 'mytickets'
                  ? 'max-w-[1600px] min-h-full'
                  : 'max-w-5xl min-h-full'
            }`}"""
if old_wrap in c:
    c = c.replace(old_wrap, new_wrap, 1)
    print("wrap ok")
else:
    # try if already partially patched with max-w-5xl only
    old2 = "view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl min-h-full'"
    new2 = "view === 'community' ? 'max-w-6xl flex-1 min-h-0' : view === 'mytickets' ? 'max-w-[1600px] min-h-full' : 'max-w-5xl min-h-full'"
    if old2 in c:
        c = c.replace(old2, new2, 1)
        print("wrap alt ok")
    else:
        print("wrap miss")

c = c.replace(
    'className="xl:col-span-8 portal-mytickets-panel min-h-[420px] flex flex-col',
    'className="xl:col-span-9 portal-mytickets-panel min-h-[480px] flex flex-col',
)
c = c.replace(
    'className="xl:col-span-4 portal-mytickets-guide',
    'className="xl:col-span-3 portal-mytickets-guide',
)
c = c.replace("xl:col-span-8 portal-mytickets-panel", "xl:col-span-9 portal-mytickets-panel")
c = c.replace("xl:col-span-4 portal-mytickets-guide", "xl:col-span-3 portal-mytickets-guide")

c = c.replace(
    'className="w-full text-sm min-w-[720px]"',
    'className="w-full text-sm min-w-[900px]"',
)
c = c.replace(
    '<table className="w-full text-sm">',
    '<table className="w-full text-sm min-w-[900px]">',
)

c = c.replace(
    '<th className="px-4 py-2.5 font-semibold text-right">Action</th>',
    '<th className="px-4 py-2.5 font-semibold text-right sticky right-0 z-10 bg-inherit portal-mytickets-action-col">Action</th>',
)
c = c.replace(
    '<td className="px-4 py-3 text-right relative">',
    '<td className="px-4 py-3 text-right relative sticky right-0 z-10 portal-mytickets-action-col">',
)
c = c.replace(
    'className="px-4 sm:px-5 py-3.5 text-right relative"',
    'className="px-4 sm:px-5 py-3.5 text-right relative sticky right-0 z-10 portal-mytickets-action-col"',
)

if "mytickets-wider-v1" not in c:
    c = "/* mytickets-wider-v1 */\n" + c
cp.write_text(c)
print("cp done")

css = """

/* mytickets-wider-v1 — sticky Action column */
.portal-mytickets-action-col {
  background: rgba(30, 20, 55, 0.95);
  box-shadow: -6px 0 12px rgba(0, 0, 0, 0.15);
}
html.nexus-light .portal-mytickets-action-col,
html:not(.nexus-dark):not(.dark) .portal-mytickets-action-col {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: -6px 0 12px rgba(15, 23, 42, 0.06);
}
html.nexus-dark .portal-mytickets-action-col,
.dark .portal-mytickets-action-col {
  background: rgba(24, 20, 42, 0.98);
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "mytickets-wider-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
