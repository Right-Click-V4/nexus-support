import { supabase, isSupabaseConfigured } from './supabase';

export type NotifyPayload = {
  title: string;
  body: string;
  link?: string;
  /** Target a single auth user; omit to broadcast to all agents */
  userId?: string | null;
};

const LOCAL_KEY = 'nexus-notif-v1';
const EVENT = 'nexus-agent-notify';

function uid() {
  return `n-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function pushLocal(items: Array<{ id: string; user_id?: string; title: string; body: string; link?: string; read: boolean; created_at: string }>) {
  try {
    const raw = localStorage.getItem(LOCAL_KEY);
    const prev = raw ? JSON.parse(raw) : [];
    const next = [...items, ...(Array.isArray(prev) ? prev : [])].slice(0, 80);
    localStorage.setItem(LOCAL_KEY, JSON.stringify(next));
  } catch {}
  window.dispatchEvent(new CustomEvent(EVENT, { detail: items }));
}

/** Notify one agent (by auth user id) or all agents when userId is omitted. */
export async function notifyAgents(payload: NotifyPayload) {
  const { title, body, link, userId } = payload;
  const created_at = new Date().toISOString();

  if (isSupabaseConfigured && supabase) {
    try {
      if (userId) {
        await supabase.from('notifications').insert({
          user_id: userId,
          title,
          body,
          link: link || null,
          read: false,
        });
      } else {
        const { data: agents } = await supabase
          .from('agents')
          .select('user_id')
          .not('user_id', 'is', null);
        const ids = [...new Set((agents || []).map((a: { user_id: string }) => a.user_id).filter(Boolean))];
        if (ids.length === 0) {
          // Fallback broadcast row (any signed-in agent can see if we treat null as broadcast)
          await supabase.from('notifications').insert({
            user_id: null,
            title,
            body,
            link: link || null,
            read: false,
          });
        } else {
          await supabase.from('notifications').insert(
            ids.map((id) => ({
              user_id: id,
              title,
              body,
              link: link || null,
              read: false,
            }))
          );
        }
      }
      window.dispatchEvent(new CustomEvent(EVENT));
      return;
    } catch (e) {
      console.warn('notifyAgents supabase failed, using local', e);
    }
  }

  pushLocal([
    {
      id: uid(),
      user_id: userId || undefined,
      title,
      body,
      link,
      read: false,
      created_at,
    },
  ]);
}

export function onAgentNotify(handler: () => void) {
  const fn = () => handler();
  window.addEventListener(EVENT, fn);
  return () => window.removeEventListener(EVENT, fn);
}


const CUSTOMER_KEY = 'nexus-customer-notif-v1';
const CUSTOMER_EVENT = 'nexus-customer-notify';

/** Notify a customer by email (local). link: mytickets | chat */
export async function notifyCustomer(payload: {
  email?: string | null;
  title: string;
  body: string;
  link?: string;
}) {
  const email = (payload.email || '').trim().toLowerCase();
  if (!email) return;
  const created_at = new Date().toISOString();
  const item = {
    id: uid(),
    customer_email: email,
    title: payload.title,
    body: payload.body,
    link: payload.link || 'mytickets',
    read: false,
    created_at,
  };
  try {
    const raw = localStorage.getItem(CUSTOMER_KEY);
    const prev = raw ? JSON.parse(raw) : [];
    const next = [item, ...(Array.isArray(prev) ? prev : [])].slice(0, 80);
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(next));
  } catch {}
  try {
    window.dispatchEvent(new CustomEvent(CUSTOMER_EVENT, { detail: item }));
  } catch {}
}
