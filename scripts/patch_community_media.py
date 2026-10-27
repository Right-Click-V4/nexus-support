#!/usr/bin/env python3
"""Community media/style: dark transparent middle, more emoji/GIF + search, center info header."""
from pathlib import Path
import re

p = Path("src/components/PortalCommunityChat.tsx")
t = p.read_text()
if "community-media-v2" in t:
    print("already patched")
    raise SystemExit(0)

t = t.replace(
    "export default function PortalCommunityChat",
    "/* community-media-v2 */\nexport default function PortalCommunityChat",
    1,
)

old_emoji = "const EMOJIS = ['😀','😂','😍','🤩','😎','🤔','🙌','👏','🔥','✨','💜','🎉','💯','✅','⭐','🚀','👍','🙏','💪','❤️'];"
new_emoji = """const EMOJIS = [
  '😀','😃','😄','😁','😆','😅','🤣','😂','🙂','😉','😊','😇','🥰','😍','🤩','😘','😗','😚','😙',
  '😋','😛','😜','🤪','😝','🤑','🤗','🤭','🤫','🤔','🤐','🤨','😐','😑','😶','😏','😒','🙄','😬',
  '😮','😯','😲','😳','🥺','😢','😭','😤','😠','😡','🤬','😈','👿','💀','👻','👽','🤖','💩','🎃',
  '👋','🤚','✋','🖖','👌','🤌','🤏','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','👇','👍','👎','✊','👊',
  '👏','🙌','👐','🤲','🤝','🙏','💪','🦾','❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣️','💕',
  '🔥','✨','⭐','🌟','💫','💥','🎉','🎊','🎈','🎁','🏆','🥇','🚀','🌈','☀️','🌙','⚡','❄️','🍕','🍔',
  '✅','❌','❓','❗','💯','🔔','💡','🔒','🔑','💰','💎','🎯','🎮','📱','💻','☕','🍺','🌮','🍣','🍩',
];"""
if old_emoji in t:
    t = t.replace(old_emoji, new_emoji, 1)
    print("emojis ok")
else:
    print("emojis miss")

old_gifs = """const QUICK_GIFS = [
  { label: 'Wave', url: 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif' },
  { label: 'Clap', url: 'https://media.giphy.com/media/7rj2ZgQq6qpI9m7vXd/giphy.gif' },
  { label: 'Party', url: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif' },
  { label: 'Thumbs', url: 'https://media.giphy.com/media/111ebonMs90YLu/giphy.gif' },
  { label: 'Wow', url: 'https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif' },
  { label: 'Heart', url: 'https://media.giphy.com/media/3oz8xLd9DJq2l2VFtu/giphy.gif' },
];"""
new_gifs = """const QUICK_GIFS = [
  { label: 'Wave hello', url: 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif' },
  { label: 'Clap applause', url: 'https://media.giphy.com/media/7rj2ZgQq6qpI9m7vXd/giphy.gif' },
  { label: 'Party celebrate', url: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif' },
  { label: 'Thumbs up', url: 'https://media.giphy.com/media/111ebonMs90YLu/giphy.gif' },
  { label: 'Wow mind blown', url: 'https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif' },
  { label: 'Heart love', url: 'https://media.giphy.com/media/3oz8xLd9DJq2l2VFtu/giphy.gif' },
  { label: 'Laugh lmao', url: 'https://media.giphy.com/media/10JhviFuU2wBA0/giphy.gif' },
  { label: 'Cry sad', url: 'https://media.giphy.com/media/ROF8OVviPSk0M/giphy.gif' },
  { label: 'Dance happy', url: 'https://media.giphy.com/media/l0M9C2XT6F6eYjR1e/giphy.gif' },
  { label: 'Facepalm', url: 'https://media.giphy.com/media/XIqCqxNjSHlx1gYRbk/giphy.gif' },
  { label: 'Nod yes', url: 'https://media.giphy.com/media/ASd0UJjgB4Hy0/giphy.gif' },
  { label: 'No shake', url: 'https://media.giphy.com/media/15aGGXfR66ug/giphy.gif' },
  { label: 'High five', url: 'https://media.giphy.com/media/l4JyOHT67pTaS5sJO/giphy.gif' },
  { label: 'Mic drop', url: 'https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif' },
  { label: 'Coffee work', url: 'https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif' },
  { label: 'Fire lit', url: 'https://media.giphy.com/media/xT0xeJpnrWC2RdTYNg/giphy.gif' },
  { label: 'Cool sunglasses', url: 'https://media.giphy.com/media/dXFKDUolyLLi8gqHA3/giphy.gif' },
  { label: 'Thinking hmm', url: 'https://media.giphy.com/media/3o7TKTDn976rzVgky4/giphy.gif' },
  { label: 'Victory win', url: 'https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif' },
  { label: 'Thank you', url: 'https://media.giphy.com/media/osjgQPWRn3rwyB5c0V/giphy.gif' },
  { label: 'Good morning', url: 'https://media.giphy.com/media/l0MYC0LajbaPoEADu/giphy.gif' },
  { label: 'Good night', url: 'https://media.giphy.com/media/xUA7aN1ESkXgXVlXMs/giphy.gif' },
  { label: 'Excited jump', url: 'https://media.giphy.com/media/5GoVLqeAOo6PK/giphy.gif' },
  { label: 'Confused', url: 'https://media.giphy.com/media/1X7l0Rp1ZqUIuJ0e6j/giphy.gif' },
];"""
if old_gifs in t:
    t = t.replace(old_gifs, new_gifs, 1)
    print("gifs ok")
