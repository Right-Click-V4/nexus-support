#!/usr/bin/env python3
"""Emoji only for Custom Status; Active Now shows Available/Away/etc with colors (not role)."""
from pathlib import Path

pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    t = pp.read_text()
    if "status-active-labels-v1" not in t:
        old_emoji_beside_select = """                </select>
                <div className="relative">
                  <button
                    type="button"
                    title="Add emoji"
                    onClick={() => setEmojiOpen((o) => !o)}
                    className="h-[42px] min-w-[42px] px-2 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900/60 text-lg hover:bg-zinc-50 dark:hover:bg-white/5"
                  >
                    {statusEmoji || '😊'}
                  </button>
                  {emojiOpen && (
                    <div className="absolute right-0 z-30 mt-1 p-2 w-56 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl grid grid-cols-6 gap-1">
                      {['😊','🙂','😎','🫡','💼','📞','🎧','☕','🍔','🚗','🏠','💤','🔥','⚡','✅','❌','🟢','🟡','🟠','🔵','⚪','🛠️','💬','🚀'].map((em) => (
                        <button
                          key={em}
                          type="button"
                          className="h-8 w-8 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10 text-base"
                          onClick={() => {
                            setStatusEmoji(em);
                            setEmojiOpen(false);
                            const msg = status === 'custom' ? statusMessage.trim() || null : null;
                            void updateAgentStatus(status === 'offline' ? 'online' : status, msg, em);
                          }}
                        >
                          {em}
                        </button>
                      ))}
                      <button
                        type="button"
                        className="col-span-6 text-[11px] text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 py-1"
                        onClick={() => {
                          setStatusEmoji('');
                          setEmojiOpen(false);
                          const msg = status === 'custom' ? statusMessage.trim() || null : null;
                          void updateAgentStatus(status === 'offline' ? 'online' : status, msg, null);
                        }}
                      >
                        Clear emoji
                      </button>
                    </div>
                  )}
                </div>
              </div>"""
        new_after_select = """                </select>
              </div>"""
        if old_emoji_beside_select in t:
            t = t.replace(old_emoji_beside_select, new_after_select, 1)
            print("removed emoji beside select")

        custom_block = """              {status === 'custom' && (
                <div className="mt-2 flex gap-2 items-start">
                  <input
                    value={statusMessage}
                    onChange={(e) => setStatusMessage(e.target.value)}
                    onBlur={() => {
                      void updateAgentStatus('custom', statusMessage.trim() || null, statusEmoji || null);
                    }}
                    placeholder="Write your custom status\u2026"
                    className="flex-1 px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-white dark:text-white placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                  />
                  <div className="relative">
                    <button
                      type="button"
                      title="Add emoji"
                      onClick={() => setEmojiOpen((o) => !o)}
                      className="h-[42px] min-w-[42px] px-2 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900/60 text-lg hover:bg-zinc-50 dark:hover:bg-white/5"
                    >
                      {statusEmoji || '😊'}
                    </button>
                    {emojiOpen && (
                      <div className="absolute right-0 z-30 mt-1 p-2 w-56 rounded-xl border border-zinc-200 dark:border-white/15 bg-white dark:bg-zinc-900 shadow-xl grid grid-cols-6 gap-1">
                        {['😊','🙂','😎','🫡','💼','📞','🎧','☕','🍔','🚗','🏠','💤','🔥','⚡','✅','❌','🟢','🟡','🟠','🔵','⚪','🛠️','💬','🚀'].map((em) => (
                          <button
                            key={em}
                            type="button"
                            className="h-8 w-8 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10 text-base"
                            onClick={() => {
                              setStatusEmoji(em);
                              setEmojiOpen(false);
                              void updateAgentStatus('custom', statusMessage.trim() || null, em);
                            }}
                          >
                            {em}
                          </button>
                        ))}
                        <button
                          type="button"
                          className="col-span-6 text-[11px] text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 py-1"
                          onClick={() => {
                            setStatusEmoji('');
                            setEmojiOpen(false);
                            void updateAgentStatus('custom', statusMessage.trim() || null, null);
                          }}
                        >
                          Clear emoji
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}""".replace("\\u2026", "\u2026")

        old_c = """              {status === 'custom' && (
                <input
                  value={statusMessage}
                  onChange={(e) => setStatusMessage(e.target.value)}
                  onBlur={() => {
                    void updateAgentStatus('custom', statusMessage.trim() || null, statusEmoji || null);
                  }}
                  placeholder="Write your custom status\u2026"
                  className="mt-2 w-full px-4 py-2.5 text-sm border border-zinc-200 dark:border-white/15 rounded-xl bg-white dark:bg-zinc-900/60 text-white dark:text-white placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400"
                />
              )}""".replace("\\u2026", "\u2026")
        if old_c in t:
            t = t.replace(old_c, custom_block, 1)
            print("custom block with emoji")
        elif "status === 'custom' && (" not in t:
            help_line = "Online/Offline is automatic from your session. Status updates Live Chat Active Now in real time."
            if help_line in t:
                t = t.replace(help_line + "\n              </p>", help_line + "\n              </p>\n" + custom_block, 1)
                print("inserted custom block")

        t = "/* status-active-labels-v1 */\n" + t
        pp.write_text(t)
    else:
        print("profile already")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    pl = plc.read_text()
    if "active-now-status-labels-v1" not in pl:
        old_sub = """                        <div className="text-[11px] text-zinc-500 dark:text-zinc-400 capitalize">
                          {(() => {
                            const st = (a.status || 'online').toLowerCase();
                            if (st === 'busy') return 'Busy';
                            if (st === 'away') return 'Away';
                            if (st === 'in_call') return 'In a call / meeting';
                            if (st === 'custom') return a.status_message || 'Custom status';
                            return 'Online';
                          })()}
                          {a.role ? ` \u00b7 ${a.role}` : ''}
                        </div>""".replace("\\u00b7", "\u00b7")
        new_sub = """                        <div className="text-[11px] truncate flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full shrink-0 bg-emerald-400" />
                          {a.status_emoji ? <span className="shrink-0">{a.status_emoji}</span> : null}
                          <span
                            className={(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'away') return 'text-sky-400 font-medium';
                              if (st === 'busy') return 'text-yellow-300 font-medium';
                              if (st === 'in_call') return 'text-orange-400 font-medium';
                              if (st === 'custom') return 'text-white font-medium';
                              return 'text-emerald-400 font-medium';
                            })()}
                          >
                            {(() => {
                              const st = (a.status || 'online').toLowerCase();
                              if (st === 'busy') return 'Busy';
                              if (st === 'away') return 'Away';
                              if (st === 'in_call') return 'In a call';
                              if (st === 'custom') return a.status_message || 'Custom status';
                              return 'Available';
                            })()}
                          </span>
                        </div>"""
        if old_sub in pl:
            pl = pl.replace(old_sub, new_sub, 1)
            print("plc subtitle")
        else:
            if "{a.role ? ` \u00b7 ${a.role}` : ''}" in pl or "{a.role ? ` · ${a.role}` : ''}" in pl:
                pl = pl.replace("{a.role ? ` · ${a.role}` : ''}", "", 1)
                pl = pl.replace("return 'Online';", "return 'Available';", 1)
                print("plc subtitle partial")
            else:
                print("plc subtitle miss")

        for a, b in [
            ("if (st === 'busy' || st === 'in_call') return 'bg-amber-400';",
             "if (st === 'busy') return 'bg-yellow-400';\n                              if (st === 'in_call') return 'bg-orange-400';"),
            ("if (st === 'away') return 'bg-yellow-300';", "if (st === 'away') return 'bg-sky-400';"),
            ("if (st === 'away') return 'bg-yellow-400';", "if (st === 'away') return 'bg-sky-400';"),
            ("if (st === 'busy') return 'bg-amber-400';", "if (st === 'busy') return 'bg-yellow-400';"),
            ("if (st === 'in_call') return 'bg-violet-400';", "if (st === 'in_call') return 'bg-orange-400';"),
            ("if (st === 'custom') return 'bg-sky-400';", "if (st === 'custom') return 'bg-white';"),
        ]:
            if a in pl:
                pl = pl.replace(a, b, 1)

        pl = "/* active-now-status-labels-v1 */\n" + pl
        plc.write_text(pl)
        print("plc done")
    else:
        print("plc already")
print("done")
