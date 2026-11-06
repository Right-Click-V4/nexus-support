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

/** Offline fallback roster — keep empty so demo mode does not invent a fake team. */
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

export const INITIAL_CUSTOMERS: Customer[] = [];

export const INITIAL_TICKETS: Ticket[] = [];

export function nextTicketId(existing: Ticket[]): string {
  const nums = existing
    .map((t) => {
      const m = String(t.id).match(/(\d+)/);
      return m ? parseInt(m[1], 10) : 0;
    })
    .filter((n) => !Number.isNaN(n));
  const max = nums.length ? Math.max(...nums) : 1000;
  return `T-${max + 1}`;
}
