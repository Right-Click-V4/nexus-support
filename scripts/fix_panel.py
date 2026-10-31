#!/usr/bin/env python3
from pathlib import Path
import re
p = Path('src/components/AccountProfilePanel.tsx')
if not p.exists():
    print('no panel')
    raise SystemExit(0)
t = p.read_text()
lines = t.splitlines()
out = []
changed = False
for line in lines:
    if 'truncate' in line and 'email' in line and 'className' in line:
        fixed = '              <div className="text-sm text-zinc-600 dark:text-zinc-400 truncate">{email}</div>'
        if line.strip() != fixed.strip():
            changed = True
        out.append(fixed)
    else:
        out.append(line)
t2 = '\n'.join(out)
if t.endswith('\n'):
    t2 += '\n'
if changed:
    p.write_text(t2)
    print('panel email className fixed')
else:
    print('panel already ok')
