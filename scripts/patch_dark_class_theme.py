#!/usr/bin/env python3
"""Wire Tailwind dark: to app theme (nexus-dark) so Live Chat & cards match dark mode."""
from pathlib import Path

ui = Path("src/lib/uiPrefs.ts")
if ui.exists():
    t = ui.read_text()
    if "dark-class-tailwind-v1" not in t:
        old = """  root.classList.toggle('nexus-dark', dark);
  root.classList.toggle('nexus-light', !dark);
  root.style.colorScheme = dark ? 'dark' : 'light';"""
        new = """  root.classList.toggle('nexus-dark', dark);
  root.classList.toggle('nexus-light', !dark);
  root.classList.toggle('dark', dark);
  root.style.colorScheme = dark ? 'dark' : 'light';"""
        if old in t:
            t = t.replace(old, new, 1)
        elif "classList.toggle('dark'" not in t:
            t = t.replace(
                "root.classList.toggle('nexus-light', !dark);",
                "root.classList.toggle('nexus-light', !dark);\n  root.classList.toggle('dark', dark);",
                1,
            )
        t = "/* dark-class-tailwind-v1 */\n" + t
        ui.write_text(t)
        print("uiPrefs")

for name in ("tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs"):
    tw = Path(name)
    if not tw.exists():
        continue
    c = tw.read_text()
    if "darkMode: 'class'" not in c and 'darkMode: "class"' not in c:
        if "export default {" in c:
            c = c.replace("export default {", "export default {\n  darkMode: 'class',", 1)
        elif "module.exports" in c:
            c = c.replace("module.exports = {", "module.exports = {\n  darkMode: 'class',", 1)
        c = c.replace("darkMode: 'media'", "darkMode: 'class'")
        tw.write_text(c)
        print("tailwind", name)

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "livechat-nexus-dark-hard-v1" not in p:
        for old, new in [
            (
                'className="w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/40 dark:border-white/15 bg-white/50 dark:bg-zinc-950/80 backdrop-blur-xl shadow-lg shadow-black/10"',
                'className="livechat-shell w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/50 dark:border-white/10 bg-white/55 dark:bg-zinc-950/85 backdrop-blur-xl shadow-lg shadow-black/20"',
            ),
            (
                'className="w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/50 dark:border-white/10 bg-white/50 dark:bg-zinc-950/80 backdrop-blur-xl shadow-lg shadow-black/10"',
                'className="livechat-shell w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/50 dark:border-white/10 bg-white/55 dark:bg-zinc-950/85 backdrop-blur-xl shadow-lg shadow-black/20"',
            ),
            (
                'className="w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] portal-overview-glass rounded-2xl overflow-hidden border border-white/15"',
                'className="livechat-shell w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/50 dark:border-white/10 bg-white/55 dark:bg-zinc-950/85 backdrop-blur-xl shadow-lg shadow-black/20"',
            ),
        ]:
            if old in p:
                p = p.replace(old, new, 1)
                break
        p = "/* livechat-nexus-dark-hard-v1 */\n" + p
        plc.write_text(p)
        print("plc")

css = Path("src/index.css")
if css.exists():
    c = css.read_text()
    if "livechat-shell" not in c:
        c += """
/* Live Chat panel — force dark glass when app theme is dark (nexus-dark) */
.nexus-dark .livechat-shell {
  background: rgba(9, 9, 11, 0.82) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  color: #f4f4f5;
}
.nexus-dark .livechat-shell > div:first-child,
.nexus-dark .livechat-shell > div:last-child {
  background: rgba(9, 9, 11, 0.72) !important;
  border-color: rgba(255, 255, 255, 0.08) !important;
}
.nexus-light .livechat-shell {
  background: rgba(255, 255, 255, 0.55) !important;
}
"""
        css.write_text(c)
        print("css")
print("done")
