#!/usr/bin/env python3
"""Approve/request assist via chat system messages so unlock uses working message realtime."""
from pathlib import Path

MARKER_REQ = "__ASSIST_REQ__:"
MARKER_OK = "__ASSIST_OK__:"
MARKER_NO = "__ASSIST_NO__:"

pc = Path("src/context/PlatformContext.tsx")
if not pc.exists() or pc.stat().st_size < 5000:
    print("skip PC")
else:
    t = pc.read_text()
    if "ASSIST_MSG_V7" not in t and "respondAssist" in t:
        marker = "const respondAssist = async (conversationId: string, agentId: string, accept: boolean)"
        start = t.find(marker)
        if start < 0:
            print("respondAssist not found")
        else:
            end_cand = t.find("\n  const claimChat", start)
            if end_cand < 0:
                end_cand = t.find("\n  const setChatStatus", start)
            if end_cand < 0:
                end_cand = t.find("\n  const archiveChat", start)
            if end_cand < 0:
                print("end of respondAssist miss")
            else:
                inject = f"""
    // ASSIST_MSG_V7 — persist approve/deny as system message (works cross-browser via chat realtime)
    try {{
      const flag = accept ? '{MARKER_OK}' : '{MARKER_NO}';
      const text = flag + agentId;
      const sysMsg = {{
        id: `m-assist-${{Date.now()}}`,
        text,
        sender: 'agent' as const,
        created_at: new Date().toISOString(),
        author: 'system',
      }};
      setConversations((prev) =>
        prev.map((c) => {{
          if (c.id !== conversationId) return c;
          const msgs = [...(c.messages || [])];
          if (!msgs.some((m) => m.text === text)) msgs.push(sysMsg);
          return {{ ...c, messages: msgs, updated_at: sysMsg.created_at }};
        }}),
      );
      if (supabase) {{
        try {{
          await supabase.from('chat_messages').insert({{
            conversation_id: conversationId,
            text,
            sender: 'agent',
            author: 'system',
          }});
        }} catch (e) {{
          console.warn('assist msg insert', e);
        }}
      }}
      try {{
        if (typeof BroadcastChannel !== 'undefined') {{
          const bc = new BroadcastChannel('nexus-chat-rt');
          bc.postMessage({{ type: 'assist', conversationId, agentId, accept: !!accept }});
          bc.close();
        }}
      }} catch {{}}
    }} catch (e) {{
      console.warn('assist sysmsg', e);
    }}
"""
                t = t[:end_cand] + inject + t[end_cand:]
                print("respondAssist sysmsg injected")

        marker2 = "const requestAssist = async (conversationId: string, agentId: string)"
        start2 = t.find(marker2)
        end2 = t.find("const respondAssist = async", start2)
        if start2 > 0 and end2 > start2 and "ASSIST_MSG_REQ_V7" not in t[start2:end2]:
            inject_req = f"""
    // ASSIST_MSG_REQ_V7
    try {{
      const text = '{MARKER_REQ}' + agentId;
      const sysMsg = {{
        id: `m-assist-req-${{Date.now()}}`,
        text,
        sender: 'agent' as const,
        created_at: new Date().toISOString(),
        author: 'system',
      }};
      setConversations((prev) =>
        prev.map((c) => {{
          if (c.id !== conversationId) return c;
          const msgs = [...(c.messages || [])];
          if (!msgs.some((m) => m.text === text)) msgs.push(sysMsg);
          return {{ ...c, messages: msgs }};
        }}),
      );
      if (supabase) {{
        try {{
          await supabase.from('chat_messages').insert({{
            conversation_id: conversationId,
            text,
            sender: 'agent',
            author: 'system',
          }});
        }} catch (e) {{
          console.warn('assist req msg', e);
        }}
      }}
    }} catch {{}}
"""
            t = t[:end2] + inject_req + t[end2:]
            print("requestAssist sysmsg injected")

        pc.write_text(t)
        print("PC", len(t))
    else:
        print("PC skip", "ASSIST_MSG_V7" in t)

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip LC")
    raise SystemExit(0)

