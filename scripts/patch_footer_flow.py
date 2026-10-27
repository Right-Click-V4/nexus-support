#!/usr/bin/env python3
"""Footer after content in normal document flow; Community not shrunk to fit footer."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "footer-flow-v2" in c:
    print("already")
    raise SystemExit(0)

c = c.replace(
    "export default function CustomerPortal",
    "/* footer-flow-v2 */\nexport default function CustomerPortal",
    1,
)

old_main = """        <main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 flex flex-col ${
            view === 'community' ? 'overflow-hidden' : 'overflow-y-auto'
          }`}
        >
          <div
            className={`w-full mx-auto flex flex-col flex-1 min-h-0 gap-5 ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={`flex-1 min-h-0 ${view === 'community' ? 'flex flex-col' : 'pb-2'}`}>"""

new_main = """        <main className="relative z-10 flex-1 min-h-0 p-3 lg:p-5 overflow-y-auto">
          {/* Content grows naturally; footer sits below it — page scrolls when needed */}
          <div
            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl'
            }`}
          >
            <div className={view === 'community' ? 'min-h-[calc(100vh-12.5rem)] flex flex-col' : 'pb-1'}>"""

if old_main in c:
    c = c.replace(old_main, new_main, 1)
    print("main structure ok")
else:
    t2, n = re.subn(
        r'<main\s+className=\{`relative z-10 flex-1 min-h-0 p-3 lg:p-5 flex flex-col \$\{[\s\S]*?\}`\}\s*>',
        '<main className="relative z-10 flex-1 min-h-0 p-3 lg:p-5 overflow-y-auto">',
        c,
        count=1,
    )
    if n:
        c = t2
        print("main tag ok")
    elif "view === 'community' ? 'overflow-hidden'" in c:
        c = c.replace(
            """        <main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 flex flex-col ${
            view === 'community' ? 'overflow-hidden' : 'overflow-y-auto'
          }`}
        >""",
            """        <main className="relative z-10 flex-1 min-h-0 p-3 lg:p-5 overflow-y-auto">""",
            1,
        )
        print("main community special removed")
    else:
        print("main miss")

    t2, n = re.subn(
        r'className=\{`w-full mx-auto flex flex-col flex-1 min-h-0(?: gap-5)? \$\{[\s\S]*?\}`\}',
        """className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl'
            }`}""",
        c,
        count=1,
    )
    if n:
        c = t2
        print("wrapper ok")
    else:
        print("wrapper miss")

    t2, n = re.subn(
        r"<div className=\{`flex-1 min-h-0 \$\{view === 'community' \? 'flex flex-col' : 'pb-2'\}`\}>",
        """<div className={view === 'community' ? 'min-h-[calc(100vh-12.5rem)] flex flex-col' : 'pb-1'}>""",
        c,
        count=1,
    )
    if n:
        c = t2
        print("content div ok")
    else:
        print("content div miss")

c2, n = re.subn(
    r'className="portal-footer relative z-10 mt-\d+ shrink-0 mb-\d+ px-2 py-\d+(?:\.\d+)? rounded-xl"',
    'className="portal-footer relative z-10 mt-8 mb-4 shrink-0 px-2 py-4 rounded-xl"',
    c,
    count=1,
)
if n:
    c = c2
    print("footer classes ok")
else:
    c = c.replace(
        'portal-footer relative z-10 mt-6 shrink-0 mb-3 px-2 py-4 rounded-xl',
        'portal-footer relative z-10 mt-8 mb-4 shrink-0 px-2 py-4 rounded-xl',
        1,
    )
    c = c.replace(
        'portal-footer relative z-10 mt-auto shrink-0 mb-1 px-2 py-3.5 rounded-xl',
        'portal-footer relative z-10 mt-8 mb-4 shrink-0 px-2 py-4 rounded-xl',
        1,
    )
    print("footer classes alt")

cp.write_text(c)

for css_path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not css_path.exists():
        continue
    css = css_path.read_text()
    if "portal-footer-flow-v2" in css:
        continue
    if ".portal-footer {" in css:
        css += """

/* portal-footer-flow-v2 — always after content, never overlay */
.portal-footer {
  position: relative !important;
  top: auto !important;
  bottom: auto !important;
  left: auto !important;
  right: auto !important;
  margin-top: 2rem !important;
  margin-bottom: 1rem !important;
  flex-shrink: 0;
  clear: both;
}
"""
        css_path.write_text(css)
        print(f"{css_path.name}: flow override")

print("done")
