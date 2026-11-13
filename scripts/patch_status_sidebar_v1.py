#!/usr/bin/env python3
"""Sidebar shows agent name; Active Now status colors + custom text/emoji."""
from pathlib import Path
import re

core = Path("src/SystemAppCore.tsx")
if core.exists() and core.stat().st_size > 2000:
    t = core.read_text()
    span = t[t.find("<Sidebar"): t.find("<Sidebar") + 500] if "<Sidebar" in t else ""
    if "displayName={" not in span:
        needle = "agentStatus={currentAgent?.status || 'online'}"
        if needle in t:
            t = t.replace(
                needle,
                "displayName={currentAgent?.name || (user?.user_metadata?.full_name as string | undefined) || user?.email?.split('@')[0] || 'Agent'}\n"
                "        userName={currentAgent?.name || (user?.user_metadata?.full_name as string | undefined) || user?.email?.split('@')[0] || 'Agent'}\n"
                "        agentStatus={currentAgent?.status || 'online'}",
                1,
            )
            core.write_text(t)
            print("SystemAppCore displayName")
        else:
            print("SystemAppCore needle miss")
    else:
        print("SystemAppCore already")
else:
    print("SystemAppCore skip")

plv = Path("src/components/PortalLiveChatView.tsx")
if plv.exists() and plv.stat().st_size > 3000:
    s = plv.read_text()
    if "ACTIVE_STATUS_COLORS_V1" in s:
        print("PLV already")
    else:
        pattern = re.compile(
            r"\{onlineAgents\.slice\(0,\s*6\)\.map\(\(a\)\s*=>\s*\([\s\S]*?</li>\s*\)\)\}",
            re.M,
        )
        replacement = r"""{onlineAgents.slice(0, 6).map((a) => {
                  // ACTIVE_STATUS_COLORS_V1
                  const st = (a.status || 'online').toLowerCase();
                  const dot =
                    st === 'away' ? 'bg-sky-500'
                    : st === 'busy' ? 'bg-amber-400'
                    : st === 'in_call' ? 'bg-orange-500'
                    : st === 'custom' ? 'bg-violet-400'
                    : st === 'offline' ? 'bg-zinc-400'
                    : 'bg-emerald-500';
                  const textCls =
                    st === 'away' ? 'text-sky-600 dark:text-sky-400'
                    : st === 'busy' ? 'text-amber-600 dark:text-amber-400'
                    : st === 'in_call' ? 'text-orange-600 dark:text-orange-400'
                    : st === 'custom' ? 'text-violet-600 dark:text-violet-400'
                    : st === 'offline' ? 'text-zinc-500'
                    : 'text-emerald-600 dark:text-emerald-400';
                  const label =
                    st === 'custom'
                      ? [a.status_emoji, a.status_message].filter(Boolean).join(' ').trim() || 'Custom'
                      : st === 'in_call'
                        ? 'In a call'
                        : st === 'online'
                          ? 'Available'
                          : (a.status || 'online');
                  const ring =
                    st === 'away' ? 'ring-sky-500/30'
                    : st === 'busy' ? 'ring-amber-400/30'
                    : st === 'in_call' ? 'ring-orange-500/30'
                    : st === 'custom' ? 'ring-violet-400/30'
                    : 'ring-emerald-500/30';
                  return (
                  <li key={a.id} className="flex items-center gap-2.5 min-w-0">
                    <div className="relative shrink-0">
                      <AgentAvatar
                        agent={{
                          id: a.id,
                          name: a.name,
                          initials: a.initials,
                          color: a.color,
                          avatar_url: a.avatar_url,
                        }}
                        size={32}
                        className={`ring-1 ${ring}`}
                      />
                      <span className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ${dot} ring-2 ring-white dark:ring-zinc-900`} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-xs font-medium text-zinc-900 dark:text-zinc-100 truncate">{a.name}</div>
                      <div className={`text-[11px] ${textCls} truncate capitalize`}>{label}</div>
                    </div>
                  </li>
                  );
                })}"""
        s2, n = pattern.subn(replacement, s, count=1)
        if n:
            plv.write_text(s2)
            print("PLV Active Now replaced", n)
        else:
            print("PLV regex miss")
    print("PLV braces", plv.read_text().count("{") - plv.read_text().count("}"))
else:
    print("PLV skip")

print("patch_status_sidebar_v1 done")
