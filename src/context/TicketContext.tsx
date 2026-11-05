/* status-desk-publish-v1 */
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
// egress-optimize-v1
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

const TICKET_COLS =
  'id, title, description, priority, status, channel, assignee_id, customer_name, customer_email, branch, tags, created_at, updated_at, sla_due_at, first_response_at, deleted_at, notes, messages, attachments';
const AGENT_COLS =
  'id, name, initials, role, status, status_message, last_seen_at, status_emoji, color, email, user_id, is_admin, avatar_url, branch, approval_status, phone, bio, timezone, skills, ooo, signature';
const CUSTOMER_COLS = 'id, name, email, company, role, branch, status, created_at';
