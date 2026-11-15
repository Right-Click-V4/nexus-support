#!/usr/bin/env python3
"""Customer Live Chat inbox: list ongoing/ended chats before opening a conversation."""
from pathlib import Path
import re

plc = Path('src/components/PortalLiveChat.tsx')
if not plc.exists() or plc.stat().st_size < 5000:
    print('PortalLiveChat skip')
    raise SystemExit(0)

s = plc.read_text()
if 'LIVECHAT_INBOX_V1' in s:
    print('already')
    raise SystemExit(0)

if 'Inbox' not in s.split("from 'lucide-react'")[0]:
    s = re.sub(
        r"import \{([^}]+)\} from 'lucide-react';",
        lambda m: (
            "import { " + m.group(1).strip().rstrip(',') + ", Inbox } from 'lucide-react';"
            if 'Inbox' not in m.group(1)
            else m.group(0)
        ),
        s,
        count=1,
    )

if 'showStartForm' not in s:
    s = s.replace(
        "const [chatId, setChatId] = useState<string | null>(() => sessionStorage.getItem(STORAGE_KEY));",
        "const [chatId, setChatId] = useState<string | null>(() => sessionStorage.getItem(STORAGE_KEY));\n"
        "  // LIVECHAT_INBOX_V1\n"
        "  const [showStartForm, setShowStartForm] = useState(false);",
        1,
    )
    print('state')

inject_list = """
  // LIVECHAT_INBOX_V1 — customer's chats for inbox
  const myEmail = (user?.email || email || '').trim().toLowerCase();
  const myConversations = useMemo(() => {
    const list = (conversations || []).filter((c) => {
      const em = (c.customer_email || '').trim().toLowerCase();
      if (myEmail && em) return em === myEmail;
      const nm = (c.customer_name || '').trim().toLowerCase();
      const me = (accountName || name || '').trim().toLowerCase();
      return me && nm && nm === me;
    });
    const rank = (st: string) => {
      const x = (st || '').toLowerCase();
      if (x === 'active' || x === 'waiting' || x === 'on_hold' || x === 'open') return 0;
      return 1;
    };
    return [...list].sort((a, b) => {
      const ra = rank(a.status);
      const rb = rank(b.status);
      if (ra !== rb) return ra - rb;
      return new Date(b.updated_at || b.created_at || 0).getTime() - new Date(a.updated_at || a.created_at || 0).getTime();
    });
  }, [conversations, myEmail, accountName, name]);

  const isOngoingStatus = (st?: string) => {
    const x = (st || '').toLowerCase();
    return x === 'active' || x === 'waiting' || x === 'on_hold' || x === 'open' || x === '';
  };

  const openConversation = (id: string) => {
    setChatId(id);
    try { sessionStorage.setItem(STORAGE_KEY, id); } catch { /* ignore */ }
    setShowStartForm(false);
  };

  const goInbox = () => {
    try { sessionStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ }
    setChatId(null);
    setShowStartForm(false);
    setDraft('');
  };
"""

if 'myConversations' not in s:
    if "const isOnHold = ['on_hold', 'waiting'].includes((conversation?.status || '').toLowerCase());" in s:
        s = s.replace(
            "const isOnHold = ['on_hold', 'waiting'].includes((conversation?.status || '').toLowerCase());",
            "const isOnHold = ['on_hold', 'waiting'].includes((conversation?.status || '').toLowerCase());\n" + inject_list,
            1,
        )
        print('list helpers')
    else:
        s = s.replace(
            "const messages = conversation?.messages || [];",
            "const messages = conversation?.messages || [];\n" + inject_list,
            1,
        )
        print('list helpers soft')

s = s.replace(
    """        <button
          type="button"
          onClick={() => {
            sessionStorage.removeItem(STORAGE_KEY);
            setChatId(null);
          }}
          className="text-xs text-zinc-500 hover:text-rose-600 dark:hover:text-rose-400 px-2 py-1 rounded-lg hover:bg-white/40 dark:hover:bg-white/5"
        >
          End / new chat
        </button>""",
    """        <button
          type="button"
          onClick={goInbox}
          className="text-xs text-zinc-500 hover:text-rose-600 dark:hover:text-rose-400 px-2 py-1 rounded-lg hover:bg-white/40 dark:hover:bg-white/5"
        >
          Inbox
        </button>""",
    1,
)

