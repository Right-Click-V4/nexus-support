/**
 * Browser-session lifetime for auth:
 * - Stays logged in across tabs while ANY tab of this origin is open.
 * - Logging out when the user closes ALL windows/tabs (new browser session).
 * - Survives refresh of an existing tab (sessionStorage marker).
 *
 * Chrome / Edge / Opera: sessionStorage is wiped when the whole browser session ends.
 * A new tab with no siblings answering BroadcastChannel = new browser session → clear auth.
 */

const BC_NAME = 'nexus-auth-tabs-v2';
const LIVE_KEY = 'nexus-auth-live-v2'; // sessionStorage (per-tab; dies with browser session)
const TABS_KEY = 'nexus-live-tabs-v2';
const HEARTBEAT_MS = 2500;
const STALE_MS = 12_000;
const SIBLING_WAIT_MS = 150;

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
    /* ignore */
  }
}

function prune(tabs: Record<string, number>, now = Date.now()): Record<string, number> {
  const next: Record<string, number> = {};
  for (const [id, ts] of Object.entries(tabs)) {
    if (typeof ts === 'number' && now - ts < STALE_MS) next[id] = ts;
  }
  return next;
}

/** Strip every Supabase auth key from localStorage (sync — safe on unload). */
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
 * Returns true when this load is a brand-new browser session
 * (all previous windows/tabs closed — user must log in again).
 */
export function detectNewBrowserSession(): Promise<boolean> {
  try {
    // Same tab refresh keeps sessionStorage → not a new browser session
    if (sessionStorage.getItem(LIVE_KEY) === '1') {
      return Promise.resolve(false);
    }
  } catch {
    /* private mode */
  }

  // Any other live tab heartbeating?
  try {
    const others = Object.keys(prune(readTabs()));
    if (others.length > 0) {
      return Promise.resolve(false);
    }
  } catch {
    /* ignore */
  }

  // Ask open siblings via BroadcastChannel (Chrome/Edge/Opera)
  return new Promise((resolve) => {
    let settled = false;
    let bc: BroadcastChannel | null = null;

    const finish = (isNew: boolean) => {
      if (settled) return;
      settled = true;
      try {
        bc?.close();
      } catch {
        /* ignore */
      }
      resolve(isNew);
    };

    try {
      bc = new BroadcastChannel(BC_NAME);
      bc.onmessage = (ev) => {
        const data = ev.data;
        if (data === 'pong' || data?.type === 'pong') {
          finish(false);
        }
      };
      bc.postMessage({ type: 'ping' });
    } catch {
      /* BroadcastChannel unavailable */
    }

    window.setTimeout(() => finish(true), SIBLING_WAIT_MS);
  });
}

export function markTabSessionLive() {
  try {
    sessionStorage.setItem(LIVE_KEY, '1');
  } catch {
    /* ignore */
  }
}

/**
 * Heartbeats + answers sibling pings. Clears auth storage when this is the last tab closing.
 */
export function startTabSession(opts?: {
  onLastTabClose?: TabSessionClearFn;
}): { tabId: string; stop: () => void } {
  const tabId =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `t-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

  markTabSessionLive();

  const beat = () => {
    const tabs = prune(readTabs());
    tabs[tabId] = Date.now();
    writeTabs(tabs);
  };

  beat();
  const interval = window.setInterval(beat, HEARTBEAT_MS);

  let bc: BroadcastChannel | null = null;
  try {
    bc = new BroadcastChannel(BC_NAME);
    bc.onmessage = (ev) => {
      const data = ev.data;
      if (data === 'ping' || data?.type === 'ping') {
        try {
          bc?.postMessage({ type: 'pong' });
        } catch {
          /* ignore */
        }
      }
    };
  } catch {
    /* ignore */
  }

  const onLastClose = () => {
    const tabs = prune(readTabs());
    delete tabs[tabId];
    writeTabs(tabs);
    if (Object.keys(tabs).length === 0) {
      clearSupabaseAuthStorage();
      try {
        void opts?.onLastTabClose?.();
      } catch {
        /* ignore */
      }
    }
  };

  window.addEventListener('pagehide', onLastClose);
  window.addEventListener('beforeunload', onLastClose);

  const onVis = () => {
    if (document.visibilityState === 'visible') {
      markTabSessionLive();
      beat();
    }
  };
  document.addEventListener('visibilitychange', onVis);

  const stop = () => {
    window.clearInterval(interval);
    window.removeEventListener('pagehide', onLastClose);
    window.removeEventListener('beforeunload', onLastClose);
    document.removeEventListener('visibilitychange', onVis);
    try {
      bc?.close();
    } catch {
      /* ignore */
    }
  };

  return { tabId, stop };
}

/** @deprecated */
export function shouldClearSessionOnLoad(_thisTabId?: string): boolean {
  try {
    return sessionStorage.getItem(LIVE_KEY) !== '1';
  } catch {
    return true;
  }
}
