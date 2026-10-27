#!/usr/bin/env python3
"""Enhance Community chat: dark mode, avatars, emoji/GIF/photo, typing indicators."""
from pathlib import Path
import re

t = Path('src/components/PortalCommunityChat.tsx').read_text()
if 'AvatarBubble' in t and 'emojiOpen' in t:
    print('community ux already')
    raise SystemExit(0)
t = t

if "useRef" not in t[:150]:
    t = t.replace(
        "import { useCallback, useEffect, useMemo, useState } from 'react';",
        "import { useCallback, useEffect, useMemo, useRef, useState } from 'react';",
    )

t = t.replace(
    "MoreHorizontal, X, Hash, Info,",
    "MoreHorizontal, X, Hash, Info, Smile, Image as ImageIcon, Film,",
)

t = t.replace(
    "type Message = {\n  id: string;\n  author_name: string;\n  author_email: string;\n  text: string;\n  created_at: string;\n  pinned?: boolean;\n};",
    "type Message = {\n  id: string;\n  author_name: string;\n  author_email: string;\n  text: string;\n  created_at: string;\n  pinned?: boolean;\n  image_data?: string;\n  gif_url?: string;\n};",
)

helpers = """
function initials(name: string) {
  const parts = (name || '?').trim().split(/\\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (parts[0] || '?').slice(0, 2).toUpperCase();
}
const AVATAR_COLORS = [
  'from-violet-500 to-fuchsia-500', 'from-sky-500 to-blue-600', 'from-emerald-500 to-teal-600',
  'from-amber-500 to-orange-600', 'from-rose-500 to-pink-600', 'from-indigo-500 to-violet-600',
];
function avatarGradient(key: string) {
  let h = 0;
  for (let i = 0; i < key.length; i++) h = key.charCodeAt(i) + ((h << 5) - h);
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
}
function AvatarBubble({ name, email }: { name: string; email: string }) {
  return (
    <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${avatarGradient(email || name)} flex items-center justify-center text-white text-[10px] font-semibold shrink-0 shadow-md`} title={name}>
      {initials(name)}
    </div>
  );
}
const EMOJIS = ['😀','😂','😍','🤩','😎','🤔','🙌','👏','🔥','✨','💜','🎉','💯','✅','⭐','🚀','👍','🙏','💪','❤️'];
const QUICK_GIFS = [
  { label: 'Wave', url: 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif' },
  { label: 'Clap', url: 'https://media.giphy.com/media/7rj2ZgQq6qpI9m7vXd/giphy.gif' },
  { label: 'Party', url: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif' },
  { label: 'Thumbs', url: 'https://media.giphy.com/media/111ebonMs90YLu/giphy.gif' },
  { label: 'Wow', url: 'https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif' },
  { label: 'Heart', url: 'https://media.giphy.com/media/3oz8xLd9DJq2l2VFtu/giphy.gif' },
];

"""
t = t.replace("interface Props {", helpers + "interface Props {", 1)

t = t.replace(
    "const [inviteName, setInviteName] = useState('');",
    "const [inviteName, setInviteName] = useState('');\n  const [emojiOpen, setEmojiOpen] = useState(false);\n  const [gifOpen, setGifOpen] = useState(false);\n  const [typingPeers, setTypingPeers] = useState<{ name: string; email: string; at: number }[]>([]);\n  const fileRef = useRef<HTMLInputElement>(null);\n  const bcRef = useRef<BroadcastChannel | null>(null);",
)

effect = """
  useEffect(() => {
    try {
      const bc = new BroadcastChannel('nexus-community-v1');
      bcRef.current = bc;
      bc.onmessage = (ev) => {
        const d = ev.data;
        if (d?.type === 'typing' && d.groupId === activeId) {
          const peer = d.peer as { name: string; email: string };
          if (!peer?.email || peer.email.toLowerCase() === email.toLowerCase()) return;
          setTypingPeers((prev) => {
            const others = prev.filter((p) => p.email.toLowerCase() !== peer.email.toLowerCase());
            return [...others, { ...peer, at: Date.now() }];
          });
        }
        if (d?.type === 'store' && d.store) setStore(d.store as Store);
      };
    } catch { /* ignore */ }
    const onStorage = () => setStore(loadStore());
    window.addEventListener('storage', onStorage);
    const tick = window.setInterval(() => {
      const now = Date.now();
      setTypingPeers((prev) => prev.filter((p) => now - p.at < 2500));
    }, 800);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.clearInterval(tick);
      try { bcRef.current?.close(); } catch { /* ignore */ }
    };
  }, [activeId, email]);

"""
if "nexus-community-v1" not in t:
    t = t.replace("  const active = useMemo(", effect + "  const active = useMemo(", 1)

