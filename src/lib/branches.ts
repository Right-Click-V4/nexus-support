/** Shared branch list — same source as agent Branches tab (localStorage). */
export const BRANCH_LS_KEY = 'nexus-branches-v1';

export type StoredBranch = {
  id?: string;
  name: string;
  email?: string;
  members?: unknown[];
};

/** Branch names available on the agent Branches tab. */
export function loadAvailableBranches(extraNames: string[] = []): string[] {
  const names = new Set<string>();
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(BRANCH_LS_KEY);
      if (raw) {
        const list = JSON.parse(raw) as StoredBranch[];
        if (Array.isArray(list)) {
          for (const b of list) {
            const n = String(b?.name || '').trim().toUpperCase();
            if (n) names.add(n);
          }
        }
      }
    }
  } catch {
    /* ignore */
  }
  for (const x of extraNames) {
    const n = String(x || '').trim().toUpperCase();
    if (n) names.add(n);
  }
  if (names.size === 0) {
    for (const n of [
      'MAASIN BRANCH',
      'KANANGA BRANCH',
      'AVENIDA BRANCH',
      'CIRIAN BRANCH',
      'SOGOD BRANCH',
      'ORMOC BRANCH',
      'ABUCAY BRANCH',
      'CATARMAN BRANCH',
    ]) {
      names.add(n);
    }
  }
  return Array.from(names).sort((a, b) => a.localeCompare(b));
}
