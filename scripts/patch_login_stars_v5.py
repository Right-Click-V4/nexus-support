#!/usr/bin/env python3
"""Login v5: slightly longer trail; stars+dust pure slow top\u2192bottom only (no sideways)."""
from pathlib import Path
import re

p = Path("src/components/LoginScene.tsx")
if p.exists() and p.stat().st_size > 3000:
    s = p.read_text()
    if "TRAIL_MAX_DIST = 175" not in s:
        s = re.sub(r"const TRAIL_MAX_DIST = \d+;", "const TRAIL_MAX_DIST = 175; // TRAIL_V5 slightly longer", s, count=1)
        print("trail len 175")

    s = re.sub(
        r"speed:\s*layer\s*<=\s*1\s*\?\s*[0-9.]+\s*:\s*layer\s*===\s*2\s*\?\s*[0-9.]+(?:\s*:\s*layer\s*===\s*3\s*\?\s*[0-9.]+)?\s*:\s*[0-9.]+",
        "speed: layer <= 1 ? 0.003 : layer === 2 ? 0.005 : layer === 3 ? 0.008 : 0.012",
        s,
    )
    s = re.sub(
        r"s\.y\s*\+=\s*s\.speed\s*\*\s*dt\s*\*\s*[0-9.]+\s*;",
        "s.y += s.speed * dt * 0.014; // pure top\u2192bottom, slow",
        s,
    )
    s = re.sub(r"\n\s*s\.x\s*\+=\s*[^;]+;", "\n", s)
    if "STARS_V5_PURE" not in s:
        s = s.replace("function StarCanvas", "// STARS_V5_PURE\nfunction StarCanvas", 1)
    p.write_text(s)
    print("LoginScene", len(s), "braces", s.count("{") - s.count("}"))
else:
    print("LoginScene skip")

for css_name in ("src/login-glass.css", "src/login-galaxy-polish.css", "src/index.css", "src/login-perf.css"):
    cp = Path(css_name)
    if not cp.exists():
        continue
    c = cp.read_text()
    orig = c
    c = re.sub(
        r"@keyframes login-dust-drift\s*\{[^}]+\}",
        "@keyframes login-dust-drift {\n"
        "  from { transform: translate3d(0, -8%, 0); }\n"
        "  to { transform: translate3d(0, 8%, 0); }\n"
        "}",
        c,
        count=1,
    )
    c = re.sub(r"animation:\s*login-dust-drift\s+[0-9.]+s", "animation: login-dust-drift 70s", c)
    c = re.sub(
        r"@keyframes login-nebula-drift\s*\{[^}]+\}",
        "@keyframes login-nebula-drift {\n"
        "  from { transform: translate3d(0, -1.5%, 0) scale(1); }\n"
        "  to { transform: translate3d(0, 2%, 0) scale(1.04); }\n"
        "}",
        c,
        count=1,
    )
    c = re.sub(
        r"@keyframes login-galaxy-drift\s*\{[^}]+\}",
        "@keyframes login-galaxy-drift {\n"
        "  from { transform: rotate(12deg) scale(1.05) translate3d(0, -1%, 0); }\n"
        "  to { transform: rotate(13deg) scale(1.07) translate3d(0, 1.5%, 0); }\n"
        "}",
        c,
        count=1,
    )
    c = re.sub(
        r"@keyframes login-star-fall\s*\{[\s\S]*?\n\}",
        "@keyframes login-star-fall {\n"
        "  from { transform: translate3d(0, -12vh, 0); opacity: 0; }\n"
        "  8% { opacity: 1; }\n"
        "  to { transform: translate3d(0, 112vh, 0); opacity: 0.15; }\n"
        "}",
        c,
    )
    if c != orig:
        cp.write_text(c)
        print("css", css_name)
    else:
        print("css unchanged", css_name)

print("patch_login_stars_v5 done")
