/** Desk presence: agent + customer share one Realtime channel. */
import { supabase, isSupabaseConfigured } from './supabase';

export type DeskAgent = {
  id: string;
  name: string;
  status: string;
  avatar_url?: string | null;
  initials?: string;
  color?: string;
  at: number;
};

const KEY = 'nexus-desk-presence-v1';
const BC = 'nexus-desk-presence';
const CHANNEL = 'desk-agents-v1';
const LIVE_MS = 120_000;

type PresenceChannel = ReturnType<NonNullable<typeof supabase>['channel']>;

let sharedCh: PresenceChannel | null = null;
let sharedReady: Promise<void> | null = null;
let trackedId: string | null = null;

function readLocal(): DeskAgent[] {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? (JSON.parse(raw) as DeskAgent[]) : [];
    const now = Date.now();
    return (list || []).filter((a) => a?.id && now - (a.at || 0) < LIVE_MS);
  } catch {
    return [];
  }
}

function writeLocal(list: DeskAgent[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      const bc = new BroadcastChannel(BC);
      bc.postMessage({ type: 'desk', list });
      bc.close();
    }
  } catch {
    /* ignore */
  }
  try {
    window.dispatchEvent(new CustomEvent('nexus-desk-presence', { detail: list }));
  } catch {
    /* ignore */
  }
}

function ensureChannel(): PresenceChannel | null {
  if (!isSupabaseConfigured || !supabase) return null;
  if (sharedCh) return sharedCh;
  try {
    sharedCh = supabase.channel(CHANNEL, {
      config: { presence: { key: 'desk' } },
    });
    sharedReady = new Promise((resolve) => {
      sharedCh!.subscribe((status) => {
        if (status === 'SUBSCRIBED') resolve();
      });
    });
    return sharedCh;
  } catch {
    sharedCh = null;
    return null;
  }
}

export async function publishDeskPresence(agent: {
  id: string;
  name: string;
  status?: string;
  avatar_url?: string | null;
  initials?: string;
  color?: string;
} | null) {
  if (!agent?.id) return;
  const statusRaw = (agent.status || 'online').toLowerCase();
  const status = statusRaw === 'offline' || statusRaw === '' ? 'online' : statusRaw;
  const row: DeskAgent = {
    id: agent.id,
    name: agent.name || 'Agent',
    status,
    avatar_url: agent.avatar_url || null,
    initials: agent.initials,
    color: agent.color,
    at: Date.now(),
  };

  const others = readLocal().filter((a) => a.id !== row.id);
  writeLocal([...others, row]);

  const ch = ensureChannel();
  if (!ch) return;
  try {
    await sharedReady;
    trackedId = agent.id;
    await ch.track({
      id: row.id,
      name: row.name,
      status: row.status,
      avatar_url: row.avatar_url,
      initials: row.initials,
      color: row.color,
      at: row.at,
    });
  } catch {
    /* never crash */
  }
}

export async function clearDeskPresence(agentId?: string | null) {
  if (agentId) {
    writeLocal(readLocal().filter((a) => a.id !== agentId));
  }
  if (sharedCh) {
    try {
      await sharedCh.untrack();
    } catch {
      /* ignore */
    }
  }
  if (agentId && trackedId === agentId) trackedId = null;
}

function fromPresence(): DeskAgent[] {
  if (!sharedCh) return [];
  try {
    const state = sharedCh.presenceState() as Record<string, Array<Partial<DeskAgent>>>;
    const now = Date.now();
    const out: DeskAgent[] = [];
    for (const metas of Object.values(state)) {
      for (const m of metas || []) {
        if (!m?.id) continue;
        out.push({
          id: String(m.id),
          name: String(m.name || 'Agent'),
          status: String(m.status || 'online'),
          avatar_url: (m.avatar_url as string) || null,
          initials: m.initials as string | undefined,
          color: m.color as string | undefined,
          at: Number(m.at || now),
        });
      }
    }
    return out;
  } catch {
    return [];
  }
}

export function getDeskPresence(): DeskAgent[] {
  const now = Date.now();
  const map = new Map<string, DeskAgent>();
  for (const a of [...fromPresence(), ...readLocal()]) {
    if (!a?.id) continue;
    if (now - (a.at || 0) > LIVE_MS) continue;
    if ((a.status || '').toLowerCase() === 'offline') continue;
    map.set(a.id, a);
  }
  return [...map.values()];
}

export function watchDeskPresence(onChange: (agents: DeskAgent[]) => void): () => void {
  const emit = () => {
    try {
      onChange(getDeskPresence());
    } catch {
      onChange(readLocal());
    }
  };
  emit();

  const ch = ensureChannel();
  if (ch) {
    try {
      try {
        ch.on('presence', { event: 'sync' }, emit);
        ch.on('presence', { event: 'join' }, emit);
        ch.on('presence', { event: 'leave' }, emit);
      } catch {
        /* already subscribed — polling still works */
      }
    } catch {
      /* ignore */
    }
  }

  const onEvt = () => emit();
  window.addEventListener('nexus-desk-presence', onEvt);
  window.addEventListener('storage', onEvt);
  let bc: BroadcastChannel | null = null;
  try {
    bc = new BroadcastChannel(BC);
    bc.onmessage = () => emit();
  } catch {
    /* ignore */
  }
  const tick = window.setInterval(emit, 2000);

  return () => {
    window.removeEventListener('nexus-desk-presence', onEvt);
    window.removeEventListener('storage', onEvt);
    try {
      bc?.close();
    } catch {
      /* ignore */
    }
    window.clearInterval(tick);
  };
}
