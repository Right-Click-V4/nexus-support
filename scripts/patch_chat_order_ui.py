#!/usr/bin/env python3
"""Messenger-style ascending message order in agent + customer chat UIs."""
from pathlib import Path
import re

p = Path("src/components/LiveChatPage.tsx")
if p.exists():
    t = p.read_text()
    if "sortedMessages" not in t:
        m = re.search(r"const selected = conversations\.find\([^\n]+\n?", t)
        if m:
            insert = m.group(0) + """  const sortedMessages = [...((selected?.messages || []) as { created_at?: string }[])].sort(
    (a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime(),
  );
"""
            t = t[: m.start()] + insert + t[m.end() :]
            print("agent sortedMessages")
        if "(selected.messages || []).map" in t:
            t = t.replace(
                "(selected.messages || []).map",
                "(sortedMessages as typeof selected.messages).map",
                1,
            )
            print("agent map wired")
    p.write_text(t)

p = Path("src/components/PortalLiveChatView.tsx")
if p.exists():
    t = p.read_text()
    if "const messages = conversation?.messages || [];" in t and "sort(" not in t[t.find("const messages") : t.find("const messages") + 200]:
        t = t.replace(
            "const messages = conversation?.messages || [];",
            """const messages = [...(conversation?.messages || [])].sort(
    (a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime(),
  );""",
            1,
        )
        print("portal sort")
        p.write_text(t)
    elif "sort(" in t:
        print("portal already sorted")
print("ui order done")
