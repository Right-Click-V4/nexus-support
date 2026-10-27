import { supabase, isSupabaseConfigured } from './supabase';

export const DEFAULT_GROUP_ID = 'default-nexus-community';

export type Member = { name: string; email: string; joined_at: string };
export type Message = {
  id: string;
  author_name: string;
  author_email: string;
  text: string;
  created_at: string;
  pinned?: boolean;
  image_data?: string;
  gif_url?: string;
};
export type Group = {
  id: string;
  name: string;
  description?: string;
  created_by: string;
  created_at: string;
  members: Member[];
  messages: Message[];
  muted_by?: string[];
};
export type Store = { groups: Group[] };

const LS_KEY = 'nexus-community-groups-v1';
const MAX_IMAGE = 400_000;

export function defaultGroup(): Group {
  return {
    id: DEFAULT_GROUP_ID,
    name: 'Nexus Community',
    description: 'Default room for all customers — share tips and issues without opening a ticket.',
    created_by: 'system',
    created_at: new Date(0).toISOString(),
    members: [],
    messages: [],
    muted_by: [],
  };
}

export function loadLocalStore(): Store {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Store;
      if (Array.isArray(parsed.groups) && parsed.groups.length) {
        const hasDefault = parsed.groups.some((g) => g.id === DEFAULT_GROUP_ID);
        return hasDefault ? parsed : { groups: [defaultGroup(), ...parsed.groups] };
      }
    }
  } catch {
    /* ignore */
  }
  return { groups: [defaultGroup()] };
}

export function saveLocalStore(store: Store) {
  try {
    const trimmed: Store = {
      groups: store.groups.map((g) => ({
        ...g,
        messages: g.messages.slice(-300),
        members: g.members.slice(-100),
      })),
    };
    localStorage.setItem(LS_KEY, JSON.stringify(trimmed));
    try {
      window.dispatchEvent(new CustomEvent('nexus-community-sync'));
      new BroadcastChannel('nexus-community-store-v1').postMessage({ type: 'store', store: trimmed });
    } catch {
      /* ignore */
    }
  } catch {
    /* ignore */
  }
}

export function ensureMember(group: Group, name: string, email: string): Group {
  if (!email) return group;
  const exists = group.members.some((m) => m.email.toLowerCase() === email.toLowerCase());
  if (exists) return group;
  return {
    ...group,
    members: [
      ...group.members,
      { name: name || email.split('@')[0], email, joined_at: new Date().toISOString() },
    ],
  };
}

export function communityCloudEnabled(): boolean {
  return !!(isSupabaseConfigured && supabase);
}

export async function fetchCloudStore(): Promise<Store | null> {
  if (!communityCloudEnabled() || !supabase) return null;
  try {
    const [{ data: groups, error: gErr }, { data: members, error: mErr }, { data: messages, error: msgErr }] =
      await Promise.all([
        supabase.from('community_groups').select('*').order('created_at', { ascending: true }),
        supabase.from('community_members').select('*'),
        supabase
          .from('community_messages')
          .select('id, group_id, author_name, author_email, body, gif_url, image_data, pinned, created_at')
          .order('created_at', { ascending: true })
          .limit(800),
      ]);
    if (gErr || mErr || msgErr) {
      console.warn('[community] fetch error', gErr || mErr || msgErr);
      return null;
    }
    const list = (groups || []).map((g) => {
      const gid = String(g.id);
      return {
        id: gid,
        name: String(g.name || 'Group'),
        description: g.description ? String(g.description) : undefined,
        created_by: String(g.created_by || 'system'),
        created_at: String(g.created_at || new Date().toISOString()),
        members: (members || [])
          .filter((m) => String(m.group_id) === gid)
          .map((m) => ({
            name: String(m.name || m.email || ''),
            email: String(m.email || ''),
            joined_at: String(m.joined_at || new Date().toISOString()),
          })),
        messages: (messages || [])
          .filter((m) => String(m.group_id) === gid)
          .map((m) => ({
            id: String(m.id),
            author_name: String(m.author_name || ''),
            author_email: String(m.author_email || ''),
            text: String(m.body || ''),
            created_at: String(m.created_at || new Date().toISOString()),
            pinned: !!m.pinned,
            gif_url: m.gif_url ? String(m.gif_url) : undefined,
            image_data: m.image_data ? String(m.image_data) : undefined,
          })),
        muted_by: [] as string[],
      } satisfies Group;
    });
    if (!list.some((g) => g.id === DEFAULT_GROUP_ID)) {
      list.unshift(defaultGroup());
    }
    return { groups: list };
  } catch (e) {
    console.warn('[community] fetch failed', e);
    return null;
  }
}

