import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured, getSupabaseConfigError } from '../lib/supabase';

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
  if (lower.includes('invalid login credentials')) {
    return new Error('Invalid email or password.');
  }
  if (lower.includes('user already registered')) {
    return new Error('An account with this email already exists. Sign in instead.');
  }
  if (lower.includes('email not confirmed')) {
    return new Error(
      'Email not confirmed. In Supabase → Authentication → Providers → Email, turn OFF "Confirm email", then try again.'
    );
  }
  return err;
}

function roleFromMetadata(user: User | null): AccountRole {
  const r = (user?.user_metadata?.role as string | undefined) || '';
  if (r === 'customer') return 'customer';
  if (r === 'admin') return 'admin';
  if (r === 'agent') return 'agent';
  return 'agent';
}

async function resolveRole(
  user: User,
  preferred?: 'agent' | 'customer'
): Promise<AccountRole> {
  const meta = roleFromMetadata(user);
  if (!supabase) return preferred || meta;

  const loadAgent = async () => {
    try {
      const { data } = await supabase
        .from('agents')
        .select('is_admin, approval_status')
        .eq('user_id', user.id)
        .maybeSingle();
      if (data) return data;
      if (user.email) {
        const { data: byEmail } = await supabase
          .from('agents')
          .select('is_admin, approval_status')
          .eq('email', user.email)
          .maybeSingle();
        return byEmail;
      }
    } catch {
      /* ignore */
    }
    return null;
  };

  const loadCustomer = async () => {
    try {
      const { data } = await supabase
        .from('customers')
        .select('id, status')
        .eq('user_id', user.id)
        .maybeSingle();
      if (data) return data;
      if (user.email) {
        const { data: byEmail } = await supabase
          .from('customers')
          .select('id, status')
          .eq('email', user.email)
          .maybeSingle();
        return byEmail;
      }
    } catch {
      /* ignore */
    }
    return null;
  };

  if (preferred === 'customer') {
    const customer = await loadCustomer();
    if (customer) return 'customer';
    const agent = await loadAgent();
    if (agent) return agent.is_admin ? 'admin' : 'agent';
    return meta === 'customer' ? 'customer' : meta;
  }

  if (preferred === 'agent') {
    const agent = await loadAgent();
    if (agent) return agent.is_admin ? 'admin' : 'agent';
    const customer = await loadCustomer();
    if (customer) return 'customer';
    return meta === 'customer' ? 'customer' : 'agent';
  }

  const agent = await loadAgent();
  if (agent) return agent.is_admin ? 'admin' : 'agent';
  const customer = await loadCustomer();
  if (customer) return 'customer';
  return meta;
}

async function assertApproved(user: User, role: AccountRole): Promise<void> {
  if (!supabase) return;

  if (role === 'customer') {
    try {
      let row: { status?: string | null } | null = null;
      const { data } = await supabase
        .from('customers')
        .select('status')
        .eq('user_id', user.id)
        .maybeSingle();
      row = data;
      if (!row && user.email) {
        const { data: byEmail } = await supabase
          .from('customers')
          .select('status')
          .eq('email', user.email)
          .maybeSingle();
        row = byEmail;
      }
      if (!row) {
        await supabase.auth.signOut();
        throw new Error(
          'Your customer account is pending admin approval. An administrator must approve it under Users → Pending before you can sign in.'
        );
      }
      const status = (row.status || 'approved').toLowerCase();
      if (status === 'approved' || status === '') return;
      if (status === 'rejected') {
        await supabase.auth.signOut();
        throw new Error('Your customer account was rejected. Contact an administrator.');
      }
      if (status === 'pending') {
        await supabase.auth.signOut();
        throw new Error(
          'Your customer account is pending admin approval. An administrator must approve it under Users → Pending before you can sign in.'
        );
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
    return;
  }

  try {
    let row: { approval_status?: string | null; is_admin?: boolean } | null = null;
    const { data } = await supabase
      .from('agents')
      .select('approval_status, is_admin')
      .eq('user_id', user.id)
      .maybeSingle();
    row = data;
    if (!row && user.email) {
      const { data: byEmail } = await supabase
        .from('agents')
        .select('approval_status, is_admin')
        .eq('email', user.email)
        .maybeSingle();
      row = byEmail;
    }
    if (row?.is_admin) return;

    if (!row) {
      await supabase.auth.signOut();
      throw new Error(
        'Your agent account is pending admin approval. An administrator must approve it under Users → Pending before you can sign in.'
      );
    }

    const approval = (row.approval_status || 'approved').toLowerCase();
    if (approval === 'approved' || approval === '') return;
    if (approval === 'rejected') {
      await supabase.auth.signOut();
      throw new Error('Your agent account was rejected. Contact an administrator.');
    }
    if (approval === 'pending') {
      await supabase.auth.signOut();
      throw new Error(
        'Your agent account is pending admin approval. An administrator must approve it under Users → Pending before you can sign in.'
      );
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

    supabase.auth.getSession().then(({ data }) => {
      void applySession(data.session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, next) => {
      void applySession(next);
    });

    return () => {
      cancelled = true;
      subscription.unsubscribe();
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
      setLoading(false);
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

      if (data.user) {
        try {
          if (role === 'agent') {
            await supabase.from('agents').upsert(
              {
                user_id: data.user.id,
                email: email.trim().toLowerCase(),
                name: fullName || email.split('@')[0],
                initials: (fullName || email)
                  .split(/\s+/)
                  .map((p) => p[0])
                  .join('')
                  .slice(0, 2)
                  .toUpperCase(),
                role: 'Agent',
                status: 'offline',
                approval_status: 'pending',
                is_admin: false,
              },
              { onConflict: 'user_id' }
            );
          } else {
            await supabase.from('customers').upsert(
              {
                user_id: data.user.id,
                email: email.trim().toLowerCase(),
                name: fullName || email.split('@')[0],
                status: 'pending',
              },
              { onConflict: 'user_id' }
            );
          }
        } catch {
          /* optional */
        }
      }

      if (data.session) {
        await supabase.auth.signOut();
      }

      throw new Error(
        role === 'agent'
          ? 'Account created. An admin must approve your account under Users → Pending before you can sign in.'
          : 'Account created. Check your email if confirmation is required, then sign in on the Customer tab.'
      );
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
