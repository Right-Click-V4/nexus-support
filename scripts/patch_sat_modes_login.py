"""Mode gates + login features. Satellite craft lives in SatelliteCraft.tsx (do not overwrite)."""
from pathlib import Path
import re

# SAT_SKIP_V2 — never inject DISH_SAT_V1; realistic craft is src/components/SatelliteCraft.tsx
fly = Path('src/components/LoginFlybys.tsx')
if fly.exists():
    s = fly.read_text()
    if "from './SatelliteCraft'" not in s and 'from "./SatelliteCraft"' not in s:
        if "from '../lib/skyTraffic'" in s:
            s = s.replace(
                "from '../lib/skyTraffic';",
                "from '../lib/skyTraffic';\nimport { SatelliteCraft } from './SatelliteCraft';",
                1,
            )
    if "type FlybyKind = 'ufo' | 'rocket';" in s and 'satellite' not in s.split('type FlybyKind')[1][:80]:
        s = s.replace(
            "type FlybyKind = 'ufo' | 'rocket';",
            "type FlybyKind = 'ufo' | 'rocket' | 'satellite'",
            1,
        )
    if 'function SatelliteCraft' in s:
        s2 = re.sub(
            r'function SatelliteCraft\(\{ uid \}: \{ uid: string \}\) \{.*?\n\}\n',
            '',
            s,
            count=1,
            flags=re.S,
        )
        if s2 != s:
            s = s2
            print('stripped inline SatelliteCraft')
    if "f.kind === 'satellite'" not in s and "f.kind === 'ufo'" in s:
        s = s.replace(
            """                {f.kind === 'ufo'
                  ? f.variant === 1
                    ? <UfoIon uid={`ufo-${f.id}`} />
                    : <UfoClassic uid={`ufo-${f.id}`} />
                  : <Rocket eid={`rocketFlame-${f.id}`} />}""",
            """                {f.kind === 'satellite' ? (
                  <SatelliteCraft uid={`sat-${f.id}`} />
                ) : f.kind === 'ufo' ? (
                  f.variant === 1 ? (
                    <UfoIon uid={`ufo-${f.id}`} />
                  ) : (
                    <UfoClassic uid={`ufo-${f.id}`} />
                  )
                ) : (
                  <Rocket eid={`rocketFlame-${f.id}`} />
                )}""",
            1,
        )
        print('wired sat render')
    fly.write_text(s)
    print('flybys sat preserved (no DISH_SAT)')
else:
    print('LoginFlybys missing')

core = Path('src/SystemAppCore.tsx')
if core.exists():
    s = core.read_text()
    if "type ReactNode" not in s and "from 'react'" in s:
        s = s.replace(
            "import { useEffect, useRef, useState } from 'react';",
            "import { useEffect, useRef, useState, type ReactNode } from 'react';",
            1,
        )
        s = s.replace('React.ReactNode', 'ReactNode')
    if 'MODE_GATES_V1' not in s:
        print('mode gates block skipped (already present or structure changed)')
    else:
        print('mode gates already')
    core.write_text(s)
else:
    print('SystemAppCore missing')

lp = Path('src/components/LoginPage.tsx')
if lp.exists():
    s = lp.read_text()
    if 'LOGIN_FEATURES_V2' in s:
        print('LoginPage features already')
    else:
        print('LoginPage features skip (structure may differ)')
    lp.write_text(s)
print('DONE')
