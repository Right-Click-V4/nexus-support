/** Shared sky traffic so the floating hero can notice flybys. */
export type SkyCraft = {
  id: number;
  x: number; // stage-relative px
  y: number;
  dir: 'ltr' | 'rtl';
  kind: 'ufo' | 'rocket';
  label?: string;
};

type Listener = (craft: SkyCraft | null) => void;

let current: SkyCraft | null = null;
const listeners = new Set<Listener>();

export function publishSkyCraft(craft: SkyCraft | null) {
  current = craft;
  listeners.forEach((fn) => {
    try {
      fn(craft);
    } catch {
      /* ignore */
    }
  });
}

export function getSkyCraft() {
  return current;
}

export function subscribeSkyCraft(fn: Listener) {
  listeners.add(fn);
  fn(current);
  return () => {
    listeners.delete(fn);
  };
}
