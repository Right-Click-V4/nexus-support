#!/usr/bin/env python3
"""Fix bidirectional customer notification sync."""
from pathlib import Path

an = Path("src/lib/agentNotify.ts")
t = an.read_text()
if "customer-notif-supabase-v1" not in t:
    old = """/** Notify a customer by email (local). link: mytickets | chat */
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
}"""
    new = """/** Notify a customer by email. Writes Supabase (when possible) + local + BC for realtime. */
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

  if (isSupabaseConfigured && supabase) {
    try {
      let userId: string | null = null;
      const { data: cust } = await supabase
        .from('customers')
        .select('user_id,email')
        .ilike('email', email)
        .maybeSingle();
      if (cust && (cust as { user_id?: string }).user_id) {
        userId = (cust as { user_id: string }).user_id;
      }
      const row: Record<string, unknown> = {
        title: payload.title,
        body: payload.body,
        link: payload.link || 'mytickets',
        read: false,
      };
      if (userId) row.user_id = userId;
      const { error } = await supabase.from('notifications').insert({
        ...row,
        customer_email: email,
      });
      if (error) {
        const { error: e2 } = await supabase.from('notifications').insert(row);
        if (e2 && userId) {
          await supabase.from('notifications').insert({
            user_id: userId,
            title: payload.title,
            body: payload.body,
            link: payload.link || 'mytickets',
            read: false,
          });
        }
      }
    } catch (e) {
      console.warn('notifyCustomer supabase failed', e);
    }
  }

  try {
    const raw = localStorage.getItem(CUSTOMER_KEY);
    const prev = raw ? JSON.parse(raw) : [];
    const next = [item, ...(Array.isArray(prev) ? prev : [])].slice(0, 80);
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(next));
  } catch {}
  try {
    window.dispatchEvent(new CustomEvent(CUSTOMER_EVENT, { detail: item }));
  } catch {}
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      const bc = new BroadcastChannel('nexus-customer-notify');
      bc.postMessage(item);
      bc.close();
    }
  } catch {}
}"""
    if old in t:
        t = t.replace(old, new, 1)
        print("notifyCustomer fixed")
    t = "/* customer-notif-supabase-v1 */\n" + t
    an.write_text(t)
else:
    print("agentNotify already")

pc = Path("src/context/PlatformContext.tsx")
p = pc.read_text()
if "customer-notif-merge-v1" not in p:
    old_set = "    if (notifs.data) setNotifications(notifs.data as AppNotification[]);"
    new_set = """    if (notifs.data) {
      let merged = notifs.data as AppNotification[];
      try {
        const email = (user?.email || '').trim().toLowerCase();
        if (email) {
          const raw = localStorage.getItem('nexus-customer-notif-v1');
          const local = raw ? JSON.parse(raw) : [];
          const mine = (Array.isArray(local) ? local : []).filter(
            (n: { customer_email?: string }) => (n.customer_email || '').toLowerCase() === email,
          );
          const ids = new Set(merged.map((n) => n.id));
          for (const n of mine) {
            if (n && n.id && !ids.has(n.id)) {
              merged = [n as AppNotification, ...merged];
              ids.add(n.id);
            }
          }
        }
      } catch { /* ignore */ }
      setNotifications(merged);
    }"""
    if old_set in p:
        p = p.replace(old_set, new_set, 1)
        print("merge local customer notifs")

    marker = "  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);"
    inject = marker + """

  useEffect(() => {
    const email = (user?.email || '').trim().toLowerCase();
    if (!email) return;
    const pullLocal = () => {
      try {
        const raw = localStorage.getItem('nexus-customer-notif-v1');
        const local = raw ? JSON.parse(raw) : [];
        const mine = (Array.isArray(local) ? local : []).filter(
          (n: { customer_email?: string }) => (n.customer_email || '').toLowerCase() === email,
        );
        if (!mine.length) return;
        setNotifications((prev) => {
          const ids = new Set(prev.map((n) => n.id));
          const add = mine.filter((n: { id?: string }) => n.id && !ids.has(n.id));
          return add.length ? [...(add as AppNotification[]), ...prev] : prev;
        });
      } catch { /* ignore */ }
    };
    pullLocal();
    const onEvt = () => pullLocal();
    window.addEventListener('nexus-customer-notify', onEvt);
    window.addEventListener('storage', onEvt);
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-customer-notify');
      bc.onmessage = () => pullLocal();
    } catch { /* ignore */ }
    const tick = window.setInterval(pullLocal, 12000);
    return () => {
      window.removeEventListener('nexus-customer-notify', onEvt);
      window.removeEventListener('storage', onEvt);
      try { bc?.close(); } catch { /* ignore */ }
      window.clearInterval(tick);
    };
  }, [user?.email]);
"""
    if marker in p and "nexus-customer-notify" not in p:
        p = p.replace(marker, inject, 1)
        print("customer notif listener")

    p = "/* customer-notif-merge-v1 */\n" + p
    pc.write_text(p)
else:
    print("pc already")
print("done")
