#!/usr/bin/env python3
"""OVERVIEW_PRESENCE_V1: custom status green, MetricBar presence, customers online."""
from pathlib import Path
import re

# 1) portalPresence.ts
pp = Path('src/lib/portalPresence.ts')
pp.write_text('''/** PORTAL_PRESENCE_V1 - customers online while Customer Portal is open. */
export type PortalCustomer = {
  id: string;
  name: string;
  email?: string;
  at: number;
};

const KEY = 'nexus-portal-presence-v1';
const BC = 'nexus-portal-presence';
export const PORTAL_LIVE_MS = 90_000;

function read(): PortalCustomer[] {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function write(list: PortalCustomer[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      const bc = new BroadcastChannel(BC);
      bc.postMessage({ type: 'portal', list });
      bc.close();
    }
  } catch {
    /* ignore */
  }
  try {
    window.dispatchEvent(new CustomEvent('nexus-portal-presence', { detail: list }));
  } catch {
    /* ignore */
  }
}

export function getPortalPresence(now = Date.now()): PortalCustomer[] {
  return read().filter((c) => c?.id && now - (c.at || 0) < PORTAL_LIVE_MS);
}

export function publishPortalPresence(customer: { id: string; name?: string; email?: string }) {
  if (!customer?.id) return;
  const now = Date.now();
  const cleaned = read().filter((c) => c.id !== customer.id && now - (c.at || 0) < PORTAL_LIVE_MS);
  cleaned.push({
    id: customer.id,
    name: customer.name || customer.email || 'Customer',
    email: customer.email,
    at: now,
  });
  write(cleaned);
}

export function clearPortalPresence(id: string) {
  if (!id) return;
  write(read().filter((c) => c.id !== id));
}

export function watchPortalPresence(onChange: (list: PortalCustomer[]) => void): () => void {
  const emit = () => onChange(getPortalPresence());
  emit();
  const onEvt = () => emit();
  const onStorage = (e: StorageEvent) => {
    if (e.key === KEY) emit();
  };
  window.addEventListener('nexus-portal-presence', onEvt);
  window.addEventListener('storage', onStorage);
  let bc: BroadcastChannel | null = null;
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      bc = new BroadcastChannel(BC);
      bc.onmessage = () => emit();
    }
  } catch {
    /* ignore */
  }
  const tick = window.setInterval(emit, 10_000);
  return () => {
    window.removeEventListener('nexus-portal-presence', onEvt);
    window.removeEventListener('storage', onStorage);
    window.clearInterval(tick);
    try {
      bc?.close();
    } catch {
      /* ignore */
    }
  };
}
''')
print('portalPresence written', pp.stat().st_size)

# 2) PLC custom -> emerald
plc = Path('src/components/PortalLiveChat.tsx')
if plc.exists() and plc.stat().st_size > 5000:
    s = plc.read_text()
    s2 = s
    s2 = s2.replace("if (st === 'custom') return 'bg-white';", "if (st === 'custom') return 'bg-emerald-400';")
    s2 = s2.replace("if (st === 'custom') return 'w-1.5 h-1.5 rounded-full shrink-0 bg-white';", "if (st === 'custom') return 'w-1.5 h-1.5 rounded-full shrink-0 bg-emerald-400';")
    s2 = s2.replace("if (st === 'custom') return 'text-white font-medium';", "if (st === 'custom') return 'text-emerald-400 font-medium';")
    s2 = s2.replace("st === 'custom') return 'bg-white'", "st === 'custom') return 'bg-emerald-400'")
    if s2 != s:
        plc.write_text(s2)
        print('PLC custom green')
    else:
        print('PLC custom already or miss')

# 3) MetricBar
mb = Path('src/components/MetricBar.tsx')
if mb.exists():
    s = mb.read_text()
    if 'CUSTOMERS_ONLINE_V1' not in s:
        if "from '../lib/portalPresence'" not in s:
            s = s.replace(
                "import { useTickets } from '../context/TicketContext';",
                "import { useTickets } from '../context/TicketContext';\n"
                "import { watchDeskPresence, type DeskAgent } from '../lib/deskPresence';\n"
                "import { computeOnlineAgents } from '../lib/onlineAgents';\n"
                "import { watchPortalPresence, type PortalCustomer } from '../lib/portalPresence';",
                1,
            )
        s = s.replace(
            "const [lastSynced, setLastSynced] = useState(() => Date.now());",
            "const [lastSynced, setLastSynced] = useState(() => Date.now());\n"
            "  // CUSTOMERS_ONLINE_V1\n"
            "  const [deskAgents, setDeskAgents] = useState<DeskAgent[]>([]);\n"
            "  const [portalCustomers, setPortalCustomers] = useState<PortalCustomer[]>([]);\n"
            "  useEffect(() => watchDeskPresence(setDeskAgents), []);\n"
            "  useEffect(() => watchPortalPresence(setPortalCustomers), []);",
            1,
        )
        s = s.replace(
            "const agentsOnline = agents.filter((a) => a.status === 'online' || a.status === 'busy').length;\n"
            "    const agentsAway = agents.filter((a) => a.status === 'away').length;",
            "const onlineRows = computeOnlineAgents(agents, deskAgents, now);\n"
            "    const agentsOnline = onlineRows.length;\n"
            "    const agentsAway = agents.filter((a) => (a.status || '').toLowerCase() === 'away').length;\n"
            "    const customersOnline = portalCustomers.length;",
            1,
        )
        if 'customersOnline,' not in s:
            s = s.replace("agentsOnline,\n", "agentsOnline,\n      customersOnline,\n", 1)
        s = s.replace("[tickets, agents, now]", "[tickets, agents, now, deskAgents, portalCustomers]", 1)
        old = (
            '      <div className="h-8 w-px bg-white/10 hidden sm:block" />\n\n'
            '      <div className="flex flex-col min-w-[110px]">\n'
            '        <div className="text-[11px] uppercase tracking-wider text-zinc-400 font-medium">SLA score</div>'
        )
        new = (
            '      <div className="h-8 w-px bg-white/10 hidden sm:block" />\n\n'
            '      <div className="flex flex-col min-w-[110px]">\n'
            '        <div className="text-[11px] uppercase tracking-wider text-zinc-400 font-medium">Customers online</div>\n'
            '        <div className="flex items-end gap-2">\n'
            '          <span className="text-2xl font-bold tabular-nums">{metrics.customersOnline ?? 0}</span>\n'
            '          <Users size={16} className="text-sky-400 mb-1" />\n'
            '        </div>\n'
            '      </div>\n\n'
            '      <div className="h-8 w-px bg-white/10 hidden sm:block" />\n\n'
            '      <div className="flex flex-col min-w-[110px]">\n'
            '        <div className="text-[11px] uppercase tracking-wider text-zinc-400 font-medium">SLA score</div>'
        )
        if old in s and 'Customers online' not in s:
            s = s.replace(old, new, 1)
            print('MetricBar UI')
        mb.write_text(s)
        print('MetricBar braces', s.count('{') - s.count('}'))
    else:
        print('MetricBar already')

