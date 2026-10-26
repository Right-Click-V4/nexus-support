import { supabase, isSupabaseConfigured } from './supabase';

export const SITE404_FORM_NAME = '__nexus_site_404__';
const LOCAL_KEY = 'nexus-site-404-on';

export function readSite404Cache(): boolean {
  try {
    return localStorage.getItem(LOCAL_KEY) === '1';
  } catch {
    return false;
  }
}

export function writeSite404Cache(on: boolean) {
  try {
    localStorage.setItem(LOCAL_KEY, on ? '1' : '0');
  } catch {
    /* ignore */
  }
}

export async function fetchSite404(): Promise<boolean> {
  if (!isSupabaseConfigured || !supabase) return readSite404Cache();
  const { data, error } = await supabase
    .from('forms')
    .select('description, active')
    .eq('name', SITE404_FORM_NAME)
    .maybeSingle();
  if (error || !data) return readSite404Cache();
  const on = data.active === true && String(data.description || '').toLowerCase() === 'on';
  writeSite404Cache(on);
  return on;
}

export async function saveSite404(on: boolean): Promise<void> {
  writeSite404Cache(on);
  if (!isSupabaseConfigured || !supabase) return;
  const payload = {
    name: SITE404_FORM_NAME,
    description: on ? 'on' : 'off',
    active: on,
    fields: [],
  };
  const { data, error } = await supabase
    .from('forms')
    .select('id')
    .eq('name', SITE404_FORM_NAME)
    .maybeSingle();
  if (error) throw error;
  if (data?.id) {
    const { error: upErr } = await supabase.from('forms').update(payload).eq('id', data.id);
    if (upErr) throw upErr;
  } else {
    const { error: insErr } = await supabase.from('forms').insert(payload);
    if (insErr) throw insErr;
  }
}
