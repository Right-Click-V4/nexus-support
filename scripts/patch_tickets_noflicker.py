#!/usr/bin/env python3
"""Stop Tickets table flicker: soft refresh without loading flash; less aggressive poll/focus."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "tickets-noflicker-v1" in c:
    print("already")
    raise SystemExit(0)

old_refresh = """  const refresh = useCallback(async () => {
    if (!isSupabaseConfigured || !supabase) {
      setLoading(false);
      return;
    }
    setLoading(true);
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

if old_refresh in c:
    c = c.replace(old_refresh, new_refresh, 1)
    print("refresh ok")
else:
    print("refresh miss")

c = c.replace(
    "  refresh: () => Promise<void>;",
    "  refresh: (opts?: { silent?: boolean }) => Promise<void>;",
    1,
)

old_rt = """  useEffect(() => {
    if (!supabase) return;
    const channel = supabase
      .channel('nexus-live')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'tickets' }, () => refresh())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'agents' }, () => refresh())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'customers' }, () => refresh())
      .subscribe();
    let bc: BroadcastChannel | null = null;
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        bc = new BroadcastChannel('nexus-tickets-sync');
        bc.onmessage = () => {
          void refresh();
        };
      }
    } catch {
      bc = null;
    }
    const onFocus = () => {
      void refresh();
    };
    window.addEventListener('focus', onFocus);
    const poll = window.setInterval(() => {
      void refresh();
    }, 12_000);
    return () => {
      supabase?.removeChannel(channel);
      try {
        bc?.close();
      } catch {
        /* ignore */
      }
      window.removeEventListener('focus', onFocus);
      window.clearInterval(poll);
    };
  }, [refresh]);"""

new_rt = """  useEffect(() => {
    if (!supabase) return;
    const soft = () => {
      void refresh({ silent: true });
    };
    const channel = supabase
      .channel('nexus-live')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'tickets' }, soft)
      .on('postgres_changes', { event: '*', schema: 'public', table: 'agents' }, soft)
      .on('postgres_changes', { event: '*', schema: 'public', table: 'customers' }, soft)
      .subscribe();
    let bc: BroadcastChannel | null = null;
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        bc = new BroadcastChannel('nexus-tickets-sync');
        bc.onmessage = () => soft();
      }
    } catch {
      bc = null;
    }
    let focusTimer: number | undefined;
    const onFocus = () => {
      window.clearTimeout(focusTimer);
      focusTimer = window.setTimeout(() => soft(), 400);
    };
    window.addEventListener('focus', onFocus);
    const poll = window.setInterval(soft, 30_000);
    return () => {
      supabase?.removeChannel(channel);
      try {
        bc?.close();
      } catch {
        /* ignore */
      }
      window.removeEventListener('focus', onFocus);
      window.clearTimeout(focusTimer);
      window.clearInterval(poll);
    };
  }, [refresh]);"""

if old_rt in c:
    c = c.replace(old_rt, new_rt, 1)
    print("rt soft ok")
else:
    print("rt soft miss")

c = c.replace(
    """      void refresh();
    } else {
      setTickets((prev) => [ticket, ...prev]);
    }
    void notifyAgents({
      title: 'New ticket',""",
    """      void refresh({ silent: true });
    } else {
      setTickets((prev) => [ticket, ...prev]);
    }
    void notifyAgents({
      title: 'New ticket',""",
    1,
)

if "tickets-noflicker-v1" not in c:
    c = c.replace("// tickets-sync-v1\n", "// tickets-sync-v1\n// tickets-noflicker-v1\n", 1)
    if "tickets-noflicker-v1" not in c:
        c = "// tickets-noflicker-v1\n" + c

tc.write_text(c)
print("done")
