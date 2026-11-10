#!/usr/bin/env python3
"""Multi-agent assist: claim exclusivity + Request to Assist."""
from pathlib import Path

tp = Path('src/types.ts')
if tp.exists():
    s = tp.read_text()
    if 'assistant_ids' not in s:
        s = s.replace(
            "  agent_id?: string;\n  branch?: string;",
            "  agent_id?: string;\n  assistant_ids?: string[];\n  assist_requests?: string[];\n  branch?: string;",
            1,
        )
        tp.write_text(s)
        print('types ok')

pc = Path('src/context/PlatformContext.tsx')
if pc.exists():
    s = pc.read_text()
    if 'requestAssist' not in s:
        for old in [
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer') => Promise<void>;",
            "sendChatMessage: (conversationId: string, text: string, sender: 'agent' | 'customer', opts?: { agentId?: string; agentName?: string }) => Promise<void>;",
        ]:
            if old in s:
                s = s.replace(
                    old,
                    old.rstrip(';')
                    + ";\n  claimChat: (conversationId: string, agentId: string) => Promise<boolean>;\n  requestAssist: (conversationId: string, agentId: string) => Promise<void>;\n  respondAssist: (conversationId: string, agentId: string, accept: boolean) => Promise<void>;",
                    1,
                )
                break

    if 'const requestAssist' not in s:
        helpers = r'''
  const readAssistLocal = (id: string): { assistants: string[]; requests: string[] } => {
    try {
      const raw = localStorage.getItem('nexus-chat-assist-' + id);
      if (raw) return JSON.parse(raw) as { assistants: string[]; requests: string[] };
    } catch {}
    return { assistants: [], requests: [] };
  };
  const writeAssistLocal = (id: string, assistants: string[], requests: string[]) => {
    try {
      localStorage.setItem('nexus-chat-assist-' + id, JSON.stringify({ assistants, requests }));
    } catch {}
  };

  const claimChat = async (conversationId: string, agentId: string): Promise<boolean> => {
    if (!conversationId || !agentId) return false;
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== conversationId) return c;
        if (c.agent_id && c.agent_id !== agentId) return c;
        return {
          ...c,
          agent_id: agentId,
          status: (c.status === 'waiting' || c.status === 'on_hold' ? 'active' : c.status) as ChatConversation['status'],
        };
      }),
    );
    if (!supabase) return true;
    try {
      let { error } = await supabase
        .from('chat_conversations')
        .update({ agent_id: agentId, status: 'active', updated_at: new Date().toISOString() })
        .eq('id', conversationId)
        .is('agent_id', null);
      if (error) {
        const r2 = await supabase
          .from('chat_conversations')
          .update({ agent_id: agentId, updated_at: new Date().toISOString() })
          .eq('id', conversationId);
        error = r2.error;
      }
      if (error) console.warn('claimChat', error.message);
      return true;
    } catch (e) {
      console.warn('claimChat', e);
      return true;
    }
  };

  const requestAssist = async (conversationId: string, agentId: string) => {
    if (!conversationId || !agentId) return;
    const local = readAssistLocal(conversationId);
    if (!local.requests.includes(agentId) && !local.assistants.includes(agentId)) {
      local.requests.push(agentId);
      writeAssistLocal(conversationId, local.assistants, local.requests);
    }
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== conversationId) return c;
        const reqs = Array.from(new Set([...(c.assist_requests || []), ...local.requests, agentId]));
        const assists = Array.from(new Set([...(c.assistant_ids || []), ...local.assistants]));
        return { ...c, assist_requests: reqs, assistant_ids: assists };
      }),
    );
    if (supabase) {
      try {
        const conv = conversations.find((x) => x.id === conversationId);
        const reqs = Array.from(new Set([...(conv?.assist_requests || []), agentId]));
        await supabase
          .from('chat_conversations')
          .update({ assist_requests: reqs, updated_at: new Date().toISOString() })
          .eq('id', conversationId);
      } catch (e) {
        console.warn('requestAssist', e);
      }
    }
  };

  const respondAssist = async (conversationId: string, agentId: string, accept: boolean) => {
    if (!conversationId || !agentId) return;
    const local = readAssistLocal(conversationId);
    local.requests = local.requests.filter((id) => id !== agentId);
    if (accept && !local.assistants.includes(agentId)) local.assistants.push(agentId);
    writeAssistLocal(conversationId, local.assistants, local.requests);
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== conversationId) return c;
        const reqs = (c.assist_requests || []).filter((id) => id !== agentId);
        let assists = [...(c.assistant_ids || [])];
        if (accept && !assists.includes(agentId)) assists.push(agentId);
        assists = Array.from(new Set([...assists, ...local.assistants]));
        return { ...c, assist_requests: reqs, assistant_ids: assists };
      }),
    );
    if (supabase) {
      try {
        const conv = conversations.find((x) => x.id === conversationId);
        const reqs = (conv?.assist_requests || []).filter((id) => id !== agentId);
        let assists = [...(conv?.assistant_ids || [])];
        if (accept && !assists.includes(agentId)) assists.push(agentId);
        await supabase
          .from('chat_conversations')
          .update({
            assist_requests: reqs,
            assistant_ids: assists,
            updated_at: new Date().toISOString(),
          })
          .eq('id', conversationId);
      } catch (e) {
        console.warn('respondAssist', e);
      }
    }
  };

'''
        if 'const claimChat' not in s:
            if '  const archiveChat = async' in s:
                s = s.replace('  const archiveChat = async', helpers + '  const archiveChat = async', 1)
            elif '  const setChatStatus = async' in s:
                s = s.replace('  const setChatStatus = async', helpers + '  const setChatStatus = async', 1)
            print('inserted assist helpers')
        elif 'const requestAssist' not in s:
            # claim exists from older patch — still need request/respond
            if '  const archiveChat = async' in s:
                s = s.replace('  const archiveChat = async', helpers + '  const archiveChat = async', 1)
            print('inserted assist (claim existed)')

    if 'ASSIST_SEND_GUARD_V1' not in s:
        marker2 = 'const sendChatMessage = async'
        idx2 = s.find(marker2)
        if idx2 >= 0:
            brace = s.find('{', idx2)
            if brace > 0:
                guard = """
    // ASSIST_SEND_GUARD_V1
    if (sender === 'agent') {
      const conv = conversations.find((c) => c.id === conversationId);
      const optsArg = (typeof arguments !== 'undefined' && arguments.length > 3 ? arguments[3] : null) as { agentId?: string } | null;
      const aid = (optsArg && optsArg.agentId) || user?.id || '';
      if (conv?.agent_id && aid && conv.agent_id !== aid) {
        const assistants = [...(conv.assistant_ids || [])];
        try {
          const raw = localStorage.getItem('nexus-chat-assist-' + conversationId);
          if (raw) {
            const parsed = JSON.parse(raw) as { assistants?: string[] };
            if (parsed.assistants) assistants.push(...parsed.assistants);
          }
        } catch {}
        if (!assistants.includes(aid)) {
          throw new Error('This chat is claimed by another agent. Request to Assist to join.');
        }
      }
    }
"""
                s = s[: brace + 1] + guard + s[brace + 1 :]
                print('send guard')

    if 'requestAssist,' not in s:
        if 'claimChat,' in s:
            s = s.replace('claimChat,', 'claimChat,\n    requestAssist,\n    respondAssist,', 1)
        elif 'createChat, sendChatMessage,' in s:
            s = s.replace(
                'createChat, sendChatMessage,',
                'createChat, sendChatMessage,\n    claimChat,\n    requestAssist,\n    respondAssist,',
                1,
            )
        elif 'sendChatMessage, setChatStatus' in s:
            s = s.replace(
                'sendChatMessage, setChatStatus',
                'sendChatMessage, claimChat, requestAssist, respondAssist, setChatStatus',
                1,
            )
        print('exports')

    pc.write_text(s)
    print('platform done')

