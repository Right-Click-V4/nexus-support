import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { fetchMaintenance, readMaintenanceCache, saveMaintenance } from '../lib/maintenance';

type MaintenanceValue = {
  enabled: boolean;
  ready: boolean;
  saving: boolean;
  error: string | null;
  setEnabled: (on: boolean) => Promise<void>;
};

const MaintenanceContext = createContext<MaintenanceValue | null>(null);

export function MaintenanceProvider({ children }: { children: ReactNode }) {
  const [enabled, setEnabledState] = useState(readMaintenanceCache);
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchMaintenance()
      .then((on) => {
        if (!cancelled) setEnabledState(on);
      })
      .finally(() => {
        if (!cancelled) setReady(true);
      });

    if (!isSupabaseConfigured || !supabase) return () => { cancelled = true; };
    const channel = supabase
      .channel('nexus-maintenance')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'forms' }, () => {
        void fetchMaintenance().then((on) => {
          if (!cancelled) setEnabledState(on);
        });
      })
      .subscribe();
    const poll = window.setInterval(() => {
      void fetchMaintenance().then((on) => {
        if (!cancelled) setEnabledState(on);
      });
    }, 8000);
    return () => {
      cancelled = true;
      window.clearInterval(poll);
      void supabase.removeChannel(channel);
    };
  }, []);

  const setEnabled = async (on: boolean) => {
    setSaving(true);
    setError(null);
    setEnabledState(on);
    try {
      await saveMaintenance(on);
    } catch (err) {
      setEnabledState(!on);
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
