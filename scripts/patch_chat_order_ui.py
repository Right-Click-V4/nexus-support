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
    patterns = [
        (r"\{\(selected\.messages \|\| \[\]\)\.map\(",
         "{([...(selected.messages || [])].sort((a: any, b: any) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime())).map("),
        (r"\{\(conversation\.messages \|\| \[\]\)\.map\(",
         "{([...(conversation.messages || [])].sort((a: any, b: any) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime())).map("),
    ]
    changed = False
    for old, new in patterns:
        t2, n = re.subn(old, new, t, count=1)
        if n:
            t = t2
            changed = True
            print(path, "patched")
            break
    if not changed:
        for old in ["(selected.messages || []).map", "(conversation?.messages || []).map", "(active?.messages || []).map"]:
            if old in t:
                t = t.replace(old, f"[...{old.replace('.map','')}].sort((a: any, b: any) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime()).map", 1)
                print(path, "patched alt")
                changed = True
                break
    if changed:
        p.write_text(t)
    else:
        print(path, "no pattern")

fix("src/components/LiveChatPage.tsx")
fix("src/components/PortalLiveChatView.tsx")