inbox_block = '''
  if (!chatId) {
    // LIVECHAT_INBOX_V1
    if (!showStartForm) {
      return (
        <div className="w-full max-w-5xl mx-auto space-y-4">
          <div className="portal-overview-glass rounded-2xl p-5 sm:p-6">
            <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
              <div className="flex items-start gap-3 min-w-0">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/25 shrink-0">
                  <Inbox className="text-white" size={24} />
                </div>
                <div className="min-w-0">
                  <h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat Inbox</h1>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-0.5">
                    Open an ongoing chat or start a new conversation.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowStartForm(true)}
                className="shrink-0 px-4 py-2.5 text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 shadow-lg shadow-violet-500/25"
              >
                Start new chat
              </button>
            </div>

            {myConversations.length === 0 ? (
              <div className="rounded-xl border border-dashed border-zinc-300 dark:border-white/15 px-4 py-10 text-center">
                <p className="text-sm text-zinc-600 dark:text-zinc-300">No conversations yet.</p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Start a new chat to reach support.</p>
                <button
                  type="button"
                  onClick={() => setShowStartForm(true)}
                  className="mt-4 text-sm font-medium text-violet-600 dark:text-violet-300 hover:underline"
                >
                  Start new chat
                </button>
              </div>
            ) : (
              <ul className="space-y-2">
                {myConversations.map((c) => {
                  const ongoing = isOngoingStatus(c.status);
                  const agent = (agents || []).find((a) => a.id === c.agent_id);
                  const agentLabel = agent?.name || (ongoing ? 'Waiting for agent' : 'Support');
                  const when = c.updated_at || c.created_at;
                  let whenLabel = '';
                  try {
                    whenLabel = when
                      ? new Date(when).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })
                      : '';
                  } catch {
                    whenLabel = '';
                  }
                  return (
                    <li key={c.id}>
                      <button
                        type="button"
                        onClick={() => openConversation(c.id)}
                        className="w-full text-left rounded-xl border border-zinc-200 dark:border-white/10 bg-white/70 dark:bg-zinc-900/50 hover:bg-white dark:hover:bg-zinc-900/80 px-4 py-3 transition-colors"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                              <span
                                className={
                                  ongoing
                                    ? 'text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-md bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30'
                                    : 'text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-md bg-zinc-500/15 text-zinc-600 dark:text-zinc-300 border border-zinc-500/25'
                                }
                              >
                                {ongoing ? 'Ongoing' : 'Ended'}
                              </span>
                              {c.ticket_id ? (
                                <span className="text-[11px] font-mono text-zinc-500 dark:text-zinc-400">
                                  {c.ticket_id}
                                </span>
                              ) : null}
                              {c.branch ? (
                                <span className="text-[11px] text-zinc-500 dark:text-zinc-400 truncate">
                                  {c.branch}
                                </span>
                              ) : null}
                            </div>
                            <div className="mt-1 text-sm font-medium text-zinc-900 dark:text-zinc-100 truncate">
                              {agentLabel}
                            </div>
                            {c.preview ? (
                              <div className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2">
                                {c.preview}
                              </div>
                            ) : null}
                          </div>
                          <div className="shrink-0 text-[11px] text-zinc-400 dark:text-zinc-500 text-right">
                            {whenLabel}
                          </div>
                        </div>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      );
    }

    return (
'''

marker = '  if (!chatId) {\n    return ('
if marker in s:
    s = s.replace(marker, inbox_block, 1)
    print('inbox injected')
else:
    s2 = re.sub(r'  if \(!chatId\) \{\n    return \(', inbox_block, s, count=1)
    if s2 == s:
        print('inbox inject miss')
    else:
        s = s2
        print('inbox injected re')

s = s.replace(
    "setChatId(c.id);\n      sessionStorage.setItem(STORAGE_KEY, c.id);",
    "setChatId(c.id);\n      sessionStorage.setItem(STORAGE_KEY, c.id);\n      setShowStartForm(false);",
    1,
)

s = s.replace(
    '<h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>',
    '''<h1 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Live Chat</h1>
                  <button type="button" onClick={() => setShowStartForm(false)} className="text-xs text-violet-600 dark:text-violet-300 hover:underline mt-1">
                    ← Back to inbox
                  </button>''',
    1,
)

bal = s.count('{') - s.count('}')
plc.write_text(s)
print('braces', bal)
print('has inbox', 'LIVECHAT_INBOX_V1' in s)
if bal != 0:
    raise SystemExit(f'brace imbalance {bal}')
print('patch_livechat_inbox_v1 done')
