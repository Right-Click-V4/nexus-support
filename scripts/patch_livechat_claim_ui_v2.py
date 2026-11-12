#!/usr/bin/env python3
"""Single claim UI, Request to assist, Claimed-by banner, customer avatars. Fast, no ReDoS."""
from pathlib import Path
import re

lp = Path("src/components/LiveChatPage.tsx")
if lp.exists() and lp.stat().st_size > 5000:
    t = lp.read_text()

    for s in [
        '<span className="text-[11px] text-emerald-400 px-1 font-medium">Yours</span>',
        '<span className="text-[11px] text-emerald-400 px-1.5 py-1 font-medium rounded-lg bg-emerald-500/15 border border-emerald-400/30">Yours</span>',
        '<span className="text-[11px] text-violet-200 px-1.5 py-1 font-medium rounded-lg bg-violet-500/15 border border-violet-400/30">Claimed</span>',
    ]:
        if s in t:
            t = t.replace(s, "")
            print("stripped span")

    SINGLE_CLAIM = """                      {/* CLAIM_UI_V2 */}
                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button type="button" onClick={() => void claimChat(selected.id, currentAgent.id).then(() => setMsg('Chat claimed')).catch((e) => setMsg(e instanceof Error ? e.message : 'Claim failed'))} className="inline-flex items-center gap-1 text-xs font-semibold bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500" title="Claim this chat">Claim</button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] font-semibold text-emerald-300 px-2 py-1 rounded-lg bg-emerald-500/20 border border-emerald-400/40">Yours</span>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id ? (
                        <>
                          <span className="text-[11px] font-semibold text-violet-200 px-2 py-1 rounded-lg bg-violet-500/20 border border-violet-400/40">Claimed</span>
                          <button type="button" onClick={() => { try { (window as any).__nexusAssist = { ...(window as any).__nexusAssist, [selected.id]: true }; } catch {} setMsg('Assist mode on - you can send messages.'); }} className="inline-flex items-center gap-1 text-xs font-semibold bg-amber-600/90 text-white px-2.5 py-1.5 rounded-lg hover:bg-amber-500" title="Join as assisting agent">Request to assist</button>
                        </>
                      ) : null}
"""

    if "CLAIM_UI_V2" not in t:
        needle = "{(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (\n                    <>\n"
        if needle in t:
            t = t.replace(needle, needle + SINGLE_CLAIM, 1)
            print("injected CLAIM_UI_V2")
        else:
            print("claim needle miss")

    if "disabled={busy}" in t and t.count("claimChat(selected.id") > 1:
        lines = t.splitlines(keepends=True)
        out = []
        i = 0
        removed = 0
        while i < len(lines):
            line = lines[i]
            if (
                removed < 1
                and "disabled={busy}" in line
                and i + 1 < len(lines)
                and any("claimChat(selected.id" in lines[j] for j in range(i, min(i + 15, len(lines))))
                and "CLAIM_UI_V2" not in "".join(lines[max(0, i - 5) : i + 1])
            ):
                depth = 0
                started = False
                j = i
                while j < len(lines) and j < i + 40:
                    if "{" in lines[j]:
                        depth += lines[j].count("{")
                        started = True
                    if "}" in lines[j]:
                        depth -= lines[j].count("}")
                    if started and depth <= 0 and "null}" in lines[j]:
                        j += 1
                        break
                    j += 1
                print("skipped duplicate claim lines", j - i)
                removed += 1
                i = j
                continue
            out.append(line)
            i += 1
        t = "".join(out)

    if "CLAIMED_BANNER_V2" not in t and "resolveChatAgent(selected" in t:
        marker = "const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);"
        if marker in t:
            idx = t.find(marker)
            start = t.rfind('<div className="text-[11px]', 0, idx)
            end = t.find("</div>", idx)
            if start != -1 and end != -1 and end - start < 800:
                end = end + len("</div>")
                new_banner = """<div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">
                    {selected.customer_email}
                    {selected.branch ? ` \u00b7 Branch: ${selected.branch}` : ''}
                  </div>
                  {/* CLAIMED_BANNER_V2 */}
                  <div className="mt-1.5 inline-flex flex-wrap items-center gap-2 text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-violet-600/30 text-violet-50 border border-violet-400/50 shadow-sm">
                    {(() => {
                      const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);
                      return claimed ? `Claimed by ${claimed.name}` : 'Unclaimed';
                    })()}
                    {selected.ticket_id ? ` \u00b7 Ticket: ${selected.ticket_id}` : ''}
                  </div>"""
                t = t[:start] + new_banner + t[end:]
                print("claimed banner ok")
            else:
                print("banner window miss")

    while t.count(">Yours</span>") > 1:
        pos = t.find(">Yours</span>")
        span_start = t.rfind("<span", 0, pos)
        span_end = pos + len(">Yours</span>")
        if span_start != -1:
            t = t[:span_start] + t[span_end:]
        else:
            break
    print("Yours remaining", t.count(">Yours</span>"))

    lp.write_text(t)
    print("LiveChatPage updated", len(t))
else:
    print("skip LiveChatPage")

