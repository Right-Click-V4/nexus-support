import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const rawUrl = (import.meta.env.VITE_SUPABASE_URL as string | undefined)?.trim();
const rawKey = (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined)?.trim();

/** True when env looks like a real Supabase project URL (not a placeholder or bare project ref). */
function isValidSupabaseUrl(url: string | undefined): boolean {
  if (!url) return false;
  if (url.includes('YOUR_') || url.includes('YOUR_PROJECT')) return false;
  try {
    const u = new URL(url);
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return false;
    const host = u.hostname.toLowerCase();
    if (host === 'localhost' || host === '127.0.0.1') return true;
    return host.endsWith('.supabase.co') && host.split('.').length >= 3;
  } catch {
    return false;
  }
}

function isValidAnonKey(key: string | undefined): boolean {
  if (!key) return false;
  if (key.includes('YOUR_') || key === 'YOUR_ANON_KEY') return false;
  return key.length > 20;
}

export const isSupabaseConfigured =
  isValidSupabaseUrl(rawUrl) && isValidAnonKey(rawKey);

/** Human-readable reason when env is present but invalid (for debugging UI). */
export function getSupabaseConfigError(): string | null {
  if (isSupabaseConfigured) return null;
  if (!rawUrl && !rawKey) {
    if (import.meta.env.PROD) {
      return (
        'Supabase is not configured. In GitHub → Settings → Secrets and variables → Actions, ' +
        'add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY, then re-run Deploy to GitHub Pages.'
      );
    }
    return null;
  }
  if (!rawUrl || !isValidSupabaseUrl(rawUrl)) {
    return (
      'Invalid VITE_SUPABASE_URL. Use the full Project URL from Supabase → Project Settings → API ' +
      '(e.g. https://abcdefghijklmnop.supabase.co), not just the project ref.'
    );
  }
  if (!rawKey || !isValidAnonKey(rawKey)) {
    return 'Invalid VITE_SUPABASE_ANON_KEY. Paste the anon public key from Supabase → Project Settings → API.';
  }
  return null;
}

export const supabase: SupabaseClient | null = isSupabaseConfigured
  ? createClient(rawUrl!, rawKey!)
  : null;
