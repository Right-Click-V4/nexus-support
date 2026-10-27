import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured, getSupabaseConfigError } from '../lib/supabase';
import {
  startTabSession,
  detectNewBrowserSession,
  markTabSessionLive,
  clearSupabaseAuthStorage,
} from '../lib/tabSession';

export type AccountRole = 'agent' | 'customer' | 'admin';

interface AuthContextValue {
  session: Session | null;
  user: User | null;
  loading: boolean;
  /** True while signIn/signUp is validating — gates must keep the login form mounted */
  authBusy: boolean;
  requiresAuth: boolean;
  configError: string | null;
  accountRole: AccountRole;
  signIn: (email: string, password: string, expectedRole?: 'agent' | 'customer') => Promise<void>;
  signUp: (
    email: string,
    password: string,
    fullName?: string,
    role?: 'agent' | 'customer'
  ) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function friendlyAuthError(err: unknown): Error {
  if (!(err instanceof Error)) return new Error('Authentication failed');
  const msg = err.message || '';
  const lower = msg.toLowerCase();

  if (
    lower.includes('failed to fetch') ||
    lower.includes('networkerror') ||
    lower.includes('load failed') ||
    lower.includes('err_name_not_resolved')
  ) {
    return new Error(
      'Cannot reach Supabase (Failed to fetch). Check that VITE_SUPABASE_URL is the full ' +
        'https://YOUR_PROJECT.supabase.co URL and that the project is not paused. ' +
        'Update GitHub Actions secrets and redeploy if this is the live site.'
    );
  }
  return err;
}

function roleFromMetadata(user: User): AccountRole {
  const meta = (user.user_metadata || {}) as Record<string, unknown>;
  const r = String(meta.role || meta.account_role || '');
  if (r === 'admin' || r === 'customer' || r === 'agent') return r;
  return 'agent';
}

async function resolveRole(user: User, _expectedRole?: 'agent' | 'customer'): Promise<AccountRole> {
  const fromMeta = roleFromMetadata(user);
  if (!supabase) return fromMeta;
  try {
    const { data } = await supabase
      .from('profiles')
      .select('role, is_admin')
      .eq('id', user.id)
      .maybeSingle();
    if (data?.is_admin) return 'admin';
    if (data?.role === 'customer' || data?.role === 'agent' || data?.role === 'admin') {
      return data.role as AccountRole;
    }
  } catch {
    /* fall through */
  }
  return fromMeta;
}

async function assertApproved(user: User, role: AccountRole): Promise<void> {
  if (!supabase || role === 'customer') return;
  try {
    const { data } = await supabase
      .from('profiles')
      .select('status, approved')
      .eq('id', user.id)
      .maybeSingle();
    if (data?.status === 'pending' || data?.approved === false) {
      throw new Error('Your agent account is pending approval. Please wait for an admin.');
    }
    if (data?.status === 'rejected') {
      throw new Error('Your agent account was rejected. Contact support.');
    }
  } catch (e) {
    if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(isSupabaseConfigured);
  const [authBusy, setAuthBusy] = useState(false);
  const [accountRole, setAccountRole] = useState<AccountRole>('agent');
  const configError = getSupabaseConfigError();

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }
    let cancelled = false;

    const applySession = async (next: Session | null) => {
      if (cancelled) return;
      setSession(next);
      setUser(next?.user ?? null);
      if (next?.user) {
        setAccountRole(roleFromMetadata(next.user));
        try {
          const role = await resolveRole(next.user);
          if (!cancelled) setAccountRole(role);
        } catch {
          /* keep metadata */
        }
      } else {
        setAccountRole('agent');
      }
      if (!cancelled) setLoading(false);
    };

    // Tab session: keep auth across refresh; clear only on new browser session (see boot)
    const tabCtl = startTabSession();

    const boot = async () => {
      // New browser window/session (all prior tabs closed) → force login
      const isNewSession = await detectNewBrowserSession();
      if (isNewSession) {
        clearSupabaseAuthStorage();
        try {
          await supabase.auth.signOut({ scope: 'local' });
        } catch {
          /* ignore */
        }
        markTabSessionLive();
        if (!cancelled) {
          setSession(null);
          setUser(null);
          setLoading(false);
        }
        return;
      }
      markTabSessionLive();
      const { data } = await supabase.auth.getSession();
      await applySession(data.session);
    };
    void boot();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, next) => {
      void applySession(next);
    });

    return () => {
      cancelled = true;
      subscription.unsubscribe();
      tabCtl.stop();
    };
  }, []);

  const signIn = async (
    email: string,
    password: string,
    expectedRole?: 'agent' | 'customer'
  ) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');

    setAuthBusy(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });
      if (error) throw friendlyAuthError(error);
      if (!data.user) throw new Error('Authentication failed');

      const role = await resolveRole(data.user, expectedRole);
      const normalized = role === 'admin' ? 'agent' : role;

      if (expectedRole && normalized !== expectedRole) {
        await supabase.auth.signOut();
        throw new Error(
          expectedRole === 'agent'
            ? 'This account is registered as a customer. Use the Customer tab to sign in.'
            : 'This account is registered as an agent. Use the Agent tab to sign in.'
        );
      }

      await assertApproved(data.user, role);

      setAccountRole(role);
      setUser(data.user);
      setSession(data.session);
    } finally {
      setAuthBusy(false);
    }
  };

  const signUp = async (
    email: string,
    password: string,
    fullName?: string,
    role: 'agent' | 'customer' = 'customer'
  ) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    setAuthBusy(true);
    try {
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: {
          data: {
            full_name: fullName || '',
            role,
          },
        },
      });
      if (error) throw friendlyAuthError(error);
      if (data.session) {
        await supabase.auth.signOut();
      }
    } finally {
      setAuthBusy(false);
    }
  };

  const resetPassword = async (email: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const redirectTo =
      typeof window !== 'undefined'
        ? `${window.location.origin}${window.location.pathname}`
        : undefined;
    const { error } = await supabase.auth.resetPasswordForEmail(
      email.trim(),
      redirectTo ? { redirectTo } : undefined
    );
    if (error) throw friendlyAuthError(error);
  };

  const signOut = async () => {
    if (!supabase) return;
    try {
      localStorage.removeItem('nexus-live-tabs-v1');
      localStorage.removeItem('nexus-live-tabs-v2');
      localStorage.removeItem('nexus-live-tabs-v3');
      localStorage.removeItem('nexus-last-tab-close-v1');
      sessionStorage.removeItem('nexus-auth-live-v2');
      sessionStorage.removeItem('nexus-auth-live-v3');
    } catch {
      /* ignore */
    }
    clearSupabaseAuthStorage();
    await supabase.auth.signOut();
  };

  return (
    <AuthContext.Provider
      value={{
        session,
        user,
        loading,
        authBusy,
        requiresAuth: isSupabaseConfigured,
        configError,
        accountRole,
        signIn,
        signUp,
        signOut,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
