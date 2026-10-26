import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import {
  applyBrandingToDom,
  fetchBranding,
  readBrandingCache,
  saveBranding,
  writeBrandingCache,
  type BrandingSettings,
  DEFAULT_BRANDING,
} from '../lib/branding';

type BrandingValue = {
  branding: BrandingSettings;
  ready: boolean;
  saving: boolean;
  error: string | null;
  updateBranding: (partial: Partial<BrandingSettings>) => Promise<void>;
};

const BrandingContext = createContext<BrandingValue | null>(null);
const LOCAL_KEY = 'nexus-branding-v1';

export function BrandingProvider({ children }: { children: ReactNode }) {
  const [branding, setBranding] = useState<BrandingSettings>(readBrandingCache);
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    applyBrandingToDom(branding);
  }, [branding]);

  useEffect(() => {
    let cancelled = false;

    const apply = (b: BrandingSettings) => {
      if (cancelled) return;
      setBranding(b);
      writeBrandingCache(b);
      applyBrandingToDom(b);
    };

    fetchBranding()
      .then(apply)
      .finally(() => {
        if (!cancelled) setReady(true);
      });

    const onStorage = (e: StorageEvent) => {
      if (e.key === LOCAL_KEY && e.newValue) {
        try {
          apply({ ...DEFAULT_BRANDING, ...JSON.parse(e.newValue) });
        } catch {
          /* ignore */
        }
      }
    };
    window.addEventListener('storage', onStorage);

    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    if (isSupabaseConfigured && supabase) {
      channel = supabase
        .channel('nexus-branding')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'forms' }, () => {
          void fetchBranding().then(apply);
        })
        .subscribe();
    }

    const poll = window.setInterval(() => {
      void fetchBranding().then(apply);
    }, 4000);

    return () => {
      cancelled = true;
      window.removeEventListener('storage', onStorage);
      window.clearInterval(poll);
      if (channel && supabase) void supabase.removeChannel(channel);
    };
  }, []);

  const updateBranding = async (partial: Partial<BrandingSettings>) => {
    setSaving(true);
    setError(null);
    const prev = branding;
    const optimistic = { ...prev, ...partial };
    setBranding(optimistic);
    applyBrandingToDom(optimistic);
    try {
      const saved = await saveBranding(partial);
      setBranding(saved);
      applyBrandingToDom(saved);
    } catch (err) {
      setBranding(prev);
      applyBrandingToDom(prev);
      setError(err instanceof Error ? err.message : 'Could not save branding');
    } finally {
      setSaving(false);
    }
  };

  return (
    <BrandingContext.Provider value={{ branding, ready, saving, error, updateBranding }}>
      {children}
    </BrandingContext.Provider>
  );
}

export function useBranding() {
  const ctx = useContext(BrandingContext);
  if (!ctx) throw new Error('useBranding must be used within BrandingProvider');
  return ctx;
}
