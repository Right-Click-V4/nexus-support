/** Shared sky traffic so the floating hero can notice flybys. */

export type SkyCraft = {
  id: number;
  x: number;
  y: number;
  dir: 'ltr' | 'rtl';
  kind: 'ufo' | 'rocket' | 'satellite';
  label?: string;
} | null;

let current: SkyCraft = null;
const listeners = new Set<(c: SkyCraft) => void>();

export function publishSkyCraft(craft: SkyCraft) {
  current = craft;
  listeners.forEach((fn) => fn(craft));
}

export function subscribeSkyCraft(fn: (c: SkyCraft) => void) {
  listeners.add(fn);
  fn(current);
  return () => {
    listeners.delete(fn);
  };
}

export function getSkyCraft() {
  return current;
}