t = re.sub(
    r'className="flex h-\[calc\(100vh-8rem\)\] max-h-\[760px\] bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden"',
    'className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/95 border-zinc-200/80 shadow-sm dark:bg-[#12101c]/95 dark:border-violet-500/20"',
    t,
    count=1,
)

old_msg = """              <div key={m.id} className={`flex ${mine ? 'justify-end' : 'justify-start'} group`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm relative ${
                    mine
                      ? 'bg-brand-600 text-white rounded-br-md'
                      : 'bg-white border border-zinc-200 text-zinc-800 rounded-bl-md shadow-sm'
                  }`}
                >
                  {!mine && (
                    <div className="text-[11px] font-semibold mb-0.5 text-violet-600">{m.author_name}</div>
                  )}
                  <div className="whitespace-pre-wrap break-words">{m.text}</div>"""

new_msg = """              <div key={m.id} className={`flex items-end gap-2 ${mine ? 'justify-end' : 'justify-start'} group`}>
                {!mine && <AvatarBubble name={m.author_name} email={m.author_email} />}
                <div
                  className={`max-w-[78%] rounded-2xl px-3.5 py-2.5 text-sm relative shadow-sm ${
                    mine
                      ? 'bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white rounded-br-md'
                      : 'bg-white dark:bg-[#1c1830] border border-zinc-200/80 dark:border-violet-500/15 text-zinc-800 dark:text-zinc-100 rounded-bl-md'
                  }`}
                >
                  {!mine && (
                    <div className="text-[11px] font-semibold mb-0.5 text-violet-600 dark:text-violet-300">{m.author_name}</div>
                  )}
                  {m.image_data && <img src={m.image_data} alt="" className="rounded-lg max-h-48 mb-1.5" />}
                  {m.gif_url && <img src={m.gif_url} alt="gif" className="rounded-lg max-h-40 mb-1.5" />}
                  {m.text ? <div className="whitespace-pre-wrap break-words">{m.text}</div> : null}"""

print('msg', old_msg in t)
t = t.replace(old_msg, new_msg, 1)

old_end = """                    </button>
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />"""
new_end = """                    </button>
                  </div>
                </div>
                {mine && <AvatarBubble name={m.author_name} email={m.author_email} />}
              </div>
            );
          })}
          {typingPeers.some((p) => Date.now() - p.at < 2500) && (
            <div className="text-xs text-violet-600 dark:text-violet-300 pl-1 flex items-center gap-2">
              <span className="flex gap-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" />
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:300ms]" />
              </span>
              {(() => {
                const live = typingPeers.filter((p) => Date.now() - p.at < 2500);
                if (live.length === 1) return `${live[0].name} is typing…`;
                if (live.length === 2) return `${live[0].name} and ${live[1].name} are typing…`;
                return live.length ? `${live[0].name} and others are typing…` : '';
              })()}
            </div>
          )}
          <div ref={bottomRef} />"""
print('end', old_end in t)
t = t.replace(old_end, new_end, 1)

old_form = """        <form onSubmit={send} className="p-3 border-t border-zinc-100 bg-white flex gap-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={isMuted ? 'Muted — you can still post' : 'Message the group…'}
            className="flex-1 px-3.5 py-2.5 text-sm rounded-lg border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 focus:bg-white"
            maxLength={2000}
          />
          <button
            type="submit"
            disabled={!draft.trim()}
            className="px-3.5 py-2.5 rounded-lg bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-40 shrink-0"
            aria-label="Send"
          >
            <Send size={18} />
          </button>
        </form>"""

