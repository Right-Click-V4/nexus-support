#!/usr/bin/env python3
"""Render My Tickets action menu via portal to document.body so fixed coords match getBoundingClientRect."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-menu-portal-v1" in c:
    print("already")
    raise SystemExit(0)

if "createPortal" not in c:
    c = c.replace(
        "import { useState, useMemo, useEffect, useRef } from 'react';",
        "import { useState, useMemo, useEffect, useRef } from 'react';\nimport { createPortal } from 'react-dom';",
        1,
    )
    print("import portal")

if "myTicketMenuPos" in c and "MyTicketMenuState" not in c:
    c = c.replace(
        """const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);
  const [myTicketMenuPos, setMyTicketMenuPos] = useState<{ top: number; left: number; openUp: boolean }>({
    top: 0,
    left: 0,
    openUp: false,
  });""",
        """const [myTicketMenu, setMyTicketMenu] = useState<{
    id: string;
    top: number;
    left: number;
    openUp: boolean;
  } | null>(null);
  const myTicketMenuId = myTicketMenu?.id ?? null;
  const setMyTicketMenuId = (id: string | null | ((prev: string | null) => string | null)) => {
    if (typeof id === 'function') {
      const next = id(myTicketMenuId);
      if (next == null) setMyTicketMenu(null);
      return;
    }
    if (id == null) setMyTicketMenu(null);
  };""",
        1,
    )
    print("state combined")

old2 = """                                    if (myTicketMenuId === t.id) {
                                      setMyTicketMenuId(null);
                                      return;
                                    }
                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 84;
                                    const menuW = 160;
                                    const gap = 4;
                                    const spaceBelow = window.innerHeight - rect.bottom;
                                    const openUp = spaceBelow < menuH + 12;
                                    const top = openUp
                                      ? Math.max(8, rect.top - menuH - gap)
                                      : rect.bottom + gap;
                                    let left = rect.right - menuW;
                                    if (left < 8) left = 8;
                                    if (left + menuW > window.innerWidth - 8) {
                                      left = window.innerWidth - menuW - 8;
                                    }
                                    setMyTicketMenuPos({ top, left, openUp });
                                    setMyTicketMenuId(t.id);"""
new_click = """                                    if (myTicketMenuId === t.id) {
                                      setMyTicketMenu(null);
                                      return;
                                    }
                                    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                                    const menuH = 84;
                                    const menuW = 160;
                                    const gap = 4;
                                    const spaceBelow = window.innerHeight - rect.bottom;
                                    const openUp = spaceBelow < menuH + 12;
                                    const top = openUp
                                      ? Math.max(8, rect.top - menuH - gap)
                                      : rect.bottom + gap;
                                    let left = rect.right - menuW;
                                    if (left < 8) left = 8;
                                    if (left + menuW > window.innerWidth - 8) {
                                      left = window.innerWidth - menuW - 8;
                                    }
                                    setMyTicketMenu({ id: t.id, top, left, openUp });"""
if old2 in c:
    c = c.replace(old2, new_click, 1)
    print("click ok")
else:
    print("click miss")

old_menu = """                                {myTicketMenuId === t.id && (
                                  <div
                                    className="portal-mytickets-action-menu fixed z-[9998] w-40 rounded-xl border border-zinc-200/90 dark:border-white/15 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md shadow-xl py-1 text-left"
                                    style={{
                                      top: myTicketMenuPos.top,
                                      left: myTicketMenuPos.left,
                                      transformOrigin: myTicketMenuPos.openUp ? 'bottom right' : 'top right',
                                    }}
                                  >
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        const open = expandedTicketId !== t.id;
                                        setExpandedTicketId(open ? t.id : null);
                                        if (open && (t.tags || []).includes('customer_unread')) {
                                          void updateTicket(t.id, {
                                            tags: (t.tags || []).filter((x) => x !== 'customer_unread'),
                                          });
                                        }
                                      }}
                                    >
                                      {expandedTicketId === t.id ? 'Collapse' : 'View'}
                                    </button>
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenuId(null);
                                        setFollowUpTicket(t);
                                        setFollowUpText('');
                                      }}
                                    >
                                      Send Follow-Up
                                    </button>
                                  </div>
                                )}"""

new_menu = """                                {myTicketMenuId === t.id && myTicketMenu && createPortal(
                                  <div
                                    data-myticket-menu
                                    className="portal-mytickets-action-menu fixed z-[9998] w-40 rounded-xl border border-zinc-200/90 dark:border-white/15 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md shadow-xl py-1 text-left"
                                    style={{
                                      top: myTicketMenu.top,
                                      left: myTicketMenu.left,
                                    }}
                                  >
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenu(null);
                                        const open = expandedTicketId !== t.id;
                                        setExpandedTicketId(open ? t.id : null);
                                        if (open && (t.tags || []).includes('customer_unread')) {
                                          void updateTicket(t.id, {
                                            tags: (t.tags || []).filter((x) => x !== 'customer_unread'),
                                          });
                                        }
                                      }}
                                    >
                                      {expandedTicketId === t.id ? 'Collapse' : 'View'}
                                    </button>
                                    <button
                                      type="button"
                                      className="w-full px-3 py-2 text-left text-xs font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
                                      onClick={() => {
                                        setMyTicketMenu(null);
                                        setFollowUpTicket(t);
                                        setFollowUpText('');
                                      }}
                                    >
                                      Send Follow-Up
                                    </button>
                                  </div>,
                                  document.body,
                                )}"""

if old_menu in c:
    c = c.replace(old_menu, new_menu, 1)
    print("menu portal ok")
else:
    print("menu portal miss")
    c = c.replace("setMyTicketMenuId(null)", "setMyTicketMenu(null)")
    c = c.replace("myTicketMenuPos.top", "myTicketMenu?.top ?? 0")
    c = c.replace("myTicketMenuPos.left", "myTicketMenu?.left ?? 0")
    c = c.replace("myTicketMenuPos.openUp", "myTicketMenu?.openUp")
    print("menu fallback")

c = c.replace(
    """      if (t && t.closest && t.closest('[data-myticket-menu]')) return;
      setMyTicketMenuId(null);""",
    """      if (t && t.closest && t.closest('[data-myticket-menu]')) return;
      setMyTicketMenu(null);""",
    1,
)

c = "/* mytickets-menu-portal-v1 */\n" + c
cp.write_text(c)
print("done")
