#!/usr/bin/env python3
"""Harden Approve/Deny: optimistic clear pending, reliable broadcast, unlock requester."""
from pathlib import Path

pc = Path("src/context/PlatformContext.tsx")
if pc.exists() and pc.stat().st_size > 5000:
    t = pc.read_text()
    if "ASSIST_BCAST_WAIT_V6" not in t:
        old_patterns = [
            """        const ch = supabase.channel('nexus-assist-global');
        await ch.subscribe();
        await ch.send({
          type: 'broadcast',
          event: 'assist-request',
          payload: { conversationId, agentId, at: Date.now() },
        });
        try { supabase.removeChannel(ch); } catch {}""",
            """        const ch = supabase.channel('nexus-assist-global');
        await ch.subscribe();
        await ch.send({
          type: 'broadcast',
          event: 'assist-respond',
          payload: { conversationId, agentId, accept: !!accept, at: Date.now() },
        });
        try { supabase.removeChannel(ch); } catch {}""",
        ]
        new_req = """        // ASSIST_BCAST_WAIT_V6
        const ch = supabase.channel('nexus-assist-global');
        await new Promise<void>((resolve) => {
          const t = window.setTimeout(() => resolve(), 1500);
          ch.subscribe((status) => {
            if (status === 'SUBSCRIBED') {
              window.clearTimeout(t);
              resolve();
            }
          });
        });
        await ch.send({
          type: 'broadcast',
          event: 'assist-request',
          payload: { conversationId, agentId, at: Date.now() },
        });
        try { supabase.removeChannel(ch); } catch {}"""
        new_resp = """        // ASSIST_BCAST_WAIT_V6
        const ch = supabase.channel('nexus-assist-global');
        await new Promise<void>((resolve) => {
          const t = window.setTimeout(() => resolve(), 1500);
          ch.subscribe((status) => {
            if (status === 'SUBSCRIBED') {
              window.clearTimeout(t);
              resolve();
            }
          });
        });
        await ch.send({
          type: 'broadcast',
          event: 'assist-respond',
          payload: { conversationId, agentId, accept: !!accept, at: Date.now() },
        });
        try { supabase.removeChannel(ch); } catch {}"""
        n = 0
        if old_patterns[0] in t:
            t = t.replace(old_patterns[0], new_req)
            n += 1
            print("fixed request broadcast wait")
        if old_patterns[1] in t:
            t = t.replace(old_patterns[1], new_resp)
            n += 1
            print("fixed respond broadcast wait")
        if n == 0 and "nexus-assist-global" in t:
            t = t.replace(
                "const ch = supabase.channel('nexus-assist-global');\n        await ch.subscribe();",
                """const ch = supabase.channel('nexus-assist-global');
        // ASSIST_BCAST_WAIT_V6
        await new Promise<void>((resolve) => {
          const t = window.setTimeout(() => resolve(), 1500);
          ch.subscribe((status) => {
            if (status === 'SUBSCRIBED') { window.clearTimeout(t); resolve(); }
          });
        });""",
            )
            print("soft wait on all assist channels")
        pc.write_text(t)
        print("PC", len(t))
    else:
        print("PC already wait v6")

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip LC")
    raise SystemExit(0)

t = lp.read_text()

old_approve = """                      onClick={() => {
                        void (async () => {
                          if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, true);
                          setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));
                          setMsg(label + ' can now assist on this chat');
                        })();
                      }}"""

new_approve = """                      onClick={() => {
                        void (async () => {
                          // ASSIST_APPROVE_V6 — optimistic unlock + clear pending
                          try {
                            const key = 'nexus-chat-assist-' + selected.id;
                            const raw = localStorage.getItem(key);
                            const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
                            data.requests = (data.requests || []).filter((id: string) => id !== rid);
                            if (!(data.assistants || []).includes(rid)) data.assistants = [...(data.assistants || []), rid];
                            localStorage.setItem(key, JSON.stringify(data));
                          } catch {}
                          setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));
                          try {
                            if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, true);
                          } catch (e) {
                            console.warn('respondAssist', e);
                          }
                          setMsg(label + ' can now assist on this chat');
                        })();
                      }}"""

