#!/usr/bin/env python3
"""Session Online/Offline + Profile presence variants (Away/Busy/In call/Custom)."""
from pathlib import Path
import re

types = Path("src/types.ts")
t = types.read_text()
if "agent-presence-v1" not in t:
    t = t.replace(
        "export type AgentStatus = 'online' | 'busy' | 'away' | 'offline';",
        "export type AgentStatus = 'online' | 'busy' | 'away' | 'in_call' | 'custom' | 'offline';",
        1,
    )
    if "status_message" not in t:
        t = t.replace(
            "  status: AgentStatus;\n  color: string;",
            "  status: AgentStatus;\n  /** Optional note when status is custom. */\n  status_message?: string | null;\n  color: string;",
            1,
        )
    t = "/* agent-presence-v1 */\n" + t
    types.write_text(t)
    print("types ok")
else:
    print("types already")

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "agent-presence-ctx-v1" not in c:
    c = c.replace(
        "  updateAgentStatus: (status: AgentStatus) => Promise<void>;",
        "  updateAgentStatus: (status: AgentStatus, statusMessage?: string | null) => Promise<void>;",
        1,
    )
    old_uas = """  const updateAgentStatus = async (status: AgentStatus) => {
    if (!currentAgent) return;
    if (supabase) {
      const { error } = await supabase.from('agents').update({ status }).eq('id', currentAgent.id);
      if (error) throw error;
      setCurrentAgent({ ...currentAgent, status });
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? { ...a, status } : a)));
    } else {
      setCurrentAgent({ ...currentAgent, status });
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? { ...a, status } : a)));
    }
  };"""
    new_uas = """  const updateAgentStatus = async (status: AgentStatus, statusMessage?: string | null) => {
    if (!currentAgent) return;
    const msg = statusMessage === undefined ? currentAgent.status_message ?? null : statusMessage;
    const patch: { status: AgentStatus; status_message?: string | null } = { status };
    if (statusMessage !== undefined) patch.status_message = statusMessage;
    if (supabase) {
      let { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
      if (error && statusMessage !== undefined) {
        const retry = await supabase.from('agents').update({ status }).eq('id', currentAgent.id);
        error = retry.error;
      }
      if (error) throw error;
      const next = { ...currentAgent, status, status_message: msg };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    } else {
      const next = { ...currentAgent, status, status_message: msg };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    }
  };"""
    if old_uas in c:
        c = c.replace(old_uas, new_uas, 1)
        print("tc uas")
    else:
        print("tc uas miss")
    c = "/* agent-presence-ctx-v1 */\n" + c
    tc.write_text(c)
    print("tc done")
else:
    print("tc already")

pp = Path("src/components/ProfilePage.tsx")
p = pp.read_text()
if "agent-presence-profile-v1" not in p:
    if "statusMessage" not in p:
        p = p.replace(
            "  const [status, setStatus] = useState<AgentStatus>('online');",
            "  const [status, setStatus] = useState<AgentStatus>('online');\n"
            "  const [statusMessage, setStatusMessage] = useState('');",
            1,
        )
        p = p.replace(
            "      setStatus(currentAgent.status);",
            "      setStatus(\n"
            "        currentAgent.status === 'offline' || currentAgent.status === 'online'\n"
            "          ? 'online'\n"
            "          : currentAgent.status,\n"
            "      );\n"
            "      setStatusMessage(currentAgent.status_message || '');",
            1,
        )
        print("pp state")

    old_sel = """              <label className="block text-sm font-medium text-zinc-700 mb-2">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as AgentStatus)}
                className="w-full px-4 py-2.5 text-sm border border-zinc-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
              >
                <option value="online">Online</option>
                <option value="busy">Busy</option>
                <option value="away">Away</option>
                <option value="offline">Offline</option>
              </select>
            </div>"""
    new_sel = """              <label className="block text-sm font-medium text-zinc-700 mb-2">Status</label>
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
    if old_sel in p:
        p = p.replace(old_sel, new_sel, 1)
        print("pp select")
    else:
        print("pp select miss")

    p = p.replace(
        "await updateAgentStatus(status);",
        "await updateAgentStatus(status === 'offline' ? 'online' : status, status === 'custom' ? statusMessage.trim() || null : null);",
    )
    p = p.replace(
        "if (status !== currentAgent?.status) await updateAgentStatus(status);",
        "if (status !== currentAgent?.status || (status === 'custom' && statusMessage !== (currentAgent?.status_message || ''))) {\n"
        "          await updateAgentStatus(status === 'offline' ? 'online' : status, status === 'custom' ? statusMessage.trim() || null : null);\n"
        "        }",
        1,
    )
    p = p.replace(
        """{currentAgent.role} · <span className="text-brand-600 font-medium capitalize">{currentAgent.status}</span>""",
        """{currentAgent.role} · <span className="text-brand-600 font-medium capitalize">{\n                  currentAgent.status === 'in_call'\n                    ? 'In a call'\n                    : currentAgent.status === 'custom'\n                      ? (currentAgent.status_message || 'Custom')\n                      : currentAgent.status\n                }</span>""",
        1,
    )
    p = "/* agent-presence-profile-v1 */\n" + p
    pp.write_text(p)
    print("pp done")
else:
    print("pp already")

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "agent-presence-shell-v1" not in s:
    if "updateAgentStatus: setPresenceStatus" not in s:
        s = s.replace(
            "const { tickets, usingSupabase, currentAgent } = useTickets();",
            "const { tickets, usingSupabase, currentAgent, updateAgentStatus: setPresenceStatus, currentAgent: presenceAgent } = useTickets();",
            1,
        )
        # avoid duplicate currentAgent - fix if double
        s = s.replace(
            "const { tickets, usingSupabase, currentAgent, updateAgentStatus: setPresenceStatus, currentAgent: presenceAgent } = useTickets();",
            "const { tickets, usingSupabase, currentAgent, updateAgentStatus: setPresenceStatus } = useTickets();\n  const presenceAgent = currentAgent;",
            1,
        )
        print("shell tickets")

    if "Presence: logged into Agent Workspace" not in s:
        presence_fx = """
  /* Presence: logged into Agent Workspace \u2192 Online; logout / last tab \u2192 Offline */
  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {
      void setPresenceStatus('online');
    }
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const goOffline = () => {
      try {
        void setPresenceStatus('offline');
      } catch { /* ignore */ }
    };
    const onPageHide = () => {
      try {
        const raw = localStorage.getItem('nexus-tabs-v1');
        const tabs = raw ? JSON.parse(raw) : {};
        const n = tabs && typeof tabs === 'object' ? Object.keys(tabs).length : 0;
        if (n <= 1) goOffline();
      } catch {
        goOffline();
      }
    };
    window.addEventListener('pagehide', onPageHide);
    return () => window.removeEventListener('pagehide', onPageHide);
  }, [setPresenceStatus]);
