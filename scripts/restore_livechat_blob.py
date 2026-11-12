#!/usr/bin/env python3
"""Restore LiveChatPage + PortalLiveChatView from known-good SHA if stubs."""
from pathlib import Path
import urllib.request
import subprocess

# d3daf12 is after the customerInitials declaration order fix
GOOD = "d3daf12a8f0e5c1b9e2d4a6f8c0b2e4d6a8f0c2"
# Fallback known full blobs
FALLBACKS = [
    "25e8827f",
    "0ec671fe345320a3cb6a12b101f987b445c3aa7a",
    "c3edde907e5e5be48439b7fea0df6dbe3dca6611",
]

def restore(rel, min_size=5000):
    p = Path(rel)
    if p.exists() and p.stat().st_size > min_size and "PLACEHOLDER" not in p.read_text()[:200]:
        print(rel, "already good", p.stat().st_size)
        return
    for sha in [GOOD] + FALLBACKS:
        try:
            out = subprocess.check_output(["git", "show", f"{sha}:{rel}"], text=True, stderr=subprocess.DEVNULL)
            if len(out) > min_size:
                p.write_text(out)
                print(rel, "restored via git", sha, len(out))
                return
        except Exception:
            pass
        url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{sha}/{rel}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = r.read().decode("utf-8")
            if len(data) > min_size:
                p.write_text(data)
                print(rel, "restored via curl", sha, len(data))
                return
        except Exception as e:
            print(rel, "fail", sha, str(e)[:60])

restore("src/components/LiveChatPage.tsx")
restore("src/components/PortalLiveChatView.tsx")
