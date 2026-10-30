/* boot-timeout-v1 */
import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { fetchMaintenance, readMaintenanceCache, saveMaintenance, writeMaintenanceCache } from '../lib/maintenance';

type MaintenanceValue = {
  enabled: boolean;
  ready: boolean;
  saving: boolean;
  error: string | null;
  setEnabled: (on: boolean) => Promise<void>;
};

const MaintenanceContext = createContext<MaintenanceValue | null>(null);
const LOCAL_KEY = 'nexus-maintenance-on';

export function MaintenanceProvider({ children }: { children: ReactNode }) {
  const [enabled, setEnabledState] = useState(readMaintenanceCache);
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const apply = (on: boolean) => {
      if (cancelled) return;
      setEnabledState(on);
      writeMaintenanceCache(on);
    };

    const readyTimer = window.setTimeout(() => {
      if (!cancelled) setReady(true);
    }, 2500);
    fetchMaintenance()
      .then(apply)
      .finally(() => {
        window.clearTimeout(readyTimer);
        if (!cancelled) setReady(true);
      });

    const onStorage = (e: StorageEvent) => {
      if (e.key === LOCAL_KEY && e.newValue != null) {
        apply(e.newValue === '1');
      }
    };
    window.addEventListener('storage', onStorage);

    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    if (isSupabaseConfigured && supabase) {
      channel = supabase
        .channel('nexus-maintenance')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'forms' }, () => {
          void fetchMaintenance().then(apply);
        })
        .subscribe();
    }

    const poll = window.setInterval(() => {
      void fetchMaintenance().then(apply);
    }, 2500);

    return () => {
      cancelled = true;
      window.removeEventListener('storage', onStorage);
      window.clearInterval(poll);
      if (channel && supabase) void supabase.removeChannel(channel);
    };
  }, []);

  const setEnabled = async (on: boolean) => {
    setSaving(true);
    setError(null);
    setEnabledState(on);
    writeMaintenanceCache(on);
    try {
      await saveMaintenance(on);
    } catch (err) {
      setEnabledState(!on);
      writeMaintenanceCache(!on);
      setError(err instanceof Error ? err.message : 'Could not update maintenance mode');
    } finally {
      setSaving(false);
    }
  };

  return (
    <MaintenanceContext.Provider value={{ enabled, ready, saving, error, setEnabled }}>
      {children}
    </MaintenanceContext.Provider>
  );
}

export function useMaintenance() {
  const ctx = useContext(MaintenanceContext);
  if (!ctx) throw new Error('useMaintenance must be used within MaintenanceProvider');
  return ctx;
}
