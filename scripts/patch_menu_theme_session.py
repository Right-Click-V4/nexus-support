#!/usr/bin/env python3
"""Theme-aware action menu (nexus-light/dark) + reliable last-window logout."""
from pathlib import Path

ts = Path("src/lib/tabSession.ts")
t = ts.read_text()
if "tab-session-closed-flag-v1" not in t:
    if "CLOSED_KEY" not in t:
        t = t.replace(
            "const LIVE_KEY = 'nexus-auth-live-v3'; // sessionStorage — survives refresh, dies with browser session",
            "const LIVE_KEY = 'nexus-auth-live-v3'; // sessionStorage — survives refresh, dies with browser session\n"
            "const CLOSED_KEY = 'nexus-auth-closed-v1'; // localStorage — set when last tab closes",
            1,
        )
        print("ts closed key")

    t = t.replace("const STALE_MS = 12_000;", "const STALE_MS = 4_000;", 1)
    t = t.replace("const SIBLING_WAIT_MS = 200;", "const SIBLING_WAIT_MS = 280;", 1)

    old_detect_mid = """  // Other tabs still heartbeating?
  try {
    const others = Object.keys(prune(readTabs()));
    if (others.length > 0) {
      return Promise.resolve(false);
    }
  } catch {
    /* ignore */
  }

  // Ask open siblings via BroadcastChannel"""
    new_detect_mid = """  // Explicit flag: last tab/window was closed → force login
  try {
    if (localStorage.getItem(CLOSED_KEY) === '1') {
      localStorage.removeItem(CLOSED_KEY);
      return Promise.resolve(true);
    }
  } catch {
    /* ignore */
  }

  // Other tabs still heartbeating?
  try {
    const others = Object.keys(prune(readTabs()));
    if (others.length > 0) {
      return Promise.resolve(false);
    }
  } catch {
    /* ignore */
  }

  // Ask open siblings via BroadcastChannel"""
    if old_detect_mid in t:
        t = t.replace(old_detect_mid, new_detect_mid, 1)
        print("ts detect ok")
    else:
        print("ts detect miss")

    old_hide = """  const onPageHide = () => {
    try {
      const tabs = prune(readTabs());
      delete tabs[tabId];
      writeTabs(tabs);
    } catch {
      /* ignore */
    }
  };"""
    new_hide = """  const onPageHide = () => {
    try {
      const tabs = prune(readTabs());
      delete tabs[tabId];
      writeTabs(tabs);
      if (Object.keys(prune(tabs)).length === 0) {
        try {
          localStorage.setItem(CLOSED_KEY, '1');
        } catch {
          /* ignore */
        }
      }
    } catch {
      /* ignore */
    }
  };"""
    if old_hide in t:
        t = t.replace(old_hide, new_hide, 1)
        print("ts pagehide ok")
    else:
        print("ts pagehide miss")

    old_mark = """export function markTabSessionLive() {
  try {
    sessionStorage.setItem(LIVE_KEY, '1');
  } catch {
    /* ignore */
  }
}"""
    new_mark = """export function markTabSessionLive() {
  try {
    sessionStorage.setItem(LIVE_KEY, '1');
  } catch {
    /* ignore */
  }
  try {
    localStorage.removeItem(CLOSED_KEY);
  } catch {
    /* ignore */
  }
}"""
    if old_mark in t:
        t = t.replace(old_mark, new_mark, 1)
        print("ts mark ok")
    else:
        print("ts mark miss")

    t = "/* tab-session-closed-flag-v1 */\n" + t
    ts.write_text(t)
    print("ts done")
else:
    print("ts already")

css = Path("src/index.css")
if css.exists():
    c = css.read_text()
    if "portal-mytickets-action-menu-theme-v1" not in c:
        c += """

/* portal-mytickets-action-menu-theme-v1 */
.portal-mytickets-action-menu {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
}
html.nexus-light .portal-mytickets-action-menu {
  background: rgba(255, 255, 255, 0.92) !important;
  border-color: rgba(124, 58, 237, 0.28) !important;
  color: #1e1b4b;
}
html.nexus-light .portal-mytickets-action-menu button {
  color: #312e81 !important;
}
html.nexus-light .portal-mytickets-action-menu button:hover {
  background: rgba(124, 58, 237, 0.1) !important;
  color: #4c1d95 !important;
}
html.nexus-dark .portal-mytickets-action-menu {
  background: rgba(24, 24, 27, 0.92) !important;
  border-color: rgba(167, 139, 250, 0.35) !important;
  color: #f4f4f5;
}
html.nexus-dark .portal-mytickets-action-menu button {
  color: #e4e4e7 !important;
}
html.nexus-dark .portal-mytickets-action-menu button:hover {
  background: rgba(167, 139, 250, 0.15) !important;
  color: #f5f3ff !important;
}
"""
        css.write_text(c)
        print("css ok")
    else:
        print("css already")
else:
    print("css miss")

print("done")
