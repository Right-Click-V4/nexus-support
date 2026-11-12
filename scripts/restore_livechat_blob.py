#!/usr/bin/env python3
"""Restore LiveChatPage + PortalLiveChatView from known-good SHAs if stubs."""
from pathlib import Path
import urllib.request
import subprocess

FALLBACKS = [
    "25e8827f",  # full LiveChatPage
    "0ec671fe345320a3cb6a12b101f987b445c3aa7a",
    "c3edde907e5e5be48439b7fea0df6dbe3dca6611",
    "9da2fccde137836cea2c0651da8f808d1051f67e",
]

def restore(rel, min_size=5000):
    p = Path(rel)
    if p.exists() and p.stat().st_size > min_size and b"PLACEHOLDER" not in p.read_bytes()[:80]:
        print(rel, "already good", p.stat().st_size)
        return True
    for sha in FALLBACKS:
        try:
            out = subprocess.check_output(
                ["git", "show", f"{sha}:{rel}"],
                text=True, stderr=subprocess.DEVNULL, timeout=15
            )
            if len(out) > min_size:
                p.write_text(out)
                print(rel, "restored via git", sha, len(out))
                return True
        except Exception:
            pass
        url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{sha}/{rel}"
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                data = r.read().decode("utf-8")
            if len(data) > min_size:
                p.write_text(data)
                print(rel, "restored via curl", sha, len(data))
                return True
        except Exception as e:
            print(rel, "fail", sha, str(e)[:50])
    print("FAILED to restore", rel)
    return False

ok1 = restore("src/components/LiveChatPage.tsx")
ok2 = restore("src/components/PortalLiveChatView.tsx")
raise SystemExit(0 if (ok1 and ok2) else 1)
