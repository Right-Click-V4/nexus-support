/** Lightweight in-memory + sessionStorage cache to cut Supabase egress on reloads. */
type Entry<T> = { data: T; at: number };

const mem = new Map<string, Entry<unknown>>();

const DEFAULT_TTL_MS = 45_000;

export function getCached<T>(key: string, ttlMs = DEFAULT_TTL_MS): T | null {
  const now = Date.now();
  const hit = mem.get(key) as Entry<T> | undefined;
  if (hit && now - hit.at < ttlMs) return hit.data;
  try {
    const raw = sessionStorage.getItem(`nexus-cache:${key}`);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Entry<T>;
    if (now - parsed.at < ttlMs) {
      mem.set(key, parsed);
      return parsed.data;
    }
  } catch {
    /* ignore */
  }
  return null;
}

export function setCached<T>(key: string, data: T) {
  const entry: Entry<T> = { data, at: Date.now() };
  mem.set(key, entry);
  try {
    sessionStorage.setItem(`nexus-cache:${key}`, JSON.stringify(entry));
  } catch {
    /* quota / private mode */
  }
}

export function invalidateCache(prefix?: string) {
  if (!prefix) {
    mem.clear();
    try {
      const keys: string[] = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const k = sessionStorage.key(i);
        if (k?.startsWith('nexus-cache:')) keys.push(k);
      }
      keys.forEach((k) => sessionStorage.removeItem(k));
    } catch {
      /* ignore */
    }
    return;
  }
  for (const k of [...mem.keys()]) {
    if (k.startsWith(prefix)) mem.delete(k);
  }
  try {
    const keys: string[] = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const k = sessionStorage.key(i);
      if (k?.startsWith(`nexus-cache:${prefix}`)) keys.push(k);
    }
    keys.forEach((k) => sessionStorage.removeItem(k));
  } catch {
    /* ignore */
  }
}

export async function cachedQuery<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlMs = DEFAULT_TTL_MS,
): Promise<T> {
  const hit = getCached<T>(key, ttlMs);
  if (hit !== null) return hit;
  const data = await fetcher();
  setCached(key, data);
  return data;
}
