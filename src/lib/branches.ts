/** Shared branch list — same source as agent Branches tab (localStorage). */
export const BRANCH_LS_KEY = 'nexus-branches-v1';

export type StoredBranch = {
  id?: string;
  name: string;
  email?: string;
  members?: unknown[];
};

/** Strip trailing " BRANCH" so labels are just the place name (MAASIN, not MAASIN BRANCH). */
export function normalizeBranchName(raw: string | null | undefined): string {
  let n = String(raw || '').trim().toUpperCase();
  if (n.endsWith(' BRANCH')) n = n.slice(0, -7).trim();
  if (n.endsWith('BRANCH') && n.length > 6) n = n.slice(0, -6).trim();
  return n;
}

/** Branch names available on the agent Branches tab (without redundant BRANCH suffix). */
export function loadAvailableBranches(extraNames: string[] = []): string[] {
  const names = new Set<string>();
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(BRANCH_LS_KEY);
      if (raw) {
        const list = JSON.parse(raw) as StoredBranch[];
        if (Array.isArray(list)) {
          for (const b of list) {
            const n = normalizeBranchName(b?.name);
            if (n) names.add(n);
          }
        }
      }
    }
  } catch {
    /* ignore */
  }
  for (const x of extraNames) {
    const n = normalizeBranchName(x);
    if (n) names.add(n);
  }
  if (names.size === 0) {
    for (const n of ['MAASIN', 'KANANGA', 'AVENIDA', 'CIRIAN', 'SOGOD', 'ORMOC', 'ABUCAY', 'CATARMAN']) {
      names.add(n);
    }
  }
  return Array.from(names).sort((a, b) => a.localeCompare(b));
}
