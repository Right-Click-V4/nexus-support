import { supabase, isSupabaseConfigured } from './supabase';

export const BRANDING_FORM_NAME = '__nexus_branding__';
const LOCAL_KEY = 'nexus-branding-v1';

export type BrandingSettings = {
  logoUrl: string;
  faviconUrl: string;
  primaryColor: string;
  appName: string;
  maintenanceMessage: string;
};

export const DEFAULT_BRANDING: BrandingSettings = {
  logoUrl: '',
  faviconUrl: '',
  primaryColor: '#8b5cf6',
  appName: 'Nexus Ops',
  maintenanceMessage: "Nexus Ops is under maintenance. We'll be right back!",
};

function normalize(raw: Partial<BrandingSettings> | null | undefined): BrandingSettings {
  return {
    logoUrl: String(raw?.logoUrl || '').trim(),
    faviconUrl: String(raw?.faviconUrl || '').trim(),
    primaryColor: normalizeHex(raw?.primaryColor) || DEFAULT_BRANDING.primaryColor,
    appName: String(raw?.appName || DEFAULT_BRANDING.appName).trim() || DEFAULT_BRANDING.appName,
    maintenanceMessage:
      String(raw?.maintenanceMessage || DEFAULT_BRANDING.maintenanceMessage).trim() ||
      DEFAULT_BRANDING.maintenanceMessage,
  };
}

