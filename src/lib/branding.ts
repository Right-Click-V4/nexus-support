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

/** Apply primary color + favicon to the live document. */
export function applyBrandingToDom(b: BrandingSettings) {
  const root = document.documentElement;
  const hex = normalizeHex(b.primaryColor) || DEFAULT_BRANDING.primaryColor;
  root.style.setProperty('--brand-500', hex);
  root.style.setProperty('--brand-600', shade(hex, -12));
  root.style.setProperty('--brand-700', shade(hex, -22));
  root.style.setProperty('--brand-400', shade(hex, 12));

  // Tailwind brand utilities often use hardcoded colors; also set a data attr for CSS hooks
  root.setAttribute('data-brand', hex);

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
    // restore default public favicon if cleared
    const base = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL || '/';
    link.href = `${base}favicon.svg`;
  }

  if (b.appName) {
    document.title = b.appName;
  }
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
