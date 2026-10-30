#!/usr/bin/env python3
"""Unstick ticket loading + fix Active Now presence detection."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
t = tc.read_text()
if "tickets-presence-fix-v1" not in t:
    old_refresh = """  const refresh = useCallback(async (opts?: { silent?: boolean }) => {
    if (!isSupabaseConfigured || !supabase) {
      setLoading(false);
      return;
    }
    const silent = opts?.silent === true;
    /* Only show full-page loading on the first load — never flash the table away on poll/focus/realtime */
    if (!silent) setLoading(true);
    try {
      const [tRes, aRes, cRes] = await Promise.all([
        supabase.from('tickets').select('*').order('created_at', { ascending: false }),
        supabase.from('agents').select('*'),
        supabase.from('customers').select('*'),
      ]);
      const agentList = filterAgents(((aRes.data as Agent[]) || []).map(hydrateAvatar));
      if (aRes.data) setAgents(agentList);
      if (cRes.data) setCustomers(cRes.data as Customer[]);
      if (tRes.data) {
        const list = (tRes.data as Ticket[]).map((t) => ({
          ...t,
          assignee: agentList.find((a) => a.id === t.assignee_id) || null,
          notes: t.notes || [],
          messages: t.messages || [],
          attachments: t.attachments || [],
          tags: t.tags || [],
        }));
        setTickets(list);
      }
    } finally {
      setLoading(false);
    }
  }, []);"""

    new_refresh = """  const refresh = useCallback(async (opts?: { silent?: boolean }) => {
    if (!isSupabaseConfigured || !supabase) {
      setLoading(false);
      return;
    }
    const silent = opts?.silent === true;
    if (!silent) setLoading(true);
    const withTimeout = <T,>(p: PromiseLike<T>, ms: number): Promise<T | null> =>
      Promise.race([
        Promise.resolve(p).then((v) => v as T).catch(() => null),
        new Promise<null>((r) => window.setTimeout(() => r(null), ms)),
      ]);
    try {
      const [tRes, aRes, cRes] = await Promise.all([
        withTimeout(supabase.from('tickets').select('*').order('created_at', { ascending: false }), 10000),
        withTimeout(supabase.from('agents').select('*'), 10000),
        withTimeout(supabase.from('customers').select('*'), 10000),
      ]);
      const agentRows = aRes && typeof aRes === 'object' && 'data' in aRes ? (aRes as { data: Agent[] | null }).data : null;
      const customerRows = cRes && typeof cRes === 'object' && 'data' in cRes ? (cRes as { data: Customer[] | null }).data : null;
      const ticketRows = tRes && typeof tRes === 'object' && 'data' in tRes ? (tRes as { data: Ticket[] | null }).data : null;
      const agentList = filterAgents((agentRows || []).map(hydrateAvatar));
      if (agentRows) setAgents(agentList);
      if (customerRows) setCustomers(customerRows as Customer[]);
      if (ticketRows) {
        const list = (ticketRows as Ticket[]).map((row) => ({
          ...row,
          assignee: agentList.find((a) => a.id === row.assignee_id) || null,
          notes: row.notes || [],
          messages: row.messages || [],
          attachments: row.attachments || [],
          tags: row.tags || [],
        }));
        setTickets(list);
      }
    } catch {
      /* never leave UI stuck on Loading tickets */
    } finally {
      setLoading(false);
    }
  }, []);"""

    if old_refresh in t:
        t = t.replace(old_refresh, new_refresh, 1)
        print("refresh timeout")
    else:
        print("refresh pattern miss")

    old_touch = """  const touchPresence = async () => {
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

    new_touch = """  const touchPresence = async () => {
    if (!currentAgent || !supabase) return;
    if ((currentAgent.status || 'offline') === 'offline') return;
    const seen = new Date().toISOString();
    setCurrentAgent((prev) => (prev ? { ...prev, last_seen_at: seen } : prev));
    setAgents((prev) =>
      prev.map((a) => (a.id === currentAgent.id ? { ...a, last_seen_at: seen } : a)),
    );
    try {
      const { error } = await supabase
        .from('agents')
        .update({ last_seen_at: seen })
        .eq('id', currentAgent.id);
      if (error) {
        await supabase.from('agents').update({ status: currentAgent.status || 'online' }).eq('id', currentAgent.id);
      }
    } catch {
      /* ignore */
    }
  };"""

    if old_touch in t:
        t = t.replace(old_touch, new_touch, 1)
        print("touchPresence")

    old_uas_err = """      if (error) throw error;
      const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
      try {
        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
      } catch { /* ignore */ }"""
    new_uas_err = """      const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
      try {
        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
      } catch { /* ignore */ }
      if (error) {
        // non-fatal for UI presence
      }"""
    if old_uas_err in t:
        t = t.replace(old_uas_err, new_uas_err, 1)
        print("uas local first")

    t = "/* tickets-presence-fix-v1 */\n" + t
    tc.write_text(t)
else:
    print("tc already")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "presence-window-v2" not in p:
        old_f = """  const onlineAgents = useMemo(() => {
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
  }, [agents, presenceTick]);"""
        new_f = """  const onlineAgents = useMemo(() => {
    const now = Date.now();
    const LIVE_WINDOW_MS = 120_000;
    return (agents || []).filter((a) => {
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved') return false;
      const status = (a.status || 'offline').toLowerCase();
      if (status === 'offline' || status === '') return false;
      const seen = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
      if (seen && !Number.isNaN(seen)) return now - seen <= LIVE_WINDOW_MS;
      return status === 'online' || status === 'busy' || status === 'away' || status === 'in_call' || status === 'custom';
    });
  }, [agents, presenceTick]);"""
        if old_f in p:
            p = p.replace(old_f, new_f, 1)
            print("plc window")
        p = "/* presence-window-v2 */\n" + p
        plc.write_text(p)
    else:
        print("plc already")
print("done")
