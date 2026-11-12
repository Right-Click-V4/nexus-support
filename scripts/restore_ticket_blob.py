#!/usr/bin/env python3
"""Restore TicketContext from known-good SHA if currently a stub."""
from pathlib import Path
import urllib.request
import subprocess

p = Path("src/context/TicketContext.tsx")
GOOD = "c3edde907e5e5be48439b7fea0df6dbe3dca6611"

def size_ok():
    return p.exists() and p.stat().st_size > 8000 and "PLACEHOLDER" not in p.read_text()[:200]

if size_ok():
    print("TicketContext already good", p.stat().st_size)
    raise SystemExit(0)

print("Restoring TicketContext from", GOOD)
try:
    out = subprocess.check_output(["git", "show", f"{GOOD}:src/context/TicketContext.tsx"], text=True, stderr=subprocess.DEVNULL)
    if len(out) > 8000:
        p.write_text(out)
        print("restored via git show", len(out))
        raise SystemExit(0)
except Exception as e:
    print("git show failed:", e)

url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD}/src/context/TicketContext.tsx"
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read().decode("utf-8")
    if len(data) > 8000:
        p.write_text(data)
        print("restored via curl", len(data))
except Exception as e:
    print("curl failed:", e)
