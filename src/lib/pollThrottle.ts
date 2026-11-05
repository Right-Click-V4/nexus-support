/**
 * Remap known high-frequency setInterval delays so legacy 2s/3s/4s/5s polls
 * stop burning Supabase egress/logs on the Free plan.
 * Import this once from main.tsx before the app mounts.
 */
export function installPollThrottle() {
  if (typeof window === 'undefined') return;
  const w = window as Window & { __nexusPollThrottle?: boolean };
  if (w.__nexusPollThrottle) return;
  w.__nexusPollThrottle = true;

  const original = window.setInterval.bind(window);

  const remap: Record<number, number> = {
    500: 8_000,
    700: 8_000,
    2000: 60_000,
    2500: 120_000,
    3000: 180_000,
    4000: 120_000,
    5000: 60_000,
    8000: 30_000,
    10000: 30_000,
    15000: 45_000,
    30000: 90_000,
  };

  window.setInterval = ((handler: TimerHandler, timeout?: number, ...args: unknown[]) => {
    let ms = typeof timeout === 'number' ? timeout : 0;
    if (remap[ms] != null) ms = remap[ms];
    return original(handler, ms, ...args);
  }) as typeof window.setInterval;
}