lp = Path('src/components/LiveChatPage.tsx')
if lp.exists():
    t = lp.read_text()
    if 'requestAssist' not in t.split('usePlatform')[1][:800]:
        if 'refreshPlatform,' in t and 'requestAssist,' not in t:
            t = t.replace(
                'refreshPlatform,',
                'refreshPlatform,\n    claimChat,\n    requestAssist,\n    respondAssist,',
                1,
            )

    if 'canSendAsAgent' not in t:
        needle = "const selected = conversations.find((c) => c.id === selectedId) || null;"
        if needle in t:
            t = t.replace(
                needle,
                needle
                + """
  const myId = currentAgent?.id || '';
  const ownerId = (selected as { agent_id?: string } | null)?.agent_id || '';
  const assistantIds = Array.from(
    new Set([
      ...(((selected as { assistant_ids?: string[] } | null)?.assistant_ids) || []),
      ...(() => {
        try {
          if (!selected) return [] as string[];
          const raw = localStorage.getItem('nexus-chat-assist-' + selected.id);
          if (!raw) return [] as string[];
          return (JSON.parse(raw) as { assistants?: string[] }).assistants || [];
        } catch {
          return [] as string[];
        }
      })(),
    ]),
  );
  const pendingRequests = Array.from(
    new Set([
      ...(((selected as { assist_requests?: string[] } | null)?.assist_requests) || []),
      ...(() => {
        try {
          if (!selected) return [] as string[];
          const raw = localStorage.getItem('nexus-chat-assist-' + selected.id);
          if (!raw) return [] as string[];
          return (JSON.parse(raw) as { requests?: string[] }).requests || [];
        } catch {
          return [] as string[];
        }
      })(),
    ]),
  );
  const isOwner = Boolean(myId && ownerId && myId === ownerId);
  const isAssistant = Boolean(myId && assistantIds.includes(myId));
  const canSendAsAgent = !ownerId || isOwner || isAssistant;
  const hasPendingMine = Boolean(myId && pendingRequests.includes(myId));
""",
                1,
            )

    if 'Request to Assist' not in t:
        marker = "{(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting' ? ("
        ui = """{myId ? (
                    !ownerId ? (
                      <button type="button" disabled={busy} onClick={() => { void (async () => { setBusy(true); try { await claimChat?.(selected.id, myId); setMsg('Chat claimed'); } catch (e) { setMsg(e instanceof Error ? e.message : 'Claim failed'); } finally { setBusy(false); } })(); }} className="inline-flex items-center gap-1 text-xs font-semibold bg-violet-500 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-400 disabled:opacity-60">Claim</button>
                    ) : isOwner ? (
                      <span className="inline-flex items-center text-xs font-semibold text-emerald-300 px-2.5 py-1.5 rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>
                    ) : isAssistant ? (
                      <span className="inline-flex items-center text-xs font-semibold text-sky-300 px-2.5 py-1.5 rounded-lg bg-sky-500/15 border border-sky-400/30">Assisting</span>
                    ) : hasPendingMine ? (
                      <span className="inline-flex items-center text-xs font-medium text-amber-200 px-2.5 py-1.5 rounded-lg bg-amber-500/15 border border-amber-400/30">Assist requested</span>
                    ) : (
                      <button type="button" disabled={busy} onClick={() => { void (async () => { setBusy(true); try { await requestAssist?.(selected.id, myId); setMsg('Assist request sent to the claiming agent'); } catch (e) { setMsg(e instanceof Error ? e.message : 'Request failed'); } finally { setBusy(false); } })(); }} className="inline-flex items-center gap-1 text-xs font-semibold bg-fuchsia-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-fuchsia-500 disabled:opacity-60">Request to Assist</button>
                    )
                  ) : null}
                  {isOwner && pendingRequests.filter((id) => id !== myId).length > 0 ? (
                    <div className="flex items-center gap-1 flex-wrap">
                      {pendingRequests.filter((id) => id !== myId).map((rid) => (
                        <span key={rid} className="inline-flex items-center gap-1 text-[10px] px-1.5 py-1 rounded-lg bg-amber-500/10 border border-amber-400/30 text-amber-100">
                          Assist req
                          <button type="button" className="font-bold text-emerald-300 hover:underline" onClick={() => void respondAssist?.(selected.id, rid, true)}>Accept</button>
                          <button type="button" className="font-bold text-rose-300 hover:underline" onClick={() => void respondAssist?.(selected.id, rid, false)}>Deny</button>
                        </span>
                      ))}
                    </div>
                  ) : null}
                  """
        if marker in t:
            t = t.replace(marker, ui + marker, 1)
            print('assist UI')

    if 'canSendAsAgent' in t and "as === 'agent' && !canSendAsAgent" not in t:
        if "await sendChatMessage(selected.id, draft.trim(), as);" in t:
            t = t.replace(
                "await sendChatMessage(selected.id, draft.trim(), as);",
                "if (as === 'agent' && !canSendAsAgent) { setMsg('Request to Assist first — this chat is claimed by another agent.'); return; }\n      await sendChatMessage(selected.id, draft.trim(), as);",
                1,
            )
    if 'value={draft}' in t and "disabled={as === 'agent' && !canSendAsAgent}" not in t:
        t = t.replace(
            'value={draft}',
            "value={draft}\n                    disabled={as === 'agent' && !canSendAsAgent}",
            1,
        )
    if 'canSendAsAgent' in t and 'Only the claiming agent' not in t and 'Request to Assist</strong>' not in t:
        banner_marker = '<div className="flex-1 overflow-y-auto p-4 space-y-3">'
        if banner_marker in t:
            t = t.replace(
                banner_marker,
                "{!canSendAsAgent && as === 'agent' ? (\n                <div className=\"mx-4 mt-2 mb-0 text-xs text-amber-100 bg-amber-500/15 border border-amber-400/30 rounded-xl px-3 py-2\">\n                  This chat is claimed by another agent. You can read messages but cannot reply until they accept your <strong>Request to Assist</strong>.\n                </div>\n              ) : null}\n              <div className=\"flex-1 overflow-y-auto p-4 space-y-3\">",
                1,
            )

    lp.write_text(t)
    print('livechat done')

print('ASSIST PATCH COMPLETE')
