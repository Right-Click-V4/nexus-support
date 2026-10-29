#!/usr/bin/env python3
"""Raise notif dropdown above marquee; glass expand card by status for readability."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "notif-z-expand-glass-v1" in c:
    print("already")
    raise SystemExit(0)

c = c.replace(
    'header className="relative z-20 min-h-[3.75rem] shrink-0 nexus-topbar',
    'header className="relative z-[60] min-h-[3.75rem] shrink-0 nexus-topbar',
    1,
)
print("header z ok")

c = c.replace(
    '<div className="relative z-[50]" ref={portalNotifRef}>',
    '<div className="relative z-[80]" ref={portalNotifRef}>',
    1,
)
c = c.replace(
    'absolute right-0 mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950 shadow-2xl overflow-hidden"',
    'absolute right-0 mt-2 z-[90] w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950 shadow-2xl overflow-hidden"',
    1,
)
print("notif z ok")

old_full = """                                  <div className="rounded-xl border border-zinc-200/70 dark:border-white/10 bg-white/50 dark:bg-zinc-950/80 p-4 sm:p-5 space-y-4 text-left shadow-sm">"""
new_full = """                                  <div className={`rounded-xl border p-4 sm:p-5 space-y-4 text-left shadow-sm backdrop-blur-md ${
                                    t.status === 'resolved' || t.status === 'closed'
                                      ? 'border-emerald-400/35 bg-white/75 dark:bg-emerald-950/50 dark:border-emerald-400/30'
                                      : t.status === 'pending'
                                        ? 'border-orange-400/35 bg-white/75 dark:bg-orange-950/40 dark:border-orange-400/30'
                                        : t.status === 'on-hold'
                                          ? 'border-yellow-400/35 bg-white/75 dark:bg-yellow-950/35 dark:border-yellow-400/30'
                                          : 'border-violet-400/35 bg-white/75 dark:bg-violet-950/50 dark:border-violet-400/30'
                                  }`}>"""
if old_full in c:
    c = c.replace(old_full, new_full, 1)
    print("glass card ok")
else:
    # try after darker card patch variant
    old2 = 'className="rounded-xl border border-zinc-200/70 dark:border-white/10 bg-white/50 dark:bg-zinc-950/80 p-4 sm:p-5 space-y-4 text-left shadow-sm"'
    if old2 in c:
        c = c.replace(old2, new_full.replace('<div className=`', 'className={`').replace('</div>', '').rstrip('>') + '"', 1)
        print("glass alt")
    else:
        print("glass card miss")

old_msg = """                                          <div key={m.id} className="rounded-xl px-3.5 py-3 text-sm bg-white/80 dark:bg-zinc-900/90 border border-zinc-200/70 dark:border-white/12 shadow-sm">
                                            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-1.5">
                                              <div className="text-sm font-bold text-zinc-900 dark:text-zinc-50">{m.author}</div>
                                              <div className="text-[10px] text-zinc-500 tabular-nums">{new Date(m.created_at).toLocaleString()}</div>
                                            </div>
                                            <div className="text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap leading-relaxed">{m.text}</div>
                                          </div>"""
new_msg = """                                          <div key={m.id} className="rounded-xl px-3.5 py-3 text-sm bg-white dark:bg-zinc-900/95 border border-zinc-200 dark:border-white/20 shadow-sm">
                                            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-1.5">
                                              <div className="text-sm font-bold text-zinc-900 dark:text-white">{m.author}</div>
                                              <div className="text-[10px] text-zinc-500 dark:text-zinc-400 tabular-nums">{new Date(m.created_at).toLocaleString()}</div>
                                            </div>
                                            <div className="text-sm text-zinc-800 dark:text-zinc-100 whitespace-pre-wrap leading-relaxed">{m.text}</div>
                                          </div>"""
if old_msg in c:
    c = c.replace(old_msg, new_msg, 1)
    print("msg contrast ok")
else:
    print("msg miss")

c = c.replace(
    'text-sm text-zinc-800 dark:text-zinc-100 whitespace-pre-wrap leading-relaxed">{t.description}',
    'text-sm font-medium text-zinc-900 dark:text-zinc-50 whitespace-pre-wrap leading-relaxed">{t.description}',
    1,
)
c = c.replace(
    'tracking-wide text-zinc-500">Agent Response</div>',
    'tracking-wide text-zinc-500 dark:text-zinc-300">Agent Response</div>',
    1,
)

c = "/* notif-z-expand-glass-v1 */\n" + c
cp.write_text(c)
print("cp done")

css = Path("src/portal-lounge.css")
if css.exists():
    s = css.read_text()
    if "notif-z-expand-glass-v1" not in s:
        if ".portal-marquee {" in s and "z-index: 25" not in s:
            s = s.replace(
                ".portal-marquee {\n  display: flex;",
                ".portal-marquee {\n  position: relative;\n  z-index: 25;\n  display: flex;",
                1,
            )
            print("marquee z ok")
        s = "/* notif-z-expand-glass-v1 */\n" + s
        css.write_text(s)
        print("css done")
    else:
        print("css already")
print("done")
