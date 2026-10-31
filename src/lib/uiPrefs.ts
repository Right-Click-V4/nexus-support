/* dark-class-tailwind-v1 */
/* dark-default-v2 */
const DARK_KEY = 'nexus-dark-v1';
const COMPACT_KEY = 'nexus-compact-v1';

export const THEME_EVENT = 'nexus-theme';

/** Dark is the default until the user explicitly chooses light. */
export function getDarkMode(): boolean {
  try {
    const v = localStorage.getItem(DARK_KEY);
    if (v === '0') return false;
    if (v === '1') return true;
    localStorage.setItem(DARK_KEY, '1');
  } catch {}
  return true;
}

export function setDarkMode(on: boolean) {
  try {
    localStorage.setItem(DARK_KEY, on ? '1' : '0');
  } catch {}
  applyUiPrefs();
  try {
    window.dispatchEvent(new Event(THEME_EVENT));
  } catch {}
}

export function getCompactMode(): boolean {
  try {
    return localStorage.getItem(COMPACT_KEY) === '1';
  } catch {
    return false;
  }
}

export function setCompactMode(on: boolean) {
  try {
    localStorage.setItem(COMPACT_KEY, on ? '1' : '0');
  } catch {}
  applyUiPrefs();
}

/** Apply dark + compact classes on documentElement */
export function applyUiPrefs() {
  const root = document.documentElement;
  const dark = getDarkMode();
  root.classList.toggle('nexus-dark', dark);
  root.classList.toggle('nexus-light', !dark);
  root.classList.toggle('dark', dark);
  root.style.colorScheme = dark ? 'dark' : 'light';
  if (getCompactMode()) root.classList.add('nexus-compact');
  else root.classList.remove('nexus-compact');
}
