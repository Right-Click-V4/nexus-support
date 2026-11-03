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

  // Old ms -> new ms (only exact matches used by our app)
  const remap: Record<number, number> = {
    500: 5_000, // localStorage announce pull
    2000: 60_000, // announcements light poll
    2500: 20_000, // community chat
    3000: 45_000, // refreshPlatform
    4000: 30_000, // presence / platform refresh
    5000: 20_000, // live chat beat / presence tick
    8000: 30_000, // tickets silent refresh
  };

  window.setInterval = ((handler: TimerHandler, timeout?: number, ...args: unknown[]) => {
    let ms = typeof timeout === 'number' ? timeout : 0;
    if (remap[ms] != null) ms = remap[ms];
    return original(handler, ms, ...args);
  }) as typeof window.setInterval;
}