else:
    print("gifs miss")

if "gifSearch" not in t:
    t = t.replace(
        "const [gifOpen, setGifOpen] = useState(false);",
        """const [gifOpen, setGifOpen] = useState(false);
  const [gifSearch, setGifSearch] = useState('');
  const [gifResults, setGifResults] = useState<{ label: string; url: string }[]>([]);
  const [gifSearching, setGifSearching] = useState(false);""",
        1,
    )
    print("gif state ok")

if "runGifSearch" not in t:
    helper = """
  const runGifSearch = useCallback(async (q: string) => {
    const term = q.trim().toLowerCase();
    if (!term) {
      setGifResults([]);
      return;
    }
    const local = QUICK_GIFS.filter((g) => g.label.toLowerCase().includes(term));
    setGifResults(local);
    setGifSearching(true);
    try {
      const res = await fetch(
        `https://api.giphy.com/v1/gifs/search?api_key=dc6zaTOxFJmzC&q=${encodeURIComponent(term)}&limit=18&rating=g`
      );
      if (res.ok) {
        const data = await res.json();
        const remote = (data.data || [])
          .map((g: any) => ({
            label: String(g.title || term),
            url: String(g.images?.fixed_height?.url || g.images?.original?.url || ''),
          }))
          .filter((g: { url: string }) => !!g.url);
        if (remote.length) setGifResults(remote);
      }
    } catch {
      /* keep local */
    } finally {
      setGifSearching(false);
    }
  }, []);

"""
    m = re.search(r"  const refresh = useCallback[\s\S]*?\}, \[\]\);\n", t)
    if m:
        t = t[: m.end()] + helper + t[m.end() :]
        print("helper after refresh")
    else:
        needle = "const [gifSearching, setGifSearching] = useState(false);"
        if needle in t:
            t = t.replace(needle, needle + "\n" + helper, 1)
            print("helper after state")
        else:
            print("helper miss")

t = t.replace(
    'className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-transparent"',
    'className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-[#0c0a16]/40"',
)
t = t.replace(
    'className="flex-1 flex flex-col min-w-0"',
    'className="flex-1 flex flex-col min-w-0 bg-[#0c0a16]/30"',
    1,
)
t = t.replace(
    'className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/10 bg-white/25 dark:bg-[#161225]/70 backdrop-blur"',
    'className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/10 bg-[#0c0a16]/55 backdrop-blur"',
    1,
)
t = t.replace(
    "border-t border-zinc-200/80 dark:border-white/10 bg-white/30 dark:bg-[#14101f]/80 backdrop-blur",
    "border-t border-white/10 bg-[#0c0a16]/55 backdrop-blur",
)

old_hdr = """          <div className="px-4 py-4 border-b border-zinc-800 flex items-start justify-between">
            <div className="min-w-0">
              <div className="w-14 h-14 rounded-full bg-zinc-800 flex items-center justify-center mx-auto mb-2">
                {active.id === DEFAULT_GROUP_ID ? <Users size={24} className="text-violet-400" /> : <Hash size={24} className="text-zinc-400" />}
              </div>
              <div className="text-center text-sm font-semibold">{active.name}</div>
              <div className="text-center text-[11px] text-zinc-500 mt-0.5">
                {active.members.length} members
              </div>
            </div>
          </div>"""
new_hdr = """          <div className="px-4 py-5 border-b border-zinc-800 flex flex-col items-center justify-center text-center">
            <div className="w-14 h-14 rounded-full bg-zinc-800/90 flex items-center justify-center mb-2 ring-1 ring-violet-500/30">
              {active.id === DEFAULT_GROUP_ID ? <Users size={24} className="text-violet-400" /> : <Hash size={24} className="text-zinc-400" />}
            </div>
            <div className="text-sm font-semibold text-zinc-100">{active.name}</div>
            <div className="text-[11px] text-zinc-400 mt-0.5">
              {active.members.length} member{active.members.length === 1 ? '' : 's'}
            </div>
          </div>"""
if old_hdr in t:
    t = t.replace(old_hdr, new_hdr, 1)
    print("header ok")
