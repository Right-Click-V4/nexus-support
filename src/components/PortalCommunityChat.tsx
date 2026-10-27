import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Send, Users, ArrowLeft, Plus, Search, BellOff, Bell, Pin,
  Pencil, UserPlus, LogOut, MoreHorizontal, X, Hash, Info, Smile, Image as ImageIcon, Film,
} from 'lucide-react';
import {
  DEFAULT_GROUP_ID as CLOUD_DEFAULT_ID,
  loadLocalStore, saveLocalStore, ensureMember as ensureMemberCloudLocal,
  communityCloudEnabled, fetchCloudStore, ensureDefaultGroupCloud,
  upsertMemberCloud, insertMessageCloud, setPinnedCloud, createGroupCloud,
  renameGroupCloud, removeMemberCloud, subscribeCommunity, subscribeTyping,
  type Message as CloudMessage, type Store as CloudStore,
} from '../lib/communityApi';

const LS_KEY = 'nexus-community-groups-v1';
const DEFAULT_GROUP_ID = 'default-nexus-community';

type Member = { name: string; email: string; joined_at: string };
type Message = {
  id: string;
  author_name: string;
  author_email: string;
  text: string;
  created_at: string;
  pinned?: boolean;
  image_data?: string;
  gif_url?: string;
};
type Group = {
  id: string;
  name: string;
  description?: string;
  created_by: string;
  created_at: string;
  members: Member[];
  messages: Message[];
  muted_by?: string[];
};

type Store = { groups: Group[] };

function defaultGroup(): Group {
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

function loadStore(): Store {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Store;
      if (Array.isArray(parsed.groups) && parsed.groups.length) {
        const hasDefault = parsed.groups.some((g) => g.id === DEFAULT_GROUP_ID);
        return hasDefault ? parsed : { groups: [defaultGroup(), ...parsed.groups] };
      }
    }
  } catch {}
  return { groups: [defaultGroup()] };
}

function saveStore(store: Store) {
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
    } catch {}
  } catch {}
}

