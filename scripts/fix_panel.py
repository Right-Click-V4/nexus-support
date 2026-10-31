#!/usr/bin/env python3
from pathlib import Path
import re
p = Path('src/components/AccountProfilePanel.tsx')
if not p.exists():
    print('no panel')
    raise SystemExit(0)
t = p.read_text()
t2 = re.sub(
    r'className="text-sm text-zinc-600 dark:text-zinc-400 truncate\\?\s*\{email\}"',
    'className="text-sm text-zinc-600 dark:text-zinc-400 truncate"'+'{email}'+'"'.replace('{email}','{email}'),
    t,
)
# simpler replacements
for bad in ['truncate\\ {email}', 'truncate {email}', 'truncate\\{email}', 'truncate\\s*{email}']:
    pass
t2 = t.replace('truncate\\ {email}', 'truncate>{email}'.replace('>','{').replace('email}','email}'))
# robust:
import re as _re
t2 = _re.sub(r'truncate(?:\\)?\s*\{email\}', 'truncate{email}'.replace('{email}', '{email}'), t)
# final clear approach
t2 = t
if 'truncate' in t and 'email' in t:
    lines = t.splitlines()
    out = []
    for line in lines:
        if 'truncate' in line and '{email}' in line.replace(' ',''):
            out.append('              <div className="text-sm text-zinc-600 dark:text-zinc-400 truncate">{email}</div>')
        else:
            out.append(line)
    t2 = '\n'.join(out) + ('\n' if t.endswith('\n') else '')
if t2 != t:
    p.write_text(t2)
    print('panel fixed')
else:
    print('panel already ok')
    for i, line in enumerate(t.splitlines(), 1):
        if 'truncate' in line and 'email' in line:
            print(i, repr(line))
