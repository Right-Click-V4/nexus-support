"""Remove redundant hero chip pills (Live status / Omnichannel inbox row)."""
from pathlib import Path
import re

p = Path('src/components/LoginPage.tsx')
if not p.exists():
    print('LoginPage missing')
    raise SystemExit(0)
s = p.read_text()
if 'login-hero-chips' not in s and 'Live status' not in s:
    print('chips already gone')
    raise SystemExit(0)
s2, n = re.subn(
    r'\s*<div className="login-hero-chips mt-5 flex flex-wrap gap-2">.*?</div>\n',
    '\n',
    s,
    count=1,
    flags=re.S,
)
if not n:
    s2, n = re.subn(
        r'\s*<div className="mt-5 flex flex-wrap gap-2">\s*\{\(isAgent[\s\S]*?\)\}\s*</div>\n',
        '\n',
        s,
        count=1,
    )
if n:
    p.write_text(s2)
    print('hero chips removed')
else:
    print('chips pattern miss')