# 4) SystemAppCore header
sac = Path('src/SystemAppCore.tsx')
if sac.exists() and sac.stat().st_size > 3000:
    s = sac.read_text()
    if 'portalOnlineCount' not in s:
        if "from './lib/deskPresence'" in s and 'portalPresence' not in s:
            s = s.replace(
                "from './lib/deskPresence';",
                "from './lib/deskPresence';\nimport { watchPortalPresence } from './lib/portalPresence';",
                1,
            )
        elif 'portalPresence' not in s:
            s = "import { watchPortalPresence } from './lib/portalPresence';\n" + s
        m = re.search(r'function AgentShell\([^)]*\) \{', s)
        if m:
            inject = (
                "\n  // CUSTOMERS_ONLINE_HEADER_V1\n"
                "  const [portalOnlineCount, setPortalOnlineCount] = useState(0);\n"
                "  useEffect(() => watchPortalPresence((list) => setPortalOnlineCount(list.length)), []);\n"
            )
            s = s[: m.end()] + inject + s[m.end() :]
        old = '<h1 className="text-sm font-semibold text-zinc-800 dark:text-zinc-100">{title}</h1>'
        new = (
            '<div className="flex items-center gap-3 min-w-0">\n'
            '            <h1 className="text-sm font-semibold text-zinc-800 dark:text-zinc-100">{title}</h1>\n'
            '            <span\n'
            '              className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border border-sky-500/30 bg-sky-500/10 text-sky-700 dark:text-sky-300"\n'
            '              title="Customers with Customer Portal open right now"\n'
            '            >\n'
            '              <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />\n'
            "              {portalOnlineCount} customer{portalOnlineCount === 1 ? '' : 's'} online\n"
            '            </span>\n'
            '          </div>'
        )
        if old in s:
            s = s.replace(old, new, 1)
            print('header chip')
        sac.write_text(s)
        print('SAC braces', s.count('{') - s.count('}'))
    else:
        print('SAC already')

# 5) CustomerPortal heartbeat
cp = Path('src/components/CustomerPortal.tsx')
if cp.exists() and cp.stat().st_size > 50000:
    s = cp.read_text()
    if 'publishPortalPresence' not in s:
        if "from '../context/AuthContext'" in s:
            s = s.replace(
                "from '../context/AuthContext';",
                "from '../context/AuthContext';\nimport { publishPortalPresence, clearPortalPresence } from '../lib/portalPresence';",
                1,
            )
        else:
            s = "import { publishPortalPresence, clearPortalPresence } from '../lib/portalPresence';\n" + s
        s = re.sub(
            r"import \{([^}]+)\} from 'react';",
            lambda m: (
                "import { " + m.group(1).strip().rstrip(',') + ", useEffect } from 'react';"
                if 'useEffect' not in m.group(1)
                else m.group(0)
            ),
            s,
            count=1,
        )
        inject = (
            "\n  // PORTAL_PRESENCE_V1\n"
            "  useEffect(() => {\n"
            "    const uid = user?.id || user?.email;\n"
            "    if (!uid) return;\n"
            "    const name =\n"
            "      (user?.user_metadata?.full_name as string | undefined)?.trim() ||\n"
            "      (user?.user_metadata?.name as string | undefined)?.trim() ||\n"
            "      user?.email?.split('@')[0] ||\n"
            "      'Customer';\n"
            "    const beat = () => publishPortalPresence({ id: String(uid), name, email: user?.email || undefined });\n"
            "    beat();\n"
            "    const id = window.setInterval(beat, 25_000);\n"
            "    return () => {\n"
            "      window.clearInterval(id);\n"
            "      clearPortalPresence(String(uid));\n"
            "    };\n"
            "  }, [user?.id, user?.email]);\n"
        )
        m = re.search(r"const \{[^}]*user[^}]*\} = useAuth\(\);", s)
        if m:
            s = s[: m.end()] + inject + s[m.end() :]
            print('CP presence')
        cp.write_text(s)
        print('CP braces', s.count('{') - s.count('}'))
    else:
        print('CP already')
else:
    print('CP skip')

print('patch_overview_presence_v1 done')
