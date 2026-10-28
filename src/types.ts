export type Priority = 'critical' | 'high' | 'medium' | 'low';
export type Status = 'new' | 'open' | 'pending' | 'resolved' | 'on-hold' | 'closed';
export type Channel = 'email' | 'chat' | 'phone' | 'portal' | 'social';
export type AgentStatus = 'online' | 'busy' | 'away' | 'offline';

export interface Agent {
  id: string;
  name: string;
  initials: string;
  role: string;
  status: AgentStatus;
  color: string;
  email?: string;
  user_id?: string | null;
  phone?: string;
  bio?: string;
  timezone?: string;
  is_admin?: boolean;
  avatar_url?: string | null;
  branch?: string | null;
  skills?: string[];
  working_hours?: string;
  ooo?: boolean;
  signature?: string;
  /** Account approval for self-signup agents (not presence status) */
  approval_status?: 'pending' | 'approved' | 'rejected' | null;
}

export interface BranchMember {
  id: string;
  name: string;
  email?: string;
  role?: string;
}

export interface Branch {
  id: string;
  name: string;
  email?: string;
  members: BranchMember[];
}

export interface Customer {
  id: string;
  name: string;
  email?: string;
  company?: string;
  role?: string;
  branch?: string | null;
  status?: 'pending' | 'approved' | 'rejected' | null;
  created_at?: string;
}

export interface TicketMessage {
  id: string;
  ticket_id?: string;
  author: string;
  text: string;
  kind: 'public' | 'internal';
  created_at: string;
}

export interface TicketNote {
  id: string;
  text: string;
  author: string;
  created_at: string;
}

export interface TicketAttachment {
  id: string;
  name: string;
  size: number;
  mime: string;
  url: string;
  created_at: string;
  uploaded_by?: string;
}

export const MAX_ATTACHMENT_BYTES = 8_000_000;
export const MAX_CHAT_FILE_BYTES = 8_000_000;

export interface Ticket {
  id: string;
  title: string;
  description?: string;
  priority: Priority;
  status: Status;
  channel: Channel;
  assignee_id?: string | null;
  assignee?: Agent | null;
  customer_name: string;
  customer_email?: string;
  branch?: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
  sla_due_at?: string | null;
  first_response_at?: string | null;
  deleted_at?: string | null;
  messages?: TicketMessage[];
  notes?: TicketNote[];
  attachments?: TicketAttachment[];
  csat?: number | null;
}

const SLA_HOURS: Record<Priority, number> = {
  critical: 4,
  high: 8,
  medium: 24,
  low: 72,
};

export function computeSlaDue(priority: Priority, fromIso?: string): string {
  const start = fromIso ? new Date(fromIso).getTime() : Date.now();
  const hours = SLA_HOURS[priority] ?? 24;
  return new Date(start + hours * 3_600_000).toISOString();
}

export function ticketBranch(t: Pick<Ticket, 'branch' | 'customer_name'>): string {
  if (t.branch && t.branch.trim()) return t.branch.trim();
  return '';
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  body: string;
  category?: string;
  tags?: string[];
  updated_at?: string;
  published?: boolean;
}

export interface ChatMessage {
  id: string;
  conversation_id?: string;
  sender: 'agent' | 'customer';
  text: string;
  created_at: string;
  author?: string;
  is_agent?: boolean;
  file_url?: string;
  file_name?: string;
}

export interface ChatConversation {
  id: string;
  customer_name: string;
  customer_email?: string;
  status: 'open' | 'closed' | 'waiting' | 'active' | 'ended';
  agent_id?: string;
  branch?: string;
  ticket_id?: string;
  preview?: string;
  unread?: number;
  created_at: string;
  updated_at?: string;
  messages?: ChatMessage[];
}

export interface AppNotification {
  id: string;
  title: string;
  body?: string;
  read?: boolean;
  created_at: string;
  type?: string;
  link?: string;
  agent_id?: string;
  user_id?: string;
}

export interface Announcement {
  id: string;
  title: string;
  body: string;
  active?: boolean;
  severity?: 'info' | 'warning' | 'critical';
  /** Where it appears on the Customer Portal: marquee banner, Overview card, or both */
  channel?: 'marquee' | 'portal' | 'both';
  created_at?: string;
}

export interface Automation {
  id: string;
  name: string;
  trigger: string;
  action: string;
  active?: boolean;
  enabled?: boolean;
  description?: string;
  condition_field?: string;
  condition_op?: string;
  condition_value?: string;
  action_value?: string;
}

export interface CannedResponse {
  id: string;
  title: string;
  body: string;
  shortcut?: string;
}

export interface Survey {
  id: string;
  ticket_id?: string;
  score: number;
  comment?: string;
  customer_name?: string;
  created_at?: string;
}

export type SurveyResponse = Survey;

export interface QualityReview {
  id: string;
  ticket_id?: string;
  score: number;
  notes?: string;
  reviewer?: string;
  agent_name?: string;
  created_at?: string;
}

export interface SupportForm {
  id: string;
  name: string;
  description?: string;
  fields: { id: string; label: string; type: string; required?: boolean }[];
  active: boolean;
}

export type FormDef = SupportForm;

export interface FormField {
  id: string;
  label: string;
  type: string;
  required?: boolean;
  options?: string[];
}

export interface ReleaseNote {
  id: string;
  version: string;
  title: string;
  notes: string;
  released_at: string;
}

export type Release = ReleaseNote;

export interface AuditEntry {
  id: string;
  entity: string;
  entity_id: string;
  action: string;
  detail?: string;
  actor?: string;
  created_at: string;
}
