#!/usr/bin/env python3
"""Dark Live Chat + real-time agent viewers (uses src/lib/chatPresence.ts)."""
from pathlib import Path
import re

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "livechat-dark-presence-v1" not in p:
        if "chatPresence" not in p:
            p = p.replace(
                "from '../lib/chatAttachments';",
                "from '../lib/chatAttachments';\nimport { watchChatViewers, type ChatViewer } from '../lib/chatPresence';",
                1,
            )
        if "const [chatViewers" not in p:
            p = p.replace(
                "const [chatId, setChatId] = useState<string | null>(() => sessionStorage.getItem(STORAGE_KEY));",
                "const [chatId, setChatId] = useState<string | null>(() => sessionStorage.getItem(STORAGE_KEY));\n  const [chatViewers, setChatViewers] = useState<ChatViewer[]>([]);",
                1,
            )
        if "watchChatViewers(chatId" not in p:
            needle = "const messages = conversation?.messages || [];"
            if needle in p:
                p = p.replace(
                    needle,
                    needle
                    + """
  useEffect(() => {
    return watchChatViewers(chatId, setChatViewers);
  }, [chatId]);
  useEffect(() => {
    if (!chatId) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 4000);
    return () => window.clearInterval(id);
  }, [chatId, refreshPlatform]);
""",
                    1,
                )
        for a, b in [
            ("bg-white/40 dark:bg-black/25 backdrop-blur-xl", "bg-white/50 dark:bg-zinc-950/80 backdrop-blur-xl"),
            ("bg-white/50 dark:bg-black/30 backdrop-blur-md", "bg-white/55 dark:bg-zinc-950/70 backdrop-blur-md"),
            ("bg-white/45 dark:bg-black/30 backdrop-blur-md", "bg-white/50 dark:bg-zinc-950/75 backdrop-blur-md"),
            ("bg-white/70 dark:bg-zinc-900/60", "bg-white/75 dark:bg-zinc-900/80"),
            (
                "min-h-[min(70vh,640px)] portal-overview-glass rounded-2xl overflow-hidden border border-white/15",
                "min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/50 dark:border-white/10 bg-white/50 dark:bg-zinc-950/80 backdrop-blur-xl shadow-lg shadow-black/10",
            ),
        ]:
            p = p.replace(a, b)
        old_sub = "{conversation?.status === 'ended' ? 'Chat ended' : 'Connected with support'}"
        new_sub = "{conversation?.status === 'ended' ? 'Chat ended' : chatViewers.length > 0 ? `Connected · ${chatViewers.map((v) => v.name).join(', ')}` : 'Connected with support'}"
        if old_sub in p:
            p = p.replace(old_sub, new_sub, 1)
        if "chatViewers.map((v)" not in p and "Connected ·" in p:
            p = p.replace(
                new_sub,
                new_sub
                + """
            {conversation?.status !== 'ended' && chatViewers.length > 0 && (
              <div className=\"flex flex-wrap gap-1 mt-1\">
                {chatViewers.map((v) => (
                  <span key={v.id} className=\"inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/25\">
                    <span className=\"w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse\" />
                    {v.name}
                  </span>
                ))}
              </div>
            )}""",
                1,
            )
        p = "/* livechat-dark-presence-v1 */\n" + p
        plc.write_text(p)
        print("plc")
    else:
        print("plc already")

lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists():
    l = lcp.read_text()
    # Dedupe imports always
    lines = l.splitlines(True)
    seen = False
    out = []
    for line in lines:
        if "import { useTickets } from '../context/TicketContext';" in line:
            if seen:
                continue
            seen = True
        out.append(line)
    l = "".join(out)
    l = re.sub(
        r"(const \{ currentAgent, createTicket, findTicket \} = useTickets\(\);\n)(?:const \{[^}]*\} = useTickets\(\);\n)+",
        r"\1",
        l,
    )
    l = re.sub(
        r"const \{ currentAgent, createTicket, findTicket \} = useTickets\(\);\n\s*const \{ createTicket, findTicket \} = useTickets\(\);",
        "const { currentAgent, createTicket, findTicket } = useTickets();",
        l,
    )

    if "chat-viewer-publish-v1" not in l:
        if "chatPresence" not in l:
            if "from '../context/TicketContext'" in l:
                l = l.replace(
                    "from '../context/PlatformContext';",
                    "from '../context/PlatformContext';\nimport { publishChatViewer, clearChatViewer } from '../lib/chatPresence';",
                    1,
                )
            else:
                l = l.replace(
                    "from '../context/PlatformContext';",
                    "from '../context/PlatformContext';\nimport { useTickets } from '../context/TicketContext';\nimport { publishChatViewer, clearChatViewer } from '../lib/chatPresence';",
                    1,
                )
        if "currentAgent" not in l:
            if "const { createTicket, findTicket } = useTickets();" in l:
                l = l.replace(
                    "const { createTicket, findTicket } = useTickets();",
                    "const { currentAgent, createTicket, findTicket } = useTickets();",
                    1,
                )
            elif "useTickets()" not in l:
                l = re.sub(
                    r"const \{([^}]+)\} = usePlatform\(\);",
                    lambda m: m.group(0) + "\n  const { currentAgent, createTicket, findTicket } = useTickets();",
                    l,
                    count=1,
                )
        if "if (!selectedId || !currentAgent)" not in l:
            effect = """
  useEffect(() => {
    if (!selectedId || !currentAgent) return;
    const beat = () =>
      publishChatViewer(selectedId, { id: currentAgent.id, name: currentAgent.name || 'Agent' });
    beat();
    const t = window.setInterval(beat, 5000);
    return () => {
      window.clearInterval(t);
      clearChatViewer(selectedId, currentAgent.id);
    };
  }, [selectedId, currentAgent?.id, currentAgent?.name]);
"""
            if "const selected = conversations.find" in l:
                l = l.replace(
                    "const selected = conversations.find",
                    effect + "\n  const selected = conversations.find",
                    1,
                )
        if "linkTicketId," in l and "refreshPlatform" not in l.split("= usePlatform")[0][-250:]:
            l = l.replace("linkTicketId,", "linkTicketId,\n    refreshPlatform,", 1)
        if "void refreshPlatform(); }, 4000)" not in l and "refreshPlatform" in l:
            if "const selected = conversations.find" in l:
                l = l.replace(
                    "const selected = conversations.find",
                    """
  useEffect(() => {
    if (!selectedId) return;
    const id = window.setInterval(() => { void refreshPlatform(); }, 4000);
    return () => window.clearInterval(id);
  }, [selectedId, refreshPlatform]);

  const selected = conversations.find""",
                    1,
                )
        l = "/* chat-viewer-publish-v1 */\n" + l
        print("lcp patched")
    else:
        print("lcp presence already")

    lcp.write_text(l)
print("done")