function ensureMember(group: Group, name: string, email: string): Group {
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


function initials(name: string) {
  const parts = (name || '?').trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (parts[0] || '?').slice(0, 2).toUpperCase();
}
const AVATAR_COLORS = [
  'from-violet-500 to-fuchsia-500', 'from-sky-500 to-blue-600', 'from-emerald-500 to-teal-600',
  'from-amber-500 to-orange-600', 'from-rose-500 to-pink-600', 'from-indigo-500 to-violet-600',
];
function avatarGradient(key: string) {
  let h = 0;
  for (let i = 0; i < key.length; i++) h = key.charCodeAt(i) + ((h << 5) - h);
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
}
function AvatarBubble({ name, email }: { name: string; email: string }) {
  return (
    <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${avatarGradient(email || name)} flex items-center justify-center text-white text-[10px] font-semibold shrink-0 shadow-md`} title={name}>
      {initials(name)}
    </div>
  );
}
const EMOJIS = [
  '😀','😃','😄','😁','😆','😅','🤣','😂','🙂','😉','😊','😇','🥰','😍','🤩','😘','😗','😚','😙',
  '😋','😛','😜','🤪','😝','🤑','🤗','🤭','🤫','🤔','🤐','🤨','😐','😑','😶','😏','😒','🙄','😬',
  '😮','😯','😲','😳','🥺','😢','😭','😤','😠','😡','🤬','😈','👿','💀','👻','👽','🤖','💩','🎃',
  '👋','🤚','✋','🖖','👌','🤌','🤏','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','👇','👍','👎','✊','👊',
  '👏','🙌','👐','🤲','🤝','🙏','💪','🦾','❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣️','💕',
  '🔥','✨','⭐','🌟','💫','💥','🎉','🎊','🎈','🎁','🏆','🥇','🚀','🌈','☀️','🌙','⚡','❄️','🍕','🍔',
  '✅','❌','❓','❗','💯','🔔','💡','🔒','🔑','💰','💎','🎯','🎮','📱','💻','☕','🍺','🌮','🍣','🍩',
];
const QUICK_GIFS = [
  { label: 'Wave hello', url: 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif' },
  { label: 'Clap applause', url: 'https://media.giphy.com/media/7rj2ZgQq6qpI9m7vXd/giphy.gif' },
  { label: 'Party celebrate', url: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif' },
  { label: 'Thumbs up', url: 'https://media.giphy.com/media/111ebonMs90YLu/giphy.gif' },
  { label: 'Wow mind blown', url: 'https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif' },
  { label: 'Heart love', url: 'https://media.giphy.com/media/3oz8xLd9DJq2l2VFtu/giphy.gif' },
  { label: 'Laugh lmao', url: 'https://media.giphy.com/media/10JhviFuU2wBA0/giphy.gif' },
  { label: 'Cry sad', url: 'https://media.giphy.com/media/ROF8OVviPSk0M/giphy.gif' },
  { label: 'Dance happy', url: 'https://media.giphy.com/media/l0M9C2XT6F6eYjR1e/giphy.gif' },
  { label: 'Facepalm', url: 'https://media.giphy.com/media/XIqCqxNjSHlx1gYRbk/giphy.gif' },
  { label: 'Nod yes', url: 'https://media.giphy.com/media/ASd0UJjgB4Hy0/giphy.gif' },
  { label: 'No shake', url: 'https://media.giphy.com/media/15aGGXfR66ug/giphy.gif' },
  { label: 'High five', url: 'https://media.giphy.com/media/l4JyOHT67pTaS5sJO/giphy.gif' },
  { label: 'Mic drop', url: 'https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif' },
  { label: 'Coffee work', url: 'https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif' },
  { label: 'Fire lit', url: 'https://media.giphy.com/media/xT0xeJpnrWC2RdTYNg/giphy.gif' },
  { label: 'Cool sunglasses', url: 'https://media.giphy.com/media/dXFKDUolyLLi8gqHA3/giphy.gif' },
  { label: 'Thinking hmm', url: 'https://media.giphy.com/media/3o7TKTDn976rzVgky4/giphy.gif' },
  { label: 'Victory win', url: 'https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif' },
  { label: 'Thank you', url: 'https://media.giphy.com/media/osjgQPWRn3rwyB5c0V/giphy.gif' },
  { label: 'Good morning', url: 'https://media.giphy.com/media/l0MYC0LajbaPoEADu/giphy.gif' },
  { label: 'Good night', url: 'https://media.giphy.com/media/xUA7aN1ESkXgXVlXMs/giphy.gif' },
  { label: 'Excited jump', url: 'https://media.giphy.com/media/5GoVLqeAOo6PK/giphy.gif' },
  { label: 'Confused', url: 'https://media.giphy.com/media/1X7l0Rp1ZqUIuJ0e6j/giphy.gif' },
];

interface Props {
  displayName: string;
  email: string;
  onBack?: () => void;
}

/* community-media-v2 */
export default function PortalCommunityChat({ displayName, email, onBack }: Props) {
  const [store, setStore] = useState<Store>(() => loadStore());
  const [activeId, setActiveId] = useState(DEFAULT_GROUP_ID);
  const [draft, setDraft] = useState('');
  const [query, setQuery] = useState('');
  const [showInfo, setShowInfo] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [emojiOpen, setEmojiOpen] = useState(false);
  const [gifOpen, setGifOpen] = useState(false);
  const [gifSearch, setGifSearch] = useState('');
  const [gifResults, setGifResults] = useState<{ label: string; url: string }[]>([]);
  const [gifSearching, setGifSearching] = useState(false);

  const runGifSearch = useCallback(async (q: string) => {
    const term = q.trim().toLowerCase();
    if (!term) {
      setGifResults([]);
      return;
    }
    const local = QUICK_GIFS.filter((g) => g.label.toLowerCase().includes(term));
    setGifResults(local);
    setGifSearching(true);
    try {
      const res = await fetch(
        `https://api.giphy.com/v1/gifs/search?api_key=dc6zaTOxFJmzC&q=${encodeURIComponent(term)}&limit=18&rating=g`
      );
      if (res.ok) {
        const data = await res.json();
        const remote = (data.data || [])
          .map((g: any) => ({
            label: String(g.title || term),
            url: String(g.images?.fixed_height?.url || g.images?.original?.url || ''),
          }))
          .filter((g: { url: string }) => !!g.url);
        if (remote.length) setGifResults(remote);
      }
    } catch {
      /* keep local */
    } finally {
      setGifSearching(false);
    }
  }, []);


  const [typingPeers, setTypingPeers] = useState<{ name: string; email: string; at: number }[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const bcRef = useRef<BroadcastChannel | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const refresh = useCallback(() => setStore(loadStore()), []);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === LS_KEY) refresh();
    };
    window.addEventListener('storage', onStorage);
    const t = setInterval(refresh, 2500);
    return () => {
      window.removeEventListener('storage', onStorage);
      clearInterval(t);
    };
  }, [refresh]);

  // Auto-join current user into active group
  useEffect(() => {
    if (!email) return;
    setStore((prev) => {
      const next = {
        groups: prev.groups.map((g) =>
          g.id === activeId ? ensureMember(g, displayName, email) : g
        ),
      };
      // also ensure default membership
      next.groups = next.groups.map((g) =>
        g.id === DEFAULT_GROUP_ID ? ensureMember(g, displayName, email) : g
      );
      saveStore(next);
      return next;
    });
    void upsertMemberCloud(activeId, displayName, email);
    if (activeId !== DEFAULT_GROUP_ID) void upsertMemberCloud(DEFAULT_GROUP_ID, displayName, email);
  }, [email, displayName, activeId]);

  const groups = store.groups;
  const active = groups.find((g) => g.id === activeId) || groups[0];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [active?.messages.length, activeId]);

  const filteredMessages = useMemo(() => {
    if (!active) return [];
    const q = query.trim().toLowerCase();
    if (!q) return active.messages;
    return active.messages.filter((m) => {
      const hay = [m.text || '', m.author_name || '', m.author_email || '', m.gif_url ? 'gif' : '', m.image_data ? 'photo image' : ''].join(' ').toLowerCase();
      return hay.includes(q);
    });
  }, [active, query]);

  const pinned = useMemo(
    () => (active?.messages || []).filter((m) => m.pinned),
    [active]
  );

  const isMuted = !!(email && active?.muted_by?.includes(email.toLowerCase()));

  const updateGroup = (id: string, fn: (g: Group) => Group) => {
    setStore((prev) => {
      const next = { groups: prev.groups.map((g) => (g.id === id ? fn(g) : g)) };
      saveStore(next);
      return next;
    });
  };

  const send = (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = draft.trim();
    if (!text || !active) return;
    const msg: Message = {
      id: `cm-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      author_name: displayName || 'Customer',
      author_email: email || '',
      text,
      created_at: new Date().toISOString(),
    };
    updateGroup(active.id, (g) => ({
      ...ensureMember(g, displayName, email),
      messages: [...g.messages, msg],
    }));
    void insertMessageCloud(active.id, msg as any); void upsertMemberCloud(active.id, displayName, email); setDraft('');
  };

  const createGroup = (e: React.FormEvent) => {
    e.preventDefault();
    const name = newName.trim();
    if (!name) return;
    const g: Group = {
      id: `grp-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      name,
      description: newDesc.trim() || undefined,
      created_by: email || displayName,
      created_at: new Date().toISOString(),
      members: email
        ? [{ name: displayName || email.split('@')[0], email, joined_at: new Date().toISOString() }]
        : [],
      messages: [],
      muted_by: [],
    };
    setStore((prev) => {
      const next = { groups: [...prev.groups, g] };
      saveStore(next);
      return next;
    });
    setActiveId(g.id);
    setNewName('');
    setNewDesc('');
    setShowCreate(false);
    setShowInfo(false);
  };

  const renameGroup = () => {
    if (!active || active.id === DEFAULT_GROUP_ID) return;
    const name = window.prompt('Group name', active.name)?.trim();
    if (!name) return;
    updateGroup(active.id, (g) => ({ ...g, name }));
  };

  const toggleMute = () => {
    if (!active || !email) return;
    const key = email.toLowerCase();
    updateGroup(active.id, (g) => {
      const muted = new Set(g.muted_by || []);
      if (muted.has(key)) muted.delete(key);
      else muted.add(key);
      return { ...g, muted_by: Array.from(muted) };
    });
  };

  const addMember = (e: React.FormEvent) => {
    e.preventDefault();
    if (!active || !inviteEmail.trim()) return;
    const em = inviteEmail.trim().toLowerCase();
    updateGroup(active.id, (g) =>
      ensureMember(g, inviteName.trim() || em.split('@')[0], em)
    );
    setInviteEmail('');
    setInviteName('');
  };

  const leaveGroup = () => {
    if (!active || !email || active.id === DEFAULT_GROUP_ID) return;
    if (!window.confirm(`Leave “${active.name}”?`)) return;
    updateGroup(active.id, (g) => ({
      ...g,
      members: g.members.filter((m) => m.email.toLowerCase() !== email.toLowerCase()),
    }));
    setActiveId(DEFAULT_GROUP_ID);
    setShowInfo(false);
  };

  const togglePin = (msgId: string) => {
    if (!active) return;
    updateGroup(active.id, (g) => ({
      ...g,
      messages: g.messages.map((m) =>
        m.id === msgId ? { ...m, pinned: !m.pinned } : m
      ),
    }));
  };

  return (
    <div className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/25 dark:bg-[#0c0a14]/55 border-white/20 dark:border-violet-500/20 backdrop-blur-md shadow-sm">
      {/* Group list */}
      <aside className="w-56 shrink-0 border-r border-white/15 dark:border-white/10 bg-white/20 dark:bg-[#0a0812]/60 flex flex-col hidden sm:flex backdrop-blur-sm">
        <div className="px-3 py-3 border-b border-zinc-200 flex items-center justify-between gap-2">
          <div className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Groups</div>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="p-1.5 rounded-lg text-violet-600 hover:bg-violet-50"
            title="Create group"
          >
            <Plus size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {groups.map((g) => {
            const activeRow = g.id === active?.id;
            const last = g.messages[g.messages.length - 1];
            return (
              <button
                key={g.id}
                type="button"
                onClick={() => { setActiveId(g.id); setShowInfo(false); setQuery(''); }}
                className={`w-full text-left rounded-lg px-2.5 py-2 transition-colors ${
                  activeRow ? 'bg-violet-100/80 text-violet-900' : 'hover:bg-zinc-100 text-zinc-700'
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    g.id === DEFAULT_GROUP_ID ? 'bg-brand-600 text-white' : 'bg-zinc-200 text-zinc-600'
                  }`}>
                    {g.id === DEFAULT_GROUP_ID ? <Users size={14} /> : <Hash size={14} />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium truncate">{g.name}</div>
                    <div className="text-[10px] text-zinc-400 truncate">
                      {last ? last.text : 'No messages yet'}
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
        <div className="p-2 border-t border-zinc-200">
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-violet-600 hover:bg-violet-50 rounded-lg"
          >
            <Plus size={14} /> New group
          </button>
        </div>
      </aside>

      {/* Main chat */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#0c0a16]/30">
        <div className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/10 bg-[#0c0a16]/55 backdrop-blur">
          {onBack && (
            <button type="button" onClick={onBack} className="md:hidden p-1.5 rounded-lg text-zinc-500 hover:bg-zinc-100">
              <ArrowLeft size={18} />
            </button>
          )}
          <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${
            active?.id === DEFAULT_GROUP_ID ? 'bg-brand-600 text-white' : 'bg-zinc-200 text-zinc-600'
          }`}>
            {active?.id === DEFAULT_GROUP_ID ? <Users size={16} /> : <Hash size={16} />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 truncate">{active?.name || 'Community'}</div>
            <div className="text-[11px] text-zinc-500 dark:text-zinc-400 truncate">
              {(active?.members.length || 0)} member{(active?.members.length || 0) === 1 ? '' : 's'}
              {active?.description ? ` · ${active.description}` : ''}
            </div>
          </div>
          <button
            type="button"
            onClick={toggleMute}
            className="p-2 rounded-lg text-zinc-500 hover:bg-zinc-100"
            title={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? <BellOff size={18} /> : <Bell size={18} />}
          </button>
        </div>

        {/* Mobile group switcher */}
        <div className="sm:hidden flex gap-1.5 px-3 py-2 border-b border-zinc-100 overflow-x-auto">
          {groups.map((g) => (
            <button
              key={g.id}
              type="button"
              onClick={() => setActiveId(g.id)}
              className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-medium ${
                g.id === active?.id ? 'bg-violet-100 text-violet-700' : 'bg-zinc-100 text-zinc-600'
              }`}
            >
              {g.name}
            </button>
          ))}
          <button type="button" onClick={() => setShowCreate(true)} className="shrink-0 px-2 py-1 rounded-full text-xs text-violet-600 bg-violet-50">
            +
          </button>
        </div>

        {pinned.length > 0 && (
          <div className="px-4 py-2 bg-amber-50/80 border-b border-amber-100 text-xs text-amber-900 flex items-start gap-2">
            <Pin size={14} className="shrink-0 mt-0.5" />
            <div className="min-w-0">
              <span className="font-semibold">Pinned · </span>
              {pinned[pinned.length - 1].text}
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-[#0c0a16]/40">
          {filteredMessages.length === 0 && (
            <div className="text-center py-12 px-4">
              <Users className="mx-auto text-violet-300/50 mb-3" size={32} />
              <p className="text-sm font-medium text-zinc-300">
                {query ? 'No matches' : 'No messages yet'}
              </p>
              <p className="text-xs text-zinc-400 mt-1 max-w-xs mx-auto">
                {query
                  ? 'Try a different search.'
                  : 'Be the first to ask the community about an issue or share a tip.'}
              </p>
            </div>
          )}
          {filteredMessages.map((m) => {
            const mine = m.author_email && email && m.author_email.toLowerCase() === email.toLowerCase();
            return (
              <div key={m.id} className={`flex items-end gap-2 ${mine ? 'justify-end' : 'justify-start'} group`}>
                {!mine && <AvatarBubble name={m.author_name} email={m.author_email} />}
                <div
                  className={`max-w-[78%] rounded-2xl px-3.5 py-2.5 text-sm relative shadow-sm ${
                    mine
                      ? 'bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white rounded-br-md'
                      : 'bg-white/70 dark:bg-[#1c1830]/95 border border-white/30 dark:border-violet-500/15 text-zinc-900 dark:text-zinc-100 rounded-bl-md backdrop-blur-sm'
                  }`}
                >
                  {!mine && (
                    <div className="text-[11px] font-semibold mb-0.5 text-violet-600 dark:text-violet-300">{m.author_name}</div>
                  )}
                  {m.image_data && <img src={m.image_data} alt="" className="rounded-lg max-h-48 mb-1.5" />}
                  {m.gif_url && <img src={m.gif_url} alt="gif" className="rounded-lg max-h-40 mb-1.5" />}
                  {m.text ? <div className="whitespace-pre-wrap break-words">{m.text}</div> : null}
                  <div className={`flex items-center gap-2 text-[10px] mt-1 ${mine ? 'text-white/60' : 'text-zinc-400'}`}>
                    <span>
                      {new Date(m.created_at).toLocaleString([], {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                    {m.pinned && <Pin size={10} />}
                    <button
                      type="button"
                      onClick={() => togglePin(m.id)}
                      className={`opacity-0 group-hover:opacity-100 ${mine ? 'hover:text-white' : 'hover:text-zinc-700'}`}
                      title={m.pinned ? 'Unpin' : 'Pin'}
                    >
                      <Pin size={12} />
                    </button>
                  </div>
                </div>
                {mine && <AvatarBubble name={m.author_name} email={m.author_email} />}
              </div>
            );
          })}
          {typingPeers.some((p) => Date.now() - p.at < 2500) && (
            <div className="text-xs text-violet-600 dark:text-violet-300 pl-1 flex items-center gap-2">
              <span className="flex gap-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" />
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:300ms]" />
              </span>
              {(() => {
                const live = typingPeers.filter((p) => Date.now() - p.at < 2500);
                if (live.length === 1) return `${live[0].name} is typing…`;
                if (live.length === 2) return `${live[0].name} and ${live[1].name} are typing…`;
                return live.length ? `${live[0].name} and others are typing…` : '';
              })()}
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-white/10 bg-[#0c0a16]/55 backdrop-blur">
          {emojiOpen && (
            <div className="px-3 pt-2 flex flex-wrap gap-1 max-h-40 overflow-y-auto">
              {EMOJIS.map((e) => (
                <button key={e} type="button" onClick={() => { setDraft((d) => d + e); try { bcRef.current?.postMessage({ type: 'typing', groupId: activeId, peer: { name: displayName, email } }); } catch {} }} className="w-8 h-8 text-lg rounded-lg hover:bg-violet-100 dark:hover:bg-violet-500/20">{e}</button>
              ))}
            </div>
          )}
                    {gifOpen && (
            <div className="px-3 pt-2 space-y-2 max-h-52 overflow-y-auto">
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-400" />
                  <input
                    value={gifSearch}
                    onChange={(e) => {
                      const v = e.target.value;
                      setGifSearch(v);
                      void runGifSearch(v);
                    }}
                    placeholder="Search GIFs…"
                    className="w-full pl-8 pr-2.5 py-1.5 text-xs rounded-lg bg-white/10 border border-white/15 text-zinc-100 placeholder:text-zinc-500 outline-none focus:border-violet-500"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => void runGifSearch(gifSearch)}
                  className="px-2.5 py-1.5 text-xs rounded-lg bg-violet-600 hover:bg-violet-500 text-white shrink-0"
                >
                  Search
                </button>
              </div>
              {gifSearching && <div className="text-[10px] text-zinc-400 px-1">Searching…</div>}
              <div className="grid grid-cols-3 gap-2">
                {(gifSearch.trim() ? gifResults : QUICK_GIFS).map((g) => (
                  <button
                    key={g.url + g.label}
                    type="button"
                    onClick={() => {
                      if (!active) return;
                      const msg: Message = {
                        id: `m-${Date.now()}`,
                        author_name: displayName || 'You',
                        author_email: email || 'anon',
                        text: '',
                        created_at: new Date().toISOString(),
                        gif_url: g.url,
                      };
                      updateGroup(active.id, (gg) => ({ ...gg, messages: [...gg.messages, msg] }));
                      try { void insertMessageCloud(active.id, msg as any); } catch {}
                      try { void upsertMemberCloud(active.id, displayName, email); } catch {}
                      setGifOpen(false);
                      setGifSearch('');
                      setGifResults([]);
                    }}
                    className="rounded-lg overflow-hidden border border-white/10 hover:border-violet-400/50"
                    title={g.label}
                  >
                    <img src={g.url} alt={g.label} className="w-full h-14 object-cover" />
                  </button>
                ))}
              </div>
              {gifSearch.trim() && !gifSearching && gifResults.length === 0 && (
                <div className="text-[10px] text-zinc-500 px-1 py-2">No GIFs found — try another word.</div>
              )}
            </div>
          )}
          <form onSubmit={send} className="p-3 flex items-end gap-2">
            <div className="flex gap-0.5 shrink-0">
              <button type="button" onClick={() => { setEmojiOpen((v)=>!v); setGifOpen(false); }} className={`p-2 rounded-lg ${emojiOpen ? 'bg-violet-100 text-violet-700 dark:bg-violet-500/25 dark:text-violet-200' : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-white/10'}`} title="Emoji"><Smile size={18} /></button>
              <button type="button" onClick={() => { setGifOpen((v)=>!v); setEmojiOpen(false); }} className={`p-2 rounded-lg ${gifOpen ? 'bg-violet-100 text-violet-700 dark:bg-violet-500/25 dark:text-violet-200' : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-white/10'}`} title="GIF"><Film size={18} /></button>
              <button type="button" onClick={() => fileRef.current?.click()} className="p-2 rounded-lg text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-white/10" title="Photo"><ImageIcon size={18} /></button>
              <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file || !file.type.startsWith('image/') || !active) return;
                if (file.size > 1200000) { window.alert('Image must be under ~1.2MB'); return; }
                const reader = new FileReader();
                reader.onload = () => {
                  const msg: Message = { id: `m-${Date.now()}`, author_name: displayName || 'You', author_email: email || 'anon', text: draft.trim(), created_at: new Date().toISOString(), image_data: String(reader.result || '') };
                  updateGroup(active.id, (gg) => ({ ...gg, messages: [...gg.messages, msg] }));
                  setDraft('');
                };
                reader.readAsDataURL(file);
              }} />
            </div>
            <input
              value={draft}
              onChange={(e) => {
                setDraft(e.target.value);
                try { bcRef.current?.postMessage({ type: 'typing', groupId: activeId, peer: { name: displayName || email, email } }); } catch {}
              }}
              placeholder={isMuted ? 'Muted — you can still post' : 'Message the group…'}
              className="flex-1 px-3.5 py-2.5 text-sm rounded-xl border border-zinc-200 dark:border-violet-500/20 bg-white/55 dark:bg-[#0e0c18]/90 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
              maxLength={2000}
            />
            <button type="submit" disabled={!draft.trim()} className="px-3.5 py-2.5 rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white hover:opacity-95 disabled:opacity-40 shrink-0" aria-label="Send">
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>

      {/* Info panel permanent-info-rail */}
      {active && (
        <aside className="w-72 shrink-0 border-l border-white/10 bg-[#0c0a16]/90 text-zinc-100 flex flex-col overflow-y-auto backdrop-blur-md">
          <div className="px-4 py-5 border-b border-zinc-800 flex flex-col items-center justify-center text-center">
            <div className="w-14 h-14 rounded-full bg-zinc-800/90 flex items-center justify-center mb-2 ring-1 ring-violet-500/30">
              {active.id === DEFAULT_GROUP_ID ? <Users size={24} className="text-violet-400" /> : <Hash size={24} className="text-zinc-400" />}
            </div>
            <div className="text-sm font-semibold text-zinc-100">{active.name}</div>
            <div className="text-[11px] text-zinc-400 mt-0.5">
              {active.members.length} member{active.members.length === 1 ? '' : 's'}
            </div>
          </div>

          <div className="px-3 py-3 space-y-1 border-b border-zinc-800">
            <button type="button" onClick={toggleMute} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-300 hover:bg-white/5">
              {isMuted ? <Bell size={16} /> : <BellOff size={16} />}
              {isMuted ? 'Unmute notifications' : 'Mute notifications'}
            </button>
            <div className="px-3 py-2">
              <div className="flex items-center gap-2 text-zinc-400 text-xs mb-1.5">
                <Search size={14} /> Search in conversation
              </div>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search messages…"
                className="w-full px-2.5 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-100 placeholder:text-zinc-600 outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="px-4 py-3 border-b border-zinc-800">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 mb-2">Chat info</div>
            {pinned.length > 0 && (
              <div className="text-sm text-zinc-300 flex items-start gap-2 mb-2">
                <Pin size={14} className="mt-0.5 text-amber-400 shrink-0" />
                <span className="text-xs">{pinned.length} pinned message{pinned.length === 1 ? '' : 's'}</span>
              </div>
            )}
            {active.description && (
              <p className="text-xs text-zinc-400 leading-relaxed">{active.description}</p>
            )}
          </div>

          {active.id !== DEFAULT_GROUP_ID && (
            <div className="px-4 py-3 border-b border-zinc-800 space-y-1">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 mb-2">Customize</div>
              <button type="button" onClick={renameGroup} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-300 hover:bg-white/5">
                <Pencil size={16} /> Change group name
              </button>
            </div>
          )}

          <div className="px-4 py-3 border-b border-zinc-800">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 mb-2">Members</div>
            <ul className="space-y-2 max-h-40 overflow-y-auto">
              {active.members.length === 0 && (
                <li className="text-xs text-zinc-500 px-1">No members listed yet</li>
              )}
              {active.members.map((m) => (
                <li key={m.email} className="flex items-center gap-2 px-1">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 text-[10px] font-semibold flex items-center justify-center text-white">
                    {(m.name || m.email).slice(0, 2).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-zinc-200 truncate">{m.name}</div>
                    <div className="text-[10px] text-zinc-500 dark:text-zinc-400 truncate">{m.email}</div>
                  </div>
                </li>
              ))}
            </ul>
            {active.id !== DEFAULT_GROUP_ID && (
              <form onSubmit={addMember} className="mt-3 space-y-2">
                <div className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 flex items-center gap-1">
                  <UserPlus size={12} /> Add people
                </div>
                <input
                  value={inviteName}
                  onChange={(e) => setInviteName(e.target.value)}
                  placeholder="Name"
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-100 outline-none focus:border-violet-500"
                />
                <input
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="Email"
                  type="email"
                  required
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-100 outline-none focus:border-violet-500"
                />
                <button type="submit" className="w-full py-1.5 text-xs font-medium rounded-lg bg-violet-600 hover:bg-violet-500 text-white">
                  Add member
                </button>
              </form>
            )}
          </div>

          {active.id !== DEFAULT_GROUP_ID && (
            <div className="p-3 mt-auto">
              <button
                type="button"
                onClick={leaveGroup}
                className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm text-rose-400 hover:bg-rose-500/10"
              >
                <LogOut size={16} /> Leave group
              </button>
            </div>
          )}
        </aside>
      )}

      {/* Create group modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form
            onSubmit={createGroup}
            className="w-full max-w-md bg-white rounded-xl shadow-xl border border-zinc-200 p-5 space-y-4"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-zinc-900">Create group chat</h2>
              <button type="button" onClick={() => setShowCreate(false)} className="p-1 text-zinc-400 hover:text-zinc-700">
                <X size={16} />
              </button>
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-600 mb-1">Group name *</label>
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                required
                placeholder="e.g. Branch North issues"
                className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-600 mb-1">Description (optional)</label>
              <input
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                placeholder="What is this group for?"
                className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400"
              />
            </div>
            <div className="flex gap-2 justify-end pt-1">
              <button type="button" onClick={() => setShowCreate(false)} className="px-3 py-2 text-sm rounded-lg border border-zinc-200 text-zinc-600 hover:bg-zinc-50">
                Cancel
              </button>
              <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-brand-600 text-white hover:bg-brand-700">
                Create
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
