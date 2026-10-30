#!/usr/bin/env python3
"""Hard refresh must not log out — do not age heartbeat on pagehide."""
from pathlib import Path

path = Path("src/lib/tabSession.ts")
text = path.read_text()
if "session-refresh-keep-v1" in text:
    print("already")
    raise SystemExit(0)

old = """      if (Object.keys(prune(tabs)).length === 0) {
        try {
          localStorage.setItem(CLOSED_KEY, '1');
        } catch {
          /* ignore */
        }
        // Age the heartbeat so the next cold open is treated as a new session
        try {
          localStorage.setItem(LAST_BEAT_KEY, String(Date.now() - IDLE_MS - 1000));
        } catch {
          /* ignore */
        }
      }"""

new = """      if (Object.keys(prune(tabs)).length === 0) {
        try {
          localStorage.setItem(CLOSED_KEY, '1');
        } catch {
          /* ignore */
        }
        // Do NOT age LAST_BEAT here — pagehide also runs on hard refresh.
        // Idle logout uses wall-clock last_beat age; overnight close naturally ages it.
      }"""

if old in text:
    text = text.replace(old, new, 1)
    print("removed age on pagehide")
else:
    old2 = """      if (Object.keys(prune(tabs)).length === 0) {
        try {
          localStorage.setItem(CLOSED_KEY, '1');
        } catch {
          /* ignore */
        }
        // Stop advertising a live session for idle detection
        try {
          localStorage.setItem(LAST_BEAT_KEY, String(Date.now() - IDLE_MS - 1000));
        } catch {
          /* ignore */
        }
      }"""
    if old2 in text:
        text = text.replace(old2, new, 1)
        print("removed age on pagehide (alt)")
    else:
        print("pagehide block miss")

old_detect = """export function detectNewBrowserSession(): Promise<boolean> {
  const now = Date.now();

  // Other tabs still heartbeating in this browser?
  try {
    const others = Object.keys(prune(readTabs(), now));
    if (others.length > 0) {
      return Promise.resolve(false);
    }
  } catch {
    /* ignore */
  }

  // Heartbeats stopped → previous session is dead (also fixes Chrome session restore
  // restoring sessionStorage LIVE_KEY after the user fully closed the browser).
  const age = lastBeatAge(now);
  if (age > IDLE_MS) {
    try {
      sessionStorage.removeItem(LIVE_KEY);
    } catch {
      /* ignore */
    }
    try {
      localStorage.removeItem(CLOSED_KEY);
    } catch {
      /* ignore */
    }
    return Promise.resolve(true);
  }

  // Same tab refresh / navigation keeps sessionStorage + recent beat → keep session
  try {
    if (sessionStorage.getItem(LIVE_KEY) === '1') {
      return Promise.resolve(false);
    }
  } catch {
    /* private mode */
  }

  // Explicit flag: last tab/window was closed → force login
  try {
    if (localStorage.getItem(CLOSED_KEY) === '1') {
      localStorage.removeItem(CLOSED_KEY);
      return Promise.resolve(true);
    }
  } catch {
    /* ignore */
  }"""

new_detect = """export function detectNewBrowserSession(): Promise<boolean> {
  const now = Date.now();

  // Other tabs still heartbeating in this browser?
  try {
    const others = Object.keys(prune(readTabs(), now));
    if (others.length > 0) {
      return Promise.resolve(false);
    }
  } catch {
    /* ignore */
  }

  // Same-tab refresh: sessionStorage survives; heartbeat was recent (pagehide must not age it).
  let liveFlag = false;
  try {
    liveFlag = sessionStorage.getItem(LIVE_KEY) === '1';
  } catch {
    /* private mode */
  }

  const age = lastBeatAge(now);

  // Hard refresh / soft reload: keep session when this tab still has LIVE_KEY and beat is fresh
  if (liveFlag && age <= IDLE_MS) {
    try {
      localStorage.removeItem(CLOSED_KEY);
    } catch {
      /* ignore */
    }
    return Promise.resolve(false);
  }

  // Genuinely idle (browser closed long enough) — even if Chrome restored LIVE_KEY
  if (age > IDLE_MS) {
    try {
      sessionStorage.removeItem(LIVE_KEY);
    } catch {
      /* ignore */
    }
    try {
      localStorage.removeItem(CLOSED_KEY);
    } catch {
      /* ignore */
    }
    return Promise.resolve(true);
  }

  // Explicit flag: last tab closed and this is a cold open (no LIVE_KEY)
  try {
    if (localStorage.getItem(CLOSED_KEY) === '1') {
      localStorage.removeItem(CLOSED_KEY);
      return Promise.resolve(true);
    }
  } catch {
    /* ignore */
  }"""

if old_detect in text:
    text = text.replace(old_detect, new_detect, 1)
    print("detect reorder")
else:
    print("detect miss")

text = "/* session-refresh-keep-v1 */\n" + text
path.write_text(text)
print("done")
