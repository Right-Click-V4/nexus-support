/**
 * Multi-tab session lifetime:
 * - Session stays alive while ANY app tab is open (shared via localStorage heartbeats).
 * - When the last tab/window closes, the session is cleared so the next visit requires login.
 * - A short grace window allows refresh of the only open tab without forcing re-login.
 */

const TABS_KEY = 'nexus-live-tabs-v1';
const LAST_CLOSE_KEY = 'nexus-last-tab-close-v1';
const HEARTBEAT_MS = 2000;
const STALE_MS = 10_000;
/** If the only tab reloads within this window, keep the session (refresh). */
const REFRESH_GRACE_MS = 4_000;

export type TabSessionClearFn = () => void | Promise<void>;

function readTabs(): Record<string, number> {
  try {
    const raw = localStorage.getItem(TABS_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, number>;
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

function writeTabs(tabs: Record<string, number>) {
  try {
    localStorage.setItem(TABS_KEY, JSON.stringify(tabs));
  } catch {
    /* ignore quota / private mode */
  }
}

function prune(tabs: Record<string, number>, now = Date.now()): Record<string, number> {
  const next: Record<string, number> = {};
  for (const [id, ts] of Object.entries(tabs)) {
    if (typeof ts === 'number' && now - ts < STALE_MS) next[id] = ts;
  }
  return next;
}

/** True when every tab was closed (not a same-tab refresh). */
export function shouldClearSessionOnLoad(thisTabId: string): boolean {
  try {
    const tabs = prune(readTabs());
    const others = Object.keys(tabs).filter((id) => id !== thisTabId);
    if (others.length > 0) return false;

    const lastClose = Number(localStorage.getItem(LAST_CLOSE_KEY) || 0);
    if (!lastClose) return false;
    return Date.now() - lastClose > REFRESH_GRACE_MS;
  } catch {
    return false;
  }
}

/** Remove Supabase auth keys from localStorage (sync — safe on unload). */
export function clearSupabaseAuthStorage() {
  try {
    const toRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k) continue;
      if (
        (k.startsWith('sb-') && k.includes('auth-token')) ||
        k.startsWith('supabase.auth') ||
        k === 'supabase.auth.token'
      ) {
        toRemove.push(k);
      }
    }
    toRemove.forEach((k) => localStorage.removeItem(k));
  } catch {
    /* ignore */
  }
}

/**
 * Registers this tab, heartbeats while open, and clears auth when the last tab closes.
 * Returns a cleanup function.
 */
export function startTabSession(opts?: {
  onLastTabClose?: TabSessionClearFn;
}): { tabId: string; stop: () => void } {
  const tabId =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `t-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

  const beat = () => {
    const tabs = prune(readTabs());
    tabs[tabId] = Date.now();
    writeTabs(tabs);
  };

  const markLastCloseIfAlone = () => {
    const tabs = prune(readTabs());
    delete tabs[tabId];
    writeTabs(tabs);
    if (Object.keys(tabs).length === 0) {
      try {
        localStorage.setItem(LAST_CLOSE_KEY, String(Date.now()));
      } catch {
        /* ignore */
      }
      clearSupabaseAuthStorage();
      try {
        void opts?.onLastTabClose?.();
      } catch {
        /* ignore */
      }
    }
  };

  beat();
  const interval = window.setInterval(beat, HEARTBEAT_MS);

  const onHide = () => {
    markLastCloseIfAlone();
  };

  window.addEventListener('pagehide', onHide);
  window.addEventListener('beforeunload', onHide);

  const onShow = () => {
    if (document.visibilityState === 'visible') beat();
  };
  document.addEventListener('visibilitychange', onShow);

  const stop = () => {
    window.clearInterval(interval);
    window.removeEventListener('pagehide', onHide);
    window.removeEventListener('beforeunload', onHide);
    document.removeEventListener('visibilitychange', onShow);
  };

  return { tabId, stop };
}
