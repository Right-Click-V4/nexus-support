#!/usr/bin/env python3
"""Assist modal for claimer, force owner-only Hold/End, fix agent message avatars."""
from pathlib import Path
import re

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip LiveChatPage")
    raise SystemExit(0)

t = lp.read_text()

# ---------- 1) Fix avatar: use message author, not currentAgent ----------
if "AVATAR_BY_AUTHOR_V3" not in t:
    old_av = """                  const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);
                  const agentName = (m as { author?: string }).author || claimed?.name || currentAgent?.name || 'Agent';
                  const agentAvatar = claimed?.avatar_url || currentAgent?.avatar_url || '';
                  const agentInitials = agentName
                    .split(/\\s+/)
                    .map((x) => x[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase();"""
    new_av = """                  // AVATAR_BY_AUTHOR_V3 — show the agent who actually sent the message
                  const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);
                  const msgAuthor = ((m as { author?: string }).author || '').trim();
                  const msgAgentId = (m as { agent_id?: string }).agent_id || '';
                  const msgAgent =
                    (msgAgentId && (agents || []).find((a) => a.id === msgAgentId)) ||
                    (msgAuthor && (agents || []).find((a) => a.name === msgAuthor || a.name?.toLowerCase() === msgAuthor.toLowerCase())) ||
                    null;
                  const agentName = msgAuthor || msgAgent?.name || claimed?.name || 'Agent';
                  const agentAvatar = msgAgent?.avatar_url || '';
                  const agentInitials = agentName
                    .split(/\\s+/)
                    .map((x) => x[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase();"""
    if old_av in t:
        t = t.replace(old_av, new_av)
        print("avatar by author")
    else:
        print("avatar pattern miss")

# Fix bubble img that still uses currentAgent
old_bub = """                      {isAgent && (
                        <div className=\"shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden\">
                          {currentAgent?.avatar_url ? (
                            <img src={currentAgent.avatar_url} alt=\"\" className=\"w-full h-full object-cover\" />
                          ) : (
                            agentInitials || 'A'
                          )}
                        </div>
                      )}"""
new_bub = """                      {isAgent && (
                        <div className=\"shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10 overflow-hidden\">
                          {agentAvatar ? (
                            <img src={agentAvatar} alt=\"\" className=\"w-full h-full object-cover\" />
                          ) : (
                            agentInitials || 'A'
                          )}
                        </div>
                      )}"""
if old_bub in t:
    t = t.replace(old_bub, new_bub)
    print("bubble avatar fixed")

# ---------- 2) Force owner-only Hold/Resume/End (idempotent) ----------
if "OWNER_ONLY_HOLD_V3" not in t:
    if "OWNER_ONLY_HOLD_V2" in t:
        t = t.replace("OWNER_ONLY_HOLD_V2", "OWNER_ONLY_HOLD_V3", 1)
        print("bumped hold marker to V3")
    if "isOwner || !ownerId" not in t:
        if "setChatStatus(selected.id, 'on_hold')" in t and "Only the claiming agent" not in t:
            t = t.replace(
                "onClick={() => void setChatStatus(selected.id, 'on_hold')}",
                "onClick={() => { if (!isOwner && ownerId) { setMsg('Only the claiming agent can put this chat on hold'); return; } void setChatStatus(selected.id, 'on_hold'); }}",
            )
            t = t.replace(
                "onClick={() => void setChatStatus(selected.id, 'active')}",
                "onClick={() => { if (!isOwner && ownerId) { setMsg('Only the claiming agent can resume this chat'); return; } void setChatStatus(selected.id, 'active'); }}",
            )
            t = t.replace(
                "onClick={() => void setChatStatus(selected.id, 'ended')}",
                "onClick={() => { if (!isOwner && ownerId) { setMsg('Only the claiming agent can end this chat'); return; } void setChatStatus(selected.id, 'ended'); }}",
            )
            print("gated hold/end onclicks")

if "isOwner || !ownerId" in t:
    print("owner gate present")
else:
    print("WARNING: no isOwner gate on hold block")

