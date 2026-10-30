#!/usr/bin/env python3
"""Dark default theme; Profile status realtime + emoji; Active Now status colors."""
from pathlib import Path

ui = Path("src/lib/uiPrefs.ts")
if ui.exists():
    t = ui.read_text()
    if "dark-default-v2" not in t:
        t = t.replace(
            """export function getDarkMode(): boolean {
  try {
    const v = localStorage.getItem(DARK_KEY);
    if (v === '0') return false;
    if (v === '1') return true;
  } catch {}
  return true;
}""",
            """export function getDarkMode(): boolean {
  try {
    const v = localStorage.getItem(DARK_KEY);
    if (v === '0') return false;
    if (v === '1') return true;
    localStorage.setItem(DARK_KEY, '1');
  } catch {}
  return true;
}""",
        )
        t = "/* dark-default-v2 */\n" + t
        ui.write_text(t)
        print("uiPrefs")
    else:
        print("uiPrefs already")

types = Path("src/types.ts")
if types.exists():
    t = types.read_text()
    if "status_emoji" not in t:
        t = t.replace(
            "  last_seen_at?: string | null;\n  color: string;",
            "  last_seen_at?: string | null;\n  status_emoji?: string | null;\n  color: string;",
            1,
        )
        if "status_emoji" not in t:
            t = t.replace(
                "  status_message?: string | null;\n  color: string;",
                "  status_message?: string | null;\n  status_emoji?: string | null;\n  last_seen_at?: string | null;\n  color: string;",
                1,
            )
        types.write_text(t)
        print("types")
    else:
        print("types ok")

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "status-emoji-ctx-v1" not in c:
    c = c.replace(
        "  updateAgentStatus: (status: AgentStatus, statusMessage?: string | null) => Promise<void>;",
        "  updateAgentStatus: (status: AgentStatus, statusMessage?: string | null, statusEmoji?: string | null) => Promise<void>;",
        1,
    )
    old = """  const updateAgentStatus = async (status: AgentStatus, statusMessage?: string | null) => {
    if (!currentAgent) return;
    const msg = statusMessage === undefined ? currentAgent.status_message ?? null : statusMessage;
    const seen = status === 'offline' ? null : new Date().toISOString();
    const patch: Record<string, unknown> = { status, last_seen_at: seen };
    if (statusMessage !== undefined) patch.status_message = statusMessage;"""
    new = """  const updateAgentStatus = async (
    status: AgentStatus,
    statusMessage?: string | null,
    statusEmoji?: string | null,
  ) => {
    if (!currentAgent) return;
    const msg = statusMessage === undefined ? currentAgent.status_message ?? null : statusMessage;
    const emoji = statusEmoji === undefined ? currentAgent.status_emoji ?? null : statusEmoji;
    const seen = status === 'offline' ? null : new Date().toISOString();
    const patch: Record<string, unknown> = { status, last_seen_at: seen };
    if (statusMessage !== undefined) patch.status_message = statusMessage;
    if (statusEmoji !== undefined) patch.status_emoji = statusEmoji;"""
    if old in c:
        c = c.replace(old, new, 1)
        c = c.replace(
            "const next = { ...currentAgent, status, status_message: msg, last_seen_at: seen };\n      setCurrentAgent(next);\n      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));\n      try {\n        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);",
            "const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };\n      setCurrentAgent(next);\n      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));\n      try {\n        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);",
            1,
        )
        c = c.replace(
            "const next = { ...currentAgent, status, status_message: msg, last_seen_at: seen };\n      setCurrentAgent(next);\n      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));\n    }\n  };",
            "const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };\n      setCurrentAgent(next);\n      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));\n    }\n  };",
            1,
        )
        print("tc uas")
    else:
        print("tc uas miss")
    c = "/* status-emoji-ctx-v1 */\n" + c
    tc.write_text(c)
else:
    print("tc already")

pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    p = pp.read_text()
    if "status-emoji-profile-v1" not in p:
        if "statusEmoji" not in p:
            p = p.replace(
                "const [statusMessage, setStatusMessage] = useState('');",
                "const [statusMessage, setStatusMessage] = useState('');\n  const [statusEmoji, setStatusEmoji] = useState('');\n  const [emojiOpen, setEmojiOpen] = useState(false);",
                1,
            )
            p = p.replace(
                "setStatusMessage(currentAgent.status_message || '');",
                "setStatusMessage(currentAgent.status_message || '');\n      setStatusEmoji(currentAgent.status_emoji || '');",
                1,
            )
        if "updateAgentStatus" not in p[p.find("useTickets"):p.find("useTickets")+120]:
            p = p.replace(
                "const { currentAgent, refresh } = useTickets();",
                "const { currentAgent, updateAgentStatus, refresh } = useTickets();",
                1,
            )
            p = p.replace(
                "const { currentAgent, updateAgentStatus, updateAgentStatus, refresh } = useTickets();",
                "const { currentAgent, updateAgentStatus, refresh } = useTickets();",
                1,
            )
        old_block = """            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-2">Status</label>
              <select
                value={status === 'offline' || status === 'online' ? 'online' : status}
                onChange={(e) => {
                  const v = e.target.value as AgentStatus;
                  setStatus(v === 'online' ? 'online' : v);
                }}
                className="w-full px-4 py-2.5 text-sm border border-zinc-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
              >
                <option value="online">Available (default)</option>
                <option value="away">Away</option>
                <option value="busy">Busy</option>
                <option value="in_call">In a Call / Meeting</option>
                <option value="custom">Custom Status</option>
              </select>
              <p className="text-[11px] text-zinc-500 mt-1">
                Online/Offline is automatic from your session. This sets how you appear while logged in.
              </p>
              {status === 'custom' && (
                <input
                  value={statusMessage}
                  onChange={(e) => setStatusMessage(e.target.value)}
                  placeholder="e.g. Back in 10 minutes"
                  className="mt-2 w-full px-4 py-2.5 text-sm border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                />
              )}
            </div>"""
        new_block = """            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-200 mb-2">Status</label>
              <div className="flex gap-2 items-start">
                <select
                  value={status === 'offline' || status === 'online' ? 'online' : status}
                  onChange={(e) => {
                    const v = e.target.value as AgentStatus;
                    const next = v === 'online' ? 'online' : v;
                    setStatus(next);
                    const msg = next === 'custom' ? statusMessage.trim() || null : null;
                    void updateAgentStatus(next === 'offline' ? 'online' : next, msg, statusEmoji || null);
                  }}
                  className="flex-1 px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                >
                  <option value="online">Available (default)</option>
                  <option value="away">Away</option>
                  <option value="busy">Busy</option>
                  <option value="in_call">In a Call / Meeting</option>
                  <option value="custom">Custom Status</option>
                </select>
                <div className="relative">
                  <button
                    type="button"
                    title="Add emoji"
                    onClick={() => setEmojiOpen((o) => !o)}
                    className="h-[42px] min-w-[42px] px-2 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900/60 text-lg hover:bg-zinc-50 dark:hover:bg-white/5"
                  >
                    {statusEmoji || '😊'}
                  </button>
                  {emojiOpen && (
                    <div className="absolute right-0 z-30 mt-1 p-2 w-56 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl grid grid-cols-6 gap-1">
                      {['😊','🙂','😎','🫡','💼','📞','🎧','☕','🍔','🚗','🏠','💤','🔥','⚡','✅','❌','🟢','🟡','🟠','🔵','⚪','🛠️','💬','🚀'].map((em) => (
                        <button
                          key={em}
                          type="button"
                          className="h-8 w-8 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10 text-base"
                          onClick={() => {
                            setStatusEmoji(em);
                            setEmojiOpen(false);
                            const msg = status === 'custom' ? statusMessage.trim() || null : null;
                            void updateAgentStatus(status === 'offline' ? 'online' : status, msg, em);
                          }}
                        >
                          {em}
                        </button>
                      ))}
                      <button
                        type="button"
                        className="col-span-6 text-[11px] text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 py-1"
                        onClick={() => {
                          setStatusEmoji('');
                          setEmojiOpen(false);
                          const msg = status === 'custom' ? statusMessage.trim() || null : null;
                          void updateAgentStatus(status === 'offline' ? 'online' : status, msg, null);
                        }}
                      >
                        Clear emoji
                      </button>
                    </div>
                  )}
                </div>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1">
                Online/Offline is automatic from your session. Status updates Live Chat Active Now in real time.
              </p>
              {status === 'custom' && (
                <input
                  value={statusMessage}
                  onChange={(e) => setStatusMessage(e.target.value)}
                  onBlur={() => {
                    void updateAgentStatus('custom', statusMessage.trim() || null, statusEmoji || null);
                  }}
                  placeholder="Write your custom status…"
                  className="mt-2 w-full px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-white dark:text-white placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                />
              )}
            </div>"""
        if old_block in p:
            p = p.replace(old_block, new_block, 1)
            print("profile status")
        else:
            print("profile status miss")
        p = p.replace(
            "const { currentAgent, updateAgentStatus, updateAgentStatus, refresh } = useTickets();",
            "const { currentAgent, updateAgentStatus, refresh } = useTickets();",
        )
        p = p.replace(
            "await updateAgentStatus(status === 'offline' ? 'online' : status, status === 'custom' ? statusMessage.trim() || null : null);",
            "await updateAgentStatus(status === 'offline' ? 'online' : status, status === 'custom' ? statusMessage.trim() || null : null, statusEmoji || null);",
        )
        p = "/* status-emoji-profile-v1 */\n" + p
        pp.write_text(p)
        print("profile done")
    else:
        print("profile already")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    pl = plc.read_text()
    if "status-colors-active-v1" not in pl:
        if "if (st === 'busy') return 'Busy';" in pl:
            pl = pl.replace(
                """                          {(() => {
                            const st = (a.status || 'online').toLowerCase();
                            if (st === 'busy') return 'Busy';
                            if (st === 'away') return 'Away';
                            if (st === 'in_call') return 'In a call';
                            if (st === 'custom') return a.status_message || 'Custom status';
                            return 'Online';
                          })()}
                          {a.role ? ` · ${a.role}` : ''}""",
                """{a.status_emoji ? <span className="shrink-0">{a.status_emoji}</span> : null}
                          <span
                            className={(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'away') return 'text-sky-400 font-medium';
                              if (st === 'busy') return 'text-yellow-300 font-medium';
                              if (st === 'in_call') return 'text-orange-400 font-medium';
                              if (st === 'custom') return 'text-white font-medium';
                              return 'text-emerald-400 font-medium';
                            })()}
                          >
                            {(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'busy') return 'Busy';
                              if (st === 'away') return 'Away';
                              if (st === 'in_call') return 'In a call';
                              if (st === 'custom') return a.status_message || 'Custom status';
                              return 'Online';
                            })()}
                          </span>
                          {a.role ? <span className="text-zinc-500 dark:text-zinc-400"> · {a.role}</span> : null}""",
                1,
            )
            print("plc subtitle")
        for a, b in [
            ("if (st === 'busy') return 'bg-amber-400';", "if (st === 'busy') return 'bg-yellow-400';"),
            ("if (st === 'away') return 'bg-yellow-400';", "if (st === 'away') return 'bg-sky-400';"),
            ("if (st === 'in_call') return 'bg-violet-400';", "if (st === 'in_call') return 'bg-orange-400';"),
            ("if (st === 'custom') return 'bg-sky-400';", "if (st === 'custom') return 'bg-white';"),
        ]:
            if a in pl:
                pl = pl.replace(a, b, 1)
        pl = "/* status-colors-active-v1 */\n" + pl
        plc.write_text(pl)
        print("plc done")
    else:
        print("plc already")

pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    p = pp.read_text()
    p2 = p.replace(
        "const { currentAgent, updateAgentStatus, updateAgentStatus, refresh } = useTickets();",
        "const { currentAgent, updateAgentStatus, refresh } = useTickets();",
    )
    if p2 != p:
        pp.write_text(p2)
        print("profile dedupe")
print("done")
