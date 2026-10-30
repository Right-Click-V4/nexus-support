/** Real-time chat viewers: Supabase Presence when available, else localStorage. */
import { supabase, isSupabaseConfigured } from './supabase';

export type ChatViewer = {
  id: string;
  name: string;
  at: number;
};

const KEY = 'nexus-chat-viewers-v1';
const BC_NAME = 'nexus-chat-viewers';
const LIVE_MS = 30_000;

type PresenceChannel = ReturnType<NonNullable<typeof supabase>['channel']>;

const channels = new Map<string, PresenceChannel>();

function readLocal(): Record<string, ChatViewer[]> {
  try {
    const raw = localStorage.getItem(KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

function writeLocal(map: Record<string, ChatViewer[]>) {
  try {
    localStorage.setItem(KEY, JSON.stringify(map));
  } catch {
    /* ignore */
  }
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      const bc = new BroadcastChannel(BC_NAME);
      bc.postMessage({ type: 'viewers', map });
      bc.close();
    }
  } catch {
    /* ignore */
  }
  try {
    window.dispatchEvent(new CustomEvent('nexus-chat-viewers', { detail: map }));
  } catch {
    /* ignore */
  }
}

export function publishChatViewer(
  conversationId: string | null | undefined,
  agent: { id: string; name: string } | null | undefined,
) {
  if (!conversationId || !agent?.id) return;
  const now = Date.now();

  const map = readLocal();
  const list = (map[conversationId] || []).filter((v) => v.id !== agent.id && now - v.at < LIVE_MS);
  list.push({ id: agent.id, name: agent.name || 'Agent', at: now });
  map[conversationId] = list;
  for (const k of Object.keys(map)) {
    map[k] = (map[k] || []).filter((v) => now - v.at < LIVE_MS);
    if (!map[k].length) delete map[k];
  }
  writeLocal(map);

  if (!isSupabaseConfigured || !supabase) return;

  let ch = channels.get(conversationId);
  if (!ch) {
    ch = supabase.channel(`chat-viewers:${conversationId}`, {
      config: { presence: { key: agent.id } },
    });
    channels.set(conversationId, ch);
    void ch.subscribe(async (status) => {
      if (status === 'SUBSCRIBED') {
        try {
          await ch!.track({
            id: agent.id,
            name: agent.name || 'Agent',
            at: Date.now(),
          });
        } catch {
          /* ignore */
        }
      }
    });
  } else {
    void ch.track({
      id: agent.id,
      name: agent.name || 'Agent',
      at: Date.now(),
    });
  }
}

export function clearChatViewer(
  conversationId: string | null | undefined,
  agentId: string | null | undefined,
) {
  if (!conversationId || !agentId) return;
  const map = readLocal();
  map[conversationId] = (map[conversationId] || []).filter((v) => v.id !== agentId);
  if (!map[conversationId]?.length) delete map[conversationId];
  writeLocal(map);

  const ch = channels.get(conversationId);
  if (ch && supabase) {
    try {
      void ch.untrack();
      void supabase.removeChannel(ch);
    } catch {
      /* ignore */
    }
    channels.delete(conversationId);
  }
}

export function getChatViewers(conversationId: string | null | undefined): ChatViewer[] {
  if (!conversationId) return [];
  const now = Date.now();
  const local = (readLocal()[conversationId] || []).filter((v) => now - v.at < LIVE_MS);

  const ch = channels.get(conversationId);
  if (ch) {
    try {
      const state = ch.presenceState() as Record<string, Array<{ id?: string; name?: string; at?: number }>>;
      const fromPresence: ChatViewer[] = [];
      for (const metas of Object.values(state)) {
        for (const m of metas || []) {
          if (m?.id) {
            fromPresence.push({
              id: String(m.id),
              name: String(m.name || 'Agent'),
              at: Number(m.at || now),
            });
          }
        }
      }
      if (fromPresence.length) {
        const byId = new Map<string, ChatViewer>();
        for (const v of [...fromPresence, ...local]) byId.set(v.id, v);
        return [...byId.values()];
      }
    } catch {
      /* ignore */
    }
  }
  return local;
}

export function watchChatViewers(
  conversationId: string | null | undefined,
  onChange: (viewers: ChatViewer[]) => void,
): () => void {
  if (!conversationId) {
    onChange([]);
    return () => {};
  }

  const emit = () => onChange(getChatViewers(conversationId));
  emit();

  let ch: PresenceChannel | null = null;
  if (isSupabaseConfigured && supabase) {
    ch = supabase.channel(`chat-viewers:${conversationId}`);
    channels.set(conversationId, ch);
    ch.on('presence', { event: 'sync' }, emit);
    ch.on('presence', { event: 'join' }, emit);
    ch.on('presence', { event: 'leave' }, emit);
    void ch.subscribe();
  }

  const unsubLocal = subscribeChatViewers(emit);
  return () => {
    unsubLocal();
    if (ch && supabase) {
      try {
        void supabase.removeChannel(ch);
      } catch {
        /* ignore */
      }
      if (channels.get(conversationId) === ch) channels.delete(conversationId);
    }
  };
}

export function subscribeChatViewers(handler: () => void): () => void {
  const onEvt = () => handler();
  window.addEventListener('nexus-chat-viewers', onEvt);
  window.addEventListener('storage', onEvt);
  let bc: BroadcastChannel | null = null;
  try {
    bc = new BroadcastChannel(BC_NAME);
    bc.onmessage = () => handler();
  } catch {
    /* ignore */
  }
  const tick = window.setInterval(handler, 4000);
  return () => {
    window.removeEventListener('nexus-chat-viewers', onEvt);
    window.removeEventListener('storage', onEvt);
    try {
      bc?.close();
    } catch {
      /* ignore */
    }
    window.clearInterval(tick);
  };
}