old_deny = """                      onClick={() => {
                        void (async () => {
                          if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, false);
                          setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));
                          setMsg('Assist request from ' + label + ' declined');
                        })();
                      }}"""

new_deny = """                      onClick={() => {
                        void (async () => {
                          try {
                            const key = 'nexus-chat-assist-' + selected.id;
                            const raw = localStorage.getItem(key);
                            const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
                            data.requests = (data.requests || []).filter((id: string) => id !== rid);
                            data.assistants = (data.assistants || []).filter((id: string) => id !== rid);
                            localStorage.setItem(key, JSON.stringify(data));
                          } catch {}
                          setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));
                          try {
                            if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, false);
                          } catch (e) {
                            console.warn('respondAssist', e);
                          }
                          setMsg('Assist request from ' + label + ' declined');
                        })();
                      }}"""

if old_approve in t:
    t = t.replace(old_approve, new_approve)
    print("modal approve hardened")
else:
    print("modal approve pattern miss")

if old_deny in t:
    t = t.replace(old_deny, new_deny)
    print("modal deny hardened")
else:
    print("modal deny pattern miss")

old_chip_accept = """onClick={() => void (typeof respondAssist === 'function' ? respondAssist(selected.id, rid, true) : null)}"""
new_chip_accept = """onClick={() => void (async () => {
                              try {
                                const key = 'nexus-chat-assist-' + selected.id;
                                const raw = localStorage.getItem(key);
                                const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
                                data.requests = (data.requests || []).filter((id: string) => id !== rid);
                                if (!(data.assistants || []).includes(rid)) data.assistants = [...(data.assistants || []), rid];
                                localStorage.setItem(key, JSON.stringify(data));
                              } catch {}
                              setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));
                              try { if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, true); } catch {}
                              setMsg('Assist approved');
                            })()}"""

old_chip_deny = """onClick={() => void (typeof respondAssist === 'function' ? respondAssist(selected.id, rid, false) : null)}"""
new_chip_deny = """onClick={() => void (async () => {
                              try {
                                const key = 'nexus-chat-assist-' + selected.id;
                                const raw = localStorage.getItem(key);
                                const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
                                data.requests = (data.requests || []).filter((id: string) => id !== rid);
                                data.assistants = (data.assistants || []).filter((id: string) => id !== rid);
                                localStorage.setItem(key, JSON.stringify(data));
                              } catch {}
                              setLiveAssistReqs((prev) => prev.filter((x) => x !== rid));
                              try { if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, false); } catch {}
                              setMsg('Assist declined');
                            })()}"""

if old_chip_accept in t:
    t = t.replace(old_chip_accept, new_chip_accept)
    print("chip accept hardened")
else:
    print("chip accept miss")

if old_chip_deny in t:
    t = t.replace(old_chip_deny, new_chip_deny)
    print("chip deny hardened")
else:
    print("chip deny miss")

if "ASSIST_PENDING_FILTER_V6" not in t:
    old_eff = """  const effectivePending = Array.from(
    new Set([...(typeof pendingRequests !== 'undefined' ? pendingRequests : []), ...liveAssistReqs]),
  ).filter((id) => id && id !== myId);"""
    new_eff = """  // ASSIST_PENDING_FILTER_V6 — drop already-approved assistants from pending UI
  const effectivePending = Array.from(
    new Set([...(typeof pendingRequests !== 'undefined' ? pendingRequests : []), ...liveAssistReqs]),
  ).filter((id) => {
    if (!id || id === myId) return false;
    if (typeof assistantIds !== 'undefined' && assistantIds.includes(id)) return false;
    try {
      if (selectedId) {
        const raw = localStorage.getItem('nexus-chat-assist-' + selectedId);
        if (raw) {
          const data = JSON.parse(raw) as { assistants?: string[] };
          if ((data.assistants || []).includes(id)) return false;
        }
      }
    } catch {}
    return true;
  });"""
    if old_eff in t:
        t = t.replace(old_eff, new_eff)
        print("pending filter v6")
    else:
        print("effectivePending pattern miss")

print("braces", t.count("{") - t.count("}"), "parens", t.count("(") - t.count(")"))
lp.write_text(t)
print("done", len(t))
