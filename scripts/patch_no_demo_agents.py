#!/usr/bin/env python3
"""Remove demo seed agents from Active Now; require real presence when Supabase is on."""
from pathlib import Path
import re

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    t = tc.read_text()
    if "no-demo-agents-v1" not in t:
        t = t.replace(
            "const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);",
            "const [agents, setAgents] = useState<Agent[]>(() => (isSupabaseConfigured ? [] : INITIAL_AGENTS));",
            1,
        )
        t = t.replace(
            "const agentList = filterAgents((agentRows || []).map(hydrateAvatar));\n      if (agentRows) setAgents(agentList);",
            "const agentList = filterAgents((agentRows || []).map(hydrateAvatar)).filter(\n"
            "        (a) => !['1','2','3','4','5','6'].includes(String(a.id)) &&\n"
            "          !['Sarah Chen','Marcus Reed','Aisha Lane','Tom\u00e1s Garc\u00eda','Tomas Garcia','Rachel Kim','David Okonkwo'].includes(a.name),\n"
            "      );\n"
            "      if (aRes && typeof aRes === 'object' && 'data' in aRes) setAgents(agentList);",
            1,
        )
        t2, n = re.subn(
            r"function filterAgents\(list: Agent\[\]\): Agent\[\] \{[\s\S]*?\n\}",
            """function filterAgents(list: Agent[]): Agent[] {
  const DEMO_IDS = new Set(['1', '2', '3', '4', '5', '6']);
  const DEMO_NAMES = new Set([
    'sarah chen', 'marcus reed', 'aisha lane', 'tom\u00e1s garc\u00eda', 'tomas garcia',
    'rachel kim', 'david okonkwo',
  ]);
  const seen = new Set<string>();
  return list.filter((a) => {
    if (isSupabaseConfigured) {
      if (DEMO_IDS.has(String(a.id))) return false;
      if (DEMO_NAMES.has((a.name || '').toLowerCase())) return false;
    }
    const key = (a.email || a.name || a.id).toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}""",
            t,
            count=1,
        )
        if n:
            t = t2
        t = "/* no-demo-agents-v1 */\n" + t
        tc.write_text(t)
        print("tc")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "active-now-real-only-v1" not in p:
        new = """  const onlineAgents = useMemo(() => {
    const now = Date.now();
    const LIVE_WINDOW_MS = 120_000;
    const DEMO_NAMES = new Set([
      'sarah chen', 'marcus reed', 'aisha lane', 'tom\u00e1s garc\u00eda', 'tomas garcia',
      'rachel kim', 'david okonkwo',
    ]);
    return (agents || []).filter((a) => {
      if (['1', '2', '3', '4', '5', '6'].includes(String(a.id))) return false;
      if (DEMO_NAMES.has((a.name || '').toLowerCase())) return false;
      const st = (a.approval_status || 'approved').toLowerCase();
      if (st && st !== 'approved' && st !== 'active') return false;
      const status = (a.status || 'offline').toLowerCase();
      if (status === 'offline' || status === '') return false;
      const seen = a.last_seen_at ? new Date(a.last_seen_at).getTime() : 0;
      if (!seen || Number.isNaN(seen) || now - seen > LIVE_WINDOW_MS) return false;
      return status === 'online' || status === 'busy' || status === 'away' || status === 'in_call' || status === 'custom';
    });
  }, [agents, presenceTick]);"""
        m = re.search(
            r"const onlineAgents = useMemo\(\(\) => \{[\s\S]*?\}, \[agents, presenceTick\]\);",
            p,
        )
        if m:
            p = p[: m.start()] + new + p[m.end() :]
        p = "/* active-now-real-only-v1 */\n" + p
        plc.write_text(p)
        print("plc")
print("done")
