#!/usr/bin/env python3
"""Action menu near dots; close on outside click; 20 tickets per page."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "menu-page20-v1" in c:
    print("already")
    raise SystemExit(0)

c = c.replace("const PAGE_SIZE = 8;", "const PAGE_SIZE = 20;")
c = c.replace("const PAGE_SIZE = 10;", "const PAGE_SIZE = 20;")

if "portal-mytickets-action-menu absolute right-full" in c:
    c = c.replace(
        "portal-mytickets-action-menu absolute right-full top-1/2 -translate-y-1/2 mr-1 z-[100] w-44",
        "portal-mytickets-action-menu absolute right-0 top-full mt-1 z-[100] w-40",
        1,
    )
    print("menu pos ok")
elif "portal-mytickets-action-menu absolute right-0 top-full" in c:
    print("menu pos already")
else:
    print("menu pos miss")

if "useRef" not in c[:500]:
    c = c.replace(
        "import { useState, useMemo, useEffect } from 'react';",
        "import { useState, useMemo, useEffect, useRef } from 'react';",
    )

marker = "  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);"
effect = """  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);
  useEffect(() => {
    if (!myTicketMenuId) return;
    const onDoc = (e: MouseEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && t.closest && t.closest('[data-myticket-menu]')) return;
      setMyTicketMenuId(null);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [myTicketMenuId]);"""
if marker in c and "closest('[data-myticket-menu]')" not in c:
    c = c.replace(marker, effect, 1)
    print("outside click ok")
else:
    print("outside skip")

old_td = '<td className="px-4 py-3 text-right relative">'
new_td = '<td className="px-4 py-3 text-right relative" data-myticket-menu>'
if 'data-myticket-menu>' not in c and old_td in c:
    idx = c.find('aria-label="Ticket actions"')
    if idx > 0:
        before = c.rfind(old_td, 0, idx)
        if before >= 0:
            c = c[:before] + new_td + c[before + len(old_td):]
            print("td attr ok")
        else:
            print("td find miss")
    else:
        print("btn miss")
elif 'data-myticket-menu>' in c:
    print("td attr already")
else:
    print("td miss")

if "menu-page20-v1" not in c:
    c = "/* menu-page20-v1 */\n" + c
cp.write_text(c)
print("done")
