import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { fetchSite404, readSite404Cache, saveSite404, writeSite404Cache } from '../lib/site404';

type Site404Value = {
  enabled: boolean;
  ready: boolean;
  saving: boolean;
  error: string | null;
  setEnabled: (on: boolean) => Promise<void>;
};

const Site404Context = createContext<Site404Value | null>(null);
const LOCAL_KEY = 'nexus-site-404-on';

export function Site404Provider({ children }: { children: ReactNode }) {
  const [enabled, setEnabledState] = useState(readSite404Cache);
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const apply = (on: boolean) => {
      if (cancelled) return;
      setEnabledState(on);
      writeSite404Cache(on);
    };

    fetchSite404()
      .then(apply)
      .finally(() => {
        if (!cancelled) setReady(true);
      });

    const onStorage = (e: StorageEvent) => {
      if (e.key === LOCAL_KEY && e.newValue != null) apply(e.newValue === '1');
    };
    window.addEventListener('storage', onStorage);

    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    if (isSupabaseConfigured && supabase) {
      channel = supabase
        .channel('nexus-site-404')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'forms' }, () => {
          void fetchSite404().then(apply);
        })
        .subscribe();
    }

    const poll = window.setInterval(() => {
      void fetchSite404().then(apply);
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
    writeSite404Cache(on);
    try {
      await saveSite404(on);
    } catch (err) {
      setEnabledState(!on);
      writeSite404Cache(!on);
      setError(err instanceof Error ? err.message : 'Could not update 404 mode');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Site404Context.Provider value={{ enabled, ready, saving, error, setEnabled }}>
      {children}
    </Site404Context.Provider>
  );
}

export function useSite404() {
  const ctx = useContext(Site404Context);
  if (!ctx) throw new Error('useSite404 must be used within Site404Provider');
  return ctx;
}