function normalizeHex(v?: string | null): string {
  if (!v) return '';
  let s = String(v).trim();
  if (!s.startsWith('#')) s = `#${s}`;
  if (/^#[0-9a-fA-F]{3}$/.test(s)) {
    s = `#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}`;
  }
  if (!/^#[0-9a-fA-F]{6}$/.test(s)) return '';
  return s.toLowerCase();
}

export function readBrandingCache(): BrandingSettings {
  try {
    const raw = localStorage.getItem(LOCAL_KEY);
    if (!raw) return { ...DEFAULT_BRANDING };
    return normalize(JSON.parse(raw));
  } catch {
    return { ...DEFAULT_BRANDING };
  }
}

export function writeBrandingCache(b: BrandingSettings) {
  try {
    localStorage.setItem(LOCAL_KEY, JSON.stringify(b));
  } catch {
    /* ignore */
  }
}

export async function fetchBranding(): Promise<BrandingSettings> {
  if (!isSupabaseConfigured || !supabase) return readBrandingCache();
  const { data, error } = await supabase
    .from('forms')
    .select('description')
    .eq('name', BRANDING_FORM_NAME)
    .maybeSingle();
  if (error || !data?.description) return readBrandingCache();
  try {
    const parsed = normalize(JSON.parse(String(data.description)));
    writeBrandingCache(parsed);
    return parsed;
  } catch {
    return readBrandingCache();
  }
}

export async function saveBranding(partial: Partial<BrandingSettings>): Promise<BrandingSettings> {
  const next = normalize({ ...readBrandingCache(), ...partial });
  writeBrandingCache(next);
  if (!isSupabaseConfigured || !supabase) return next;

  const payload = {
    name: BRANDING_FORM_NAME,
    description: JSON.stringify(next),
    active: true,
    fields: [],
  };
  const { data, error } = await supabase
    .from('forms')
    .select('id')
    .eq('name', BRANDING_FORM_NAME)
    .maybeSingle();
  if (error) throw error;
  if (data?.id) {
    const { error: upErr } = await supabase.from('forms').update(payload).eq('id', data.id);
    if (upErr) throw upErr;
  } else {
    const { error: insErr } = await supabase.from('forms').insert(payload);
    if (insErr) throw insErr;
  }
  return next;
}

function shade(hex: string, percent: number): string {
  const n = hex.replace('#', '');
  const num = parseInt(n, 16);
  let r = (num >> 16) & 0xff;
  let g = (num >> 8) & 0xff;
  let b = num & 0xff;
  const t = percent < 0 ? 0 : 255;
  const p = Math.abs(percent) / 100;
  r = Math.round((t - r) * p + r);
  g = Math.round((t - g) * p + g);
  b = Math.round((t - b) * p + b);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

function hexToRgb(hex: string): string {
  const n = parseInt(hex.replace('#', ''), 16);
  return `${(n >> 16) & 0xff} ${(n >> 8) & 0xff} ${n & 0xff}`;
}

/** Apply primary color + favicon + title to the live document. */
export function applyBrandingToDom(b: BrandingSettings) {
  const root = document.documentElement;
  const hex = normalizeHex(b.primaryColor) || DEFAULT_BRANDING.primaryColor;
  const c400 = shade(hex, 18);
  const c500 = hex;
  const c600 = shade(hex, -12);
  const c700 = shade(hex, -22);
  const c800 = shade(hex, -32);

  root.style.setProperty('--brand-400', c400);
  root.style.setProperty('--brand-500', c500);
  root.style.setProperty('--brand-600', c600);
  root.style.setProperty('--brand-700', c700);
  root.style.setProperty('--brand-800', c800);
  root.style.setProperty('--brand-500-rgb', hexToRgb(c500));
  root.setAttribute('data-brand', hex);

  // Tailwind compiles brand-* to fixed hex at build time — override at runtime
  let style = document.getElementById('nexus-brand-runtime') as HTMLStyleElement | null;
  if (!style) {
    style = document.createElement('style');
    style.id = 'nexus-brand-runtime';
    document.head.appendChild(style);
  }
  style.textContent = `
    .bg-brand-400, .hover\\:bg-brand-400:hover { background-color: ${c400} !important; }
    .bg-brand-500, .hover\\:bg-brand-500:hover { background-color: ${c500} !important; }
    .bg-brand-600, .hover\\:bg-brand-600:hover, .hover\\:bg-brand-700:hover { background-color: ${c600} !important; }
    .bg-brand-700 { background-color: ${c700} !important; }
    .bg-brand-600\\/20 { background-color: color-mix(in srgb, ${c600} 20%, transparent) !important; }
    .bg-brand-500\\/20 { background-color: color-mix(in srgb, ${c500} 20%, transparent) !important; }
    .bg-brand-50, .bg-brand-50\\/60 {
      background-color: color-mix(in srgb, ${c500} 18%, transparent) !important;
    }
    .text-brand-400 { color: ${c400} !important; }
    .text-brand-500, .text-brand-600, .hover\\:text-brand-600:hover { color: ${c600} !important; }
    .text-brand-700, .text-brand-800, .text-brand-900 { color: ${c700} !important; }
    .border-brand-100, .border-brand-200 { border-color: color-mix(in srgb, ${c500} 35%, transparent) !important; }
    .border-brand-500, .border-brand-600 { border-color: ${c600} !important; }
    .ring-brand-500\\/30, .focus\\:ring-brand-500\\/30:focus {
      --tw-ring-color: color-mix(in srgb, ${c500} 30%, transparent) !important;
    }
    .from-brand-400 { --tw-gradient-from: ${c400} var(--tw-gradient-from-position) !important; --tw-gradient-to: rgb(255 255 255 / 0) var(--tw-gradient-to-position) !important; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to) !important; }
    .from-brand-500 { --tw-gradient-from: ${c500} var(--tw-gradient-from-position) !important; --tw-gradient-to: rgb(255 255 255 / 0) var(--tw-gradient-to-position) !important; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to) !important; }
    .to-violet-500, .to-violet-600 {
      /* keep secondary gradient stop; primary from-* already set */
    }
    .shadow-brand-900\\/40 { --tw-shadow-color: color-mix(in srgb, ${c800} 40%, transparent) !important; }
  `;

  const fav = b.faviconUrl.trim();
  let link = document.querySelector<HTMLLinkElement>('link[data-nexus-favicon="1"]');
  if (!link) {
    link = document.createElement('link');
    link.rel = 'icon';
    link.setAttribute('data-nexus-favicon', '1');
    document.head.appendChild(link);
  }
  if (fav) {
    link.href = fav;
  } else {
    const base = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL || '/';
    link.href = `${base}favicon.svg`;
  }

  if (b.appName) {
    document.title = b.appName;
  }
}
