"""Ensure agent LiveChat messages render oldest→newest (Messenger top-to-bottom)."""
from pathlib import Path

p = Path('src/components/LiveChatPage.tsx')
if not p.exists():
    print('LiveChatPage.tsx missing')
    raise SystemExit(0)

s = p.read_text()
if 'oldest at top, newest at bottom' in s:
    print('already patched')
    raise SystemExit(0)

old = '''              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {(selected.messages || []).map((m, i) => {'''

new = '''              <div className="flex-1 min-h-0 overflow-y-auto p-4 flex flex-col gap-3">
                {/* Messenger-style: oldest at top, newest at bottom */}
                {[...(selected.messages || [])]
                  .sort((a, b) => {
                    const ta = new Date(a.created_at || 0).getTime();
                    const tb = new Date(b.created_at || 0).getTime();
                    return ta - tb;
                  })
                  .map((m, i) => {'''

if old not in s:
    old2 = '''              <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-3">
                {(selected.messages || []).map((m, i) => {'''
    if old2 in s:
        s = s.replace(old2, new, 1)
        p.write_text(s)
        print('patched (min-h variant)')
    else:
        print('pattern not found — skip')
        raise SystemExit(0)
else:
    s = s.replace(old, new, 1)
    p.write_text(s)
    print('patched LiveChatPage message order')

s = p.read_text()
s2 = s.replace(
    '<div className="flex-1 flex flex-col min-w-0">',
    '<div className="flex-1 flex flex-col min-w-0 min-h-0">',
    1,
)
if s2 != s:
    p.write_text(s2)
    print('added min-h-0 on chat pane')