else:
    t2, n = re.subn(
        r'<div className="px-4 py-4 border-b border-zinc-800 flex items-start justify-between">\s*<div className="min-w-0">[\s\S]*?</div>\s*</div>\s*\n\n          <div className="px-3 py-3 space-y-1',
        '''<div className="px-4 py-5 border-b border-zinc-800 flex flex-col items-center justify-center text-center">
            <div className="w-14 h-14 rounded-full bg-zinc-800/90 flex items-center justify-center mb-2 ring-1 ring-violet-500/30">
              {active.id === DEFAULT_GROUP_ID ? <Users size={24} className="text-violet-400" /> : <Hash size={24} className="text-zinc-400" />}
            </div>
            <div className="text-sm font-semibold text-zinc-100">{active.name}</div>
            <div className="text-[11px] text-zinc-400 mt-0.5">
              {active.members.length} member{active.members.length === 1 ? '' : 's'}
            </div>
          </div>

          <div className="px-3 py-3 space-y-1''',
        t,
        count=1,
    )
    if n:
        t = t2
        print("header loose ok")
    else:
        print("header miss")

new_gif_ui = """          {gifOpen && (
            <div className="px-3 pt-2 space-y-2 max-h-52 overflow-y-auto">
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-400" />
                  <input
                    value={gifSearch}
                    onChange={(e) => {
                      const v = e.target.value;
                      setGifSearch(v);
                      void runGifSearch(v);
                    }}
                    placeholder="Search GIFs…"
                    className="w-full pl-8 pr-2.5 py-1.5 text-xs rounded-lg bg-white/10 border border-white/15 text-zinc-100 placeholder:text-zinc-500 outline-none focus:border-violet-500"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => void runGifSearch(gifSearch)}
                  className="px-2.5 py-1.5 text-xs rounded-lg bg-violet-600 hover:bg-violet-500 text-white shrink-0"
                >
                  Search
                </button>
              </div>
              {gifSearching && <div className="text-[10px] text-zinc-400 px-1">Searching…</div>}
              <div className="grid grid-cols-3 gap-2">
                {(gifSearch.trim() ? gifResults : QUICK_GIFS).map((g) => (
                  <button
                    key={g.url + g.label}
                    type="button"
                    onClick={() => {
                      if (!active) return;
                      const msg: Message = {
                        id: `m-${Date.now()}`,
                        author_name: displayName || 'You',
                        author_email: email || 'anon',
                        text: '',
                        created_at: new Date().toISOString(),
                        gif_url: g.url,
                      };
                      updateGroup(active.id, (gg) => ({ ...gg, messages: [...gg.messages, msg] }));
                      try { void insertMessageCloud(active.id, msg as any); } catch {}
                      try { void upsertMemberCloud(active.id, displayName, email); } catch {}
                      setGifOpen(false);
                      setGifSearch('');
                      setGifResults([]);
                    }}
                    className="rounded-lg overflow-hidden border border-white/10 hover:border-violet-400/50"
                    title={g.label}
                  >
                    <img src={g.url} alt={g.label} className="w-full h-14 object-cover" />
                  </button>
                ))}
              </div>
              {gifSearch.trim() && !gifSearching && gifResults.length === 0 && (
                <div className="text-[10px] text-zinc-500 px-1 py-2">No GIFs found — try another word.</div>
              )}
            </div>
          )}"""

m = re.search(
    r"\{gifOpen && \(\s*<div className=\"px-3 pt-2 grid grid-cols-3[\s\S]*?\{QUICK_GIFS\.map\([\s\S]*?</div>\s*\)\}",
    t,
)
if m:
    t = t[: m.start()] + new_gif_ui + t[m.end() :]
    print("gif ui ok")
else:
    m2 = re.search(r"\{gifOpen && \([\s\S]*?QUICK_GIFS\.map\([\s\S]*?\)\}\s*</div>\s*\)\}", t)
    if m2:
        t = t[: m2.start()] + new_gif_ui + t[m2.end() :]
        print("gif ui loose ok")
    else:
        print("gif ui MISS")

t = t.replace(
    'className="px-3 pt-2 flex flex-wrap gap-1 max-h-28 overflow-y-auto"',
    'className="px-3 pt-2 flex flex-wrap gap-1 max-h-40 overflow-y-auto"',
)
t = t.replace(
    '<Users className="mx-auto text-zinc-300 mb-3" size={32} />',
    '<Users className="mx-auto text-violet-300/50 mb-3" size={32} />',
)
t = t.replace(
    'className="text-sm font-medium text-zinc-600"',
    'className="text-sm font-medium text-zinc-300"',
    1,
)

p.write_text(t)
print("DONE", "community-media-v2" in t, "runGifSearch" in t, "Search GIFs" in t)
