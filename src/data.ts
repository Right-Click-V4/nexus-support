import type { Ticket, Agent, Customer, Branch } from './types';

export const pulseData = [
  { time: '00:00', tickets: 12 },
  { time: '02:00', tickets: 8 },
  { time: '04:00', tickets: 5 },
  { time: '06:00', tickets: 9 },
  { time: '08:00', tickets: 22 },
  { time: '10:00', tickets: 38 },
  { time: '12:00', tickets: 45 },
  { time: '14:00', tickets: 52 },
  { time: '16:00', tickets: 41 },
  { time: '18:00', tickets: 33 },
  { time: '20:00', tickets: 28 },
  { time: '22:00', tickets: 19 },
];

/** Offline fallback roster — empty so demo mode does not invent a fake team. */
export const INITIAL_AGENTS: Agent[] = [];

export const INITIAL_BRANCHES: Branch[] = [
  {
    id: 'b1',
    name: 'CIRIAN BRANCH',
    email: 'cirian@company.com',
    members: [
      { id: 'm1', name: 'Ana Reyes', email: 'ana.reyes@company.com', role: 'Branch lead' },
      { id: 'm2', name: 'Ben Cruz', email: 'ben.cruz@company.com', role: 'Staff' },
    ],
  },
  {
    id: 'b2',
    name: 'ORMOC BRANCH',
    email: 'ormoc@company.com',
    members: [
      { id: 'm3', name: 'Carla Santos', email: 'carla.santos@company.com', role: 'Branch lead' },
      { id: 'm4', name: 'Diego Lim', email: 'diego.lim@company.com', role: 'Staff' },
    ],
  },
  {
    id: 'b3',
    name: 'MAASIN BRANCH',
    email: 'maasin@company.com',
    members: [
      { id: 'm5', name: 'Elena Flores', email: 'elena.flores@company.com', role: 'Branch lead' },
    ],
  },
  {
    id: 'b4',
    name: 'SOGOD BRANCH',
    email: 'sogod@company.com',
    members: [
      { id: 'm6', name: 'Felix Tan', email: 'felix.tan@company.com', role: 'Branch lead' },
      { id: 'm7', name: 'Gina Ong', email: 'gina.ong@company.com', role: 'Staff' },
    ],
  },
  {
    id: 'b5',
    name: 'AVENIDA BRANCH',
    email: 'avenida@company.com',
    members: [
      { id: 'm8', name: 'Harold Yu', email: 'harold.yu@company.com', role: 'Branch lead' },
    ],
  },
  {
    id: 'b6',
    name: 'ABUCAY BRANCH',
    email: 'abucay@company.com',
    members: [
      { id: 'm9', name: 'Irene Valdez', email: 'irene.valdez@company.com', role: 'Branch lead' },
    ],
  },
];

/** Real people (end-users) — each belongs to a branch workplace */
export const INITIAL_CUSTOMERS: Customer[] = [
  { id: 'c1', name: 'Ana Reyes', email: 'ana.reyes@company.com', company: 'Acme Retail', role: 'Customer', branch: 'CIRIAN BRANCH' },
  { id: 'c2', name: 'Ben Cruz', email: 'ben.cruz@company.com', company: 'Acme Retail', role: 'Customer', branch: 'CIRIAN BRANCH' },
  { id: 'c3', name: 'Carla Santos', email: 'carla.santos@company.com', company: 'Ormoc Trading', role: 'Customer', branch: 'ORMOC BRANCH' },
  { id: 'c4', name: 'Diego Lim', email: 'diego.lim@company.com', company: 'Ormoc Trading', role: 'Customer', branch: 'ORMOC BRANCH' },
  { id: 'c5', name: 'Elena Flores', email: 'elena.flores@company.com', company: 'Maasin Co', role: 'Customer', branch: 'MAASIN BRANCH' },
  { id: 'c6', name: 'Felix Tan', email: 'felix.tan@company.com', company: 'Sogod Group', role: 'Customer', branch: 'SOGOD BRANCH' },
  { id: 'c7', name: 'Gina Ong', email: 'gina.ong@company.com', company: 'Sogod Group', role: 'Customer', branch: 'SOGOD BRANCH' },
  { id: 'c8', name: 'Harold Yu', email: 'harold.yu@company.com', company: 'Avenida Ltd', role: 'Customer', branch: 'AVENIDA BRANCH' },
  { id: 'c9', name: 'Irene Valdez', email: 'irene.valdez@company.com', company: 'Abucay Inc', role: 'Customer', branch: 'ABUCAY BRANCH' },
];

