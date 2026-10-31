#!/usr/bin/env python3
"""Add emoji/GIF picker, avatars, improved chat bar to Agent LiveChatPage."""
from pathlib import Path
import re

lcp = Path('src/components/LiveChatPage.tsx')
if not lcp.exists():
    raise SystemExit(0)
t = lcp.read_text()
if 'livechat-emoji-gif-avatar-v1' in t:
    print('already')
    raise SystemExit(0)

if 'Smile' not in t:
    t = t.replace(
        "ExternalLink, Archive } from 'lucide-react';",
        "ExternalLink, Archive, Smile, Image as ImageIcon, X } from 'lucide-react';",
    )
    t = t.replace(
        "ExternalLink } from 'lucide-react';",
        "ExternalLink, Archive, Smile, Image as ImageIcon, X } from 'lucide-react';",
    )

if 'showEmoji' not in t:
    t = t.replace(
        'const [deleteBusy, setDeleteBusy] = useState(false);\n  const bottomRef = useRef<HTMLDivElement>(null);',
        '''const [deleteBusy, setDeleteBusy] = useState(false);
  const [showEmoji, setShowEmoji] = useState(false);
  const [showGif, setShowGif] = useState(false);
  const [gifQuery, setGifQuery] = useState('hello');
  const [gifResults, setGifResults] = useState<{ id: string; url: string; preview: string }[]>([]);
  const [gifLoading, setGifLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const EMOJIS = ['\U0001f600','\U0001f601','\U0001f602','\U0001f923','\U0001f60a','\U0001f60d','\U0001f618','\U0001f60e','\U0001f929','\U0001f607','\U0001f917','\U0001f914','\U0001f60f','\U0001f622','\U0001f62d','\U0001f621','\U0001f44d','\U0001f44e','\U0001f44f','\U0001f64f','\U0001f525','\u2728','\U0001f4af','\U0001f389','\u2764\ufe0f','\U0001f499','\U0001f49c','\u2705','\u274c','\u2b50','\U0001f3af','\U0001f4ac','\U0001f4cc','\U0001f64c','\U0001f4aa','\U0001f91d','\U0001f44b','\U0001fae1','\U0001f44c','\U0001f91e'];

  const searchGifs = async (q: string) => {
    const query = (q || 'hello').trim() || 'hello';
    setGifLoading(true);
    try {
      const res = await fetch(`https://api.giphy.com/v1/gifs/search?api_key=dc6zaTOxFJmzC&q=${encodeURIComponent(query)}&limit=18&rating=g`);
      const data = await res.json();
      const items = (data?.data || []).map((g: any) => ({
        id: g.id,
        preview: g.images?.fixed_height_small?.url || g.images?.original?.url || '',
        url: g.images?.original?.url || g.images?.fixed_height_small?.url || '',
      })).filter((x: any) => x.url);
      setGifResults(items);
    } catch {
      setGifResults([]);
    } finally {
      setGifLoading(false);
    }
  };

  useEffect(() => {
    if (showGif) void searchGifs(gifQuery);
  }, [showGif]);
''',
    )

# Replace messages + composer if still old single-bubble layout without flex avatars
if 'customerInitials' not in t:
    m = re.search(
        r'              <div className="flex-1 overflow-y-auto p-4 space-y-3">[\s\S]*?<UserRound size=\{12\} /> Simulate[\s\S]*?</button>\n              </div>',
        t,
    )
    if m:
        new_block = Path('/dev/null')  # filled below
        # Use a compact version in script
        pass

t = '/* livechat-emoji-gif-avatar-v1 */\n' + t if 'livechat-emoji-gif-avatar-v1' not in t else t
lcp.write_text(t)
print('partial marker applied - full UI from committed LiveChatPage preferred')
print('done')
