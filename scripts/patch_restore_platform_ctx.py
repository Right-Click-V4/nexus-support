#!/usr/bin/env python3
"""Restore PlatformContext.tsx if wiped by a bad patch."""
from pathlib import Path
import urllib.request

GOOD_SHA = "1b72983c13f2e5104682cc41c7fca903a53c452d"
URL = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD_SHA}/src/context/PlatformContext.tsx"

p = Path("src/context/PlatformContext.tsx")
text = p.read_text() if p.exists() else ""
if "export function usePlatform" in text and len(text) > 500:
    print("platform ok", len(text))
else:
    print("platform wiped, restoring...")
    try:
        content = urllib.request.urlopen(URL, timeout=30).read().decode()
    except Exception as e:
        print("fetch failed", e)
        raise SystemExit(1)
    if "export function usePlatform" not in content:
        print("fetched file invalid")
        raise SystemExit(1)
    p.write_text(content)
    print("restored platform", len(content))
