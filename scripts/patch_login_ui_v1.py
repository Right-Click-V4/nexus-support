#!/usr/bin/env python3
"""Login UI: slower top→bottom stars, remove planets, Branch field only for customer signup."""
from pathlib import Path
import re

# --- LoginScene ---
p = Path("src/components/LoginScene.tsx")
if p.exists() and p.stat().st_size > 2000:
    s = p.read_text()
    changed = False
    # Remove planet elements
    for cls in ("login-planet-a", "login-planet-b", "login-planet-c"):
        pat = re.compile(rf'\s*<DistantPlanet className="login-planet {cls}"[^/]*/>\s*')
        if pat.search(s):
            s = pat.sub("\n", s)
            changed = True
    # Slow star fall
    if "s.y += s.speed * dt * 0.06;" in s:
        s = s.replace("s.y += s.speed * dt * 0.06;", "s.y += s.speed * dt * 0.035;")
        changed = True
    if "speed: layer <= 1 ? 0.012 : layer === 2 ? 0.02 : 0.035," in s:
        s = s.replace(
            "speed: layer <= 1 ? 0.012 : layer === 2 ? 0.02 : 0.035,",
            "speed: layer <= 1 ? 0.007 : layer === 2 ? 0.012 : 0.02,",
        )
        changed = True
    if changed:
        p.write_text(s)
        print("LoginScene patched", len(s))
    else:
        print("LoginScene no change")
else:
    print("LoginScene skip")

# --- LoginPage: Branch only for customers ---
p = Path("src/components/LoginPage.tsx")
if p.exists() and p.stat().st_size > 2000:
    s = p.read_text()
    changed = False
    old_val = """      if (!branch.trim()) {
        setLocalError('Please select your branch');
        return;
      }"""
    new_val = """      if (!isAgent && !branch.trim()) {
        setLocalError('Please select your branch');
        return;
      }"""
    if old_val in s:
        s = s.replace(old_val, new_val)
        changed = True
        print("branch validation agent-aware")
    # Hide Branch field for agent signup
    if 'name="nexus-signup-branch"' in s and "{!isAgent &&" not in s:
        m = re.search(
            r'(<div>\s*<label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Branch</label>[\s\S]*?name="nexus-signup-branch"[\s\S]*?</select>\s*</div>)',
            s,
        )
        if m:
            block = m.group(1)
            s = s[: m.start()] + "{!isAgent && (\n              " + block + "\n              )}" + s[m.end() :]
            changed = True
            print("branch field agent-hidden")
        else:
            print("branch block regex miss")
    if changed:
        p.write_text(s)
        print("LoginPage patched", len(s))
    else:
        print("LoginPage no change")
else:
    print("LoginPage skip")
print("patch_login_ui_v1 done")
