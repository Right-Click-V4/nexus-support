#!/usr/bin/env python3
"""Wire desk presence: Agent Workspace publishes, Customer Active Now subscribes."""
from pathlib import Path
import re

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "desk-presence-publish-v1" not in s:
        if "deskPresence" not in s:
            s = s.replace(
                "from './context/TicketContext';",
                "from './context/TicketContext';\nimport { publishDeskPresence, clearDeskPresence } from './lib/deskPresence';",
                1,
            )
        old = """  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {
      void setPresenceStatus('online');
    } else {
      void touchPresence?.();
    }
    void touchPresence?.();
    const quick = window.setTimeout(() => { void touchPresence?.(); }, 500);
    return () => window.clearTimeout(quick);
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!presenceAgent?.id) return;
    const tick = () => { void touchPresence?.(); };
    tick();
    const id = window.setInterval(tick, 5000);
    return () => window.clearInterval(id);
  }, [presenceAgent?.id, touchPresence]);"""
        new = """  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {
      void setPresenceStatus('online');
    }
    void touchPresence?.();
    void publishDeskPresence({
      id: presenceAgent.id,
      name: presenceAgent.name || 'Agent',
      status: presenceAgent.status || 'online',
      avatar_url: presenceAgent.avatar_url,
      initials: presenceAgent.initials,
      color: presenceAgent.color,
    });
    const quick = window.setTimeout(() => {
      void touchPresence?.();
      void publishDeskPresence({
        id: presenceAgent.id,
        name: presenceAgent.name || 'Agent',
        status: (presenceAgent.status || 'online') === 'offline' ? 'online' : (presenceAgent.status || 'online'),
        avatar_url: presenceAgent.avatar_url,
        initials: presenceAgent.initials,
        color: presenceAgent.color,
      });
    }, 400);
    return () => window.clearTimeout(quick);
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!presenceAgent?.id) return;
    const tick = () => {
      void touchPresence?.();
      void publishDeskPresence({
        id: presenceAgent.id,
        name: presenceAgent.name || 'Agent',
        status: (presenceAgent.status || 'online') === 'offline' ? 'online' : (presenceAgent.status || 'online'),
        avatar_url: presenceAgent.avatar_url,
        initials: presenceAgent.initials,
        color: presenceAgent.color,
      });
    };
    tick();
    const id = window.setInterval(tick, 4000);
    return () => {
      window.clearInterval(id);
      void clearDeskPresence(presenceAgent.id);
    };
  }, [presenceAgent?.id, presenceAgent?.status, presenceAgent?.name, touchPresence]);"""
        if old in s:
            s = s.replace(old, new, 1)
        s = "/* desk-presence-publish-v1 */\n" + s
        sa.write_text(s)
        print("sa")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "desk-presence-active-now-v1" not in p:
        if "deskPresence" not in p:
            p = p.replace(
                "from '../lib/chatAttachments';",
                "from '../lib/chatAttachments';\nimport { watchDeskPresence, type DeskAgent } from '../lib/deskPresence';",
                1,
            )
        if "deskAgents" not in p:
            p = p.replace(
                "const [presenceTick, setPresenceTick] = useState(0);",
                "const [deskAgents, setDeskAgents] = useState<DeskAgent[]>([]);\n  const [presenceTick, setPresenceTick] = useState(0);\n  useEffect(() => {\n    return watchDeskPresence(setDeskAgents);\n  }, []);",
                1,
            )
        if "watchDeskPresence(setDeskAgents)" not in p:
            p = p.replace(
                "const [presenceTick, setPresenceTick] = useState(0);",
                "const [presenceTick, setPresenceTick] = useState(0);\n  useEffect(() => {\n    return watchDeskPresence(setDeskAgents);\n  }, []);",
                1,
            )
        new_online = """  const onlineAgents = useMemo(() => {
    const DEMO_NAMES = new Set([
      'sarah chen', 'marcus reed', 'aisha lane', 'tom\u00e1s garc\u00eda', 'tomas garcia',
      'rachel kim', 'david okonkwo',
    ]);
    const isDemo = (id: string, name: string) =>
      ['1', '2', '3', '4', '5', '6'].includes(String(id)) || DEMO_NAMES.has((name || '').toLowerCase());
    const now = Date.now();
    const LIVE_WINDOW_MS = 180_000;
    const byId = new Map<string, {
      id: string; name: string; status: string; avatar_url?: string | null;
      initials?: string; color?: string; last_seen_at?: string | null;
    }>();
    for (const a of agents || []) {
      if (isDemo(String(a.id), a.name || '')) continue;
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved' && st !== 'active') continue;
      const status = (a.status || 'offline').toLowerCase();
      if (status === 'offline' || status === '') continue;
      const seen = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
      const fresh = seen && !Number.isNaN(seen) && now - seen <= LIVE_WINDOW_MS;
      const realId = String(a.id).includes('-') || String(a.id).length > 10;
      if (fresh || (realId && status !== 'offline')) byId.set(String(a.id), a);
    }
    for (const d of deskAgents || []) {
      if (isDemo(String(d.id), d.name || '')) continue;
      const status = (d.status || 'online').toLowerCase();
      if (status === 'offline') continue;
      const prev = byId.get(String(d.id));
      byId.set(String(d.id), {
        id: d.id,
        name: d.name || prev?.name || 'Agent',
        status,
        avatar_url: d.avatar_url ?? prev?.avatar_url,
        initials: d.initials || prev?.initials,
        color: d.color || prev?.color,
        last_seen_at: new Date(d.at || now).toISOString(),
      });
    }
    return Array.from(byId.values());
  }, [agents, presenceTick, deskAgents]);"""
        m = re.search(
            r"const onlineAgents = useMemo\(\(\) => \{[\s\S]*?\}, \[agents, presenceTick[^\]]*\]\);",
            p,
        )
        if m:
            p = p[: m.start()] + new_online + p[m.end() :]
        p = "/* desk-presence-active-now-v1 */\n" + p
        plc.write_text(p)
        print("plc")

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    t = tc.read_text()
    if "touch-presence-status-v1" not in t:
        old_tp = """  const touchPresence = async () => {
    if (!currentAgent || !supabase) return;
    if ((currentAgent.status || 'offline') === 'offline') return;
    const seen = new Date().toISOString();
    setCurrentAgent((prev) => (prev ? { ...prev, last_seen_at: seen } : prev));
    setAgents((prev) =>
      prev.map((a) => (a.id === currentAgent.id ? { ...a, last_seen_at: seen } : a)),
    );
    try {
      const { error } = await supabase
        .from('agents')
        .update({ last_seen_at: seen })
        .eq('id', currentAgent.id);
      if (error) {
        await supabase.from('agents').update({ status: currentAgent.status || 'online' }).eq('id', currentAgent.id);
      }
    } catch {
      /* ignore */
    }
  };"""
        new_tp = """  const touchPresence = async () => {
    if (!currentAgent || !supabase) return;
    const status =
      (currentAgent.status || 'offline') === 'offline' ? 'online' : (currentAgent.status || 'online');
    const seen = new Date().toISOString();
    setCurrentAgent((prev) => (prev ? { ...prev, last_seen_at: seen, status } : prev));
    setAgents((prev) =>
      prev.map((a) => (a.id === currentAgent.id ? { ...a, last_seen_at: seen, status } : a)),
    );
    try {
      const { error } = await supabase
        .from('agents')
        .update({ last_seen_at: seen, status })
        .eq('id', currentAgent.id);
      if (error) {
        await supabase.from('agents').update({ status }).eq('id', currentAgent.id);
      }
    } catch {
      /* ignore */
    }
  };"""
        if old_tp in t:
            t = t.replace(old_tp, new_tp, 1)
        t = "/* touch-presence-status-v1 */\n" + t
        tc.write_text(t)
        print("tc")
print("done")
