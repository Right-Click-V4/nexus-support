#!/usr/bin/env python3
"""When claimer Approves assist, broadcast so requester unlocks send + UI."""
from pathlib import Path

pc = Path("src/context/PlatformContext.tsx")
if pc.exists() and pc.stat().st_size > 5000:
    t = pc.read_text()
    if "ASSIST_ACCEPT_BCAST_V5" not in t and "respondAssist" in t:
        marker = "const respondAssist = async (conversationId: string, agentId: string, accept: boolean)"
        if marker in t:
            start = t.find(marker)
            window = t[start : start + 1200]
            if "writeAssistLocal(conversationId, local.assistants, local.requests);" in window and "ASSIST_ACCEPT_BCAST_V5" not in window:
                inject = """
    writeAssistLocal(conversationId, local.assistants, local.requests);
    // ASSIST_ACCEPT_BCAST_V5 — tell requester they can send (or were denied)
    try {
      if (supabase) {
        const ch = supabase.channel('nexus-assist-global');
        await ch.subscribe();
        await ch.send({
          type: 'broadcast',
          event: 'assist-respond',
          payload: { conversationId, agentId, accept: !!accept, at: Date.now() },
        });
        try { supabase.removeChannel(ch); } catch {}
      }
    } catch (e) {
      console.warn('assist respond broadcast', e);
    }
    try {
      window.dispatchEvent(
        new CustomEvent('nexus-assist-respond', {
          detail: { conversationId, agentId, accept: !!accept },
        }),
      );
    } catch {}
"""
                old_line = "writeAssistLocal(conversationId, local.assistants, local.requests);"
                abs_idx = t.find(old_line, start)
                if abs_idx > 0 and abs_idx < start + 800:
                    end_line = abs_idx + len(old_line)
                    t = t[:abs_idx] + inject.strip() + t[end_line:]
                    print("accept broadcast injected")
                else:
                    print("writeAssistLocal pos miss")
            else:
                print("already or no writeAssistLocal in respond window")
        else:
            print("respondAssist not found")
        pc.write_text(t)
        print("PC", len(t), "ACCEPT_BCAST", "ASSIST_ACCEPT_BCAST_V5" in t)
    else:
        print("PC skip", "ASSIST_ACCEPT_BCAST_V5" in t)

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip LC")
    raise SystemExit(0)

t = lp.read_text()

if "ASSIST_RESPOND_RT_V5" not in t and "ASSIST_RT_SUB_V4" in t:
    idx = t.find("ASSIST_RT_SUB_V4")
    if idx > 0:
        sub_idx = t.find(".subscribe();", idx)
        if sub_idx > 0 and sub_idx < idx + 2000:
            insert_on = """
      .on('broadcast', { event: 'assist-respond' }, (payload: { payload?: { conversationId?: string; agentId?: string; accept?: boolean } }) => {
        // ASSIST_RESPOND_RT_V5
        const cid = payload?.payload?.conversationId;
        const aid = payload?.payload?.agentId;
        const accept = !!payload?.payload?.accept;
        if (!cid || !aid) return;
        try {
          const key = 'nexus-chat-assist-' + cid;
          const raw = localStorage.getItem(key);
          const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
          data.requests = (data.requests || []).filter((id: string) => id !== aid);
          if (accept) {
            if (!data.assistants.includes(aid)) data.assistants.push(aid);
          } else {
            data.assistants = (data.assistants || []).filter((id: string) => id !== aid);
          }
          localStorage.setItem(key, JSON.stringify(data));
        } catch {}
        if (accept && aid === myId) {
          setMsg('Your assist request was approved — you can send messages now');
        } else if (!accept && aid === myId) {
          setMsg('Your assist request was declined');
        }
        try { void refreshPlatform?.(); } catch {}
        setLiveAssistReqs((prev) => prev.filter((x) => x !== aid));
      })
"""
            t = t[:sub_idx] + insert_on + t[sub_idx:]
            print("respond RT listener added")
        else:
            print("subscribe in RT block miss")
    else:
        print("ASSIST_RT_SUB_V4 miss")