export const INITIAL_TICKETS: Ticket[] = [
  { id: 'NX-2841', title: 'Billing mismatch on enterprise subscription', description: 'Customer was charged twice for the annual plan.', priority: 'high', status: 'open', channel: 'email', assignee_id: '1', customer_name: 'Ana Reyes', customer_email: 'ana.reyes@company.com', branch: 'CIRIAN BRANCH', created_at: new Date(Date.now() - 86400000).toISOString() },
  { id: 'NX-2839', title: 'SSO login failing for Okta users', description: 'Users redirected to error page after Okta auth.', priority: 'critical', status: 'open', channel: 'chat', assignee_id: '2', customer_name: 'Ben Cruz', customer_email: 'ben.cruz@company.com', branch: 'CIRIAN BRANCH', created_at: new Date(Date.now() - 18000000).toISOString() },
  { id: 'NX-2837', title: 'API rate limit exceeded unexpectedly', description: 'Production API hitting 429s under normal load.', priority: 'high', status: 'pending', channel: 'portal', assignee_id: '3', customer_name: 'Carla Santos', customer_email: 'carla.santos@company.com', branch: 'ORMOC BRANCH', created_at: new Date(Date.now() - 28800000).toISOString() },
  { id: 'NX-2835', title: 'Feature request: bulk ticket export', description: 'Need CSV/JSON export for closed tickets.', priority: 'low', status: 'new', channel: 'email', customer_name: 'Diego Lim', customer_email: 'diego.lim@company.com', branch: 'ORMOC BRANCH', created_at: new Date(Date.now() - 36000000).toISOString() },
  { id: 'NX-2832', title: 'Mobile app crashes on iOS 18', description: 'Crash on launch after updating to iOS 18.1.', priority: 'critical', status: 'open', channel: 'chat', assignee_id: '4', customer_name: 'Elena Flores', customer_email: 'elena.flores@company.com', branch: 'MAASIN BRANCH', created_at: new Date(Date.now() - 43200000).toISOString() },
  { id: 'NX-2828', title: 'Incorrect tax calculation on invoice', description: 'VAT applied incorrectly for EU customers.', priority: 'medium', status: 'on-hold', channel: 'email', assignee_id: '5', customer_name: 'Felix Tan', customer_email: 'felix.tan@company.com', branch: 'SOGOD BRANCH', created_at: new Date(Date.now() - 172800000).toISOString() },
  { id: 'NX-2825', title: 'Password reset emails not arriving', description: 'Multiple users report missing reset links.', priority: 'high', status: 'open', channel: 'portal', assignee_id: '6', customer_name: 'Gina Ong', customer_email: 'gina.ong@company.com', branch: 'SOGOD BRANCH', created_at: new Date(Date.now() - 259200000).toISOString() },
  { id: 'NX-2820', title: 'Dashboard widgets not loading', description: 'Blank widgets after latest deploy.', priority: 'medium', status: 'resolved', channel: 'chat', assignee_id: '1', customer_name: 'Harold Yu', customer_email: 'harold.yu@company.com', branch: 'AVENIDA BRANCH', created_at: new Date(Date.now() - 345600000).toISOString() },
];

export function nextTicketId(existing: Ticket[]): string {
  const nums = existing.map((t) => parseInt(t.id.replace('NX-', ''), 10)).filter((n) => !isNaN(n));
  const max = nums.length ? Math.max(...nums) : 2800;
  return `NX-${max + 1}`;
}
