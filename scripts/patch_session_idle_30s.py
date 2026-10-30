#!/usr/bin/env python3
"""Session idle after last tab close: 30 seconds (was 5 minutes)."""
from pathlib import Path

path = Path("src/lib/tabSession.ts")
text = path.read_text()
changed = False

for old, new in [
    ("const IDLE_MS = 5 * 60 * 1000; // 5 minutes", "const IDLE_MS = 30 * 1000; // 30 seconds"),
    ("const IDLE_MS = 5 * 60 * 1000;", "const IDLE_MS = 30 * 1000; // 30 seconds"),
    ("const IDLE_MS = 300000;", "const IDLE_MS = 30 * 1000; // 30 seconds"),
    ("const IDLE_MS = 30 * 1000; // 30 seconds", "const IDLE_MS = 30 * 1000; // 30 seconds"),
]:
    if old in text and "30 * 1000" not in text.split("IDLE_MS")[1][:40]:
        text = text.replace(old, new, 1)
        changed = True
        print("idle -> 30s")
        break
else:
    if "30 * 1000" in text and "IDLE_MS" in text:
        print("already 30s")

age_block = """        // Age the heartbeat so the next cold open is treated as a new session
        try {
          localStorage.setItem(LAST_BEAT_KEY, String(Date.now() - IDLE_MS - 1000));
        } catch {
          /* ignore */
        }"""
age_block2 = """        // Stop advertising a live session for idle detection
        try {
          localStorage.setItem(LAST_BEAT_KEY, String(Date.now() - IDLE_MS - 1000));
        } catch {
          /* ignore */
        }"""
keep = """        // Do NOT age LAST_BEAT here — pagehide also runs on hard refresh."""
if age_block in text:
    text = text.replace(age_block, keep, 1)
    changed = True
    print("removed age pagehide")
elif age_block2 in text:
    text = text.replace(age_block2, keep, 1)
    changed = True
    print("removed age pagehide alt")

if "session-idle-30s-v1" not in text:
    text = "/* session-idle-30s-v1 */\n" + text
    changed = True

if changed:
    path.write_text(text)
    print("done")
else:
    print("no change")