elif "ASSIST_RESPOND_RT_V5" in t:
    print("respond RT already")

if "ASSIST_RESPOND_WIN_V5" not in t:
    listener = """
  // ASSIST_RESPOND_WIN_V5
  useEffect(() => {
    const onRespond = (ev: Event) => {
      try {
        const d = (ev as CustomEvent).detail || {};
        const cid = d.conversationId as string | undefined;
        const aid = d.agentId as string | undefined;
        const accept = !!d.accept;
        if (!cid || !aid) return;
        try {
          const key = 'nexus-chat-assist-' + cid;
          const raw = localStorage.getItem(key);
          const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
          data.requests = (data.requests || []).filter((id: string) => id !== aid);
          if (accept) {
            if (!data.assistants.includes(aid)) data.assistants.push(aid);
          } else {
            data.assistants = (data.assistants || []).filter((id: string) => id !== aid);
          }
          localStorage.setItem(key, JSON.stringify(data));
        } catch {}
        if (accept && aid === myId) setMsg('Your assist request was approved — you can send messages now');
        if (!accept && aid === myId) setMsg('Your assist request was declined');
        try { void refreshPlatform?.(); } catch {}
      } catch {}
    };
    window.addEventListener('nexus-assist-respond', onRespond as EventListener);
    const poll = window.setInterval(() => {
      if (!selectedId || !myId) return;
      try {
        const raw = localStorage.getItem('nexus-chat-assist-' + selectedId);
        if (!raw) return;
        const data = JSON.parse(raw) as { assistants?: string[] };
        if ((data.assistants || []).includes(myId)) {
          void refreshPlatform?.();
        }
      } catch {}
    }, 2000);
    return () => {
      window.removeEventListener('nexus-assist-respond', onRespond as EventListener);
      window.clearInterval(poll);
    };
  }, [selectedId, myId, refreshPlatform]);
"""
    if "ASSIST_RT_SUB_V4" in t:
        idx = t.find("ASSIST_RT_SUB_V4")
        end = t.find("}, [selectedId, refreshPlatform]);", idx)
        if end > 0:
            end = end + len("}, [selectedId, refreshPlatform]);")
            t = t[:end] + "\n" + listener + t[end:]
            print("window respond listener")
        else:
            print("RT end miss")
    else:
        print("no RT to anchor window listener")

if "ASSIST_ASSISTANTS_FORCE_V5" not in t and "const isAssistant = Boolean(myId && assistantIds.includes(myId));" in t:
    t = t.replace(
        "const isAssistant = Boolean(myId && assistantIds.includes(myId));",
        """const isAssistant = Boolean(myId && assistantIds.includes(myId));
  // ASSIST_ASSISTANTS_FORCE_V5 — also treat approved local assist as sendable
  const canSendAsAgentForced = Boolean(
    !ownerId || isOwner || isAssistant ||
    (() => {
      try {
        if (!selectedId || !myId) return false;
        const raw = localStorage.getItem('nexus-chat-assist-' + selectedId);
        if (!raw) return false;
        return (JSON.parse(raw) as { assistants?: string[] }).assistants?.includes(myId) || false;
      } catch { return false; }
    })(),
  );""",
        1,
    )
    if "canSendAsAgentForced" in t:
        t = t.replace(
            "const canSendAsAgent = !ownerId || isOwner || isAssistant;",
            "const canSendAsAgent = canSendAsAgentForced;",
            1,
        )
        print("canSendAsAgent forced")

print("braces", t.count("{") - t.count("}"), "parens", t.count("(") - t.count(")"))
lp.write_text(t)
print("done", len(t), "RESPOND_RT", "ASSIST_RESPOND_RT_V5" in t, "WIN", "ASSIST_RESPOND_WIN_V5" in t)
