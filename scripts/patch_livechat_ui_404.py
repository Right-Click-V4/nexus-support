#!/usr/bin/env python3
"""404 auto-route unknown hashes; Live Chat layout + multiline intro + avatars + glass."""
from pathlib import Path
import re

sa = Path("src/SystemApp.tsx")
if sa.exists():
    s = sa.read_text()
    if "hash-404-strict-v1" not in s:
        new = """export function getModeFromHash(): 'agent' | 'portal' | 'notfound' {
  const h = (window.location.hash || '')
    .replace(/^#\\/?/, '')
    .toLowerCase()
    .split('?')[0]
    .replace(/\\/+$/, '');
  if (h === '404' || h === 'not-found' || h === 'notfound' || h === '/') return 'notfound';
  if (h.startsWith('portal')) return 'portal';
  if (!h || h === 'agent' || h === 'app' || h === 'desk') return 'agent';
  return 'notfound';
}"""
        m = re.search(r"export function getModeFromHash\(\)[\s\S]*?\n\}", s)
        if m:
            s = s[: m.start()] + new + s[m.end() :]
            print("getModeFromHash")
        s = "/* hash-404-strict-v1 */\n" + s
        sa.write_text(s)

eb = Path("src/ErrorBoundary.tsx")
if eb.exists():
    e = eb.read_text()
    if "error-to-404-v1" not in e:
        e = e.replace("window.location.hash = '#/';", "window.location.hash = '#/404';")
        e = e.replace("Go to home / 404 screen", "Show 404 page")
        e = "/* error-to-404-v1 */\n" + e
        eb.write_text(e)

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "livechat-ui-v3" not in p:
        old_parts = """      const parts = [`Hi, I'm ${nm}.`];
      if (br) parts.push(`Branch: ${br}.`);
      if (tid) parts.push(`Ticket: ${tid}.`);
      parts.push('I need assistance.');
      await sendChatMessage(c.id, parts.join(' '), 'customer');"""
        new_parts = """      const lines = [
        `Hi, I'm ${nm}.`,
        br ? `Branch: ${br}` : null,
        tid ? `Ticket: ${tid}` : null,
        'I need assistance.',
      ].filter(Boolean) as string[];
      await sendChatMessage(c.id, lines.join('\\n'), 'customer');"""
        if old_parts in p:
            p = p.replace(old_parts, new_parts, 1)
        p = p.replace(
            'className="w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] portal-overview-glass rounded-2xl overflow-hidden border border-white/15"',
            'className="w-full max-w-4xl mx-auto flex flex-col min-h-[min(70vh,640px)] rounded-2xl overflow-hidden border border-zinc-200/40 dark:border-white/15 bg-white/40 dark:bg-black/25 backdrop-blur-xl shadow-lg shadow-black/10"',
        )
        p = p.replace(
            'className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/30 dark:bg-black/20"',
            'className="flex items-center justify-between px-4 py-3 border-b border-zinc-200/50 dark:border-white/10 bg-white/50 dark:bg-black/30 backdrop-blur-md"',
        )
        p = p.replace(
            'className="flex-1 overflow-y-auto p-4 space-y-3 bg-transparent"',
            'className="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent"',
        )
        p = p.replace(
            'className="border-t border-white/10 p-3 bg-white/25 dark:bg-black/25 space-y-2"',
            'className="border-t border-zinc-200/50 dark:border-white/10 p-3 bg-white/45 dark:bg-black/30 backdrop-blur-md space-y-2"',
        )
        m = re.search(
            r"\{messages\.map\(\(m\) => \{[\s\S]*?const mine = m\.sender === 'customer';[\s\S]*?</div>\s*</div>\s*\);\s*\}\)\}",
            p,
        )
        if m:
            new_msg = """{messages.map((m) => {
          const mine = m.sender === 'customer';
          const raw = m.text || (m as { body?: string }).body || '';
          const parsed = parseChatAttachment(raw);
          const att = parsed.att;
          const bodyText = (parsed.text || raw || '').toString();
          const customerName = accountName || name || user?.email?.split('@')[0] || 'You';
          const customerInitials = customerName
            .split(/\\s+/)
            .map((x) => x[0])
            .join('')
            .slice(0, 2)
            .toUpperCase();
          return (
            <div key={m.id} className={clsx('flex items-end gap-2', mine ? 'justify-end' : 'justify-start')}>
              {!mine && (
                <div className="shrink-0 mb-0.5">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-white/20">
                    AG
                  </div>
                </div>
              )}
              <div
                className={clsx(
                  'max-w-[78%] rounded-2xl px-3.5 py-2.5 text-sm whitespace-pre-wrap break-words shadow-sm',
                  mine
                    ? 'bg-violet-600/90 text-white rounded-br-md'
                    : 'bg-white/70 dark:bg-zinc-900/60 text-zinc-800 dark:text-zinc-100 border border-zinc-200/60 dark:border-white/10 rounded-bl-md backdrop-blur-sm',
                )}
              >
                {att ? (
                  isImageMime(att?.mime) ? (
                    <img src={att.url} alt={att.name || 'attachment'} className="max-h-48 rounded-lg" />
                  ) : (
                    <a href={att.url} download={att.name} className="underline">
                      {att?.name || 'Download file'}
                    </a>
                  )
                ) : (
                  bodyText
                )}
              </div>
              {mine && (
                <div className="shrink-0 mb-0.5">
                  {user?.user_metadata?.avatar_url ? (
                    <img
                      src={String(user.user_metadata.avatar_url)}
                      alt=""
                      className="w-8 h-8 rounded-full object-cover ring-2 ring-violet-400/30"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center text-[10px] font-bold text-white ring-2 ring-violet-400/30">
                      {customerInitials || 'U'}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}"""
            p = p[: m.start()] + new_msg + p[m.end() :]
        p = "/* livechat-ui-v3 */\n" + p
        plc.write_text(p)
        print("plc ui")
print("done")
