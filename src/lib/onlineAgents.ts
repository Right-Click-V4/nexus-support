/** Shared filter: which agents are truly online for customer Live Chat. */
import type { DeskAgent } from './deskPresence';

const DEMO_NAMES = new Set([
  'sarah chen', 'marcus reed', 'aisha lane', 'tomás garcía', 'tomas garcia',
  'rachel kim', 'david okonkwo',
]);

const isDemo = (id: string, name: string) =>
  ['1', '2', '3', '4', '5', '6'].includes(String(id)) || DEMO_NAMES.has((name || '').toLowerCase());

/** Must match deskPresence LIVE_MS — only recent heartbeats count. */
export const ONLINE_WINDOW_MS = 90_000;

export type OnlineAgentRow = {
  id: string;
  name: string;
  status: string;
  avatar_url?: string | null;
  initials?: string;
  color?: string;
  last_seen_at?: string | null;
};

export function computeOnlineAgents(
  agents: Array<{
    id: string;
    name?: string;
    status?: string;
    approval_status?: string | null;
    avatar_url?: string | null;
    initials?: string;
    color?: string;
    last_seen_at?: string | null;
  }> | null | undefined,
  deskAgents: DeskAgent[] | null | undefined,
  now = Date.now(),
): OnlineAgentRow[] {
  const byId = new Map<string, OnlineAgentRow>();

  // 1) Realtime / local desk heartbeats (open agent desk tab)
  for (const d of deskAgents || []) {
    if (isDemo(String(d.id), d.name || '')) continue;
    const status = (d.status || 'online').toLowerCase();
    if (status === 'offline' || status === '') continue;
    if (!d.at || now - d.at > ONLINE_WINDOW_MS) continue;
    byId.set(String(d.id), {
      id: d.id,
      name: d.name || 'Agent',
      status,
      avatar_url: d.avatar_url ?? null,
      initials: d.initials,
      color: d.color,
      last_seen_at: new Date(d.at).toISOString(),
    });
  }

  // 2) Agents table: only if last_seen_at is fresh (never trust status alone)
  for (const a of agents || []) {
    if (isDemo(String(a.id), a.name || '')) continue;
    const st = (a.approval_status || 'approved').toLowerCase();
    if (st && st !== 'approved' && st !== 'active') continue;
    const status = (a.status || 'offline').toLowerCase();
    if (status === 'offline' || status === '') continue;
    const seen = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
    const fresh = seen > 0 && !Number.isNaN(seen) && now - seen <= ONLINE_WINDOW_MS;
    if (!fresh) continue;
    if (byId.has(String(a.id))) continue;
    byId.set(String(a.id), {
      id: String(a.id),
      name: a.name || 'Agent',
      status,
      avatar_url: a.avatar_url,
      initials: a.initials,
      color: a.color,
      last_seen_at: a.last_seen_at,
    });
  }

  return Array.from(byId.values()).sort((a, b) =>
    (a.name || '').localeCompare(b.name || ''),
  );
}
