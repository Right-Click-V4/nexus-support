#!/usr/bin/env python3
"""Show custom status text+emoji in Sidebar and Customer Active Now."""
from pathlib import Path
import re

dp = Path('src/lib/deskPresence.ts')
if dp.exists():
    t = dp.read_text()
    if 'status_message' not in t:
        t = t.replace(
            'export type DeskAgent = {\n  id: string;\n  name: string;\n  status: string;',
            'export type DeskAgent = {\n  id: string;\n  name: string;\n  status: string;\n  status_message?: string | null;\n  status_emoji?: string | null;',
        )
        t = t.replace(
            'export async function publishDeskPresence(agent: {\n  id: string;\n  name?: string;\n  status?: string;',
            'export async function publishDeskPresence(agent: {\n  id: string;\n  name?: string;\n  status?: string;\n  status_message?: string | null;\n  status_emoji?: string | null;',
        )
        t = t.replace(
            "status: (agent.status || 'online').toLowerCase() === 'offline' ? 'offline' : (agent.status || 'online'),",
            "status: (agent.status || 'online').toLowerCase() === 'offline' ? 'offline' : (agent.status || 'online'),\n"
            '    status_message: agent.status_message ?? null,\n'
            '    status_emoji: agent.status_emoji ?? null,',
        )
        t = t.replace(
            'status: st,',
            'status: st,\n          status_message: (m as DeskAgent).status_message ?? null,\n          status_emoji: (m as DeskAgent).status_emoji ?? null,',
            1,
        )
        dp.write_text(t)
        print('deskPresence ok')
    else:
        print('deskPresence already')
else:
    print('deskPresence skip')

oa = Path('src/lib/onlineAgents.ts')
if oa.exists():
    t = oa.read_text()
    if 'status_message' not in t:
        t = t.replace(
            'export type OnlineAgentRow = {\n  id: string;\n  name: string;\n  status: string;\n  avatar_url?: string | null;\n  initials?: string;\n  color?: string;\n  last_seen_at?: string | null;\n};',
            'export type OnlineAgentRow = {\n  id: string;\n  name: string;\n  status: string;\n  status_message?: string | null;\n  status_emoji?: string | null;\n  avatar_url?: string | null;\n  initials?: string;\n  color?: string;\n  last_seen_at?: string | null;\n};',
        )
        t = t.replace(
            'status?: string;\n    approval_status?: string | null;',
            'status?: string;\n    status_message?: string | null;\n    status_emoji?: string | null;\n    approval_status?: string | null;',
        )
        t = t.replace(
            '      status,\n      avatar_url: d.avatar_url ?? null,',
            '      status,\n      status_message: d.status_message ?? null,\n      status_emoji: d.status_emoji ?? null,\n      avatar_url: d.avatar_url ?? null,',
        )
        t = t.replace(
            'if (byId.has(String(a.id))) continue;',
            'if (byId.has(String(a.id))) {\n'
            '      const prev = byId.get(String(a.id))!;\n'
            '      if (!prev.status_message && a.status_message) prev.status_message = a.status_message;\n'
            '      if (!prev.status_emoji && a.status_emoji) prev.status_emoji = a.status_emoji;\n'
            '      if (a.status) prev.status = (a.status || prev.status).toLowerCase();\n'
            '      continue;\n'
            '    }',
        )
        t = t.replace(
            '      status,\n      avatar_url: a.avatar_url,',
            '      status,\n      status_message: a.status_message ?? null,\n      status_emoji: a.status_emoji ?? null,\n      avatar_url: a.avatar_url,',
        )
        oa.write_text(t)
        print('onlineAgents ok')
    else:
        print('onlineAgents already')
else:
    print('onlineAgents skip')

