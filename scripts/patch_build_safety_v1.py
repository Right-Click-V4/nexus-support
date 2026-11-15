#!/usr/bin/env python3
"""Last-mile build safety: fix common broken tokens that fail vite/esbuild."""
from pathlib import Path
import re

ls = Path('src/components/LoginScene.tsx')
if ls.exists():
    t = ls.read_text()
    t2 = re.sub(r',\\n(\s+\w+:)', r',\n\1', t)
    if t2 != t:
        ls.write_text(t2)
        print('LoginScene fixed literal \\n')
    else:
        print('LoginScene ok')

sac = Path('src/SystemAppCore.tsx')
if sac.exists():
    t = sac.read_text()
    if 'Rootexport function Root' in t:
        t = t.replace('export function Rootexport function Root', 'export function Root')
        sac.write_text(t)
        print('SystemAppCore fixed doubled Root')
    else:
        print('SystemAppCore Root ok')

plc = Path('src/components/PortalLiveChat.tsx')
if plc.exists():
    t = plc.read_text()
    t2 = re.sub(
        r'disabled=\{isOnHold\}\s+onClick=\{\(\) => void send\(\)\}\s+disabled=\{!draft\.trim\(\)\}',
        'disabled={isOnHold || !draft.trim()} onClick={() => void send()}',
        t,
    )
    if t2 != t:
        plc.write_text(t2)
        print('PortalLiveChat fixed duplicate disabled')
    else:
        print('PortalLiveChat disabled ok')

cp = Path('src/components/CustomerPortal.tsx')
if cp.exists():
    if 'export default' not in cp.read_text() or cp.stat().st_size < 50000:
        print('CustomerPortal STUB/MISSING default')
    else:
        print('CustomerPortal ok', cp.stat().st_size)

print('patch_build_safety_v1 done')