new_form = """        <div className="border-t border-zinc-200/80 dark:border-white/10 bg-white/90 dark:bg-[#14101f]/95">
          {emojiOpen && (
            <div className="px-3 pt-2 flex flex-wrap gap-1 max-h-28 overflow-y-auto">
              {EMOJIS.map((e) => (
                <button key={e} type="button" onClick={() => { setDraft((d) => d + e); try { bcRef.current?.postMessage({ type: 'typing', groupId: activeId, peer: { name: displayName, email } }); } catch {} }} className="w-8 h-8 text-lg rounded-lg hover:bg-violet-100 dark:hover:bg-violet-500/20">{e}</button>
              ))}
            </div>
          )}
          {gifOpen && (
            <div className="px-3 pt-2 grid grid-cols-3 gap-2 max-h-36 overflow-y-auto">
              {QUICK_GIFS.map((g) => (
                <button key={g.url} type="button" onClick={() => {
                  if (!active) return;
                  const msg: Message = { id: `m-${Date.now()}`, author_name: displayName || 'You', author_email: email || 'anon', text: '', created_at: new Date().toISOString(), gif_url: g.url };
                  updateGroup(active.id, (gg) => ({ ...gg, messages: [...gg.messages, msg] }));
                  setGifOpen(false);
                }} className="rounded-lg overflow-hidden border border-zinc-200 dark:border-white/10" title={g.label}>
                  <img src={g.url} alt={g.label} className="w-full h-14 object-cover" />
                </button>
              ))}
            </div>
          )}
          <form onSubmit={send} className="p-3 flex items-end gap-2">
            <div className="flex gap-0.5 shrink-0">
              <button type="button" onClick={() => { setEmojiOpen((v)=>!v); setGifOpen(false); }} className={`p-2 rounded-lg ${emojiOpen ? 'bg-violet-100 text-violet-700 dark:bg-violet-500/25 dark:text-violet-200' : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-white/10'}`} title="Emoji"><Smile size={18} /></button>
              <button type="button" onClick={() => { setGifOpen((v)=>!v); setEmojiOpen(false); }} className={`p-2 rounded-lg ${gifOpen ? 'bg-violet-100 text-violet-700 dark:bg-violet-500/25 dark:text-violet-200' : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-white/10'}`} title="GIF"><Film size={18} /></button>
              <button type="button" onClick={() => fileRef.current?.click()} className="p-2 rounded-lg text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-white/10" title="Photo"><ImageIcon size={18} /></button>
              <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file || !file.type.startsWith('image/') || !active) return;
                if (file.size > 1200000) { window.alert('Image must be under ~1.2MB'); return; }
                const reader = new FileReader();
                reader.onload = () => {
                  const msg: Message = { id: `m-${Date.now()}`, author_name: displayName || 'You', author_email: email || 'anon', text: draft.trim(), created_at: new Date().toISOString(), image_data: String(reader.result || '') };
                  updateGroup(active.id, (gg) => ({ ...gg, messages: [...gg.messages, msg] }));
                  setDraft('');
                };
                reader.readAsDataURL(file);
              }} />
            </div>
            <input
              value={draft}
              onChange={(e) => {
                setDraft(e.target.value);
                try { bcRef.current?.postMessage({ type: 'typing', groupId: activeId, peer: { name: displayName || email, email } }); } catch {}
              }}
              placeholder={isMuted ? 'Muted — you can still post' : 'Message the group…'}
              className="flex-1 px-3.5 py-2.5 text-sm rounded-xl border border-zinc-200 dark:border-violet-500/20 bg-zinc-50 dark:bg-[#0e0c18] text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
              maxLength={2000}
            />
            <button type="submit" disabled={!draft.trim()} className="px-3.5 py-2.5 rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white hover:opacity-95 disabled:opacity-40 shrink-0" aria-label="Send">
              <Send size={18} />
            </button>
          </form>
        </div>"""

print('form', old_form in t)
t = t.replace(old_form, new_form, 1)

t = t.replace('bg-zinc-50/50', 'bg-zinc-50/40 dark:bg-[#0a0812]/50')
t = t.replace('text-zinc-900 truncate', 'text-zinc-900 dark:text-zinc-50 truncate')
t = t.replace('text-zinc-500 truncate', 'text-zinc-500 dark:text-zinc-400 truncate')

Path('src/components/PortalCommunityChat.tsx').write_text(t)
print('final', len(t))
for k in ['AvatarBubble','emojiOpen','is typing','QUICK_GIFS','dark:bg-[#12101c]']:
    print(k, k in t)