t = lp.read_text()

if "ASSIST_PARSE_MSG_V7" not in t:
    effect = """
  // ASSIST_PARSE_MSG_V7 — apply assist flags from system messages (cross-browser)
  useEffect(() => {
    if (!selectedId || !selected?.messages?.length) return;
    let changed = false;
    try {
      const key = 'nexus-chat-assist-' + selectedId;
      const raw = localStorage.getItem(key);
      const data = raw ? JSON.parse(raw) : { assistants: [] as string[], requests: [] as string[] };
      data.assistants = data.assistants || [];
      data.requests = data.requests || [];
      for (const m of selected.messages) {
        const text = String(m.text || '');
        if (text.startsWith('__ASSIST_OK__:')) {
          const aid = text.slice('__ASSIST_OK__:'.length).trim();
          if (aid && !data.assistants.includes(aid)) { data.assistants.push(aid); changed = true; }
          data.requests = data.requests.filter((id: string) => id !== aid);
        } else if (text.startsWith('__ASSIST_NO__:')) {
          const aid = text.slice('__ASSIST_NO__:'.length).trim();
          data.requests = data.requests.filter((id: string) => id !== aid);
          data.assistants = data.assistants.filter((id: string) => id !== aid);
          changed = true;
        } else if (text.startsWith('__ASSIST_REQ__:')) {
          const aid = text.slice('__ASSIST_REQ__:'.length).trim();
          if (aid && !data.requests.includes(aid) && !data.assistants.includes(aid)) {
            data.requests.push(aid);
            changed = true;
          }
        }
      }
      if (changed) {
        localStorage.setItem(key, JSON.stringify(data));
        setLiveAssistReqs((prev) => prev.filter((id) => data.requests.includes(id) && !data.assistants.includes(id)));
      }
    } catch {}
  }, [selectedId, selected?.messages, selected?.updated_at]);
"""
    anchors = [
        "}, [selectedId, myId, refreshPlatform]);",
        "}, [selectedId, refreshPlatform]);",
    ]
    inserted = False
    for a in anchors:
        if a in t and "ASSIST_PARSE_MSG_V7" not in t:
            idx = t.rfind(a)
            if idx > 0:
                t = t[: idx + len(a)] + "\n" + effect + t[idx + len(a) :]
                inserted = True
                print("parse effect inserted")
                break
    if not inserted:
        idx = t.find("\n  return (")
        if idx > 0:
            t = t[:idx] + "\n" + effect + t[idx:]
            print("parse effect before return")
        else:
            print("parse effect miss")

if "ASSIST_FILTER_SYS_V7" not in t:
    helper = """
  // ASSIST_FILTER_SYS_V7
  const visibleMessages = (selected?.messages || []).filter((m) => {
    const text = String(m.text || '');
    if (text.startsWith('__ASSIST_OK__:')) return false;
    if (text.startsWith('__ASSIST_NO__:')) return false;
    if (text.startsWith('__ASSIST_REQ__:')) return false;
    return true;
  });
"""
    for anchor in [
        "const canSendAsAgent = canSendAsAgentForced;",
        "const canSendAsAgent = !ownerId || isOwner || isAssistant;",
        "const canSendAsAgent",
    ]:
        if anchor in t:
            idx = t.find(anchor)
            nl = t.find("\n", idx)
            t = t[: nl + 1] + helper + t[nl + 1 :]
            print("visibleMessages helper")
            break
    if "(selected.messages || []).map(" in t:
        t = t.replace("(selected.messages || []).map(", "visibleMessages.map(", 1)
        print("map uses visibleMessages")
    elif "(selected?.messages || []).map(" in t:
        t = t.replace("(selected?.messages || []).map(", "visibleMessages.map(", 1)
        print("map uses visibleMessages optional")

print("braces", t.count("{") - t.count("}"), "parens", t.count("(") - t.count(")"))
lp.write_text(t)
print("done LC", len(t), "PARSE", "ASSIST_PARSE_MSG_V7" in t, "FILTER", "ASSIST_FILTER_SYS_V7" in t)
