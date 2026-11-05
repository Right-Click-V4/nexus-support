/* status-desk-publish-v1 */
/* automations-load-v2 */
/* status-db-normalize-v1 */
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
import { publishDeskPresence } from '../lib/deskPresence';
import { useAuth } from './AuthContext';
import { notifyAgents, notifyCustomer } from '../lib/agentNotify';
import { pushAudit } from '../lib/audit';
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

function sbTimeout<T>(p: PromiseLike<T>, ms = 8000): Promise<T> {
  return Promise.race([
    Promise.resolve(p as PromiseLike<T>).then((v) => v as T),
    new Promise<T>((_, reject) => {
      window.setTimeout(() => reject(new Error('Request timed out. Please try again.')), ms);
    }),
  ]);
}

/** Map UI statuses to values accepted by tickets_status_check on Supabase. */
function statusForDb(status: string | undefined | null): string {
  const s = String(status || 'open').toLowerCase().trim();
  if (s === 'closed') return 'resolved';
  if (s === 'on_hold' || s === 'onhold') return 'on-hold';
  if (s === 'new') return 'open';
  if (['open', 'pending', 'resolved', 'on-hold'].includes(s)) return s;
  return 'open';
}

const STORAGE_KEY = 'nexus-tickets-v1';
const AUTO_LS = 'nexus-auto-v1';

const TICKET_COLS =
  'id, title, description, priority, status, channel, assignee_id, customer_name, customer_email, branch, tags, created_at, updated_at, sla_due_at, first_response_at, deleted_at, notes, messages, attachments';
const AGENT_COLS =
  'id, name, initials, role, status, status_message, last_seen_at, status_emoji, color, email, user_id, is_admin, avatar_url, branch, approval_status, phone, bio, timezone, skills, signature';
