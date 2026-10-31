/* login-speed-tickets-v1 */
/* touch-presence-status-v1 */
/* no-demo-agents-v1 */
/* status-fetch-resilient-v1 */
/* ticket-ops-timeout-v1 */
/* tickets-presence-fix-v1 */
/* status-emoji-ctx-v1 */
/* agent-presence-ctx-v1 */
/* no-agent-toast-on-save-v1 */
/* update-silent-notify-v1 */
/* no-auto-assign-v1 */
/* customer-new-expand-v1 */
// trash-confirm-v1
// status-outline-v1
// ticket-unread-v1
// tickets-sync-v1
// tickets-noflicker-v1
import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import type { Ticket, Agent, Customer, Priority, Channel, TicketNote, TicketMessage, AgentStatus, Automation } from '../types';
import { computeSlaDue } from '../types';
import { INITIAL_TICKETS, INITIAL_AGENTS, INITIAL_CUSTOMERS, nextTicketId } from '../data';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { useAuth } from './AuthContext';
import { notifyAgents, notifyCustomer } from '../lib/agentNotify';
import { pushAudit } from '../lib/audit';
import { pickAssignee } from '../lib/assign';
import { applyTicketCreatedAutomations } from '../lib/automations';

interface CreateTicketInput {
  title: string;
  description?: string;
  priority: Priority;
  channel: Channel;
  customer_name: string;
  customer_email?: string;
  branch?: string;
  assignee_id?: string;
  tags?: string[];
}

interface TicketContextValue {
  tickets: Ticket[];
  agents: Agent[];
  customers: Customer[];
  loading: boolean;
  usingSupabase: boolean;
  currentAgent: Agent | null;
  createTicket: (data: CreateTicketInput) => Promise<Ticket>;
  updateTicket: (
    id: string,
    updates: Partial<
      Pick<
        Ticket,
        | 'status'
        | 'priority'
        | 'assignee_id'
        | 'title'
        | 'description'
        | 'notes'
        | 'messages'
        | 'first_response_at'
        | 'branch'
        | 'attachments'
        | 'deleted_at'
        | 'tags'
      >
    >,
    opts?: { silent?: boolean },
  ) => Promise<void>;
  deleteTicket: (id: string) => Promise<void>;
  softDeleteTicket: (id: string) => Promise<void>;
  addNote: (ticketId: string, text: string, author?: string) => Promise<void>;
  addMessage: (ticketId: string, text: string, kind?: 'public' | 'internal') => Promise<void>;
  updateAgentStatus: (status: AgentStatus, statusMessage?: string | null, statusEmoji?: string | null) => Promise<void>;
  touchPresence: () => Promise<void>;
  findTicket: (id: string, email?: string) => Ticket | undefined;
  ticketsForEmail: (email: string) => Ticket[];
  setAgentAdmin: (agentId: string, is_admin: boolean) => Promise<void>;
  refresh: (opts?: { silent?: boolean }) => Promise<void>;
}

const TicketContext = createContext<TicketContextValue | null>(null);

/** Never hang UI on a slow/hung Supabase request */
function sbTimeout<T>(p: PromiseLike<T>, ms = 8000): Promise<T> {
  return Promise.race([
    Promise.resolve(p as PromiseLike<T>).then((v) => v as T),
    new Promise<T>((_, reject) => {
      window.setTimeout(() => reject(new Error('Request timed out. Please try again.')), ms);
    }),
  ]);
}

const STORAGE_KEY = 'nexus-tickets-v1';
const AUTO_LS = 'nexus-auto-v1';

function loadLocal(): Ticket[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Ticket[];
  } catch {}
  return INITIAL_TICKETS;
}

function saveLocal(tickets: Ticket[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets));
  } catch {}
}

function loadAutomationsLocal(): Automation[] {
  try {
    const raw = localStorage.getItem(AUTO_LS);
    if (raw) return JSON.parse(raw) as Automation[];
  } catch {}
  return [];
}