# ---------- 3) Assist request modal for claimer ----------
if "ASSIST_MODAL_V3" not in t:
    modal = '''
      {/* ASSIST_MODAL_V3 — claimer must approve/decline assist requests */}
      {selected && isOwner && pendingRequests.filter((id) => id !== myId).length > 0 ? (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-zinc-900 border border-violet-400/40 shadow-2xl p-5 space-y-3">
            <div className="text-sm font-semibold text-white">Assist request</div>
            <div className="text-xs text-zinc-300">
              Another agent wants to join this live chat and send messages (group assist).
            </div>
            {pendingRequests.filter((id) => id !== myId).map((rid) => {
              const who = (agents || []).find((a) => a.id === rid);
              const label = who?.name || rid.slice(0, 8);
              return (
                <div key={rid} className="flex items-center justify-between gap-2 rounded-xl bg-white/5 border border-white/10 px-3 py-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
                      {label.split(/\\s+/).map((p) => p[0]).join('').slice(0, 2).toUpperCase()}
                    </div>
                    <div className="truncate text-sm text-white font-medium">{label}</div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <button
                      type="button"
                      className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500"
                      onClick={() => {
                        void (async () => {
                          if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, true);
                          setMsg(label + ' can now assist on this chat');
                        })();
                      }}
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-rose-600 text-white hover:bg-rose-500"
                      onClick={() => {
                        void (async () => {
                          if (typeof respondAssist === 'function') await respondAssist(selected.id, rid, false);
                          setMsg('Assist request from ' + label + ' declined');
                        })();
                      }}
                    >
                      Decline
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
'''
    anchor2 = "{!canSendAsAgent && as === 'agent' ? ("
    if anchor2 in t:
        t = t.replace(anchor2, modal + "\n              " + anchor2, 1)
        print("assist modal inserted before canSend banner")
    else:
        print("modal anchor miss")

# ---------- 4) Cross-tab BroadcastChannel ----------
if "ASSIST_BC_V3" not in t and "requestAssist" in t:
    if "Assist request sent to the claiming agent" in t and "ASSIST_BC_V3" not in t:
        t = t.replace(
            "setMsg('Assist request sent to the claiming agent');",
            """setMsg('Assist request sent to the claiming agent');
                                try {
                                  // ASSIST_BC_V3
                                  const bc = new BroadcastChannel('nexus-chat-assist');
                                  bc.postMessage({ type: 'assist-request', conversationId: selected.id, agentId: currentAgent.id, agentName: currentAgent.name });
                                  bc.close();
                                } catch {}
                                try { window.dispatchEvent(new CustomEvent('nexus-assist-request', { detail: { conversationId: selected.id, agentId: currentAgent.id } })); } catch {}""",
        )
        print("broadcast on request")

    if "ASSIST_BC_LISTENER_V3" not in t:
        listener = """
  // ASSIST_BC_LISTENER_V3
  useEffect(() => {
    const onMsg = (ev: MessageEvent) => {
      try {
        const d = ev.data;
        if (d?.type === 'assist-request' || d?.type === 'assist-respond') {
          void refreshPlatform?.();
          setMsg((prev) => prev || (d.type === 'assist-request' ? 'New assist request received' : 'Assist status updated'));
        }
      } catch {}
    };
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-chat-assist');
      bc.onmessage = onMsg;
    } catch {}
    const onCustom = () => { void refreshPlatform?.(); };
    window.addEventListener('nexus-assist-request', onCustom as EventListener);
    const poll = window.setInterval(() => {
      if (!selectedId) return;
      try {
        const raw = localStorage.getItem('nexus-chat-assist-' + selectedId);
        if (raw) void refreshPlatform?.();
      } catch {}
    }, 2500);
    return () => {
      try { bc?.close(); } catch {}
      window.removeEventListener('nexus-assist-request', onCustom as EventListener);
      window.clearInterval(poll);
    };
  }, [selectedId, refreshPlatform]);
"""
        marker = "  }, [selectedId, refreshPlatform]);"
        if marker in t and "ASSIST_BC_LISTENER_V3" not in t:
            idx = t.find(marker)
            if idx > 0:
                end = idx + len(marker)
                t = t[:end] + "\n" + listener + t[end:]
                print("assist BC listener inserted")
        else:
            m2 = "  const hasPendingMine = Boolean(myId && pendingRequests.includes(myId));"
            if m2 in t:
                t = t.replace(m2, m2 + "\n" + listener, 1)
                print("assist BC listener after hasPendingMine")
            else:
                print("listener insert miss")

print("Yours", t.count(">Yours</span>"), "braces", t.count("{") - t.count("}"), "parens", t.count("(") - t.count(")"))
lp.write_text(t)
print("patch_assist_modal_v3 done", len(t))
