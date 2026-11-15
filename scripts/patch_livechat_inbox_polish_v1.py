#!/usr/bin/env python3
"""Inbox polish: shine, max 10, back button, fix online agents."""
from pathlib import Path
import re

plc = Path("src/components/PortalLiveChat.tsx")
if not plc.exists() or plc.stat().st_size < 5000:
    print("PortalLiveChat skip")
    raise SystemExit(0)

s = plc.read_text()
if "LIVECHAT_INBOX_POLISH_V1" in s and "computeOnlineAgents" in s and "slice(0, 10)" in s and "Back to inbox" in s:
    print("already")
    raise SystemExit(0)

if "from '../lib/onlineAgents'" not in s and 'from "../lib/onlineAgents"' not in s:
    if "from '../lib/deskPresence'" in s:
        s = s.replace(
            "from '../lib/deskPresence';",
            "from '../lib/deskPresence';\nimport { computeOnlineAgents } from '../lib/onlineAgents';",
            1,
        )
    else:
        s = "import { computeOnlineAgents } from '../lib/onlineAgents';\n" + s
    print("import onlineAgents")

old = re.search(
    r"const onlineAgents = useMemo\(\(\) => \{[\s\S]*?\}, \[agents, presenceTick, deskAgents\]\);",
    s,
)
if old:
    s = (
        s[: old.start()]
        + "const onlineAgents = useMemo(() => {\n"
        "    // LIVECHAT_INBOX_POLISH_V1 — only fresh heartbeats\n"
        "    return computeOnlineAgents(agents, deskAgents);\n"
        "  }, [agents, presenceTick, deskAgents]);"
        + s[old.end() :]
    )
    print("onlineAgents fixed")
else:
    print("onlineAgents pattern miss")

old_sort = (
    "    return [...list].sort((a, b) => {\n"
    "      const ra = rank(a.status);\n"
    "      const rb = rank(b.status);\n"
    "      if (ra !== rb) return ra - rb;\n"
    "      return new Date(b.updated_at || b.created_at || 0).getTime() - new Date(a.updated_at || a.created_at || 0).getTime();\n"
    "    });\n"
    "  }, [conversations, myEmail, accountName, name]);"
)
new_sort = (
    "    const sorted = [...list].sort((a, b) => {\n"
    "      const ra = rank(a.status);\n"
    "      const rb = rank(b.status);\n"
    "      if (ra !== rb) return ra - rb;\n"
    "      return new Date(b.updated_at || b.created_at || 0).getTime() - new Date(a.updated_at || a.created_at || 0).getTime();\n"
    "    });\n"
    "    const ongoing = sorted.filter((c) => rank(c.status) === 0);\n"
    "    const ended = sorted.filter((c) => rank(c.status) !== 0);\n"
    "    const room = Math.max(0, 10 - ongoing.length);\n"
    "    return [...ongoing, ...ended.slice(0, room)].slice(0, 10);\n"
    "  }, [conversations, myEmail, accountName, name]);"
)
if old_sort in s:
    s = s.replace(old_sort, new_sort, 1)
    print("max 10")
elif "slice(0, 10)" in s:
    print("max 10 already")
else:
    print("max 10 miss")

old_cls = 'className="shrink-0 px-4 py-2.5 text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25"'
new_cls = (
    'className="relative overflow-hidden shrink-0 px-4 py-2.5 text-sm font-semibold rounded-xl text-white '
    "bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 "
    "shadow-lg shadow-violet-500/25 "
    "before:content-[''] before:absolute before:inset-0 before:bg-gradient-to-r "
    "before:from-transparent before:via-white/35 before:to-transparent "
    'before:translate-x-[-120%] before:animate-[shine-sweep_2.4s_ease-in-out_infinite]"'
)
if old_cls in s:
    s = s.replace(old_cls, new_cls, 1)
    print("shine")
else:
    print("shine miss")

if "@keyframes shine-sweep" not in s:
    needle = '        <div className="w-full max-w-5xl mx-auto space-y-4">\n          <div className="portal-overview-glass'
    if needle in s:
        s = s.replace(
            needle,
            '        <div className="w-full max-w-5xl mx-auto space-y-4">\n'
            "          <style>{`@keyframes shine-sweep { 0% { transform: translateX(-120%); } 100% { transform: translateX(120%); } }`}</style>\n"
            '          <div className="portal-overview-glass',
            1,
        )
        print("keyframes")
    else:
        print("keyframes miss")

pat = re.compile(
    r'<div className="flex items-start gap-3 mb-5">\s*'
    r'<div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/25 shrink-0">\s*'
    r'<MessageCircle className="text-white" size=\{24\} />\s*'
    r'</div>\s*'
    r'<div>\s*'
    r'<h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>\s*'
    r'(?:<button[^>]*>[\s\S]*?Back to inbox\s*</button>\s*)?'
    r'<p className="text-sm text-zinc-600 dark:text-zinc-400 mt-0\.5">\s*'
    r'Connect with a support agent in real time\.\s*'
    r'</p>\s*'
    r'</div>\s*'
    r'</div>',
    re.M,
)
repl = (
    '<div className="flex flex-wrap items-start justify-between gap-3 mb-5">\n'
    '                <div className="flex items-start gap-3 min-w-0">\n'
    '                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/25 shrink-0">\n'
    '                    <MessageCircle className="text-white" size={24} />\n'
    "                  </div>\n"
    '                  <div className="min-w-0">\n'
    '                    <h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>\n'
    '                    <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-0.5">\n'
    "                      Connect with a support agent in real time.\n"
    "                    </p>\n"
    "                  </div>\n"
    "                </div>\n"
    "                <button\n"
    '                  type="button"\n'
    "                  onClick={() => setShowStartForm(false)}\n"
    '                  className="shrink-0 inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border border-zinc-300 dark:border-white/20 bg-white/80 dark:bg-white/10 text-zinc-800 dark:text-zinc-100 hover:bg-white dark:hover:bg-white/15"\n'
    "                >\n"
    "                  Back to inbox\n"
    "                </button>\n"
    "              </div>"
)
s2, n = pat.subn(repl, s, count=1)
if n:
    s = s2
    print("back button right")
else:
    print("back header re miss")

if "LIVECHAT_INBOX_POLISH_V1" not in s:
    s = s.replace("// LIVECHAT_INBOX_V1", "// LIVECHAT_INBOX_V1\n  // LIVECHAT_INBOX_POLISH_V1", 1)

bal = s.count("{") - s.count("}")
plc.write_text(s)
print("braces", bal)
if bal != 0:
    raise SystemExit("brace imbalance " + str(bal))
print("patch_livechat_inbox_polish_v1 done")
