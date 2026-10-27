#!/usr/bin/env python3
"""Agent Tickets table matches portal form; stronger realtime + optimistic create."""
from pathlib import Path
import re

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    c = tc.read_text()
    if "tickets-sync-v1" not in c:
        old = """      const { error } = await supabase.from('tickets').insert(payload);
      if (error) {
        delete payload.tags;
        const { error: e2 } = await supabase.from('tickets').insert(payload);
        if (e2) throw e2;
      }
      await refresh();
    } else {
      setTickets((prev) => [ticket, ...prev]);
    }"""
        new = """      const { error } = await supabase.from('tickets').insert(payload);
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
      void refresh();
    } else {
      setTickets((prev) => [ticket, ...prev]);
    }"""
        if old in c:
            c = c.replace(old, new, 1)
            print("tc optimistic ok")
        else:
            print("tc optimistic miss")

        old_rt = """  useEffect(() => {
    if (!supabase) return;
    const channel = supabase
      .channel('nexus-live')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'tickets' }, () => refresh())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'agents' }, () => refresh())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'customers' }, () => refresh())
      .subscribe();
    return () => {
      supabase?.removeChannel(channel);
    };
  }, [refresh]);"""

        new_rt = """  useEffect(() => {
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

        if old_rt in c:
            c = c.replace(old_rt, new_rt, 1)
            print("tc realtime ok")
        else:
            print("tc realtime miss")

        c = "// tickets-sync-v1\n" + c
        tc.write_text(c)
    else:
        print("tc already")

tp = Path("src/components/TicketsPage.tsx")
t = tp.read_text()
if "tickets-table-v2" in t:
    print("tp already")
else:
    if "channelFilter" not in t:
        t = t.replace(
            "const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');",
            "const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');\n  const [channelFilter, setChannelFilter] = useState<'all' | 'portal' | 'email' | 'chat' | 'phone'>('all');",
            1,
        )
        t = t.replace(
            "if (priorityFilter !== 'all' && t.priority !== priorityFilter) return false;",
            "if (priorityFilter !== 'all' && t.priority !== priorityFilter) return false;\n      if (channelFilter !== 'all' && t.channel !== channelFilter) return false;",
            1,
        )
        t = t.replace(
            "[tickets, search, statusFilter, priorityFilter, slaFilter, showTrash]",
            "[tickets, search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash]",
            1,
        )

    m = re.search(r'<select\s+value=\{priorityFilter\}[\s\S]*?</select>', t)
    if m and 'value={channelFilter}' not in t:
        insert_after = m.group(0)
        channel_sel = insert_after + """
        <select
          value={channelFilter}
          onChange={(e) => setChannelFilter(e.target.value as typeof channelFilter)}
          className="text-sm px-3 py-2 border border-slate-200 rounded-lg bg-white"
        >
          <option value="all">All channels</option>
          <option value="portal">Portal</option>
          <option value="email">Email</option>
          <option value="chat">Chat</option>
          <option value="phone">Phone</option>
        </select>"""
        t = t.replace(insert_after, channel_sel, 1)
        print("channel select ok")

    old_head = """              <tr className="text-left text-slate-500">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Customer</th>
                <th className="px-4 py-3 font-medium">Branch</th>
                <th className="px-4 py-3 font-medium">Priority</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">SLA</th>
                <th className="px-4 py-3 font-medium">Channel</th>
                <th className="px-4 py-3 font-medium">Assignee</th>
                <th className="px-4 py-3 font-medium w-20"></th>
              </tr>"""
    new_head = """              <tr className="text-left text-slate-500">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Subject</th>
                <th className="px-4 py-3 font-medium">Customer</th>
                <th className="px-4 py-3 font-medium">Branch</th>
                <th className="px-4 py-3 font-medium">Priority</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Channel</th>
                <th className="px-4 py-3 font-medium">Submitted</th>
                <th className="px-4 py-3 font-medium">SLA</th>
                <th className="px-4 py-3 font-medium">Assignee</th>
                <th className="px-4 py-3 font-medium w-20"></th>
              </tr>"""
    if old_head in t:
        t = t.replace(old_head, new_head, 1)
        print("headers ok")

    t = t.replace(
        'className="border-b border-slate-100 hover:bg-brand-50/50 cursor-pointer transition-colors"',
        """className={clsx(
                      'border-b border-slate-100 hover:bg-brand-50/50 cursor-pointer transition-colors',
                      t.status === 'new' && t.channel === 'portal' && 'bg-violet-50/80 ring-1 ring-inset ring-violet-200/60',
                      t.status === 'new' && t.channel !== 'portal' && 'bg-brand-50/40'
                    )}""",
        1,
    )

    old_title = """                    <td className="px-4 py-3 font-medium text-slate-800 max-w-xs">
                      <div className="truncate">{t.title}</div>
                      {(t.tags || []).length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(t.tags || []).slice(0, 3).map((tag) => (
                            <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>"""
    new_title = """                    <td className="px-4 py-3 font-medium text-slate-800 max-w-[240px]">
                      <div className="truncate" title={t.title}>{t.title}</div>
                      {t.description ? (
                        <div className="text-[11px] text-slate-400 truncate mt-0.5 font-normal" title={t.description}>
                          {t.description}
                        </div>
                      ) : null}
                      {(t.tags || []).length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(t.tags || []).slice(0, 3).map((tag) => (
                            <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-normal">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>"""
    if old_title in t:
        t = t.replace(old_title, new_title, 1)
        print("subject cell ok")
    else:
        print("subject cell miss")

    t2, n = re.subn(
        r'<td className="px-4 py-3 capitalize text-slate-600">\{t\.channel\}</td>',
        '''<td className="px-4 py-3">
                      <span
                        className={clsx(
                          'text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded',
                          t.channel === 'portal' && 'bg-violet-100 text-violet-700',
                          t.channel === 'email' && 'bg-sky-100 text-sky-700',
                          t.channel === 'chat' && 'bg-fuchsia-100 text-fuchsia-700',
                          t.channel === 'phone' && 'bg-amber-100 text-amber-800',
                          !['portal', 'email', 'chat', 'phone'].includes(t.channel) && 'bg-slate-100 text-slate-600'
                        )}
                      >
                        {t.channel}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-[11px] text-slate-500 whitespace-nowrap tabular-nums" title={new Date(t.created_at).toLocaleString()}>
                      {new Date(t.created_at).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>''',
        t,
        count=1,
    )
    if n:
        t = t2
        print("channel+submitted ok")
    else:
        print("channel cell miss")

    t = "/* tickets-table-v2 */\n" + t
    tp.write_text(t)
    print("tp done")

print("done")
