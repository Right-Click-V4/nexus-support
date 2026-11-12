#!/usr/bin/env python3
"""Restore PlatformContext from known-good SHA if currently a stub."""
from pathlib import Path
import urllib.request
import subprocess

p = Path("src/context/PlatformContext.tsx")
GOOD = "9da2fccde137836cea2c0651da8f808d1051f67e"

def size_ok():
    return p.exists() and p.stat().st_size > 5000 and "PLACEHOLDER" not in p.read_text()[:200]

if size_ok():
    print("PlatformContext already good", p.stat().st_size)
    raise SystemExit(0)

print("Restoring PlatformContext from", GOOD)
try:
    out = subprocess.check_output(["git", "show", f"{GOOD}:src/context/PlatformContext.tsx"], text=True, stderr=subprocess.DEVNULL)
    if len(out) > 5000:
        p.write_text(out)
        print("restored via git show", len(out))
        raise SystemExit(0)
except Exception as e:
    print("git show failed:", e)

url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD}/src/context/PlatformContext.tsx"
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read().decode("utf-8")
    if len(data) > 5000:
        p.write_text(data)
        print("restored via curl", len(data))
    else:
        print("download too small")
except Exception as e:
    print("curl failed:", e)
