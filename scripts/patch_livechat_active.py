#!/usr/bin/env python3
"""Replace Branch list with Active agents; disable Start chat when none online."""
from pathlib import Path

plc = Path("src/components/PortalLiveChat.tsx")
p = plc.read_text()
if "livechat-active-agents-v1" in p:
    print("already")
    raise SystemExit(0)

if "import AgentAvatar" not in p:
    p = p.replace(
        "import { Send, Paperclip, MessageCircle, Sparkles, Clock, Building2, Ticket } from 'lucide-react';",
        "import { Send, Paperclip, MessageCircle, Sparkles, Clock, Building2, Ticket, Circle } from 'lucide-react';\n"
        "import AgentAvatar from './AgentAvatar';",
        1,
    )
    print("imports")

if "findTicket, agents" not in p:
    p = p.replace("const { findTicket } = useTickets();", "const { findTicket, agents } = useTickets();", 1)
    print("agents")

if "const onlineAgents = useMemo" not in p:
    needle = "}, [branch]);"
    memo = """}, [branch]);

  const onlineAgents = useMemo(() => {
    return (agents || []).filter((a) => {
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved') return false;
      const status = (a.status || 'offline').toLowerCase();
      return status === 'online' || status === 'busy';
    });
  }, [agents]);

  const hasAgentOnline = onlineAgents.length > 0;"""
    if needle in p:
        p = p.replace(needle, memo, 1)
        print("memo")
    else:
        print("memo miss")

if "No agents are online right now. Please try again later." not in p:
    if "Ticket number is required." in p:
        p = p.replace(
            """    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    setStarting(true);""",
            """    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    if (!hasAgentOnline) {
      setError('No agents are online right now. Please try again later.');
      return;
    }
    setStarting(true);""",
            1,
        )
        print("guard")
    else:
        p = p.replace(
            """    if (!nm) {
      setError('Account name is required \u2014 sign in again if this is empty.');
      return;
    }
    setStarting(true);""",
            """    if (!nm) {
      setError('Account name is required \u2014 sign in again if this is empty.');
      return;
    }
    if (!hasAgentOnline) {
      setError('No agents are online right now. Please try again later.');
      return;
    }
    setStarting(true);""",
            1,
        )
        print("guard2")

old_btn = """                <button
                  type="submit"
                  disabled={starting}
                  className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25 disabled:opacity-50 transition-all"
                >
                  {starting ? 'Connecting\u2026' : 'Start chat'}
                </button>"""
new_btn = """                <button
                  type="submit"
                  disabled={starting || !hasAgentOnline}
                  title={!hasAgentOnline ? 'No agents are online right now' : undefined}
                  className="w-full py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {starting ? 'Connecting\u2026' : !hasAgentOnline ? 'No agents online' : 'Start chat'}
                </button>
                {!hasAgentOnline && (
                  <p className="text-[11px] text-center text-amber-600 dark:text-amber-400 mt-2">
                    Chat is unavailable until an agent or admin is online.
                  </p>
                )}"""
# Use actual ellipsis chars as in source
old_btn = old_btn.replace("\\u2026", "\u2026")
new_btn = new_btn.replace("\\u2026", "\u2026")
if old_btn in p:
    p = p.replace(old_btn, new_btn, 1)
    print("btn")
else:
    # try with literal ellipsis already
    old_btn2 = old_btn
    if old_btn2 not in p:
        print("btn miss")

old_pill = """                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-white/20 bg-white/30 dark:bg-white/5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Agents online
                </span>"""
new_pill = """                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-white/20 bg-white/30 dark:bg-white/5">
                  <span className={`w-1.5 h-1.5 rounded-full ${hasAgentOnline ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-400'}`} />
                  {hasAgentOnline ? `${onlineAgents.length} agent${onlineAgents.length === 1 ? '' : 's'} online` : 'No agents online'}
                </span>"""
if old_pill in p:
    p = p.replace(old_pill, new_pill, 1)
    print("pill")

old_branch = """            <div className="portal-overview-glass rounded-2xl p-4 sm:p-5">
              <div className="flex items-center gap-2 mb-2">
                <Building2 size={16} className="text-violet-600 dark:text-violet-300" />
                <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Branch list</h2>
              </div>
              <p className="text-[12px] text-zinc-600 dark:text-zinc-400 mb-2">
                Same branches as Submit a Ticket \u2014 pick the site this chat is about.
              </p>
              <div className="flex flex-wrap gap-1.5">
                {BRANCH_OPTIONS.slice(0, 8).map((b) => (
                  <span
                    key={b}
                    className="text-[10px] px-2 py-0.5 rounded-md bg-violet-500/10 text-violet-800 dark:text-violet-200 border border-violet-400/20"
                  >
                    {b}
                  </span>
                ))}
                <span className="text-[10px] px-2 py-0.5 text-zinc-500">+ more in the list</span>
              </div>
            </div>""".replace("\\u2014", "\u2014")

new_active = """            <div className="portal-overview-glass rounded-2xl p-4 sm:p-5">
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/15 text-emerald-600 dark:text-emerald-300 flex items-center justify-center">
                    <Circle size={14} className={hasAgentOnline ? 'fill-emerald-500 text-emerald-500' : 'text-zinc-400'} />
                  </div>
                  <div>
                    <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Active now</h2>
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
                      {hasAgentOnline
                        ? `${onlineAgents.length} agent${onlineAgents.length === 1 ? '' : 's'} available`
                        : 'No agents online'}
                    </p>
                  </div>
                </div>
                <span
                  className={`text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full border ${
                    hasAgentOnline
                      ? 'border-emerald-400/40 bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                      : 'border-zinc-400/30 bg-zinc-500/10 text-zinc-500'
                  }`}
                >
                  {hasAgentOnline ? 'Live' : 'Offline'}
                </span>
              </div>
              {hasAgentOnline ? (
                <ul className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                  {onlineAgents.map((a) => (
                    <li
                      key={a.id}
                      className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 dark:bg-black/20 px-2.5 py-2"
                    >
                      <div className="relative shrink-0">
                        <AgentAvatar agent={a} size="sm" />
                        <span
                          className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-zinc-900 ${
                            (a.status || '').toLowerCase() === 'busy' ? 'bg-amber-400' : 'bg-emerald-400'
                          }`}
                          title={(a.status || 'online').toString()}
                        />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium text-zinc-900 dark:text-zinc-50 truncate">
                          {a.name}
                          {a.is_admin ? (
                            <span className="ml-1.5 text-[10px] font-semibold text-violet-500 dark:text-violet-300">Admin</span>
                          ) : null}
                        </div>
                        <div className="text-[11px] text-zinc-500 dark:text-zinc-400 capitalize">
                          {(a.status || 'online').toLowerCase() === 'busy' ? 'Busy' : 'Online'}
                          {a.role ? ` \u00b7 ${a.role}` : ''}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="rounded-xl border border-dashed border-white/15 bg-black/10 px-3 py-6 text-center">
                  <p className="text-sm text-zinc-600 dark:text-zinc-300">No agents or admins are online.</p>
                  <p className="text-[11px] text-zinc-500 mt-1">Please check back during business hours.</p>
                </div>
              )}
            </div>""".replace("\\u00b7", "\u00b7")

if old_branch in p:
    p = p.replace(old_branch, new_active, 1)
    print("branch")
else:
    print("branch miss")

p = "/* livechat-active-agents-v1 */\n" + p
plc.write_text(p)
print("done")