export async function ensureDefaultGroupCloud(): Promise<void> {
  if (!communityCloudEnabled() || !supabase) return;
  await supabase.from('community_groups').upsert(
    {
      id: DEFAULT_GROUP_ID,
      name: 'Nexus Community',
      description: 'Default room for all customers — share tips and issues without opening a ticket.',
      created_by: 'system',
      created_at: '1970-01-01T00:00:00Z',
    },
    { onConflict: 'id' },
  );
}

export async function upsertMemberCloud(groupId: string, name: string, email: string): Promise<void> {
  if (!communityCloudEnabled() || !supabase || !email) return;
  await supabase.from('community_members').upsert(
    {
      group_id: groupId,
      email: email.toLowerCase(),
      name: name || email.split('@')[0],
      joined_at: new Date().toISOString(),
    },
    { onConflict: 'group_id,email' },
  );
}

export async function insertMessageCloud(groupId: string, msg: Message): Promise<void> {
  if (!communityCloudEnabled() || !supabase) return;
  const image =
    msg.image_data && msg.image_data.length <= MAX_IMAGE ? msg.image_data : null;
  await supabase.from('community_messages').upsert({
    id: msg.id,
    group_id: groupId,
    author_name: msg.author_name,
    author_email: (msg.author_email || '').toLowerCase(),
    body: msg.text || '',
    gif_url: msg.gif_url || null,
    image_data: image,
    pinned: !!msg.pinned,
    created_at: msg.created_at,
  });
}

export async function setPinnedCloud(messageId: string, pinned: boolean): Promise<void> {
  if (!communityCloudEnabled() || !supabase) return;
  await supabase.from('community_messages').update({ pinned }).eq('id', messageId);
}

export async function createGroupCloud(g: Group): Promise<void> {
  if (!communityCloudEnabled() || !supabase) return;
  await supabase.from('community_groups').upsert({
    id: g.id,
    name: g.name,
    description: g.description || null,
    created_by: g.created_by,
    created_at: g.created_at,
  });
  for (const m of g.members) {
    await upsertMemberCloud(g.id, m.name, m.email);
  }
}

export async function renameGroupCloud(id: string, name: string): Promise<void> {
  if (!communityCloudEnabled() || !supabase) return;
  await supabase.from('community_groups').update({ name }).eq('id', id);
}

export async function removeMemberCloud(groupId: string, email: string): Promise<void> {
  if (!communityCloudEnabled() || !supabase || !email) return;
  await supabase
    .from('community_members')
    .delete()
    .eq('group_id', groupId)
    .eq('email', email.toLowerCase());
}

export function subscribeCommunity(onChange: () => void): () => void {
  if (!communityCloudEnabled() || !supabase) return () => {};
  const channel = supabase
    .channel('nexus-community-rt')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'community_groups' }, () => onChange())
    .on('postgres_changes', { event: '*', schema: 'public', table: 'community_members' }, () => onChange())
    .on('postgres_changes', { event: '*', schema: 'public', table: 'community_messages' }, () => onChange())
    .subscribe();
  return () => {
    void supabase.removeChannel(channel);
  };
}

export function subscribeTyping(
  groupId: string,
  selfEmail: string,
  onPeer: (peer: { name: string; email: string }) => void,
): { stop: () => void; send: (name: string, email: string) => void } {
  if (!communityCloudEnabled() || !supabase) {
    return { stop: () => {}, send: () => {} };
  }
  const channel = supabase.channel(`community-typing-${groupId}`, {
    config: { broadcast: { self: false } },
  });
  channel
    .on('broadcast', { event: 'typing' }, ({ payload }) => {
      const peer = payload as { name?: string; email?: string };
      if (!peer?.email || peer.email.toLowerCase() === selfEmail.toLowerCase()) return;
      onPeer({ name: peer.name || peer.email, email: peer.email });
    })
    .subscribe();
  return {
    stop: () => {
      void supabase.removeChannel(channel);
    },
    send: (name, email) => {
      void channel.send({
        type: 'broadcast',
        event: 'typing',
        payload: { name, email },
      });
    },
  };
}
