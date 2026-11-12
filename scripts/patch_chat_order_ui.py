#!/usr/bin/env python3
"""Force Messenger-style ascending message order in LiveChat UI components."""
from pathlib import Path
import re

def fix(path: str):
    p = Path(path)
    if not p.exists() or p.stat().st_size < 1000:
        print("skip", path)
        return
    t = p.read_text()
    if "Messenger-style" in t or ("sort((a" in t and "created_at" in t):
        print(path, "already sorted")
        return
    changed = False
    old1 = "const messages = conversation?.messages || [];"
    new1 = "const messages = [...(conversation?.messages || [])].sort((a: any, b: any) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime());"
    if old1 in t:
        t = t.replace(old1, new1)
        changed = True
        print(path, "patched const messages")
    if "(selected.messages || []).map" in t and "sort((a" not in t:
        t = t.replace(
            "(selected.messages || []).map",
            "[...(selected.messages || [])].sort((a: any, b: any) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime()).map",
            1,
        )
        changed = True
        print(path, "patched selected.messages map")
    if changed:
        p.write_text(t)
    else:
        print(path, "no pattern matched")

fix("src/components/LiveChatPage.tsx")
fix("src/components/PortalLiveChatView.tsx")
