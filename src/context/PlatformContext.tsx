import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { useAuth } from './AuthContext';
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
  kb: 'nexus-kb-v1', chat: 'nexus-chat-v1', notif: 'nexus-notif-v1', auto: 'nexus-auto-v1',
  canned: 'nexus-canned-v1', survey: 'nexus-survey-v1', quality: 'nexus-quality-v1',
  announce: 'nexus-announce-v1', forms: 'nexus-forms-v1', releases: 'nexus-releases-v1',
};

function load<T>(key: string, fallback: T): T {
  try { const raw = localStorage.getItem(key); if (raw) return JSON.parse(raw) as T; } catch {}
  return fallback;
}
function save(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
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
  pushNotification: (title: string, body: string, link?: string) => Promise<void>;
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
  saveAnnouncement: (a: Partial<Announcement> & { title: string; body: string }) => Promise<void>;
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
  const [announcements, setAnnouncements] = useState<Announcement[]>(() => load(LS.announce, DEFAULT_ANNOUNCE));
  const [forms, setForms] = useState<FormDef[]>(() => load(LS.forms, DEFAULT_FORMS));
  const [releases, setReleases] = useState<Release[]>(() => load(LS.releases, DEFAULT_RELEASES));

  const refreshPlatform = useCallback(async () => {
    if (!isSupabaseConfigured || !supabase) return;
    const notifQuery = user?.id
      ? supabase.from('notifications').select('*').eq('user_id', user.id).order('created_at', { ascending: false }).limit(80)
      : supabase.from('notifications').select('*').order('created_at', { ascending: false }).limit(50);
    const [kb, chats, msgs, notifs, autos, cans, surv, qa, ann, frm, rel] = await Promise.all([
      supabase.from('knowledge_articles').select('*').order('created_at', { ascending: false }),
      supabase.from('chat_conversations').select('*').order('updated_at', { ascending: false }),
      supabase.from('chat_messages').select('*').order('created_at', { ascending: true }),
      notifQuery,
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
      const list = chats.data as ChatConversation[];
      const byConv: Record<string, ChatMessage[]> = {};
      for (const m of (msgs.data || []) as ChatMessage[]) {
        const cid = (m as ChatMessage & { conversation_id?: string }).conversation_id || '';
        if (!byConv[cid]) byConv[cid] = [];
        byConv[cid].push(m);
      }
      setConversations(list.map((c) => ({ ...c, messages: byConv[c.id] || [] })));
    }
    if (notifs.data) {
      const rows = notifs.data as AppNotification[];
      const seen = new Set<string>();
      const deduped: AppNotification[] = [];
      for (const n of rows) {
        const key = `${n.title}|${n.body}|${(n.created_at || '').slice(0, 16)}`;
        if (seen.has(key)) continue;
        seen.add(key);
        deduped.push(n);
      }
      setNotifications(deduped);
    }
    if (autos.data) setAutomations(autos.data as Automation[]);
    if (cans.data?.length) setCanned(cans.data as CannedResponse[]);
    if (surv.data) setSurveys(surv.data as SurveyResponse[]);
    if (qa.data) setReviews(qa.data as QualityReview[]);
    if (ann.data) setAnnouncements(ann.data as Announcement[]);
    if (frm.data) setForms(frm.data as FormDef[]);
    if (rel.data) setReleases(rel.data as Release[]);
  }, [user?.id]);

  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);

  useEffect(() => {
    if (isSupabaseConfigured) return;
    save(LS.kb, articles); save(LS.chat, conversations); save(LS.notif, notifications);
    save(LS.auto, automations); save(LS.canned, canned); save(LS.survey, surveys);
    save(LS.quality, reviews); save(LS.announce, announcements); save(LS.forms, forms); save(LS.releases, releases);
  }, [articles, conversations, notifications, automations, canned, surveys, reviews, announcements, forms, releases]);

  const saveArticle = async (a: { id?: string; title: string; category: string; body: string; published?: boolean }) => {
    const published = a.published !== false;
    if (supabase) {
      if (a.id) await supabase.from('knowledge_articles').update({ title: a.title, category: a.category, body: a.body, published }).eq('id', a.id);
      else await supabase.from('knowledge_articles').insert({ title: a.title, category: a.category, body: a.body, published });
      await refreshPlatform();
    } else {
      setArticles((prev) =>
        a.id
          ? prev.map((x) => (x.id === a.id ? { ...x, title: a.title, category: a.category, body: a.body, published } : x))
          : [{ id: `kb-${Date.now()}`, title: a.title, category: a.category, body: a.body, published }, ...prev]
      );
    }
  };
  const deleteArticle = async (id: string) => {
    if (supabase) { await supabase.from('knowledge_articles').delete().eq('id', id); await refreshPlatform(); }
    else setArticles((p) => p.filter((x) => x.id !== id));
  };

  const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {
    const base: ChatConversation = {
      id: `chat-${Date.now()}`, customer_name, customer_email, status: 'waiting', unread: 0, preview: '', messages: [],
      branch: meta?.branch, ticket_id: meta?.ticket_id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    };
    if (supabase) {
      const payload: Record<string, unknown> = { customer_name, customer_email, status: 'waiting', preview: '', unread: 0, branch: meta?.branch || null, ticket_id: meta?.ticket_id || null };
      const { data, error } = await supabase.from('chat_conversations').insert(payload).select('*').single();
      if (error) {
        const { data: d2, error: e2 } = await supabase.from('chat_conversations').insert({ customer_name, customer_email, status: 'waiting', preview: '', unread: 0 }).select('*').single();
        if (e2) throw e2;
        const c = { ...base, ...(d2 as ChatConversation) };
        setConversations((p) => [c, ...p]);
        return c;
      }
      const c = { ...base, ...(data as ChatConversation) };
      setConversations((p) => [c, ...p]);
      return c;
    }
    setConversations((p) => [base, ...p]);
    return base;
  };

  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = { id: `cm-${Date.now()}`, conversation_id: conversationId, sender, text, created_at: new Date().toISOString() };
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, sender, text });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
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

  const pushNotification = async (title: string, body: string, link?: string) => {
    const n: AppNotification = { id: `n-${Date.now()}`, user_id: user?.id, title, body, link, read: false, created_at: new Date().toISOString() };
    if (supabase && user) { await supabase.from('notifications').insert({ user_id: user.id, title, body, link, read: false }); await refreshPlatform(); }
    else setNotifications((p) => [n, ...p].slice(0, 50));
  };

  const markNotificationRead = async (id: string) => {
    setNotifications((p) => p.map((n) => (n.id === id ? { ...n, read: true } : n)));
    if (supabase) await supabase.from('notifications').update({ read: true }).eq('id', id);
  };
  const markAllNotificationsRead = async () => {
    setNotifications((p) => p.map((n) => ({ ...n, read: true })));
    if (supabase && user) await supabase.from('notifications').update({ read: true }).eq('user_id', user.id);
  };
  const deleteNotification = async (id: string) => {
    setNotifications((p) => p.filter((n) => n.id !== id));
    if (supabase) await supabase.from('notifications').delete().eq('id', id);
  };
  const deleteAllNotifications = async () => {
    setNotifications([]);
    if (supabase && user) await supabase.from('notifications').delete().eq('user_id', user.id);
    else save(LS.notif, []);
  };

  const saveAutomation = async (a: Partial<Automation> & { name: string }) => {
    if (supabase) {
      if (a.id) await supabase.from('automations').update(a).eq('id', a.id);
      else await supabase.from('automations').insert({ name: a.name, enabled: a.enabled ?? true, trigger: a.trigger || 'ticket_created', condition_field: a.condition_field, condition_op: a.condition_op || 'contains', condition_value: a.condition_value, action: a.action || 'set_priority', action_value: a.action_value });
      await refreshPlatform();
    } else setAutomations((prev) => a.id ? prev.map((x) => (x.id === a.id ? { ...x, ...a } as Automation : x)) : [{ id: `auto-${Date.now()}`, enabled: true, trigger: 'ticket_created', action: 'set_priority', ...a } as Automation, ...prev]);
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
  const saveAnnouncement = async (a: Partial<Announcement> & { title: string; body: string }) => {
    if (supabase) {
      const row = {
        title: a.title,
        body: a.body,
        severity: a.severity || 'info',
        active: a.active ?? true,
        channel: a.channel || 'both',
      };
      if (a.id) await supabase.from('announcements').update({ ...row, ...a }).eq('id', a.id);
      else await supabase.from('announcements').insert(row);
      await refreshPlatform();
    } else setAnnouncements((prev) => a.id ? prev.map((x) => (x.id === a.id ? { ...x, ...a } as Announcement : x)) : [{ id: `an-${Date.now()}`, severity: 'info', active: true, channel: a.channel || 'both', created_at: new Date().toISOString(), ...a } as Announcement, ...prev]);
  };
  const deleteAnnouncement = async (id: string) => {
    if (supabase) { await supabase.from('announcements').delete().eq('id', id); await refreshPlatform(); }
    else setAnnouncements((p) => p.filter((x) => x.id !== id));
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
    if (supabase) { await supabase.from('releases').insert({ ...r, released_at: new Date().toISOString() }); await refreshPlatform(); }
    else setReleases((p) => [{ id: `rel-${Date.now()}`, released_at: new Date().toISOString(), ...r }, ...p]);
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