const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';

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
        withTimeout(
          supabase.from('tickets').select(TICKET_COLS).order('created_at', { ascending: false }).limit(120),
          5000,
        ),
        withTimeout(supabase.from('agents').select(AGENT_COLS).limit(80), 4000),
        withTimeout(supabase.from('customers').select(CUSTOMER_COLS).limit(200), 4000),
      ]);
      const agentRows = aRes && typeof aRes === 'object' && 'data' in aRes ? (aRes as { data: Agent[] | null }).data : null;
      const customerRows = cRes && typeof cRes === 'object' && 'data' in cRes ? (cRes as { data: Customer[] | null }).data : null;
      const ticketRows = tRes && typeof tRes === 'object' && 'data' in tRes ? (tRes as { data: Ticket[] | null }).data : null;
      const agentList = filterAgents((agentRows || []).map(hydrateAvatar));
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
      /* never leave UI stuck */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (!user || !supabase || accountRole === 'customer') {
      if (accountRole === 'customer') setCurrentAgent(null);
      if (!user) setCurrentAgent(null);
      return;
    }
    let cancelled = false;
    (async () => {
      const { data: existing } = await supabase
        .from('agents')
        .select(AGENT_COLS)
        .eq('user_id', user.id)
        .maybeSingle();
      if (cancelled) return;
      if (existing) {
        if ((existing as Agent).approval_status && (existing as Agent).approval_status !== 'approved') {
          setCurrentAgent(null);
          return;
        }
        setCurrentAgent(hydrateAvatar(existing as Agent));
        return;
      }
      if (user.email) {
        const { data: byEmail } = await supabase
          .from('agents')
          .select(AGENT_COLS)
          .eq('email', user.email)
          .maybeSingle();
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
    const poll = window.setInterval(soft, 60_000);
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
    const local = loadAutomationsLocal();
    if (supabase) {
      try {
        const res = await sbTimeout(
          supabase
            .from('automations')
            .select(
              'id, name, enabled, active, trigger, condition_field, condition_op, condition_value, action, action_value, actions, description',
            )
            .limit(80),
          4000,
        );
        const data =
          res && typeof res === 'object' && 'data' in res
            ? (res as { data: Automation[] | null }).data
            : null;
        if (data?.length) {
          const byId = new Map<string, Automation>();
          for (const r of data as Automation[]) if (r?.id) byId.set(String(r.id), r);
          for (const r of local) if (r?.id && !byId.has(String(r.id))) byId.set(String(r.id), r);
          return Array.from(byId.values());
        }
      } catch {
        /* fall through to local */
      }
    }
    return local;
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
        rules,
      );
      if (applied.priority) priority = applied.priority;
      if (applied.tagAdds?.length) tags = Array.from(new Set([...tags, ...applied.tagAdds]));
    } catch {
      /* rules optional */
    }
    const sla_due_at = computeSlaDue(priority, now);
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
        status: statusForDb(ticket.status),
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
        const error =
          ins && typeof ins === 'object' && 'error' in ins
            ? (ins as { error: { message?: string } | null }).error
            : null;
        if (error) {
          delete payload.tags;
          const ins2 = await sbTimeout(supabase.from('tickets').insert(payload), 10000);
          const e2 =
            ins2 && typeof ins2 === 'object' && 'error' in ins2
              ? (ins2 as { error: { message?: string } | null }).error
              : null;
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
      detail: ticket.title,
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
    const payload: Record<string, unknown> = { ...updates, updated_at: new Date().toISOString() };
    if (payload.status != null) payload.status = statusForDb(String(payload.status));
    setTickets((prev) =>
      prev.map((row) =>
        row.id === id
          ? {
              ...row,
              ...updates,
              status: (updates.status ? statusForDb(updates.status) : row.status) as Ticket['status'],
              updated_at: payload.updated_at as string,
              assignee:
                updates.assignee_id !== undefined
                  ? agents.find((a) => a.id === updates.assignee_id) || null
                  : row.assignee,
            }
          : row,
      ),
    );
    if (supabase) {
      try {
        const up = await sbTimeout(supabase.from('tickets').update(payload).eq('id', id), 10000);
        const error =
          up && typeof up === 'object' && 'error' in up
            ? (up as { error: { message?: string } | null }).error
            : null;
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
      if (!opts?.silent && ticket?.customer_email) {
        void notifyCustomer({
          email: ticket.customer_email,
          title: 'Ticket updated',
          body: `${ticket.title || id} was updated by support.`,
          link: 'mytickets',
        });
      }
    }
  };

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
    pushAudit({
      entity: 'ticket',
      entity_id: id,
      action: 'hard_delete',
      actor: currentAgent?.name || user?.email || 'Agent',
    });
  };

  const addNote = async (ticketId: string, text: string, author?: string) => {
    const ticket = tickets.find((t) => t.id === ticketId);
    if (!ticket) return;
    const note: TicketNote = {
      id: `n-${Date.now()}`,
      text,
      author: author || currentAgent?.name || 'Agent',
      created_at: new Date().toISOString(),
    };
    await updateTicket(ticketId, { notes: [...(ticket.notes || []), note] }, { silent: true });
  };

  const addMessage = async (ticketId: string, text: string, kind: 'public' | 'internal' = 'public') => {
    const ticket = tickets.find((t) => t.id === ticketId);
    if (!ticket) return;
    const msg: TicketMessage = {
      id: `m-${Date.now()}`,
      ticket_id: ticketId,
      author: currentAgent?.name || user?.email || 'Agent',
      text,
      kind,
      created_at: new Date().toISOString(),
    };
    const messages = [...(ticket.messages || []), msg];
    const updates: Partial<Ticket> = { messages };
    if (!ticket.first_response_at && kind === 'public') {
      updates.first_response_at = msg.created_at;
    }
    await updateTicket(ticketId, updates, { silent: kind === 'internal' });
  };

  const updateAgentStatus = async (
    status: AgentStatus,
    statusMessage?: string | null,
    statusEmoji?: string | null,
  ) => {
    if (!currentAgent || !supabase) return;
    const patch: Record<string, unknown> = {
      status,
      last_seen_at: new Date().toISOString(),
    };
    if (statusMessage !== undefined) patch.status_message = statusMessage;
    if (statusEmoji !== undefined) patch.status_emoji = statusEmoji;
    await supabase.from('agents').update(patch).eq('id', currentAgent.id);
    const next = { ...currentAgent, ...patch } as Agent;
    setCurrentAgent(next);
    setAgents((prev) => prev.map((a) => (a.id === next.id ? next : a)));
    void publishDeskPresence(next);
  };

  const touchPresence = async () => {
    if (!currentAgent || !supabase) return;
    const now = Date.now();
    const g = globalThis as unknown as { __nexusTouchAt?: number };
    if (g.__nexusTouchAt && now - g.__nexusTouchAt < 60_000) return;
    g.__nexusTouchAt = now;
    const last_seen_at = new Date().toISOString();
    try {
      await supabase.from('agents').update({ last_seen_at }).eq('id', currentAgent.id);
      setCurrentAgent((prev) => (prev ? { ...prev, last_seen_at } : prev));
    } catch {
      /* ignore */
    }
  };

  const findTicket = (id: string, email?: string) => {
    const t = tickets.find((x) => x.id === id);
    if (!t) return undefined;
    if (email && t.customer_email && t.customer_email.toLowerCase() !== email.toLowerCase()) return undefined;
    return t;
  };

  const ticketsForEmail = (email: string) =>
    tickets.filter((t) => (t.customer_email || '').toLowerCase() === email.toLowerCase());

  const setAgentAdmin = async (agentId: string, is_admin: boolean) => {
    if (!supabase) return;
    await supabase.from('agents').update({ is_admin }).eq('id', agentId);
    setAgents((prev) => prev.map((a) => (a.id === agentId ? { ...a, is_admin } : a)));
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
