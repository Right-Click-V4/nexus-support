/** Real-time desk presence for Active Now (Agent Workspace → Customer Portal). */
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
const LIVE_MS = 90_000;

type PresenceChannel = ReturnType<NonNullable<typeof supabase>['channel']>;
let channel: PresenceChannel | null = null;

function readLocal(): DeskAgent[] {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? (JSON.parse(raw) as DeskAgent[]) : [];
    const now = Date.now();
    return (list || []).filter((a) => a && a.id && now - (a.at || 0) < LIVE_MS);
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

export async function publishDeskPresence(agent: {
  id: string;
  name: string;
  status?: string;
  avatar_url?: string | null;
  initials?: string;
  color?: string;
} | null) {
  if (!agent?.id) return;
  const row: DeskAgent = {
    id: agent.id,
    name: agent.name || 'Agent',
    status: (agent.status || 'online').toLowerCase() === 'offline' ? 'online' : (agent.status || 'online'),
    avatar_url: agent.avatar_url || null,
    initials: agent.initials,
    color: agent.color,
    at: Date.now(),
  };

  const others = readLocal().filter((a) => a.id !== row.id);
  writeLocal([...others, row]);

  if (!isSupabaseConfigured || !supabase) return;

  if (!channel) {
    channel = supabase.channel(CHANNEL, { config: { presence: { key: agent.id } } });
    channel.subscribe(async (status) => {
      if (status === 'SUBSCRIBED' && channel) {
        try {
          await channel.track(row);
        } catch {
          /* ignore */
        }
      }
    });
  } else {
    try {
      await channel.track(row);
    } catch {
      /* ignore */
    }
  }
}

export async function clearDeskPresence(agentId?: string | null) {
  if (agentId) {
    writeLocal(readLocal().filter((a) => a.id !== agentId));
  }
  if (channel && supabase) {
    try {
      await channel.untrack();
      await supabase.removeChannel(channel);
    } catch {
      /* ignore */
    }
    channel = null;
  }
}

function fromPresenceState(): DeskAgent[] {
  if (!channel) return [];
  try {
    const state = channel.presenceState() as Record<string, Array<Partial<DeskAgent>>>;
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
  for (const a of [...fromPresenceState(), ...readLocal()]) {
    if (!a?.id) continue;
    if (now - (a.at || 0) > LIVE_MS) continue;
    if ((a.status || '').toLowerCase() === 'offline') continue;
    map.set(a.id, a);
  }
  return [...map.values()];
}

export function watchDeskPresence(onChange: (agents: DeskAgent[]) => void): () => void {
  const emit = () => onChange(getDeskPresence());
  emit();

  let ch: PresenceChannel | null = null;
  if (isSupabaseConfigured && supabase) {
    ch = supabase.channel(CHANNEL);
    if (!channel) channel = ch;
    ch.on('presence', { event: 'sync' }, emit);
    ch.on('presence', { event: 'join' }, emit);
    ch.on('presence', { event: 'leave' }, emit);
    void ch.subscribe();
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
  const tick = window.setInterval(emit, 3000);

  return () => {
    window.removeEventListener('nexus-desk-presence', onEvt);
    window.removeEventListener('storage', onEvt);
    try {
      bc?.close();
    } catch {
      /* ignore */
    }
    window.clearInterval(tick);
    if (ch && supabase && ch !== channel) {
      try {
        void supabase.removeChannel(ch);
      } catch {
        /* ignore */
      }
    }
  };
}