pp = Path("src/components/PortalLiveChatView.tsx")
if pp.exists() and pp.stat().st_size > 3000:
    t = pp.read_text()

    if "CUSTOMER_CHAT_BANNER_V2" not in t:
        hold = """        {isOnHold && !chatEnded && (
          <div className="px-4 py-2 text-xs bg-amber-500/15 text-amber-700 dark:text-amber-300 border-b border-amber-500/20">
            Chat is on hold \u2014 an agent will be with you shortly.
          </div>
        )}"""
        new_b = """        {/* CUSTOMER_CHAT_BANNER_V2 */}
        {conversation && (
          <div className="px-4 py-2.5 text-xs font-medium bg-violet-600/20 text-violet-100 border-b border-violet-400/30 flex flex-wrap items-center gap-x-3 gap-y-1">
            {conversation.ticket_id ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-violet-500/40 text-white font-semibold">
                Ticket: {conversation.ticket_id}
              </span>
            ) : null}
            <span>
              {(conversation as { agent_id?: string }).agent_id
                ? `Agent: ${agents.find((a) => a.id === (conversation as { agent_id?: string }).agent_id)?.name || 'Support'}`
                : 'Waiting for an agent\u2026'}
            </span>
            {conversation.customer_name ? <span>\u00b7 You: {conversation.customer_name}</span> : null}
          </div>
        )}
        {isOnHold && !chatEnded && (
          <div className="px-4 py-2 text-xs bg-amber-500/15 text-amber-700 dark:text-amber-300 border-b border-amber-500/20">
            Chat is on hold \u2014 an agent will be with you shortly.
          </div>
        )}"""
        if hold in t:
            t = t.replace(hold, new_b)
            print("customer banner ok")
        else:
            print("customer banner needle miss")

    if "BUBBLE_AVATAR_V2" not in t:
        old_map = """          {messages.map((m) => {
            const mine = m.sender === 'customer';
            const parsed = parseChatAttachment(m.text || m.body || '');
            const att = parsed.att;
            const displayText = (parsed.text || m.text || m.body || '').trim();
            return (
              <div key={m.id} className={clsx('flex', mine ? 'justify-end' : 'justify-start')}>
                <div className={clsx(
                  'max-w-[85%] rounded-2xl px-3 py-2 text-sm',
                  mine ? 'bg-violet-600 text-white' : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10',
                )}>
"""
        new_map = """          {messages.map((m) => {
            const mine = m.sender === 'customer';
            const parsed = parseChatAttachment(m.text || m.body || '');
            const att = parsed.att;
            const displayText = (parsed.text || m.text || m.body || '').trim();
            // BUBBLE_AVATAR_V2
            const agentForMsg = agents.find((a) => a.id === ((m as { agent_id?: string }).agent_id || (conversation as { agent_id?: string } | undefined)?.agent_id));
            const displayName = mine
              ? (conversation?.customer_name || name || 'You')
              : (agentForMsg?.name || (m as { agent_name?: string }).agent_name || 'Support');
            const initials = displayName.split(/\\s+/).map((p: string) => p[0]).join('').slice(0, 2).toUpperCase() || (mine ? 'C' : 'A');
            return (
              <div key={m.id} className={clsx('flex items-end gap-2', mine ? 'justify-end' : 'justify-start')}>
                {!mine && (
                  <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden ring-2 ring-white/10">
                    {agentForMsg?.avatar_url ? (
                      <img src={agentForMsg.avatar_url} alt="" className="w-full h-full object-cover" />
                    ) : initials}
                  </div>
                )}
                <div className={clsx(
                  'max-w-[75%] rounded-2xl px-3 py-2 text-sm shadow-sm',
                  mine ? 'bg-violet-600 text-white rounded-br-md' : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10 rounded-bl-md',
                )}>
                  <div className={clsx('text-[10px] font-semibold mb-0.5', mine ? 'opacity-80' : 'text-violet-600 dark:text-violet-300')}>
                    {displayName}
                  </div>
"""
        if old_map in t:
            t = t.replace(old_map, new_map)
            old_close = """                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />"""
            new_close = """                </div>
                {mine && (
                  <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10">
                    {(conversation?.customer_name || name || 'C').split(/\\s+/).map((p: string) => p[0]).join('').slice(0, 2).toUpperCase() || 'C'}
                  </div>
                )}
              </div>
            );
          })}
          <div ref={bottomRef} />"""
            if old_close in t:
                t = t.replace(old_close, new_close, 1)
            print("bubble avatars ok")
        else:
            print("bubble map pattern miss")

    if "usePlatform" in t:
        window = t[max(0, t.find("usePlatform") - 100) : t.find("usePlatform") + 150]
        if "agents" not in window:
            t2 = re.sub(r"(const \{[^}]*)(createChat)", r"\1agents, \2", t, count=1)
            if t2 != t:
                t = t2
                print("injected agents")

    if "End / new chat" in t:
        old_end = """          <button
            type="button"
            disabled={ending}
            onClick={() => {
              if (chatEnded) startNewChat();
              else void endChat();
            }}
            className="text-xs text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200 disabled:opacity-50"
          >
            {ending ? 'Ending\u2026' : chatEnded ? 'Start new chat' : 'End / new chat'}
          </button>"""
        new_end = """          {chatEnded ? (
            <button type="button" onClick={startNewChat} className="text-xs font-semibold text-violet-300 hover:text-violet-200">
              Start new chat
            </button>
          ) : null}"""
        if old_end in t:
            t = t.replace(old_end, new_end)
            print("removed customer end")

    pp.write_text(t)
    print("PortalLiveChatView updated", len(t))
else:
    print("skip Portal")

print("patch_livechat_claim_ui_v2 done")
