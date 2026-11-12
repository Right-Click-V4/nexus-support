#!/usr/bin/env python3
"""Cross-browser assist via Supabase Realtime broadcast + modal pending state."""
from pathlib import Path

pc = Path("src/context/PlatformContext.tsx")
if pc.exists() and pc.stat().st_size > 5000:
    t = pc.read_text()
    if "ASSIST_BROADCAST_V4" not in t and "requestAssist" in t:
        marker = "const requestAssist = async (conversationId: string, agentId: string)"
        endm = "const respondAssist = async"
        if marker in t and endm in t:
            a, b = t.find(marker), t.find(endm)
            chunk = t[a:b]
            if "writeAssistLocal" in chunk and "ASSIST_BROADCAST_V4" not in chunk:
                idx = chunk.rfind("writeAssistLocal(")
                nl = chunk.find("\n", idx)
                if nl > 0:
                    inject = """
    // ASSIST_BROADCAST_V4 — notify claimer on other browsers/sessions
    try {
      if (supabase) {
        const ch = supabase.channel('nexus-assist-global');
        await ch.subscribe();
        await ch.send({
          type: 'broadcast',
          event: 'assist-request',
          payload: { conversationId, agentId, at: Date.now() },
        });
        try { supabase.removeChannel(ch); } catch {}
      }
    } catch (e) {
      console.warn('assist broadcast', e);
    }
    try {
      window.dispatchEvent(new CustomEvent('nexus-assist-request', { detail: { conversationId, agentId } }));
    } catch {}
"""
                    chunk = chunk[: nl + 1] + inject + chunk[nl + 1 :]
                    t = t[:a] + chunk + t[b:]
                    print("broadcast injected")
            else:
                print("writeAssistLocal miss or already")
        else:
            print("requestAssist bounds miss")
        pc.write_text(t)
        print("PC", len(t), "BCAST", "ASSIST_BROADCAST_V4" in t)
    else:
        print("PC skip/already", "ASSIST_BROADCAST_V4" in t)

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip LC")
    raise SystemExit(0)

t = lp.read_text()

if "from '../lib/supabase'" not in t and 'from "../lib/supabase"' not in t:
    t = "import { supabase } from '../lib/supabase';\n" + t
    print("supabase import")

if "ASSIST_LIVE_PENDING_V4" not in t:
    anchors = [
        "  const hasPendingMine = Boolean(myId && pendingRequests.includes(myId));",
        "  const canSendAsAgent = !ownerId || isOwner || isAssistant;",
        "  const isOwner = Boolean(myId && ownerId && myId === ownerId);",
    ]
    for an in anchors:
        if an in t:
            block = (
                an
                + """
  // ASSIST_LIVE_PENDING_V4
  const [liveAssistReqs, setLiveAssistReqs] = useState<string[]>([]);
  const effectivePending = Array.from(
    new Set([...(typeof pendingRequests !== 'undefined' ? pendingRequests : []), ...liveAssistReqs]),
  ).filter((id) => id && id !== myId);
"""
            )
            t = t.replace(an, block, 1)
            print("live pending via", an[:50])
            break

sub = """
  // ASSIST_RT_SUB_V4
  useEffect(() => {
    if (!supabase) return;
    const ch = supabase
      .channel('nexus-assist-global')
      .on('broadcast', { event: 'assist-request' }, (payload: { payload?: { conversationId?: string; agentId?: string } }) => {
        const cid = payload?.payload?.conversationId;
        const aid = payload?.payload?.agentId;
        if (!cid || !aid) return;
        try {
          const key = 'nexus-chat-assist-' + cid;
          const raw = localStorage.getItem(key);
          const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
          if (!data.requests.includes(aid)) data.requests.push(aid);
          localStorage.setItem(key, JSON.stringify(data));
        } catch {}
        if (selectedId && cid === selectedId) {
          setLiveAssistReqs((prev) => (prev.includes(aid) ? prev : [...prev, aid]));
          setMsg('Assist request received — approve or decline');
        } else {
          setMsg('Assist request on another chat');
        }
        try { void refreshPlatform?.(); } catch {}
      })
      .subscribe();
    return () => {
      try { supabase.removeChannel(ch); } catch {}
    };
  }, [selectedId, refreshPlatform]);
"""

if "ASSIST_RT_SUB_V4" not in t:
    marker = ").filter((id) => id && id !== myId);"
    if marker in t and "ASSIST_LIVE_PENDING_V4" in t:
        t = t.replace(marker, marker + "\n" + sub, 1)
        print("rt sub after filter")
    elif "id !== myId);" in t and "liveAssistReqs" in t:
        idx = t.find("liveAssistReqs")
        pos = t.find("id !== myId);", idx)
        if pos > 0:
            pos = pos + len("id !== myId);")
            t = t[:pos] + "\n" + sub + t[pos:]
            print("rt sub after myId")
        else:
            print("rt sub miss")
    else:
        idx = t.find("\n  return (")
        if idx > 0:
            t = t[:idx] + "\n" + sub + t[idx:]
            print("rt sub before return")
        else:
            print("rt sub miss")

if "effectivePending" in t:
    t = t.replace(
        "isOwner && pendingRequests.filter((id) => id !== myId).length > 0",
        "isOwner && effectivePending.length > 0",
    )
    t = t.replace(
        "pendingRequests.filter((id) => id !== myId).map((rid) =>",
        "effectivePending.map((rid) =>",
    )
    print("modal wired")

if "setLiveAssistReqs" in t:
    for accept in ["true", "false"]:
        old = f"if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, {accept});"
        if old in t:
            window = t[t.find(old) : t.find(old) + 180]
            if "setLiveAssistReqs((prev) => prev.filter" not in window:
                t = t.replace(
                    old,
                    old + "\n                          setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));",
                    1,
                )
    print("respond clears")

print("braces", t.count("{") - t.count("}"), "parens", t.count("(") - t.count(")"))
lp.write_text(t)
print(
    "done LC",
    len(t),
    "LIVE",
    "ASSIST_LIVE_PENDING_V4" in t,
    "RT",
    "ASSIST_RT_SUB_V4" in t,
    "CH",
    "nexus-assist-global" in t,
)
