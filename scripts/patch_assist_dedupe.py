#!/usr/bin/env python3
"""Final pass: remove duplicate claimChat from LiveChat usePlatform destructure."""
from pathlib import Path
import re

lp = Path('src/components/LiveChatPage.tsx')
if not lp.exists():
    raise SystemExit(0)
t = lp.read_text()
m = re.search(r'const \{\n(?:.|\n)*?\} = usePlatform\(\);', t)
if not m:
    print('no destructure')
    raise SystemExit(0)
block = m.group(0)
if block.count('claimChat') <= 1 and 'requestAssist' in block and 'respondAssist' in block:
    print('already clean')
else:
    lines = block.split('\n')
    cleaned = []
    for line in lines:
        key = line.strip().rstrip(',')
        if key in ('claimChat', 'requestAssist', 'respondAssist'):
            continue
        cleaned.append(line)
    for i in range(len(cleaned) - 1, -1, -1):
        if 'usePlatform' in cleaned[i] and '}' in cleaned[i]:
            cleaned.insert(i, '    respondAssist,')
            cleaned.insert(i, '    requestAssist,')
            cleaned.insert(i, '    claimChat,')
            break
    new_block = '\n'.join(cleaned)
    t = t.replace(block, new_block, 1)
    lp.write_text(t)
    print('deduped livechat destructure', new_block.count('claimChat'))

pc = Path('src/context/PlatformContext.tsx')
if pc.exists():
    s = pc.read_text()
    while s.count('const claimChat = async') > 1:
        parts = s.split('  const claimChat = async')
        rebuilt = parts[0] + '  const claimChat = async' + parts[1]
        for extra in parts[2:]:
            idx = extra.find('\n  const ')
            if idx >= 0:
                rebuilt += extra[idx + 1 :]
            else:
                rebuilt += extra
        s = rebuilt
        print('deduped platform claimChat')
    if s.count('claimChat:') > 1:
        lines = s.splitlines(keepends=True)
        seen = False
        out = []
        for line in lines:
            if 'claimChat:' in line and 'conversationId' in line:
                if seen:
                    continue
                seen = True
            out.append(line)
        s = ''.join(out)
        print('deduped type')
    pc.write_text(s)
print('done')
