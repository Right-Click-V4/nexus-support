#!/usr/bin/env python3
"""Make createTicket/updateTicket/follow-up/save never hang; faster Active Now presence."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
t = tc.read_text()
if "ticket-ops-timeout-v1" not in t:
    if "function sbTimeout" not in t:
        anchor = "const STORAGE_KEY = 'nexus-tickets-v1';"
        helper = """
/** Never hang UI on a slow/hung Supabase request */
function sbTimeout<T>(p: PromiseLike<T>, ms = 8000): Promise<T> {
  return Promise.race([
    Promise.resolve(p as PromiseLike<T>).then((v) => v as T),
    new Promise<T>((_, reject) => {
      window.setTimeout(() => reject(new Error('Request timed out. Please try again.')), ms);
    }),
  ]);
}

""" + anchor
        if anchor in t:
            t = t.replace(anchor, helper, 1)
            print("sbTimeout helper")

    old_rules = """  const loadRules = async (): Promise<Automation[]> => {
    if (supabase) {
      const { data } = await supabase.from('automations').select('*');
      if (data?.length) return data as Automation[];
    }
    return loadAutomationsLocal();
  };"""
    new_rules = """  const loadRules = async (): Promise<Automation[]> => {
    if (supabase) {
      try {
        const res = await sbTimeout(supabase.from('automations').select('*'), 4000);
        const data = res && typeof res === 'object' && 'data' in res ? (res as { data: Automation[] | null }).data : null;
        if (data?.length) return data as Automation[];
      } catch {
        /* rules optional */
      }
    }
    return loadAutomationsLocal();
  };"""
    if old_rules in t:
        t = t.replace(old_rules, new_rules, 1)
        print("loadRules")

    old_ins = """      const { error } = await supabase.from('tickets').insert(payload);
      if (error) {
        delete payload.tags;
        const { error: e2 } = await supabase.from('tickets').insert(payload);
        if (e2) throw e2;
      }
      /* Optimistic: show in agent workspace immediately, then re-fetch */
      setTickets((prev) => (prev.some((t) => t.id === ticket.id) ? prev : [ticket, ...prev]));
      try {
        if (typeof BroadcastChannel !== 'undefined') {
          const bc = new BroadcastChannel('nexus-tickets-sync');
          bc.postMessage({ type: 'ticket_created', id: ticket.id, at: Date.now() });
          bc.close();
        }
      } catch {
        /* ignore */
      }
      void refresh({ silent: true });"""
    new_ins = """      try {
        const ins = await sbTimeout(supabase.from('tickets').insert(payload), 10000);
        const error = ins && typeof ins === 'object' && 'error' in ins ? (ins as { error: { message?: string } | null }).error : null;
        if (error) {
          delete payload.tags;
          const ins2 = await sbTimeout(supabase.from('tickets').insert(payload), 10000);
          const e2 = ins2 && typeof ins2 === 'object' && 'error' in ins2 ? (ins2 as { error: { message?: string } | null }).error : null;
          if (e2) throw new Error(e2.message || 'Could not create ticket');
        }
      } catch (e) {
        throw e instanceof Error ? e : new Error('Could not create ticket');
      }
      setTickets((prev) => (prev.some((t) => t.id === ticket.id) ? prev : [ticket, ...prev]));
      try {
        if (typeof BroadcastChannel !== 'undefined') {
          const bc = new BroadcastChannel('nexus-tickets-sync');
          bc.postMessage({ type: 'ticket_created', id: ticket.id, at: Date.now() });
          bc.close();
        }
      } catch {
        /* ignore */
      }
      void refresh({ silent: true });"""
    if old_ins in t:
        t = t.replace(old_ins, new_ins, 1)
        print("create insert")

    old_upd = """    if (supabase) {
      const { error } = await supabase.from('tickets').update(payload).eq('id', id);
      if (error) throw error;
      await refresh();
    } else {
      setTickets((prev) =>
        prev.map((t) =>
          t.id === id
            ? {
                ...t,
                ...updates,
                updated_at: payload.updated_at,
                assignee:
                  updates.assignee_id !== undefined
                    ? agents.find((a) => a.id === updates.assignee_id) || null
                    : t.assignee,
              }
            : t
        )
      );
    }"""
    new_upd = """    setTickets((prev) =>
      prev.map((row) =>
        row.id === id
          ? {
              ...row,
              ...updates,
              updated_at: payload.updated_at,
              assignee:
                updates.assignee_id !== undefined
                  ? agents.find((a) => a.id === updates.assignee_id) || null
                  : row.assignee,
            }
          : row
      )
    );
    if (supabase) {
      try {
        const up = await sbTimeout(supabase.from('tickets').update(payload).eq('id', id), 10000);
        const error = up && typeof up === 'object' && 'error' in up ? (up as { error: { message?: string } | null }).error : null;
        if (error) throw new Error(error.message || 'Could not update ticket');
      } catch (e) {
        void refresh({ silent: true });
        throw e instanceof Error ? e : new Error('Could not update ticket');
      }
      void refresh({ silent: true });
    }"""
    if old_upd in t:
        t = t.replace(old_upd, new_upd, 1)
        print("updateTicket")

    t = "/* ticket-ops-timeout-v1 */\n" + t
    tc.write_text(t)
else:
    print("tc already")

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "presence-fast-online-v1" not in s:
        for ms in ("8000", "15000"):
            old = f"""  useEffect(() => {{
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {{
      void setPresenceStatus('online');
    }} else {{
      void touchPresence?.();
    }}
  }}, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {{
    if (!presenceAgent?.id) return;
    const tick = () => {{ void touchPresence?.(); }};
    tick();
    const id = window.setInterval(tick, {ms});
    return () => window.clearInterval(id);
  }}, [presenceAgent?.id, touchPresence]);"""
            new = """  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {
      void setPresenceStatus('online');
    } else {
      void touchPresence?.();
    }
    void touchPresence?.();
    const quick = window.setTimeout(() => { void touchPresence?.(); }, 500);
    return () => window.clearTimeout(quick);
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!presenceAgent?.id) return;
    const tick = () => { void touchPresence?.(); };
    tick();
    const id = window.setInterval(tick, 5000);
    return () => window.clearInterval(id);
  }, [presenceAgent?.id, touchPresence]);"""
            if old in s:
                s = s.replace(old, new, 1)
                print("presence fast", ms)
                break
        s = "/* presence-fast-online-v1 */\n" + s
        sa.write_text(s)
    else:
        print("sa already")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "presence-poll-refresh-v1" not in p:
        p = p.replace(
            "const { findTicket, agents } = useTickets();",
            "const { findTicket, agents, refresh: refreshTickets } = useTickets();",
            1,
        )
        inject = """
  useEffect(() => {
    const id = window.setInterval(() => {
      void refreshTickets?.({ silent: true });
    }, 8000);
    void refreshTickets?.({ silent: true });
    return () => window.clearInterval(id);
  }, [refreshTickets]);
"""
        idx = p.find("const hasAgentOnline = onlineAgents.length > 0;")
        if idx > 0:
            p = p[:idx] + inject + "\n  " + p[idx:]
            print("plc poll")
        p = "/* presence-poll-refresh-v1 */\n" + p
        plc.write_text(p)
    else:
        if "refreshTickets" in p and "refresh: refreshTickets" not in p:
            p = p.replace(
                "const { findTicket, agents } = useTickets();",
                "const { findTicket, agents, refresh: refreshTickets } = useTickets();",
                1,
            )
            plc.write_text(p)
            print("plc destructure")
        else:
            print("plc already")
print("done")
