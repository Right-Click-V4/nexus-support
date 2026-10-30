#!/usr/bin/env python3
"""Accurate presence: last_seen heartbeat; Active Now only if seen < 45s."""
from pathlib import Path

types = Path("src/types.ts")
t = types.read_text()
if "last_seen_at" not in t:
    if "status_message" in t:
        t = t.replace(
            "  status_message?: string | null;\n  color: string;",
            "  status_message?: string | null;\n  last_seen_at?: string | null;\n  color: string;",
            1,
        )
    else:
        t = t.replace(
            "  status: AgentStatus;\n  color: string;",
            "  status: AgentStatus;\n  status_message?: string | null;\n  last_seen_at?: string | null;\n  color: string;",
            1,
        )
    types.write_text(t)
    print("types")
else:
    print("types ok")

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "const touchPresence = async" not in c:
    old = """  const updateAgentStatus = async (status: AgentStatus, statusMessage?: string | null) => {
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
    new = """  const updateAgentStatus = async (status: AgentStatus, statusMessage?: string | null) => {
    if (!currentAgent) return;
    const msg = statusMessage === undefined ? currentAgent.status_message ?? null : statusMessage;
    const seen = status === 'offline' ? null : new Date().toISOString();
    const patch: Record<string, unknown> = { status, last_seen_at: seen };
    if (statusMessage !== undefined) patch.status_message = statusMessage;
    if (supabase) {
      let { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
      if (error) {
        const minimal: Record<string, unknown> = { status };
        if (statusMessage !== undefined) minimal.status_message = statusMessage;
        const retry = await supabase.from('agents').update(minimal).eq('id', currentAgent.id);
        error = retry.error;
      }
      if (error) throw error;
      const next = { ...currentAgent, status, status_message: msg, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
      try {
        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
      } catch { /* ignore */ }
    } else {
      const next = { ...currentAgent, status, status_message: msg, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    }
  };

  const touchPresence = async () => {
    if (!currentAgent || !supabase) return;
    if ((currentAgent.status || 'offline') === 'offline') return;
    const seen = new Date().toISOString();
    const { error } = await supabase
      .from('agents')
      .update({ last_seen_at: seen })
      .eq('id', currentAgent.id);
    if (!error) {
      setCurrentAgent((prev) => (prev ? { ...prev, last_seen_at: seen } : prev));
      setAgents((prev) =>
        prev.map((a) => (a.id === currentAgent.id ? { ...a, last_seen_at: seen } : a)),
      );
    }
  };"""
    if old in c:
        c = c.replace(old, new, 1)
        print("tc uas")
    else:
        print("tc uas miss")
    if "touchPresence: () => Promise<void>" not in c:
        c = c.replace(
            "  updateAgentStatus: (status: AgentStatus, statusMessage?: string | null) => Promise<void>;",
            "  updateAgentStatus: (status: AgentStatus, statusMessage?: string | null) => Promise<void>;\n  touchPresence: () => Promise<void>;",
            1,
        )
    if ",\n        touchPresence," not in c:
        c = c.replace("        updateAgentStatus,", "        updateAgentStatus,\n        touchPresence,", 1)
    tc.write_text(c)
    print("tc done")
else:
    print("tc already")

sa = Path("src/SystemApp.tsx")
s = sa.read_text()
if "presence-heartbeat-v1" not in s:
    s = s.replace(
        "const { tickets, usingSupabase, currentAgent, updateAgentStatus: setPresenceStatus } = useTickets();\n  const presenceAgent = currentAgent;",
        "const { tickets, usingSupabase, currentAgent, updateAgentStatus: setPresenceStatus, touchPresence } = useTickets();\n  const presenceAgent = currentAgent;",
        1,
    )
    old_fx = """  /* Presence: logged into Agent Workspace \u2192 Online; logout / last tab \u2192 Offline */
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
  }, [setPresenceStatus]);""".replace("\\u2192", "\u2192")
    new_fx = """  /* Presence: workspace open \u2192 online + heartbeat; last tab / logout \u2192 offline */
  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {
      void setPresenceStatus('online');
    } else {
      void touchPresence?.();
    }
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!presenceAgent?.id) return;
    const tick = () => { void touchPresence?.(); };
    tick();
    const id = window.setInterval(tick, 15000);
    return () => window.clearInterval(id);
  }, [presenceAgent?.id, touchPresence]);

  useEffect(() => {
    const goOffline = () => {
      try { void setPresenceStatus('offline'); } catch { /* ignore */ }
    };
    const onPageHide = () => {
      try {
        const raw = localStorage.getItem('nexus-live-tabs-v3');
        const tabs = raw ? JSON.parse(raw) : {};
        const now = Date.now();
        const live = Object.entries(tabs || {}).filter(
          ([, ts]) => typeof ts === 'number' && now - (ts as number) < 8000,
        );
        if (live.length <= 1) goOffline();
      } catch {
        goOffline();
      }
    };
    window.addEventListener('pagehide', onPageHide);
    return () => window.removeEventListener('pagehide', onPageHide);
  }, [setPresenceStatus]);""".replace("\\u2192", "\u2192")
    if old_fx in s:
        s = s.replace(old_fx, new_fx, 1)
        print("sa fx")
    else:
        print("sa fx miss")
    s = "/* presence-heartbeat-v1 */\n" + s
    sa.write_text(s)
    print("sa done")
else:
    print("sa already")

plc = Path("src/components/PortalLiveChat.tsx")
p = plc.read_text()
if "presence-active-filter-v1" not in p:
    old_f = """  const onlineAgents = useMemo(() => {
    return (agents || []).filter((a) => {
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved') return false;
      const status = (a.status || 'offline').toLowerCase();
      return status !== 'offline' && status !== '';
    });
  }, [agents]);

  const hasAgentOnline = onlineAgents.length > 0;"""
    new_f = """  const [presenceTick, setPresenceTick] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => setPresenceTick((n) => n + 1), 10000);
    return () => window.clearInterval(id);
  }, []);

  const onlineAgents = useMemo(() => {
    const now = Date.now();
    const LIVE_WINDOW_MS = 45_000;
    return (agents || []).filter((a) => {
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved') return false;
      const status = (a.status || 'offline').toLowerCase();
      if (status === 'offline' || status === '') return false;
      const seen = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
      if (!seen || Number.isNaN(seen)) return false;
      return now - seen <= LIVE_WINDOW_MS;
    });
  }, [agents, presenceTick]);

  const hasAgentOnline = onlineAgents.length > 0;"""
    if old_f in p:
        p = p.replace(old_f, new_f, 1)
        print("plc")
    else:
        print("plc miss")
    p = "/* presence-active-filter-v1 */\n" + p
    plc.write_text(p)
else:
    print("plc already")

ac = Path("src/context/AuthContext.tsx")
a = ac.read_text()
if "presence-force-offline-v1" not in a:
    if "forceAgentOffline" not in a:
        a = a.replace(
            "    let suppressAuthEvents = false;",
            """    let suppressAuthEvents = false;
    const forceAgentOffline = async () => {
      try {
        const id = localStorage.getItem('nexus-presence-agent-id');
        if (!id || !supabase) return;
        await supabase.from('agents').update({ status: 'offline', last_seen_at: null }).eq('id', id);
        localStorage.removeItem('nexus-presence-agent-id');
      } catch { /* ignore */ }
    };""",
            1,
        )
        a = a.replace(
            """      if (isNewSession) {
        suppressAuthEvents = true;
        clearSupabaseAuthStorage();""",
            """      if (isNewSession) {
        suppressAuthEvents = true;
        await forceAgentOffline();
        clearSupabaseAuthStorage();""",
            1,
        )
        a = a.replace(
            "    clearSupabaseAuthStorage();\n    await supabase.auth.signOut();",
            "    await forceAgentOffline();\n    clearSupabaseAuthStorage();\n    await supabase.auth.signOut();",
            1,
        )
        print("ac")
    a = "/* presence-force-offline-v1 */\n" + a
    ac.write_text(a)
else:
    print("ac already")
print("done")
