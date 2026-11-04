#!/usr/bin/env python3
"""Slow presence / ticket polls; chat leans on less frequent silent refresh (egress-friendly)."""
from pathlib import Path

PATCHES = [
    ("src/lib/deskPresence.ts", [
        ("const LIVE_MS = 90_000;", "const LIVE_MS = 180_000;"),
        ("window.setInterval(emit, 10_000);", "window.setInterval(emit, 45_000);"),
        ("window.setInterval(emit, 10000);", "window.setInterval(emit, 45_000);"),
    ]),
    ("src/SystemApp.tsx", [
        ("setInterval(tick, 4000)", "setInterval(tick, 30_000)"),
        ("setInterval(tick, 4_000)", "setInterval(tick, 30_000)"),
        ("setInterval(tick, 5000)", "setInterval(tick, 30_000)"),
    ]),
    ("src/SystemAppCore.tsx", [
        ("setInterval(tick, 4000)", "setInterval(tick, 30_000)"),
        ("setInterval(tick, 4_000)", "setInterval(tick, 30_000)"),
        ("setInterval(tick, 5000)", "setInterval(tick, 30_000)"),
    ]),
    ("src/context/TicketContext.tsx", [
        ("window.setInterval(soft, 30_000);", "window.setInterval(soft, 90_000);"),
        ("window.setInterval(soft, 60_000);", "window.setInterval(soft, 90_000);"),
        ("if (now - last < 30_000) return;", "if (now - last < 45_000) return;"),
        ("if (now - last < 15_000) return;", "if (now - last < 45_000) return;"),
    ]),
    ("src/components/PortalLiveChat.tsx", [
        ("setInterval(() => { void refreshPlatform(); }, 4000);", "setInterval(() => { void refreshPlatform(); }, 30_000);"),
        ("setInterval(() => { void refreshPlatform(); }, 4_000);", "setInterval(() => { void refreshPlatform(); }, 30_000);"),
        ("setInterval(() => setPresenceTick((n) => n + 1), 5000);", "setInterval(() => setPresenceTick((n) => n + 1), 30_000);"),
        ("setInterval(() => setPresenceTick((n) => n + 1), 5_000);", "setInterval(() => setPresenceTick((n) => n + 1), 30_000);"),
        (", 8000);", ", 60_000);"),
        (", 8_000);", ", 60_000);"),
        ("setInterval(() => refreshPlatform(), 3000);", "setInterval(() => refreshPlatform(), 30_000);"),
        ("setInterval(() => refreshPlatform(), 3_000);", "setInterval(() => refreshPlatform(), 30_000);"),
    ]),
    ("src/components/LiveChatPage.tsx", [
        ("setInterval(beat, 5000)", "setInterval(beat, 30_000)"),
        ("setInterval(beat, 5_000)", "setInterval(beat, 30_000)"),
        ("setInterval(beat, 4000)", "setInterval(beat, 30_000)"),
        ("""setInterval(() => {
      void refreshPlatform();
    }, 4000);""", """setInterval(() => {
      void refreshPlatform();
    }, 30_000);"""),
        ("""setInterval(() => {
      void refreshPlatform();
    }, 4_000);""", """setInterval(() => {
      void refreshPlatform();
    }, 30_000);"""),
    ]),
]

applied = 0
for path, pairs in PATCHES:
    p = Path(path)
    if not p.exists():
        print("skip missing", path)
        continue
    text = p.read_text()
    orig = text
    for old, new in pairs:
        if old in text and old != new:
            text = text.replace(old, new)
            applied += 1
            print("patched", path, ":", old[:50].replace("\n", " "), "->", new[:50].replace("\n", " "))
    if text != orig:
        p.write_text(text)
        print("wrote", path, len(text))
    else:
        print("no change", path)

print("done, replacements", applied)
