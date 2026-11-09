#!/usr/bin/env python3
"""Ensure every TSX that calls useState imports it from react."""
from pathlib import Path
import re

fixed = 0
for p in Path('src').rglob('*.tsx'):
    t = p.read_text(errors='ignore')
    if not re.search(r'\buseState\s*[\(<]', t):
        continue
    if re.search(r'\{[^}]*\buseState\b[^}]*\}\s*from\s*[\'"]react[\'"]', t, re.S):
        continue
    if 'React.useState' in t:
        continue
    m = re.search(r"import\s*\{([^}]*)\}\s*from\s*['\"]react['\"]", t)
    if m:
        names = m.group(1)
        if 'useState' not in names:
            new_names = 'useState, ' + names.strip()
            t = t[:m.start(1)] + new_names + t[m.end(1):]
            p.write_text(t)
            fixed += 1
            print('fixed', p)
    else:
        t = "import { useState } from 'react';\n" + t
        p.write_text(t)
        fixed += 1
        print('added import', p)
print('ensure-react done', fixed)