function hydrateAvatar(agent: Agent): Agent {
  if (agent.avatar_url) return agent;
  try {
    const local = localStorage.getItem(`nexus-avatar-${agent.id}`);
    if (local) return { ...agent, avatar_url: local };
  } catch {}
  return agent;
}

function initialsFromName(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return 'AG';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/** Keep only real agents for team UI (hide customer-role rows + duplicates). */
function filterAgents(list: Agent[]): Agent[] {
  const DEMO_IDS = new Set(['1', '2', '3', '4', '5', '6']);
  const DEMO_NAMES = new Set([
    'sarah chen', 'marcus reed', 'aisha lane', 'tomás garcía', 'tomas garcia',
    'rachel kim', 'david okonkwo',
  ]);
  const seen = new Set<string>();
  return list.filter((a) => {
    if (isSupabaseConfigured) {
      if (DEMO_IDS.has(String(a.id))) return false;
      if (DEMO_NAMES.has((a.name || '').toLowerCase())) return false;
    }
    const key = (a.email || a.name || a.id).toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function TicketProvider({ children }: { children: ReactNode }) {
  const { user, accountRole } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>(() => (isSupabaseConfigured ? [] : loadLocal()));
  const [agents, setAgents] = useState<Agent[]>(() => (isSupabaseConfigured ? [] : INITIAL_AGENTS));
  const [customers, setCustomers] = useState<Customer[]>(INITIAL_CUSTOMERS);
  const [loading, setLoading] = useState(isSupabaseConfigured);
  const [currentAgent, setCurrentAgent] = useState<Agent | null>(null);
  const usingSupabase = isSupabaseConfigured;

  const refresh = useCallback(async (opts?: { silent?: boolean }) => {
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
        withTimeout(supabase.from('tickets').select('*').order('created_at', { ascending: false }), 5000),
        withTimeout(supabase.from('agents').select('*'), 4000),
        withTimeout(supabase.from('customers').select('*'), 4000),
      ]);
      const agentRows = aRes && typeof aRes === 'object' && 'data' in aRes ? (aRes as { data: Agent[] | null }).data : null;
      const customerRows = cRes && typeof cRes === 'object' && 'data' in cRes ? (cRes as { data: Customer[] | null }).data : null;
      const ticketRows = tRes && typeof tRes === 'object' && 'data' in tRes ? (tRes as { data: Ticket[] | null }).data : null;
      const agentList = filterAgents((agentRows || []).map(hydrateAvatar)).filter(
        (a) => !['1','2','3','4','5','6'].includes(String(a.id)) &&
          !['Sarah Chen','Marcus Reed','Aisha Lane','Tomás García','Tomas Garcia','Rachel Kim','David Okonkwo'].includes(a.name),
      );
      if (aRes && typeof aRes === 'object' && 'data' in aRes) setAgents(agentList);
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
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    // Customers must never be auto-inserted into agents table
    if (!user || !supabase || accountRole === 'customer') {
      if (accountRole === 'customer') setCurrentAgent(null);
      if (!user) setCurrentAgent(null);
      return;
    }
    let cancelled = false;
    (async () => {
      const { data: existing } = await supabase.from('agents').select('*').eq('user_id', user.id).maybeSingle();
      if (cancelled) return;
      if (existing) {
        // Only active workspace agent if approved
        if ((existing as Agent).approval_status && (existing as Agent).approval_status !== 'approved') {
          setCurrentAgent(null);
          return;
        }
        setCurrentAgent(hydrateAvatar(existing as Agent));
        return;
      }
      if (user.email) {
        const { data: byEmail } = await supabase.from('agents').select('*').eq('email', user.email).maybeSingle();
        if (byEmail && !cancelled) {
          if ((byEmail as Agent).approval_status && (byEmail as Agent).approval_status !== 'approved') {
            setCurrentAgent(null);
            return;
          }
          await supabase.from('agents').update({ user_id: user.id }).eq('id', byEmail.id);
          const linked = hydrateAvatar({ ...byEmail, user_id: user.id } as Agent);
          setCurrentAgent(linked);
          setAgents((prev) => filterAgents(prev.map((a) => (a.id === linked.id ? linked : a))));
          return;
        }
      }
      // Do NOT auto-create agent rows — new accounts stay pending until admin approves
      // (created by signup trigger / AuthContext). Avoids bypassing Users → Pending.
      setCurrentAgent(null);
    })();
    return () => {
      cancelled = true;
    };
  }, [user, accountRole]);

  useEffect(() => {
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
  }, [refresh]);

  useEffect(() => {
    if (!isSupabaseConfigured && tickets.length) saveLocal(tickets);
  }, [tickets]);

  const loadRules = async (): Promise<Automation[]> => {
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
  };

  const createTicket = async (data: CreateTicketInput): Promise<Ticket> => {
    const id = nextTicketId(tickets);
    const now = new Date().toISOString();
    let priority = data.priority;
    let tags = [...(data.tags || [])];

    try {
      const rules = await loadRules();
      const applied = applyTicketCreatedAutomations(
        {
          title: data.title,
          description: data.description,
          priority: data.priority,
          branch: data.branch,
          customer_name: data.customer_name,
        },
        rules
      );
      if (applied.priority) priority = applied.priority;
      if (applied.tagAdds?.length) tags = Array.from(new Set([...tags, ...applied.tagAdds]));
    } catch {
      // rules optional
    }

    const sla_due_at = computeSlaDue(priority, now);
    // New tickets stay unassigned until an agent claims/assigns them
    const assigneeId = data.assignee_id || null;
    const ticket: Ticket = {
      id,
      title: data.title,
      description: data.description || '',
      priority,
      status: 'open',
      channel: data.channel,
      assignee_id: assigneeId,
      customer_name: data.customer_name,
      customer_email: data.customer_email || '',
      branch: data.branch?.trim() || undefined,
      tags: Array.from(new Set([...(tags || []), 'unread'])),
      created_at: now,
      updated_at: now,
      notes: [],
      messages: [],
      attachments: [],
      sla_due_at,
    };
    if (supabase) {
      const payload: Record<string, unknown> = {
        id: ticket.id,
        title: ticket.title,
        description: ticket.description,
        priority: ticket.priority,
        status: ticket.status,
        channel: ticket.channel,
        assignee_id: ticket.assignee_id,
        customer_name: ticket.customer_name,
        customer_email: ticket.customer_email,
        branch: ticket.branch || null,
        notes: ticket.notes,
        messages: ticket.messages,
        attachments: ticket.attachments,
        sla_due_at: ticket.sla_due_at,
        created_at: ticket.created_at,
        updated_at: ticket.updated_at,
        tags: ticket.tags,
      };
      try {
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
      void refresh({ silent: true });
    } else {
      setTickets((prev) => [ticket, ...prev]);
    }
    void notifyAgents({
      title: 'New ticket',
      body: `${ticket.id}: ${ticket.title} · ${ticket.customer_name}${ticket.channel ? ` (${ticket.channel})` : ''}`,
      link: 'tickets',
    });
    pushAudit({
      entity: 'ticket',
      entity_id: ticket.id,
      action: 'create',
      detail: `${ticket.title}${autoAssignee ? ` · assigned ${autoAssignee}` : ''}${priority !== data.priority ? ` · auto priority ${priority}` : ''}`,
      actor: currentAgent?.name || user?.email || 'Agent',
    });
    return ticket;
  };

  const updateTicket = async (
    id: string,
    updates: Partial<
      Pick<
        Ticket,
        | 'status'
        | 'priority'
        | 'assignee_id'
        | 'title'
        | 'description'
        | 'notes'
        | 'messages'
        | 'first_response_at'
        | 'branch'
        | 'attachments'
        | 'deleted_at'
        | 'tags'
      >
    >,
    opts?: { silent?: boolean },
  ) => {
    const ticket = tickets.find((t) => t.id === id);
    const payload = { ...updates, updated_at: new Date().toISOString() };
    setTickets((prev) =>
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
    }
    const changed = Object.keys(updates).filter((k) => k !== 'messages' && k !== 'notes' && k !== 'attachments');
    if (changed.length) {
      pushAudit({
        entity: 'ticket',
        entity_id: id,
        action: updates.deleted_at ? 'soft_delete' : updates.deleted_at === null ? 'restore' : 'update',
        detail: changed.map((k) => `${k}=${JSON.stringify((updates as Record<string, unknown>)[k])}`).join(', '),
        actor: currentAgent?.name || user?.email || 'Agent',
      });
      if (!opts?.silent) {
        if (ticket?.customer_email) {
          void notifyCustomer({
            email: ticket.customer_email,
            title: 'Ticket updated',
            body: `${ticket.title || id} was updated by support.`,
            link: 'mytickets',
          });
        }
      }
    }
  };


  const purgeExpiredTrash = async (list: Ticket[]) => {
    const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
    const expired = list.filter((t) => t.deleted_at && new Date(t.deleted_at).getTime() < cutoff);
    if (!expired.length) return;
    for (const t of expired) {
      try {
        if (supabase) {
          await supabase.from('tickets').delete().eq('id', t.id);
        }
      } catch (e) {
        console.warn('trash purge failed', t.id, e);
      }
    }
    if (expired.length) {
      setTickets((prev) => prev.filter((t) => !expired.some((e) => e.id === t.id)));
    }
  };


  useEffect(() => {
    if (!tickets.length) return;
    void purgeExpiredTrash(tickets);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickets.length]);

  const softDeleteTicket = async (id: string) => {
    await updateTicket(id, { deleted_at: new Date().toISOString() });
  };

  const deleteTicket = async (id: string) => {
    if (!currentAgent?.is_admin) {
      throw new Error('Only admins can permanently delete tickets');
    }
    if (supabase) {
      const { error } = await supabase.from('tickets').delete().eq('id', id);
      if (error) throw error;
      await refresh();
    } else {
      setTickets((prev) => prev.filter((t) => t.id !== id));
    }
    pushAudit({ entity: 'ticket', entity_id: id, action: 'hard_delete', actor: currentAgent?.name || user?.email || 'Agent' });
  };

  const authorName = () =>
    currentAgent?.name || (user?.user_metadata?.full_name as string | undefined) || user?.email?.split('@')[0] || 'Agent';

  const addNote = async (ticketId: string, text: string, author?: string) => {
    const note: TicketNote = {
      id: `n-${Date.now()}`,
      text: text.trim(),
      author: author || authorName(),
      created_at: new Date().toISOString(),
    };
    const ticket = tickets.find((t) => t.id === ticketId);
    if (!ticket) return;
    await updateTicket(ticketId, { notes: [...(ticket.notes || []), note] });
  };

  const addMessage = async (ticketId: string, text: string, kind: 'public' | 'internal' = 'public') => {
    const msg: TicketMessage = {
      id: `m-${Date.now()}`,
      text: text.trim(),
      author: authorName(),
      kind,
      created_at: new Date().toISOString(),
    };
    const ticket = tickets.find((t) => t.id === ticketId);
    if (!ticket) return;
    const messages = [...(ticket.messages || []), msg];
    const updates: Parameters<typeof updateTicket>[1] = { messages };
    if (!ticket.first_response_at && kind === 'public') updates.first_response_at = msg.created_at;
    if (kind === 'public') {
      updates.tags = Array.from(new Set([...(ticket.tags || []).filter((t) => t !== 'customer_unread'), 'customer_unread']));
    }
    await updateTicket(ticketId, updates);
    if (kind === 'public') {
      const assignee = ticket.assignee_id ? agents.find((a) => a.id === ticket.assignee_id) : null;
      void notifyAgents({
        title: 'Ticket reply',
        body: `${ticketId}: new message on “${ticket.title}”`,
        link: 'tickets',
        userId: (assignee as Agent & { user_id?: string })?.user_id || undefined,
      });

      if (ticket.customer_email) {
        void notifyCustomer({
          email: ticket.customer_email,
          title: 'New reply on your ticket',
          body: ticket.title || ticketId,
          link: 'mytickets',
        });
      }
    }
  };

  const updateAgentStatus = async (
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
    if (statusEmoji !== undefined) patch.status_emoji = statusEmoji;
    const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
    setCurrentAgent(next);
    setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    try {
      localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
    } catch { /* ignore */ }
    if (supabase) {
      try {
        let { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
        if (error) {
          const minimal: Record<string, unknown> = { status };
          if (statusMessage !== undefined) minimal.status_message = statusMessage;
          const retry = await supabase.from('agents').update(minimal).eq('id', currentAgent.id);
          error = retry.error;
        }
        if (error) {
          // non-fatal for UI presence
        }
      } catch {
        // Failed to fetch / network — local status still applied
      }
    }
  };

  const touchPresence = async () => {
    if (!currentAgent || !supabase) return;
    const status =
      (currentAgent.status || 'offline') === 'offline' ? 'online' : (currentAgent.status || 'online');
    const seen = new Date().toISOString();
    setCurrentAgent((prev) => (prev ? { ...prev, last_seen_at: seen, status } : prev));
    setAgents((prev) =>
      prev.map((a) => (a.id === currentAgent.id ? { ...a, last_seen_at: seen, status } : a)),
    );
    try {
      const { error } = await supabase
        .from('agents')
        .update({ last_seen_at: seen, status })
        .eq('id', currentAgent.id);
      if (error) {
        await supabase.from('agents').update({ status }).eq('id', currentAgent.id);
      }
    } catch {
      /* ignore */
    }
  };

  const findTicket = (id: string, email?: string) => {
    const t = tickets.find((x) => x.id.toLowerCase() === id.trim().toLowerCase());
    if (!t) return undefined;
    if (email && t.customer_email && t.customer_email.toLowerCase() !== email.toLowerCase()) return undefined;
    return t;
  };

  const ticketsForEmail = (email: string) =>
    tickets.filter((t) => (t.customer_email || '').toLowerCase() === email.toLowerCase());

  const setAgentAdmin = async (agentId: string, is_admin: boolean) => {
    if (supabase) {
      await supabase.from('agents').update({ is_admin }).eq('id', agentId);
      setAgents((prev) => prev.map((a) => (a.id === agentId ? { ...a, is_admin } : a)));
      if (currentAgent?.id === agentId) setCurrentAgent({ ...currentAgent, is_admin });
    } else {
      setAgents((prev) => prev.map((a) => (a.id === agentId ? { ...a, is_admin } : a)));
      if (currentAgent?.id === agentId) setCurrentAgent({ ...currentAgent, is_admin });
    }
  };

  return (
    <TicketContext.Provider
      value={{
        tickets,
        agents,
        customers,
        loading,
        usingSupabase,
        currentAgent,
        createTicket,
        updateTicket,
        deleteTicket,
        softDeleteTicket,
        addNote,
        addMessage,
        updateAgentStatus,
        touchPresence,
        findTicket,
        ticketsForEmail,
        setAgentAdmin,
        refresh,
      }}
    >
      {children}
    </TicketContext.Provider>
  );
}

export function useTickets() {
  const ctx = useContext(TicketContext);
  if (!ctx) throw new Error('useTickets must be used within TicketProvider');
  return ctx;
}
