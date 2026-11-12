#!/usr/bin/env python3
"""Only claimer can Hold/Resume/End; Request to assist notifies claimer (Accept/Deny)."""
from pathlib import Path
import re

lp = Path("src/components/LiveChatPage.tsx")
if not lp.exists() or lp.stat().st_size < 5000:
    print("skip LiveChatPage")
    raise SystemExit(0)

t = lp.read_text()

old_soft = """                      <button
                        type="button"
                        onClick={() => {
                          try { (window as any).__nexusAssist = { ...(window as any).__nexusAssist, [selected.id]: true }; } catch {}
                          setMsg('Assist mode on - you can send messages.');
                        }}
                        className="inline-flex items-center gap-1 text-xs font-semibold bg-amber-600/90 text-white px-2.5 py-1.5 rounded-lg hover:bg-amber-500"
                        title="Join as assisting agent"
                      >
                        Request to assist
                      </button>"""
new_assist = """                      {hasPendingMine ? (
                        <span className="text-[11px] font-medium text-amber-200 px-2 py-1 rounded-lg bg-amber-500/15 border border-amber-400/30">Assist requested</span>
                      ) : isAssistant ? (
                        <span className="text-[11px] font-semibold text-sky-300 px-2 py-1 rounded-lg bg-sky-500/15 border border-sky-400/30">Assisting</span>
                      ) : (
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => {
                            void (async () => {
                              setBusy(true);
                              try {
                                if (typeof requestAssist === 'function') await requestAssist(selected.id, currentAgent.id);
                                else {
                                  try {
                                    const key = 'nexus-chat-assist-' + selected.id;
                                    const raw = localStorage.getItem(key);
                                    const data = raw ? JSON.parse(raw) : { assistants: [], requests: [] };
                                    if (!data.requests.includes(currentAgent.id)) data.requests.push(currentAgent.id);
                                    localStorage.setItem(key, JSON.stringify(data));
                                  } catch {}
                                }
                                setMsg('Assist request sent to the claiming agent');
                              } catch (e) {
                                setMsg(e instanceof Error ? e.message : 'Request failed');
                              } finally {
                                setBusy(false);
                              }
                            })();
                          }}
                          className="inline-flex items-center gap-1 text-xs font-semibold bg-amber-600/90 text-white px-2.5 py-1.5 rounded-lg hover:bg-amber-500 disabled:opacity-60"
                          title="Request to assist on this chat"
                        >
                          Request to assist
                        </button>
                      )}"""
if old_soft in t and "requestAssist(selected.id" not in t:
    t = t.replace(old_soft, new_assist)
    print("wired requestAssist button")
elif "requestAssist(selected.id" in t:
    print("requestAssist already wired")
else:
    print("soft assist pattern miss")

if "ASSIST_PENDING_UI_V2" not in t and "pendingRequests" in t:
    needle = """                  ) : null}
                  {(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? ("""
    pending_ui = """                  ) : null}
                  {/* ASSIST_PENDING_UI_V2 — claimer sees assist requests */}
                  {isOwner && pendingRequests.filter((id) => id !== myId).length > 0 ? (
                    <div className="flex flex-wrap items-center gap-1.5">
                      {pendingRequests.filter((id) => id !== myId).map((rid) => {
                        const who = (agents || []).find((a) => a.id === rid);
                        const label = who?.name || rid.slice(0, 6);
                        return (
                          <span key={rid} className="inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-1 rounded-lg bg-amber-500/20 border border-amber-400/40 text-amber-100">
                            Assist: {label}
                            <button
                              type="button"
                              className="font-bold text-emerald-300 hover:underline"
                              onClick={() => void (typeof respondAssist === 'function' ? respondAssist(selected.id, rid, true) : null)}
                            >
                              Accept
                            </button>
                            <button
                              type="button"
                              className="font-bold text-rose-300 hover:underline"
                              onClick={() => void (typeof respondAssist === 'function' ? respondAssist(selected.id, rid, false) : null)}
                            >
                              Deny
                            </button>
                          </span>
                        );
                      })}
                    </div>
                  ) : null}
                  {(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? ("""
    if needle in t:
        t = t.replace(needle, pending_ui, 1)
        print("pending assist UI for claimer")
    else:
        print("pending UI needle miss")

if "OWNER_ONLY_HOLD_V2" not in t:
    old_hold = """                  {(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (
                    <>
                      {(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? (
                        <button
                          type="button"
                          onClick={() => void setChatStatus(selected.id, 'active')}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-emerald-500 text-white px-2.5 py-1.5 rounded-lg hover:bg-emerald-400"
                        >
                          Resume
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => void setChatStatus(selected.id, 'on_hold')}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-amber-500 text-zinc-900 px-2.5 py-1.5 rounded-lg hover:bg-amber-400"
                        >
                          On Hold
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => void setChatStatus(selected.id, 'ended')}
                        className="inline-flex items-center gap-1 text-xs font-medium text-zinc-200 border border-white/20 px-2.5 py-1.5 rounded-lg hover:bg-white/5"
                      >
                        End chat
                      </button>
                    </>
                  ) : (
                    <span className="text-[11px] text-zinc-400 px-1">Archived</span>
                  )}"""
    new_hold = """                  {/* OWNER_ONLY_HOLD_V2 — only claimer can hold/resume/end */}
                  {(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (
                    isOwner || !ownerId ? (
                      <>
                        {(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? (
                          <button
                            type="button"
                            onClick={() => void setChatStatus(selected.id, 'active')}
                            className="inline-flex items-center gap-1 text-xs font-medium bg-emerald-500 text-white px-2.5 py-1.5 rounded-lg hover:bg-emerald-400"
                          >
                            Resume
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => void setChatStatus(selected.id, 'on_hold')}
                            className="inline-flex items-center gap-1 text-xs font-medium bg-amber-500 text-zinc-900 px-2.5 py-1.5 rounded-lg hover:bg-amber-400"
                          >
                            On Hold
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => void setChatStatus(selected.id, 'ended')}
                          className="inline-flex items-center gap-1 text-xs font-medium text-zinc-200 border border-white/20 px-2.5 py-1.5 rounded-lg hover:bg-white/5"
                        >
                          End chat
                        </button>
                      </>
                    ) : (
                      <span className="text-[11px] text-zinc-400 px-1.5" title="Only the claiming agent can hold or end this chat">
                        View only
                      </span>
                    )
                  ) : (
                    <span className="text-[11px] text-zinc-400 px-1">Archived</span>
                  )}"""
    if old_hold in t:
        t = t.replace(old_hold, new_hold, 1)
        print("owner-only hold/resume/end")
    else:
        print("hold block pattern miss")

print("Yours", t.count(">Yours</span>"), "braces", t.count("{") - t.count("}"))
lp.write_text(t)
print("patch_claim_owner_controls done", len(t))
