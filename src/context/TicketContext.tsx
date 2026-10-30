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
  const seen = new Set<string>();
  return list.filter((a) => {
    const role = (a.role || '').toLowerCase();
    if (role.includes('customer')) return false;
    const st = (a.approval_status || 'approved').toLowerCase();
    if (st === 'rejected' || st === 'pending') return false;
    const key = (a.email || a.name || a.id).toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function TicketProvider({ children }: { children: ReactNode }) {
  const { user, accountRole } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>(() => (isSupabaseConfigured ? [] : loadLocal()));
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
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
      const { data } = await supabase.from('automations').select('*');
      if (data?.length) return data as Automation[];
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
      const { error } = await supabase.from('tickets').insert(payload);
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
    if (supabase) {
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
    if (supabase) {
      let { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
      if (error) {
        const minimal: Record<string, unknown> = { status };
        if (statusMessage !== undefined) minimal.status_message = statusMessage;
        const retry = await supabase.from('agents').update(minimal).eq('id', currentAgent.id);
        error = retry.error;
      }
      if (error) throw error;
      const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
      try {
        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
      } catch { /* ignore */ }
    } else {
      const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
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
