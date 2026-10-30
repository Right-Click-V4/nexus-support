/* session-refresh-keep-v1 */
/* tab-session-closed-flag-v1 */
/* tab-session-idle-v2 */
/**
 * Auth session lifetime:
 * - Stay logged in across tabs while ANY tab is open (heartbeats).
 * - Stay logged in on refresh / hard-refresh (sessionStorage + recent heartbeat).
 * - Log out when opening the site after all tabs/windows were closed long enough
 *   that heartbeats stopped (covers Chrome "Continue where you left off").
 *
 * Never clear auth tokens on pagehide — refresh also fires pagehide.
 */

const BC_NAME = 'nexus-auth-tabs-v3';
const LIVE_KEY = 'nexus-auth-live-v3';
const CLOSED_KEY = 'nexus-auth-closed-v1';
const TABS_KEY = 'nexus-live-tabs-v3';
const LAST_BEAT_KEY = 'nexus-auth-last-beat-v1';
const HEARTBEAT_MS = 2500;
const STALE_MS = 4_000;
const SIBLING_WAIT_MS = 280;
/** If no tab heartbeat for this long, treat next load as a new browser session. */
const IDLE_MS = 5 * 60 * 1000; // 5 minutes

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

function touchBeat(now = Date.now()) {
  try {
    localStorage.setItem(LAST_BEAT_KEY, String(now));
  } catch {
    /* ignore */
  }
}

function lastBeatAge(now = Date.now()): number {
  try {
    const raw = localStorage.getItem(LAST_BEAT_KEY);
    if (!raw) return Number.POSITIVE_INFINITY;
    const ts = Number(raw);
    if (!Number.isFinite(ts) || ts <= 0) return Number.POSITIVE_INFINITY;
    return Math.max(0, now - ts);
  } catch {
    return Number.POSITIVE_INFINITY;
  }
}

/** Strip Supabase auth keys from localStorage (call only on confirmed new browser session). */
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
 * True when this load is a brand-new browser session → require login.
 */
export function detectNewBrowserSession(): Promise<boolean> {
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
  }

  // Ask open siblings via BroadcastChannel
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
  try {
    localStorage.removeItem(CLOSED_KEY);
  } catch {
    /* ignore */
  }
  touchBeat();
}

/**
 * Heartbeats + answers sibling pings.
 * Does NOT clear auth on unload (that broke hard-refresh).
 */
export function startTabSession(_opts?: {
  onLastTabClose?: TabSessionClearFn;
}): { tabId: string; stop: () => void } {
  const tabId =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `t-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

  markTabSessionLive();

  const beat = () => {
    const now = Date.now();
    touchBeat(now);
    try {
      const tabs = prune(readTabs(), now);
      tabs[tabId] = now;
      writeTabs(tabs);
    } catch {
      /* ignore */
    }
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

  const onPageHide = () => {
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
        // Do NOT age LAST_BEAT here — pagehide also runs on hard refresh.
        // Idle logout uses wall-clock last_beat age; overnight close naturally ages it.
      }
    } catch {
      /* ignore */
    }
  };

  window.addEventListener('pagehide', onPageHide);

  const onVis = () => {
    if (document.visibilityState === 'visible') {
      markTabSessionLive();
      beat();
    }
  };
  document.addEventListener('visibilitychange', onVis);

  const stop = () => {
    window.clearInterval(interval);
    window.removeEventListener('pagehide', onPageHide);
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
