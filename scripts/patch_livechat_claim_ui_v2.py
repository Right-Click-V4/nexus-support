#!/usr/bin/env python3
"""Single claim UI (no double Yours), Request to assist, prominent Claimed-by,
customer-side avatars+names+ticket banner. Runs last so it wins."""
from pathlib import Path
import re

lp = Path("src/components/LiveChatPage.tsx")
if lp.exists() and lp.stat().st_size > 5000:
    t = lp.read_text()

    patterns = [
        r"\{currentAgent && !\(selected as \{ agent_id\?: string \}\)\.agent_id \? \(\s*<button[^>]*>\s*Claim\s*</button>\s*\) : currentAgent && \(selected as \{ agent_id\?: string \}\)\.agent_id === currentAgent\.id \? \(\s*<span[^>]*>Yours</span>\s*\) : \(selected as \{ agent_id\?: string \}\)\.agent_id \? \(\s*<span[^>]*>Claimed</span>\s*\) : null\}\s*",
        r"\{currentAgent && \(selected as \{ agent_id\?: string \}\)\.agent_id !== currentAgent\.id \? \(\s*<button[^>]*>\s*Claim\s*</button>\s*\) : currentAgent && \(selected as \{ agent_id\?: string \}\)\.agent_id === currentAgent\.id \? \(\s*<span[^>]*>Yours</span>\s*\) : null\}\s*",
        r'<span className="text-\[11px\] text-emerald-400[^"]*">Yours</span>\s*',
        r'<span className="text-\[11px\] text-violet-200[^"]*">Claimed</span>\s*',
    ]
    for pat in patterns:
        t2, n = re.subn(pat, "", t, flags=re.S)
        if n:
            print("stripped claim block", n)
            t = t2

    t = re.sub(
        r"\{currentAgent && \(selected as \{ agent_id\?: string \}\)\.agent_id === currentAgent\.id \? \(\s*<span[^>]*>Yours</span>\s*\) : null\}\s*",
        "",
        t,
        flags=re.S,
    )

    SINGLE_CLAIM = '''                      {/* CLAIM_UI_V2 - single badge set */}
                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
                        <button
                          type="button"
                          onClick={() => void claimChat(selected.id, currentAgent.id).then(() => setMsg('Chat claimed')).catch((e) => setMsg(e instanceof Error ? e.message : 'Claim failed'))}
                          className="inline-flex items-center gap-1 text-xs font-semibold bg-violet-600 text-white px-2.5 py-1.5 rounded-lg hover:bg-violet-500"
                          title="Claim this chat"
                        >
                          Claim
                        </button>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id === currentAgent.id ? (
                        <span className="text-[11px] font-semibold text-emerald-300 px-2 py-1 rounded-lg bg-emerald-500/20 border border-emerald-400/40">Yours</span>
                      ) : currentAgent && (selected as { agent_id?: string }).agent_id ? (
                        <>
                          <span className="text-[11px] font-semibold text-violet-200 px-2 py-1 rounded-lg bg-violet-500/20 border border-violet-400/40">Claimed</span>
                          <button
                            type="button"
                            onClick={() => {
                              try { (window as any).__nexusAssist = { ...(window as any).__nexusAssist, [selected.id]: true }; } catch { /* */ }
                              setMsg('Assist mode on - you can send messages. Original claimer stays assigned.');
                            }}
                            className="inline-flex items-center gap-1 text-xs font-semibold bg-amber-600/90 text-white px-2.5 py-1.5 rounded-lg hover:bg-amber-500"
                            title="Join this chat as assisting agent"
                          >
                            Request to assist
                          </button>
                        </>
                      ) : null}
'''

    if "CLAIM_UI_V2" not in t:
        needle = "{(selected.status || '').toLowerCase() !== 'archived' && (selected.status || '').toLowerCase() !== 'ended' ? (\n                    <>\n"
        if needle in t:
            t = t.replace(needle, needle + SINGLE_CLAIM, 1)
            print("injected CLAIM_UI_V2")
        else:
            print("claim needle miss")

    broken = """                      {currentAgent && !(selected as { agent_id?: string }).agent_id ? (
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
                        ) : (selected as { agent_id?: string }).agent_id ? (
                        ) : null}
"""
    if broken in t:
        t = t.replace(broken, "")
        print("removed broken second claim block")
    else:
        t2, n = re.subn(
            r'\{currentAgent && !\(selected as \{ agent_id\?: string \}\)\.agent_id \? \(\s*<button\s+type="button"\s+disabled=\{busy\}[\s\S]*?Claim\s*</button>\s*\) : currentAgent && \(selected as \{ agent_id\?: string \}\)\.agent_id === currentAgent\.id \? \(\s*\) : \(selected as \{ agent_id\?: string \}\)\.agent_id \? \(\s*\) : null\}\s*',
            "",
            t,
            count=1,
        )
        if n:
            t = t2
            print("removed broken second claim via regex")

    old_banner = (
        '                  <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">\n'
        '                    {(() => {\n'
        '                      const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);\n'
        "                      return claimed ? `Claimed by ${claimed.name} \u00b7 ` : '';\n"
        '                    })()}\n'
        '                    {selected.customer_email}\n'
        "                    {selected.branch ? ` \u00b7 Branch: ${selected.branch}` : ''}\n"
        "                    {selected.ticket_id ? ` \u00b7 Ticket: ${selected.ticket_id}` : ''}\n"
        '                  </div>'
    )
    new_banner = (
        '                  <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">\n'
        '                    {selected.customer_email}\n'
        "                    {selected.branch ? ` \u00b7 Branch: ${selected.branch}` : ''}\n"
        '                  </div>\n'
        '                  {/* CLAIMED_BANNER_V2 */}\n'
        '                  <div className="mt-1.5 inline-flex flex-wrap items-center gap-2 text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-violet-600/30 text-violet-50 border border-violet-400/50 shadow-sm">\n'
        '                    {(() => {\n'
        '                      const claimed = resolveChatAgent(selected as { agent_id?: string }, agents || []);\n'
        "                      return claimed ? `Claimed by ${claimed.name}` : 'Unclaimed';\n"
        '                    })()}\n'
        "                    {selected.ticket_id ? ` \u00b7 Ticket: ${selected.ticket_id}` : ''}\n"
        '                  </div>'
    )
    if "CLAIMED_BANNER_V2" not in t and old_banner in t:
        t = t.replace(old_banner, new_banner)
        print("claimed banner exact")
    elif "CLAIMED_BANNER_V2" not in t:
        t2, n = re.subn(
            r'<div className="text-\[11px\] text-slate-500 dark:text-zinc-400 truncate">\s*\{\(\(\) => \{\s*const claimed = resolveChatAgent[\s\S]*?selected\.ticket_id \? ` . Ticket: \$\{selected\.ticket_id\}` : \'\'\\}\s*</div>',
            new_banner,
            t,
            count=1,
        )
        if n:
            t = t2
            print("claimed banner regex")

    while t.count(">Yours</span>") > 1:
        t = t.replace(
            '<span className="text-[11px] text-emerald-400 px-1 font-medium">Yours</span>',
            "",
            1,
        )
        if t.count(">Yours</span>") > 1:
            t = re.sub(
                r'<span className="text-\[11px\] text-emerald-400[^"]*">Yours</span>',
                "",
                t,
                count=1,
            )
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
        hold_banner = (
            '        {isOnHold && !chatEnded && (\n'
            '          <div className="px-4 py-2 text-xs bg-amber-500/15 text-amber-700 dark:text-amber-300 border-b border-amber-500/20">\n'
            '            Chat is on hold \u2014 an agent will be with you shortly.\n'
            '          </div>\n'
            '        )}'
        )
        new_banners = (
            '        {/* CUSTOMER_CHAT_BANNER_V2 */}\n'
            '        {conversation && (\n'
            '          <div className="px-4 py-2.5 text-xs font-medium bg-violet-600/20 text-violet-100 border-b border-violet-400/30 flex flex-wrap items-center gap-x-3 gap-y-1">\n'
            '            {conversation.ticket_id ? (\n'
            '              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-violet-500/40 text-white font-semibold">\n'
            '                Ticket: {conversation.ticket_id}\n'
            '              </span>\n'
            '            ) : null}\n'
            '            <span>\n'
            "              {(conversation as { agent_id?: string }).agent_id\n"
            "                ? `Agent: ${agents.find((a) => a.id === (conversation as { agent_id?: string }).agent_id)?.name || 'Support'}`\n"
            "                : 'Waiting for an agent\u2026'}\n"
            '            </span>\n'
            '            {conversation.customer_name ? <span>\u00b7 You: {conversation.customer_name}</span> : null}\n'
            '          </div>\n'
            '        )}\n'
            '        {isOnHold && !chatEnded && (\n'
            '          <div className="px-4 py-2 text-xs bg-amber-500/15 text-amber-700 dark:text-amber-300 border-b border-amber-500/20">\n'
            '            Chat is on hold \u2014 an agent will be with you shortly.\n'
            '          </div>\n'
            '        )}'
        )
        if hold_banner in t:
            t = t.replace(hold_banner, new_banners)
            print("customer banner ok")
        else:
            print("customer banner needle miss")

    if "BUBBLE_AVATAR_V2" not in t:
        old_map = (
            "          {messages.map((m) => {\n"
            "            const mine = m.sender === 'customer';\n"
            "            const parsed = parseChatAttachment(m.text || m.body || '');\n"
            "            const att = parsed.att;\n"
            "            const displayText = (parsed.text || m.text || m.body || '').trim();\n"
            "            return (\n"
            "              <div key={m.id} className={clsx('flex', mine ? 'justify-end' : 'justify-start')}>
"
            "                <div className={clsx(\n"
            "                  'max-w-[85%] rounded-2xl px-3 py-2 text-sm',\n"
            "                  mine ? 'bg-violet-600 text-white' : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10',\n"
            "                )}>\n"
        )
        new_map = (
            "          {messages.map((m) => {\n"
            "            const mine = m.sender === 'customer';\n"
            "            const parsed = parseChatAttachment(m.text || m.body || '');\n"
            "            const att = parsed.att;\n"
            "            const displayText = (parsed.text || m.text || m.body || '').trim();\n"
            "            // BUBBLE_AVATAR_V2\n"
            "            const agentForMsg = agents.find((a) => a.id === ((m as { agent_id?: string }).agent_id || (conversation as { agent_id?: string } | undefined)?.agent_id));\n"
            "            const displayName = mine\n"
            "              ? (conversation?.customer_name || name || 'You')\n"
            "              : (agentForMsg?.name || (m as { agent_name?: string }).agent_name || 'Support');\n"
            "            const initials = displayName.split(/\\s+/).map((p: string) => p[0]).join('').slice(0, 2).toUpperCase() || (mine ? 'C' : 'A');\n"
            "            return (\n"
            "              <div key={m.id} className={clsx('flex items-end gap-2', mine ? 'justify-end' : 'justify-start')}>
"
            "                {!mine && (\n"
            "                  <div className=\"shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden ring-2 ring-white/10\">\n"
            "                    {agentForMsg?.avatar_url ? (\n"
            "                      <img src={agentForMsg.avatar_url} alt=\"\" className=\"w-full h-full object-cover\" />\n"
            "                    ) : initials}\n"
            "                  </div>\n"
            "                )}\n"
            "                <div className={clsx(\n"
            "                  'max-w-[75%] rounded-2xl px-3 py-2 text-sm shadow-sm',\n"
            "                  mine ? 'bg-violet-600 text-white rounded-br-md' : 'bg-white/80 dark:bg-white/10 text-zinc-900 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10 rounded-bl-md',\n"
            "                )}>\n"
            "                  <div className={clsx('text-[10px] font-semibold mb-0.5', mine ? 'opacity-80' : 'text-violet-600 dark:text-violet-300')}>\n"
            "                    {displayName}\n"
            "                  </div>\n"
        )
        if old_map in t:
            t = t.replace(old_map, new_map)
            old_close = (
                "                </div>\n"
                "              </div>\n"
                "            );\n"
                "          })}\n"
                "          <div ref={bottomRef} />"
            )
            new_close = (
                "                </div>\n"
                "                {mine && (\n"
                "                  <div className=\"shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/10\">\n"
                "                    {(conversation?.customer_name || name || 'C').split(/\\s+/).map((p: string) => p[0]).join('').slice(0, 2).toUpperCase() || 'C'}\n"
                "                  </div>\n"
                "                )}\n"
                "              </div>\n"
                "            );\n"
                "          })}\n"
                "          <div ref={bottomRef} />"
            )
            if old_close in t:
                t = t.replace(old_close, new_close, 1)
            print("bubble avatars ok")
        else:
            print("bubble map pattern miss")

    if "usePlatform" in t and "agents" not in t[max(0, t.find("usePlatform") - 100) : t.find("usePlatform") + 150]:
        t2 = re.sub(r"(const \{[^}]*)(createChat)", r"\1agents, \2", t, count=1)
        if t2 != t:
            t = t2
            print("injected agents into usePlatform")

    if "End / new chat" in t:
        t = t.replace(
            """          <button
            type="button"
            disabled={ending}
            onClick={() => {
              if (chatEnded) startNewChat();
              else void endChat();
            }}
            className="text-xs text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200 disabled:opacity-50"
          >
            {ending ? 'Ending\u2026' : chatEnded ? 'Start new chat' : 'End / new chat'}
          </button>""",
            """          {chatEnded ? (
            <button
              type="button"
              onClick={startNewChat}
              className="text-xs font-semibold text-violet-300 hover:text-violet-200"
            >
              Start new chat
            </button>
          ) : null}""",
        )
        print("removed customer end button")

    pp.write_text(t)
    print("PortalLiveChatView updated", len(t))
else:
    print("skip PortalLiveChatView")

print("patch_livechat_claim_ui_v2 done")
