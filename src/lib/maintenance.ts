import { supabase, isSupabaseConfigured } from './supabase';

export const MAINTENANCE_FORM_NAME = '__nexus_maintenance__';
const LOCAL_KEY = 'nexus-maintenance-on';

export function readMaintenanceCache(): boolean {
  try {
    return localStorage.getItem(LOCAL_KEY) === '1';
  } catch {
    return false;
  }
}

export function writeMaintenanceCache(on: boolean) {
  try {
    localStorage.setItem(LOCAL_KEY, on ? '1' : '0');
  } catch {
    /* ignore */
  }
}

export async function fetchMaintenance(): Promise<boolean> {
  if (!isSupabaseConfigured || !supabase) return readMaintenanceCache();
  const { data, error } = await supabase
    .from('forms')
    .select('description, active')
    .eq('name', MAINTENANCE_FORM_NAME)
    .maybeSingle();
  if (error || !data) return readMaintenanceCache();
  const on = data.active === true && String(data.description || '').toLowerCase() === 'on';
  writeMaintenanceCache(on);
  return on;
}

export async function saveMaintenance(on: boolean): Promise<void> {
  writeMaintenanceCache(on);
  if (!isSupabaseConfigured || !supabase) return;
  const payload = {
    name: MAINTENANCE_FORM_NAME,
    description: on ? 'on' : 'off',
    active: on,
    fields: [],
  };
  const { data, error } = await supabase
    .from('forms')
    .select('id')
    .eq('name', MAINTENANCE_FORM_NAME)
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
