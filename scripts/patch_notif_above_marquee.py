#!/usr/bin/env python3
"""Force notification dropdown above marquee; glass transparency."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "notif-above-marquee-v1" not in c:
    old = """            {portalNotifOpen && (
              <div className="absolute right-0 mt-2 z-[90] w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950 shadow-2xl overflow-hidden">"""
    new = """            {portalNotifOpen && (
              <div className="portal-notif-panel absolute right-0 top-full mt-1.5 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-violet-300/40 dark:border-white/20 bg-white/85 dark:bg-zinc-950/75 backdrop-blur-xl shadow-2xl overflow-hidden">"""
    if old not in c:
        old = """            {portalNotifOpen && (
              <div className="absolute right-0 mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-950 shadow-2xl overflow-hidden">"""
    if old in c:
        c = c.replace(old, new, 1)
        print("panel ok")
    else:
        m = re.search(r'\{portalNotifOpen && \(\s*<div className="[^"]*w-80[^"]*"', c)
        if m:
            c = c.replace(
                m.group(0),
                '{portalNotifOpen && (\n              <div className="portal-notif-panel absolute right-0 top-full mt-1.5 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-violet-300/40 dark:border-white/20 bg-white/85 dark:bg-zinc-950/75 backdrop-blur-xl shadow-2xl overflow-hidden"',
                1,
            )
            print("panel re ok")
        else:
            print("panel miss")
    c = "/* notif-above-marquee-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

css = Path("src/portal-lounge.css")
s = css.read_text()
if "notif-above-marquee-v1" not in s:
    s2, n = re.subn(
        r"(\.portal-shell \.nexus-topbar\s*\{[^}]*?z-index:\s*)20(\s*;)",
        r"\g<1>70\g<2>",
        s,
        count=1,
        flags=re.S,
    )
    if n:
        s = s2
        print("topbar z 70")
    else:
        lines = s.split("\n")
        in_block = False
        for i, line in enumerate(lines):
            if ".portal-shell .nexus-topbar" in line:
                in_block = True
            if in_block and "z-index:" in line:
                lines[i] = "  z-index: 70;"
                print("topbar z line")
                in_block = False
        s = "\n".join(lines)
    if "z-index: 25;" in s and ".portal-marquee" in s:
        s = s.replace("  z-index: 25;\n  display: flex;", "  z-index: 40;\n  display: flex;", 1)
        print("marquee z 40")
    block = """
/* notif-above-marquee-v1 */
.portal-shell .nexus-topbar {
  z-index: 70 !important;
}
.portal-marquee {
  z-index: 40 !important;
}
.portal-notif-panel {
  z-index: 80 !important;
  position: absolute;
  background: rgba(255, 255, 255, 0.82) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
html.nexus-dark .portal-notif-panel {
  background: rgba(12, 10, 24, 0.72) !important;
  border-color: rgba(255, 255, 255, 0.18) !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
}
"""
    css.write_text(s + "\n" + block)
    print("css done")
else:
    print("css already")
print("done")