""".replace("\\u2192", "\u2192")
        idx = s.find("export function AgentShell()")
        j = s.find("  useEffect(() => {", idx)
        if j > 0:
            s = s[:j] + presence_fx + "\n" + s[j:]
            print("shell presence fx")

    if "setPresenceStatus('offline'); void signOut()" not in s:
        s = s.replace(
            "onClick={() => void signOut()}",
            "onClick={() => { void setPresenceStatus('offline'); void signOut(); }}",
            1,
        )
        print("signout offline")

    s = "/* agent-presence-shell-v1 */\n" + s
    sa.write_text(s)
    print("sa done")
else:
    print("sa already")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    pl = plc.read_text()
    if "presence-filter-v1" not in pl:
        old_f = """      const status = (a.status || 'offline').toLowerCase();
      return status === 'online' || status === 'busy';"""
        new_f = """      const status = (a.status || 'offline').toLowerCase();
      return status !== 'offline' && status !== '';"""
        if old_f in pl:
            pl = pl.replace(old_f, new_f, 1)
            print("plc filter")
        old_label = """                        <div className="text-[11px] text-zinc-500 dark:text-zinc-400 capitalize">
                          {(a.status || 'online').toLowerCase() === 'busy' ? 'Busy' : 'Online'}
                          {a.role ? ` \u00b7 ${a.role}` : ''}
                        </div>""".replace("\\u00b7", "\u00b7")
        new_label = """                        <div className="text-[11px] text-zinc-500 dark:text-zinc-400 capitalize">
                          {(() => {
                            const st = (a.status || 'online').toLowerCase();
                            if (st === 'busy') return 'Busy';
                            if (st === 'away') return 'Away';
                            if (st === 'in_call') return 'In a call / meeting';
                            if (st === 'custom') return a.status_message || 'Custom status';
                            return 'Online';
                          })()}
                          {a.role ? ` \u00b7 ${a.role}` : ''}
                        </div>""".replace("\\u00b7", "\u00b7")
        if old_label in pl:
            pl = pl.replace(old_label, new_label, 1)
            print("plc label")
        old_dot = """                          className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-zinc-900 ${
                            (a.status || '').toLowerCase() === 'busy' ? 'bg-amber-400' : 'bg-emerald-400'
                          }`}"""
        new_dot = """                          className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-zinc-900 ${
                            (() => {
                              const st = (a.status || '').toLowerCase();
                              if (st === 'busy' || st === 'in_call') return 'bg-amber-400';
                              if (st === 'away') return 'bg-yellow-300';
                              if (st === 'custom') return 'bg-sky-400';
                              return 'bg-emerald-400';
                            })()
                          }`}"""
        if old_dot in pl:
            pl = pl.replace(old_dot, new_dot, 1)
            print("plc dot")
        pl = "/* presence-filter-v1 */\n" + pl
        plc.write_text(pl)
        print("plc done")
    else:
        print("plc already")

print("done")
