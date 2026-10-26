export type Priority = 'critical' | 'high' | 'medium' | 'low';
export type Status = 'new' | 'open' | 'pending' | 'resolved' | 'on-hold';
export type Channel = 'email' | 'chat' | 'phone' | 'portal' | 'social';
export type AgentStatus = 'online' | 'busy' | 'away' | 'offline';

export interface Agent {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  status: AgentStatus;
  role?: string;
  team?: string;
}

export interface Ticket {
  id: string;
  subject: string;
  description?: string;
  status: Status;
  priority: Priority;
  channel?: Channel;
  customer_name?: string;
  customer_email?: string;
  assignee_id?: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
  branch?: string;
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  category: string;
  body: string;
  published?: boolean;
  updated_at?: string;
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'agent' | 'customer' | 'system';
  created_at: string;
}

export interface ChatConversation {
  id: string;
  customer_name: string;
  customer_email?: string;
  status: 'waiting' | 'active' | 'ended';
  preview?: string;
  unread?: number;
  messages?: ChatMessage[];
  branch?: string;
  ticket_id?: string;
  updated_at?: string;
  created_at?: string;
}

export interface AppNotification {
  id: string;
  title: string;
  body?: string;
  read?: boolean;
  created_at: string;
}

export interface CannedResponse {
  id: string;
  title: string;
  body: string;
  shortcut?: string;
}

export interface SurveyResponse {
  id: string;
  ticket_id?: string;
  score: number;
  comment?: string;
  created_at: string;
}

export interface QualityReview {
  id: string;
  ticket_id?: string;
  score: number;
  notes?: string;
  reviewer?: string;
  created_at: string;
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

export interface FormField {
  id: string;
  label: string;
  type: string;
  required?: boolean;
  options?: string[];
}

export interface FormDef {
  id: string;
  name: string;
  description?: string;
  fields: FormField[];
  active?: boolean;
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
