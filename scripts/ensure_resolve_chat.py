#!/usr/bin/env python3
from pathlib import Path

p = Path("src/components/LiveChatPage.tsx")
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
if "function resolveChatAgent" not in s:
    fn = """
function resolveChatAgent(
  c: { agent_id?: string } | null | undefined,
  agents: { id: string; name: string; avatar_url?: string | null; user_id?: string | null }[],
) {
  const aid = c?.agent_id;
  if (!aid) return null;
  return agents.find((a) => a.id === aid || a.user_id === aid) || null;
}

"""
    s = s.replace("export default function LiveChatPage", fn + "export default function LiveChatPage", 1)
    print("injected resolveChatAgent")

if "claimChat(selected.id" not in s:
    claim_btn = """                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button
                          type="button"
                          disabled={busy}
                          onClick={async () => {
                            try {
                              setBusy(true);
                              await claimChat(selected.id, currentAgent.id);
                              setMsg('Chat claimed');
                            } catch (e) {
                              setMsg(e instanceof Error ? e.message : 'Claim failed');
                            } finally {
                              setBusy(false);
                            }
                          }}
                          className="inline-flex items-center gap-1 text-xs font-medium bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500"
                        >
                          Claim
                        </button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] text-emerald-400 px-1.5 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>
                      ) : (selected as { agent_id?: string }).agent_id ? (
                        <span className="text-[11px] text-violet-200 px-1.5 py-1 font-medium rounded-lg bg-violet-500/15 border border-violet-400/30">Claimed</span>
                      ) : null}
"""
    needle = "{(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (\n                    <>\n"
    if needle in s:
        s = s.replace(needle, needle + claim_btn, 1)
        print("claim button injected")
    else:
        print("claim needle miss")

if "Failed to send message" not in s:
    old = """  const send = async () => {
    if (!draft.trim() || !selected) return;
    setBusy(true);
    try {
      if (selected.status === 'ended') await setChatStatus(selected.id, 'active');
      await sendChatMessage(selected.id, draft.trim(), as, as === 'agent' && currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined);
      setDraft('');
    } finally {
      setBusy(false);
    }
  };"""
    new = """  const send = async () => {
    if (!draft.trim() || !selected) return;
    setBusy(true);
    setMsg('');
    try {
      if (selected.status === 'ended' || selected.status === 'on_hold') await setChatStatus(selected.id, 'active');
      if (as === 'agent' && currentAgent && !(selected as { agent_id?: string }).agent_id) {
        try { await claimChat(selected.id, currentAgent.id); } catch { /* non-fatal */ }
      }
      await sendChatMessage(
        selected.id,
        draft.trim(),
        as,
        as === 'agent' && currentAgent ? { agentId: currentAgent.id, agentName: currentAgent.name } : undefined,
      );
      setDraft('');
    } catch (e) {
      setMsg(e instanceof Error ? e.message : 'Failed to send message');
    } finally {
      setBusy(false);
    }
  };"""
    if old in s:
        s = s.replace(old, new)
        print("send hardened")
    else:
        print("send pattern miss")

# dedupe claimChat
t2 = s.replace(
    "    claimChat,\n    requestAssist,\n    respondAssist,\n    claimChat,",
    "    claimChat,\n    requestAssist,\n    respondAssist,",
)
if t2 != s:
    s = t2
    print("deduped claimChat")

p.write_text(s)
print("ensure_resolve_chat done")
