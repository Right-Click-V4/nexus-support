/* followup-agent-notify-v1 */
/* fix-platform-import-v1 */
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { useAuth } from './AuthContext';
import { notifyCustomer, onAgentNotify } from '../lib/agentNotify';
import type {
  KnowledgeArticle,
  ChatConversation,
  ChatMessage,
  AppNotification,
  Automation,
  CannedResponse,
  SurveyResponse,
  QualityReview,
  Announcement,
  FormDef,
  Release,
} from '../types';

const LS = {
  kb: 'nexus-kb-v1',
  chat: 'nexus-chat-v1',
  notif: 'nexus-notif-v1',
  auto: 'nexus-auto-v1',
  canned: 'nexus-canned-v1',
  survey: 'nexus-survey-v1',
  quality: 'nexus-quality-v1',
  announce: 'nexus-announce-v1', forms: 'nexus-forms-v1', releases: 'nexus-releases-v1', announceChannels: 'nexus-announce-channels-v1',
};

function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function save(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}

function loadAnnounceChannels(): Record<string, 'marquee' | 'portal' | 'both'> {
  try {
    const raw = localStorage.getItem(LS.announceChannels);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

function saveAnnounceChannel(id: string, channel: 'marquee' | 'portal' | 'both') {
  const map = loadAnnounceChannels();
  map[id] = channel;
  save(LS.announceChannels, map);
}

function stripChannelMeta(body?: string): string {
  // Channel only — never strip color meta
  return (body || '')
    .replace(/<!--\s*nexus:channel=\w+\s*-->/gi, '')
    .trim();
}

function stripAllMeta(body?: string): string {
  return (body || '')
    .replace(/<!--\s*nexus:channel=\w+\s*-->/gi, '')
    .replace(/<!--\s*nexus:color=[^>]+\s*-->/gi, '')
    .trim();
}

function parseChannelFromBody(body?: string): 'marquee' | 'portal' | 'both' | null {
  const m = (body || '').match(/<!--\s*nexus:channel=(\w+)\s*-->/i);
  if (!m) return null;
  if (m[1] === 'marquee' || m[1] === 'portal' || m[1] === 'both') return m[1];
  return null;
}

function mergeAnnouncementChannels(list: Announcement[]): Announcement[] {
  const map = loadAnnounceChannels();
  return list.map((a) => {
    const fromBody = parseChannelFromBody(a.body);
    const channel =
      a.channel ||
      fromBody ||
      map[a.id] ||
      (a.title && map[`title:${a.title}`]) ||
      map[`body:${stripAllMeta(a.body).slice(0, 40)}`] ||
      'both';
    return { ...a, channel, body: a.body };
  });
}

const DEFAULT_KB: KnowledgeArticle[] = [
  { id: 'kb-1', title: 'How to reset a customer password', category: 'Account', body: 'Open profile then Security, Reset password.', published: true },
  { id: 'kb-2', title: 'API rate limits', category: 'API', body: 'Free 60/min. Pro 600/min.', published: true },
];
const DEFAULT_CANNED: CannedResponse[] = [
  { id: 'cr-1', title: 'Greeting', body: 'Hi! Thanks for contacting support. How can we help today?', shortcut: '/hi' },
  { id: 'cr-2', title: 'Need more info', body: 'Could you share screenshots and the exact error message?', shortcut: '/info' },
  { id: 'cr-3', title: 'Resolved', body: 'Glad we could help! Please rate this ticket on the portal if you have a moment.', shortcut: '/done' },
];
const DEFAULT_AUTO: Automation[] = [
  { id: 'a1', name: 'Critical keyword', enabled: true, trigger: 'ticket_created', condition_field: 'title', condition_op: 'contains', condition_value: 'down', action: 'set_priority', action_value: 'critical' },
];
const DEFAULT_FORMS: FormDef[] = [
  { id: 'f1', name: 'General support', description: 'Default', fields: [{ id: 'subject', label: 'Subject', type: 'text', required: true }], active: true },
];
const DEFAULT_RELEASES: Release[] = [
  { id: 'r1', version: '1.3.0', title: 'P1 macros & portal KB', notes: 'Macros, published KB, CSAT.', released_at: new Date().toISOString() },
];
const DEFAULT_ANNOUNCE: Announcement[] = [
  { id: 'an1', title: 'Welcome', body: 'Share #/portal with customers.', severity: 'info', active: true, channel: 'both', created_at: new Date().toISOString() },
];

export type CreateChatMeta = { branch?: string; ticket_id?: string };

interface PlatformContextValue {
  articles: KnowledgeArticle[];
  conversations: ChatConversation[];
  notifications: AppNotification[];
  automations: Automation[];
  canned: CannedResponse[];
  surveys: SurveyResponse[];
  reviews: QualityReview[];
  announcements: Announcement[];
  forms: FormDef[];
  releases: Release[];
  unreadCount: number;
  refreshPlatform: () => Promise<void>;
  saveArticle: (a: { id?: string; title: string; category: string; body: string; published?: boolean }) => Promise<void>;
  deleteArticle: (id: string) => Promise<void>;
  createChat: (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => Promise<ChatConversation>;
  sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;
  setChatStatus: (id: string, status: 'waiting' | 'active' | 'ended') => Promise<void>;
  deleteChat: (id: string) => Promise<void>;
  pushNotification: (title: string, body?: string, link?: string) => Promise<void>;
  markNotificationRead: (id: string) => Promise<void>;
  markAllNotificationsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  deleteAllNotifications: () => Promise<void>;
  saveAutomation: (a: Partial<Automation> & { name: string }) => Promise<void>;
  deleteAutomation: (id: string) => Promise<void>;
  saveCanned: (c: Partial<CannedResponse> & { title: string; body: string }) => Promise<void>;
  deleteCanned: (id: string) => Promise<void>;
  addSurvey: (s: Omit<SurveyResponse, 'id' | 'created_at'> & { id?: string }) => Promise<void>;
  addReview: (r: Omit<QualityReview, 'id' | 'created_at'> & { id?: string }) => Promise<void>;
  saveAnnouncement: (a: Partial<Announcement> & { body: string; title?: string }) => Promise<void>;
  deleteAnnouncement: (id: string) => Promise<void>;
  saveForm: (f: Partial<FormDef> & { name: string }) => Promise<void>;
  deleteForm: (id: string) => Promise<void>;
  saveRelease: (r: { version: string; title: string; notes: string }) => Promise<void>;
  deleteRelease: (id: string) => Promise<void>;
}

const PlatformContext = createContext<PlatformContextValue | null>(null);

export function PlatformProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [articles, setArticles] = useState<KnowledgeArticle[]>(() => load(LS.kb, DEFAULT_KB));
  const [conversations, setConversations] = useState<ChatConversation[]>(() => load(LS.chat, []));
  const [notifications, setNotifications] = useState<AppNotification[]>(() => load(LS.notif, []));
  const [automations, setAutomations] = useState<Automation[]>(() => load(LS.auto, DEFAULT_AUTO));
  const [canned, setCanned] = useState<CannedResponse[]>(() => load(LS.canned, DEFAULT_CANNED));
  const [surveys, setSurveys] = useState<SurveyResponse[]>(() => load(LS.survey, []));
  const [reviews, setReviews] = useState<QualityReview[]>(() => load(LS.quality, []));
  const [announcements, setAnnouncements] = useState<Announcement[]>(() => mergeAnnouncementChannels(load(LS.announce, DEFAULT_ANNOUNCE)));
  const [forms, setForms] = useState<FormDef[]>(() => load(LS.forms, DEFAULT_FORMS));
  const [releases, setReleases] = useState<Release[]>(() => load(LS.releases, DEFAULT_RELEASES));

  const refreshPlatform = useCallback(async () => {
    if (!isSupabaseConfigured || !supabase) return;
    const notifQ = user?.id
      ? supabase.from('notifications').select('*').eq('user_id', user.id).order('created_at', { ascending: false }).limit(80)
      : supabase.from('notifications').select('*').order('created_at', { ascending: false }).limit(50);
    const [kb, chats, msgs, notifs, autos, can, surv, qual, ann, frm, rel] = await Promise.all([
      supabase.from('knowledge_articles').select('*').order('created_at', { ascending: false }),
      supabase.from('chat_conversations').select('*').order('updated_at', { ascending: false }),
      supabase.from('chat_messages').select('*').order('created_at', { ascending: true }),
      notifQ,
      supabase.from('automations').select('*'),
      supabase.from('canned_responses').select('*'),
      supabase.from('survey_responses').select('*').order('created_at', { ascending: false }),
      supabase.from('quality_reviews').select('*').order('created_at', { ascending: false }),
      supabase.from('announcements').select('*').order('created_at', { ascending: false }),
      supabase.from('forms').select('*'),
      supabase.from('releases').select('*').order('released_at', { ascending: false }),
    ]);
    if (kb.data) setArticles(kb.data as KnowledgeArticle[]);
    if (chats.data) {
      const messages = (msgs.data || []) as ChatMessage[];
      const byConv: Record<string, ChatMessage[]> = {};
      for (const m of messages) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }
      setConversations(
        (chats.data as ChatConversation[]).map((c) => ({
          ...c,
          messages: byConv[c.id] || c.messages || [],
        })),
      );
    }
    if (notifs.data) setNotifications(notifs.data as AppNotification[]);
    if (autos.data) setAutomations(autos.data as Automation[]);
    if (can.data) setCanned(can.data as CannedResponse[]);
    if (surv.data) setSurveys(surv.data as SurveyResponse[]);
    if (qual.data) setReviews(qual.data as QualityReview[]);
    if (ann.data) {
      const fromDb = mergeAnnouncementChannels(ann.data as Announcement[]);
      setAnnouncements((prev) => {
        const temps = prev.filter(
          (x) =>
            String(x.id).startsWith('an-') &&
            !fromDb.some((d) => stripAllMeta(d.body) === stripAllMeta(x.body)),
        );
        const merged = [...temps, ...fromDb];
        const seen = new Set<string>();
        const out: Announcement[] = [];
        for (const a of merged) {
          if (seen.has(a.id)) continue;
          seen.add(a.id);
          out.push(a);
        }
        return out;
      });
    }
    if (frm.data) setForms(frm.data as FormDef[]);
    if (rel.data) setReleases(rel.data as Release[]);
  }, [user?.id]);

  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);

  /* Real-time agent notifications (follow-ups, etc.) */
  useEffect(() => {
    const unsub = onAgentNotify(() => {
      void refreshPlatform();
    });
    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    if (isSupabaseConfigured && supabase && user?.id) {
      channel = supabase
        .channel(`nexus-agent-notifs-${user.id}`)
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'notifications' },
          () => {
            void refreshPlatform();
          },
        )
        .subscribe();
    }
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'nexus-notif-v1') void refreshPlatform();
    };
    window.addEventListener('storage', onStorage);
    return () => {
      unsub();
      window.removeEventListener('storage', onStorage);
      if (channel && supabase) void supabase.removeChannel(channel);
    };
  }, [refreshPlatform, user?.id]);

  // Lightweight announcements/releases refresh — works across normal + incognito tabs
  const refreshAnnouncementsLight = useCallback(async () => {
    if (!isSupabaseConfigured || !supabase) return;
    try {
      const [ann, rel] = await Promise.all([
        supabase.from('announcements').select('*').order('created_at', { ascending: false }),
        supabase.from('releases').select('*').order('released_at', { ascending: false }),
      ]);
      if (ann.data) {
        const fromDb = mergeAnnouncementChannels(ann.data as Announcement[]);
        setAnnouncements((prev) => {
          const temps = prev.filter(
            (x) =>
              String(x.id).startsWith('an-') &&
              !fromDb.some((d) => stripAllMeta(d.body) === stripAllMeta(x.body)),
          );
          const merged = [...temps, ...fromDb];
          const seen = new Set<string>();
          const out: Announcement[] = [];
          for (const a of merged) {
            if (seen.has(a.id)) continue;
            seen.add(a.id);
            out.push(a);
          }
          try { save(LS.announce, out); } catch { /* ignore */ }
          return out;
        });
      } else if (!ann.error) {
        setAnnouncements((prev) => {
          const temps = prev.filter((x) => String(x.id).startsWith('an-'));
          try { save(LS.announce, temps); } catch { /* ignore */ }
          return temps;
        });
      }
      if (rel.data) {
        setReleases(rel.data as Release[]);
        try { save(LS.releases, rel.data); } catch { /* ignore */ }
      }
    } catch (err) {
      console.error('refreshAnnouncementsLight', err);
    }
  }, []);

  // Supabase Realtime + 2s poll so every browser context (incl. incognito) stays in sync
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;

    void refreshAnnouncementsLight();

    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      channel = supabase
        .channel('nexus-announcements-rt')
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'announcements' },
          () => { void refreshAnnouncementsLight(); },
        )
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'releases' },
          () => { void refreshAnnouncementsLight(); },
        )
        .subscribe();
    } catch (err) {
      console.warn('announcements realtime unavailable', err);
    }

    const poll = window.setInterval(() => {
      void refreshAnnouncementsLight();
    }, 2000);

    return () => {
      window.clearInterval(poll);
      try {
        if (channel && supabase) void supabase.removeChannel(channel);
      } catch { /* ignore */ }
    };
  }, [refreshAnnouncementsLight]);


  useEffect(() => {
    const pull = () => {
      try {
        const next = mergeAnnouncementChannels(load(LS.announce, [] as Announcement[]));
        if (Array.isArray(next)) setAnnouncements(next);
      } catch { /* ignore */ }
    };
    const onStorage = (e: StorageEvent) => {
      if (e.key === LS.announce || e.key === LS.announceChannels) pull();
    };
    const onCustom = () => pull();
    window.addEventListener('storage', onStorage);
    window.addEventListener('nexus-announce-updated', onCustom as EventListener);
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => pull();
    } catch { /* ignore */ }
    const tick = window.setInterval(pull, 500);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('nexus-announce-updated', onCustom as EventListener);
      window.clearInterval(tick);
      try { bc?.close(); } catch { /* ignore */ }
    };
  }, []);































































































































































































  useEffect(() => {
    const isCustomerPortal = () => {
      try {
        const h = window.location.hash || '';
        const p = window.location.pathname || '';
        return (
          /#\/?portal\b/i.test(h) ||
          /\/portal\b/i.test(p) ||
          !!document.querySelector('.portal-shell')
        );
      } catch {
        return false;
      }
    };
    const pull = () => {
      try {
        const next = mergeAnnouncementChannels(load(LS.announce, [] as Announcement[]));
        if (Array.isArray(next)) setAnnouncements(next);
      } catch { /* ignore */ }
    };
    let reloadTimer: number | undefined;
    let lastTick = '';
    try { lastTick = localStorage.getItem('nexus-announce-tick') || ''; } catch { /* ignore */ }
    let lastSnap = '';
    try { lastSnap = localStorage.getItem(LS.announce) || ''; } catch { /* ignore */ }
    const schedulePortalReload = () => {
      if (!isCustomerPortal()) { pull(); return; }
      pull();
      window.clearTimeout(reloadTimer);
      reloadTimer = window.setTimeout(() => {
        try { window.location.reload(); } catch { /* ignore */ }
      }, 350);
    };
    const onStorage = (e: StorageEvent) => {
      if (e.key === LS.announce || e.key === LS.announceChannels || e.key === 'nexus-announce-tick') {
        schedulePortalReload();
      }
    };
    const onCustom = () => schedulePortalReload();
    window.addEventListener('storage', onStorage);
    window.addEventListener('nexus-announce-updated', onCustom as EventListener);
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => schedulePortalReload();
    } catch { /* ignore */ }
    const tick = window.setInterval(() => {
      try {
        const tnow = localStorage.getItem('nexus-announce-tick') || '';
        const snap = localStorage.getItem(LS.announce) || '';
        if (tnow && tnow !== lastTick) { lastTick = tnow; schedulePortalReload(); return; }
        if (snap && snap !== lastSnap) {
          lastSnap = snap;
          if (isCustomerPortal()) schedulePortalReload();
          else pull();
        } else { pull(); }
      } catch { pull(); }
    }, 700);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('nexus-announce-updated', onCustom as EventListener);
      window.clearInterval(tick);
      window.clearTimeout(reloadTimer);
      try { bc?.close(); } catch { /* ignore */ }
    };
  }, []);





  useEffect(() => {
    save(LS.kb, articles); save(LS.chat, conversations); save(LS.notif, notifications);
    save(LS.auto, automations); save(LS.canned, canned); save(LS.survey, surveys);
    save(LS.quality, reviews); save(LS.announce, announcements); save(LS.forms, forms); save(LS.releases, releases);
  }, [articles, conversations, notifications, automations, canned, surveys, reviews, announcements, forms, releases]);

  const saveArticle = async (a: { id?: string; title: string; category: string; body: string; published?: boolean }) => {
    const published = a.published ?? true;
    if (supabase) {
      if (a.id) await supabase.from('knowledge_articles').update({ title: a.title, category: a.category, body: a.body, published }).eq('id', a.id);
      else await supabase.from('knowledge_articles').insert({ title: a.title, category: a.category, body: a.body, published });
      await refreshPlatform();
    } else {
      setArticles((prev) =>
        a.id
          ? prev.map((x) => (x.id === a.id ? { ...x, ...a, published } : x))
          : [{ id: `kb-${Date.now()}`, published, ...a }, ...prev],
      );
    }
  };
  const deleteArticle = async (id: string) => {
    if (supabase) { await supabase.from('knowledge_articles').delete().eq('id', id); await refreshPlatform(); }
    else setArticles((p) => p.filter((x) => x.id !== id));
  };

  const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {
    const payload: Record<string, unknown> = { customer_name, customer_email, status: 'waiting', preview: '', unread: 0 };
    if (meta?.branch) payload.branch = meta.branch;
    if (meta?.ticket_id) payload.ticket_id = meta.ticket_id;
    if (supabase) {
      const { data, error } = await supabase.from('chat_conversations').insert(payload).select('*').single();
      if (error || !data) {
        const { data: d2, error: e2 } = await supabase.from('chat_conversations').insert({ customer_name, customer_email, status: 'waiting' }).select('*').single();
        if (e2 || !d2) throw e2 || new Error('create chat failed');
        await refreshPlatform();
        return d2 as ChatConversation;
      }
      await refreshPlatform();
      return data as ChatConversation;
    }
    const c: ChatConversation = {
      id: `chat-${Date.now()}`,
      customer_name,
      customer_email,
      status: 'waiting',
      preview: '',
      unread: 0,
      messages: [],
      created_at: new Date().toISOString(),
      branch: meta?.branch,
      ticket_id: meta?.ticket_id,
    };
    setConversations((p) => [c, ...p]);
    return c;
  };

  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    const conv = conversations.find((x) => x.id === conversationId);
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
    }
    if (sender === 'agent' && conv?.customer_email) {
      void notifyCustomer({
        email: conv.customer_email,
        title: 'New live chat message',
        body: text.slice(0, 120),
        link: 'chat',
      });
    }
  };

  const setChatStatus = async (id: string, status: 'waiting' | 'active' | 'ended') => {
    if (supabase) { await supabase.from('chat_conversations').update({ status }).eq('id', id); await refreshPlatform(); }
    else setConversations((p) => p.map((c) => (c.id === id ? { ...c, status } : c)));
  };
  const deleteChat = async (id: string) => {
    if (supabase) {
      await supabase.from('chat_messages').delete().eq('conversation_id', id);
      await supabase.from('chat_conversations').delete().eq('id', id);
      await refreshPlatform();
    } else setConversations((p) => p.filter((c) => c.id !== id));
  };

  const pushNotification = async (title: string, body?: string, link?: string) => {
    if (supabase && user) { await supabase.from('notifications').insert({ user_id: user.id, title, body, link, read: false }); await refreshPlatform(); }
    else setNotifications((p) => [{ id: `n-${Date.now()}`, title, body, link, read: false, created_at: new Date().toISOString() }, ...p]);
  };
  const markNotificationRead = async (id: string) => {
    if (supabase) await supabase.from('notifications').update({ read: true }).eq('id', id);
    setNotifications((p) => p.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };
  const markAllNotificationsRead = async () => {
    if (supabase && user) await supabase.from('notifications').update({ read: true }).eq('user_id', user.id);
    setNotifications((p) => p.map((n) => ({ ...n, read: true })));
  };
  const deleteNotification = async (id: string) => {
    if (supabase) await supabase.from('notifications').delete().eq('id', id);
    setNotifications((p) => p.filter((n) => n.id !== id));
  };
  const deleteAllNotifications = async () => {
    if (supabase && user) await supabase.from('notifications').delete().eq('user_id', user.id);
    else save(LS.notif, []);
    setNotifications([]);
  };

  const saveAutomation = async (a: Partial<Automation> & { name: string }) => {
    if (supabase) {
      if (a.id) await supabase.from('automations').update(a).eq('id', a.id);
      else await supabase.from('automations').insert({ name: a.name, enabled: a.enabled ?? true, trigger: a.trigger || 'ticket_created', condition_field: a.condition_field, condition_op: a.condition_op || 'contains', condition_value: a.condition_value, action: a.action || 'set_priority', action_value: a.action_value });
      await refreshPlatform();
    } else setAutomations((prev) => a.id ? prev.map((x) => (x.id === a.id ? { ...x, ...a } as Automation : x)) : [{ id: `a-${Date.now()}`, enabled: true, trigger: 'ticket_created', action: 'set_priority', ...a } as Automation, ...prev]);
  };
  const deleteAutomation = async (id: string) => {
    if (supabase) { await supabase.from('automations').delete().eq('id', id); await refreshPlatform(); }
    else setAutomations((p) => p.filter((x) => x.id !== id));
  };
  const saveCanned = async (c: Partial<CannedResponse> & { title: string; body: string }) => {
    if (supabase) {
      if (c.id) await supabase.from('canned_responses').update(c).eq('id', c.id);
      else await supabase.from('canned_responses').insert({ title: c.title, body: c.body, shortcut: c.shortcut });
      await refreshPlatform();
    } else setCanned((prev) => c.id ? prev.map((x) => (x.id === c.id ? { ...x, ...c } as CannedResponse : x)) : [{ id: `cr-${Date.now()}`, ...c } as CannedResponse, ...prev]);
  };
  const deleteCanned = async (id: string) => {
    if (supabase) { await supabase.from('canned_responses').delete().eq('id', id); await refreshPlatform(); }
    else setCanned((p) => p.filter((x) => x.id !== id));
  };
  const addSurvey = async (s: Omit<SurveyResponse, 'id' | 'created_at'> & { id?: string }) => {
    if (supabase) { await supabase.from('survey_responses').insert(s); await refreshPlatform(); }
    else setSurveys((p) => [{ id: `sv-${Date.now()}`, created_at: new Date().toISOString(), ...s }, ...p]);
  };
  const addReview = async (r: Omit<QualityReview, 'id' | 'created_at'> & { id?: string }) => {
    if (supabase) { await supabase.from('quality_reviews').insert(r); await refreshPlatform(); }
    else setReviews((p) => [{ id: `qr-${Date.now()}`, created_at: new Date().toISOString(), ...r }, ...p]);
  };

  const notifyAnnounceSync = () => {
    try {
      localStorage.setItem('nexus-announce-tick', String(Date.now()));
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));
      const bc = new BroadcastChannel('nexus-announce');
      bc.postMessage({ type: 'updated', t: Date.now() });
      bc.close();
    } catch { /* ignore */ }
  };


  const saveAnnouncement = async (a: Partial<Announcement> & { body: string; title?: string }) => {
    const channel = a.channel || 'both';
    const severity = a.severity || 'info';
    const active = a.active ?? true;
    const title = (a.title || '').trim();
    const plainBody = stripChannelMeta(a.body || '').trim();
    const storedBody =
      channel === 'both' ? plainBody : `<!--nexus:channel=${channel}-->\n${plainBody}`;
    const dbTitle = (stripAllMeta(title) || stripAllMeta(plainBody).slice(0, 80) || 'Announcement');

    let nextList: Announcement[] = [];
    if (!a.id) {
      const tempId = `an-${Date.now()}`;
      const optimistic: Announcement = {
        id: tempId, title: stripAllMeta(title) || stripAllMeta(plainBody).slice(0, 80), body: storedBody, severity, active, channel,
        created_at: new Date().toISOString(),
      };
      nextList = [optimistic, ...announcements];
      setAnnouncements(nextList);
      saveAnnounceChannel(tempId, channel);
      if (title) saveAnnounceChannel(`title:${title}`, channel);
      saveAnnounceChannel(`body:${plainBody.slice(0, 40)}`, channel);
    } else {
      nextList = announcements.map((x) =>
        x.id === a.id ? ({ ...x, ...a, title, body: storedBody, channel, severity, active } as Announcement) : x,
      );
      setAnnouncements(nextList);
      saveAnnounceChannel(a.id, channel);
      if (title) saveAnnounceChannel(`title:${title}`, channel);
      saveAnnounceChannel(`body:${plainBody.slice(0, 40)}`, channel);
    }

    save(LS.announce, nextList);
    notifyAnnounceSync();

    if (!supabase) return;

    const row = { title: dbTitle, body: storedBody, severity, active };
    try {
      if (a.id) {
        const { error } = await supabase.from('announcements').update(row).eq('id', a.id);
        if (error) throw error;
      } else {
        const { data, error } = await supabase.from('announcements').insert(row).select('*').single();
        if (error) throw error;
        if (data?.id) {
          saveAnnounceChannel(data.id, channel);
          if (title) saveAnnounceChannel(`title:${title}`, channel);
          saveAnnounceChannel(`body:${plainBody.slice(0, 40)}`, channel);
          setAnnouncements((prev) => {
            const merged = prev.map((x) =>
              (x.body === storedBody || stripAllMeta(x.body) === stripAllMeta(plainBody)) && String(x.id).startsWith('an-')
                ? ({ ...x, ...data, title, body: storedBody, channel } as Announcement)
                : x,
            );
            save(LS.announce, merged);
            return merged;
          });
        }
      }
      await refreshPlatform();
      notifyAnnounceSync();
    } catch (err) {
      console.error('saveAnnouncement failed', err);
    }
  };

  const deleteAnnouncement = async (id: string) => {
    const next = announcements.filter((x) => x.id !== id);
    setAnnouncements(next);
    save(LS.announce, next);
    notifyAnnounceSync();
    if (!supabase) return;
    try {
      await supabase.from('announcements').delete().eq('id', id);
      void refreshPlatform();
    } catch (err) {
      console.error('deleteAnnouncement failed', err);
    }
  };
  const saveForm = async (f: Partial<FormDef> & { name: string }) => {
    if (supabase) {
      if (f.id) await supabase.from('forms').update(f).eq('id', f.id);
      else await supabase.from('forms').insert({ name: f.name, description: f.description, fields: f.fields || [], active: f.active ?? true });
      await refreshPlatform();
    } else setForms((prev) => f.id ? prev.map((x) => (x.id === f.id ? { ...x, ...f } as FormDef : x)) : [{ id: `f-${Date.now()}`, fields: [], active: true, ...f } as FormDef, ...prev]);
  };
  const deleteForm = async (id: string) => {
    if (supabase) { await supabase.from('forms').delete().eq('id', id); await refreshPlatform(); }
    else setForms((p) => p.filter((x) => x.id !== id));
  };
  const saveRelease = async (r: { version: string; title: string; notes: string }) => {
    const optimistic = {
      id: `rel-${Date.now()}`,
      released_at: new Date().toISOString(),
      version: r.version,
      title: r.title,
      notes: r.notes,
    };
    setReleases((p) => [optimistic, ...p]);
    if (!supabase) return;
    try {
      const { data, error } = await supabase
        .from('releases')
        .insert({ version: r.version, title: r.title, notes: r.notes, released_at: optimistic.released_at })
        .select('*')
        .single();
      if (error) throw error;
      if (data?.id) {
        setReleases((p) => p.map((x) => (x.id === optimistic.id ? (data as Release) : x)));
      }
      await refreshPlatform();
    } catch (err) {
      console.error('saveRelease failed', err);
    }
  };
  const deleteRelease = async (id: string) => {
    if (supabase) { await supabase.from('releases').delete().eq('id', id); await refreshPlatform(); }
    else setReleases((p) => p.filter((x) => x.id !== id));
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  const value: PlatformContextValue = {
    articles, conversations, notifications, automations, canned, surveys, reviews, announcements, forms, releases,
    unreadCount, refreshPlatform,
    saveArticle, deleteArticle, createChat, sendChatMessage, setChatStatus, deleteChat,
    pushNotification, markNotificationRead, markAllNotificationsRead, deleteNotification, deleteAllNotifications,
    saveAutomation, deleteAutomation, saveCanned, deleteCanned, addSurvey, addReview,
    saveAnnouncement, deleteAnnouncement, saveForm, deleteForm, saveRelease, deleteRelease,
  };

  return <PlatformContext.Provider value={value}>{children}</PlatformContext.Provider>;
}

export function usePlatform() {
  const ctx = useContext(PlatformContext);
  if (!ctx) throw new Error('usePlatform must be used within PlatformProvider');
  return ctx;
}