sb = Path('src/components/Sidebar.tsx')
if sb.exists() and sb.stat().st_size > 2000:
    t = sb.read_text()
    if 'agentStatusMessage' not in t:
        t = t.replace(
            "function statusLabel(status?: string) {\n  switch ((status || 'online').toLowerCase()) {",
            "function statusLabel(status?: string, message?: string | null, emoji?: string | null) {\n"
            "  const st = (status || 'online').toLowerCase();\n"
            "  if (st === 'custom') {\n"
            "    const custom = [emoji, message].filter(Boolean).join(' ').trim();\n"
            "    return custom || 'Custom';\n"
            "  }\n"
            "  switch (st) {",
        )
        t = t.replace(
            '  agentStatus?: string;\n  onSignOut?: () => void;',
            '  agentStatus?: string;\n  agentStatusMessage?: string | null;\n  agentStatusEmoji?: string | null;\n  onSignOut?: () => void;',
        )
        t = t.replace(
            "  agentStatus = 'online',\n  onSignOut,",
            "  agentStatus = 'online',\n  agentStatusMessage = null,\n  agentStatusEmoji = null,\n  onSignOut,",
        )
        t = t.replace(
            '{statusLabel(agentStatus)}',
            '{statusLabel(agentStatus, agentStatusMessage, agentStatusEmoji)}',
        )
        sb.write_text(t)
        print('Sidebar ok', t.count('{') - t.count('}'))
    else:
        print('Sidebar already')
else:
    print('Sidebar skip')

core = Path('src/SystemAppCore.tsx')
if core.exists() and core.stat().st_size > 2000:
    t = core.read_text()
    if 'agentStatusMessage' not in t:
        t = t.replace(
            "agentStatus={currentAgent?.status || 'online'}",
            "agentStatus={currentAgent?.status || 'online'}\n"
            '        agentStatusMessage={currentAgent?.status_message ?? null}\n'
            '        agentStatusEmoji={currentAgent?.status_emoji ?? null}',
            1,
        )
    needle = "status: presenceAgent.status || 'online',\n      avatar_url: presenceAgent.avatar_url,"
    repl = (
        "status: presenceAgent.status || 'online',\n"
        '      status_message: presenceAgent.status_message ?? null,\n'
        '      status_emoji: presenceAgent.status_emoji ?? null,\n'
        '      avatar_url: presenceAgent.avatar_url,'
    )
    if needle in t:
        t = t.replace(needle, repl)
    core.write_text(t)
    print('SystemAppCore', t.count('status_message: presenceAgent'), 'agentStatusMessage' in t)
else:
    print('SystemAppCore skip')

plv = Path('src/components/PortalLiveChatView.tsx')
if plv.exists() and plv.stat().st_size > 3000:
    s = plv.read_text()
    if 'ACTIVE_STATUS_COLORS_V1' not in s:
        pattern = re.compile(
            r'\{onlineAgents\.slice\(0,\s*6\)\.map\(\(a\)\s*=>\s*\([\s\S]*?</li>\s*\)\)\}',
            re.M,
        )
        replacement = '''{onlineAgents.slice(0, 6).map((a) => {
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
                      <div className={`text-[11px] ${textCls} truncate`}>{label}</div>
                    </div>
                  </li>
                  );
                })}'''
        s2, n = pattern.subn(replacement, s, count=1)
        if n:
            plv.write_text(s2)
            print('PLV replaced', n)
        else:
            print('PLV regex miss')
    else:
        print('PLV already')
    tt = plv.read_text()
    print('PLV braces', tt.count('{') - tt.count('}'), 'msg', 'status_message' in tt)
else:
    print('PLV skip')

# Ensure interval presence publish also carries custom text + refresh deps
core = Path('src/SystemAppCore.tsx')
if core.exists():
    t = core.read_text()
    t2 = t.replace(
        "status: presenceAgent.status || 'online',\n        avatar_url: presenceAgent.avatar_url,",
        "status: presenceAgent.status || 'online',\n"
        '        status_message: presenceAgent.status_message ?? null,\n'
        '        status_emoji: presenceAgent.status_emoji ?? null,\n'
        '        avatar_url: presenceAgent.avatar_url,',
    )
    t2 = t2.replace(
        "}, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps",
        "}, [presenceAgent?.id, presenceAgent?.status, presenceAgent?.status_message, presenceAgent?.status_emoji]); // eslint-disable-line react-hooks/exhaustive-deps",
    )
    if t2 != t:
        core.write_text(t2)
        print('presence interval + deps', t2.count('status_message: presenceAgent'))

print('patch_custom_status_label_v1 done')
