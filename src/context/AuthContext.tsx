/* auth-profile-update-v1 */
/* login-speed-auth-v1 */
/* supabase-paused-hint-v1 */
/* ROLE_RESOLVE_V2 */
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { getSupabaseConfigError, isSupabaseConfigured, supabase } from '../lib/supabase';

export type AccountRole = 'agent' | 'customer' | 'admin';

type AuthContextValue = {
  session: Session | null;
  user: User | null;
  loading: boolean;
  authBusy: boolean;
  accountRole: AccountRole;
  configError: string | null;
  signIn: (email: string, password: string, expectedRole?: 'agent' | 'customer') => Promise<void>;
  signUp: (email: string, password: string, name?: string, role?: 'agent' | 'customer') => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword?: (email: string) => Promise<void>;
  updateProfile?: (data: Record<string, unknown>) => Promise<void>;
  updatePassword?: (password: string) => Promise<void>;
  updateEmail?: (email: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function friendlyAuthError(error: { message?: string; status?: number }): Error {
  const msg = (error.message || '').toLowerCase();
  if (msg.includes('invalid login') || msg.includes('invalid credentials')) {
    return new Error('Incorrect email or password.');
  }
  if (msg.includes('email not confirmed')) {
    return new Error('Please confirm your email before signing in.');
  }
  if (msg.includes('rate limit') || msg.includes('too many')) {
    return new Error('Too many attempts. Please wait a moment and try again.');
  }
  if (msg.includes('paused') || msg.includes('project is paused')) {
    return new Error('The database project is paused. Resume it in the Supabase dashboard, then try again.');
  }
  return new Error(error.message || 'Authentication failed');
}

function roleFromMetadata(user: User): AccountRole {
  const meta = (user.user_metadata || {}) as Record<string, unknown>;
  const r = String(meta.role || meta.account_role || '');
  if (r === 'admin' || r === 'customer' || r === 'agent') return r;
  return 'agent';
}

async function resolveRole(user: User, expectedRole?: 'agent' | 'customer'): Promise<AccountRole> {
  // ROLE_RESOLVE_V2 — agents/admins must not be forced into customer by a stale profiles.role
  const meta = (user.user_metadata || {}) as Record<string, unknown>;
  const hasExplicitMeta = !!(meta.role || meta.account_role);
  const fromMeta = roleFromMetadata(user);
  if (!supabase) {
    if (!hasExplicitMeta && expectedRole) return expectedRole;
    return fromMeta;
  }

  try {
    const { data: prof } = await supabase
      .from('profiles')
      .select('role, is_admin')
      .eq('id', user.id)
      .maybeSingle();
    if (prof?.is_admin || prof?.role === 'admin') return 'admin';

    // Presence in agents table wins over a mistaken profiles.customer flag
    try {
      const { data: agentRow } = await supabase
        .from('agents')
        .select('id, role, is_admin')
        .eq('id', user.id)
        .maybeSingle();
      if (agentRow) {
        if ((agentRow as { is_admin?: boolean }).is_admin) return 'admin';
        const ar = String((agentRow as { role?: string }).role || 'agent');
        if (ar === 'admin') return 'admin';
        return 'agent';
      }
    } catch {
      /* agents table may not exist in all envs */
    }

    try {
      const email = (user.email || '').toLowerCase();
      if (email) {
        const { data: byEmail } = await supabase
          .from('agents')
          .select('id, role, is_admin')
          .eq('email', email)
          .maybeSingle();
        if (byEmail) {
          if ((byEmail as { is_admin?: boolean }).is_admin) return 'admin';
          return 'agent';
        }
      }
    } catch {
      /* ignore */
    }

    if (prof?.role === 'agent' || prof?.role === 'customer') {
      // Only override stale profiles.customer when metadata EXPLICITLY says agent/admin
      if (
        expectedRole === 'agent' &&
        prof.role === 'customer' &&
        hasExplicitMeta &&
        (fromMeta === 'agent' || fromMeta === 'admin')
      ) {
        return fromMeta === 'admin' ? 'admin' : 'agent';
      }
      return prof.role as AccountRole;
    }
  } catch {
    /* fall through */
  }

  if (!hasExplicitMeta && expectedRole) return expectedRole;
  return fromMeta;
}

async function assertApproved(user: User, role: AccountRole): Promise<void> {
  if (!supabase || role === 'customer') return return;
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

  const withTimeout = <T,>(p: Promise<T>, ms: number): Promise<T | null> =>
    Promise.race([
      p.then((v) => v as T | null),
      new Promise<null>((r) => window.setTimeout(() => r(null), ms)),
    ]);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }
    let alive = true;
    (async () => {
      try {
        const { data } = await supabase.auth.getSession();
        if (!alive) return;
        setSession(data.session);
        setUser(data.session?.user ?? null);
        if (data.session?.user) {
          const role = await withTimeout(resolveRole(data.session.user), 2500);
          if (alive && role) setAccountRole(role);
        }
      } finally {
        if (alive) setLoading(false);
      }
    })();
    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next);
      setUser(next?.user ?? null);
      if (next?.user) {
        void resolveRole(next.user).then((role) => setAccountRole(role));
      } else {
        setAccountRole('agent');
      }
    });
    return () => {
      alive = false;
      sub.subscription.unsubscribe();
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
      let role = roleFromMetadata(data.user);
      try {
        const refined = await Promise.race([
          resolveRole(data.user, expectedRole),
          new Promise<typeof role>((r) => window.setTimeout(() => r(role), 2000)),
        ]);
        role = refined;
      } catch {
        /* keep metadata role */
      }
      const normalized = role === 'admin' ? 'agent' : role;
      if (expectedRole && normalized !== expectedRole) {
        await supabase.auth.signOut();
        throw new Error(
          expectedRole === 'agent'
            ? 'This account is registered as a customer. Use the Customer tab to sign in.'
            : 'This account is registered as an agent. Use the Agent tab to sign in.'
        );
      }
      try {
        await Promise.race([
          assertApproved(data.user, role),
          new Promise<void>((r) => window.setTimeout(() => r(), 2000)),
        ]);
      } catch (e) {
        if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
      }
      if (expectedRole === 'customer' && role === 'customer') {
        try {
          const meta = (data.user.user_metadata || {}) as Record<string, unknown>;
          if (!meta.role && !meta.account_role) {
            await supabase.auth.updateUser({ data: { role: 'customer' } });
          }
        } catch {
          /* non-fatal */
        }
      }
      // Heal stale profiles.customer when this is clearly an agent/admin sign-in
      if (expectedRole === 'agent' && (role === 'agent' || role === 'admin')) {
        try {
          await supabase.from('profiles').upsert({
            id: data.user.id,
            role: role === 'admin' ? 'admin' : 'agent',
            email: data.user.email,
          });
        } catch {
          /* non-fatal */
        }
      }
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
    name?: string,
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
            full_name: name || '',
            role,
            account_role: role,
          },
        },
      });
      if (error) throw friendlyAuthError(error);
      if (data.user) {
        try {
          await supabase.from('profiles').upsert({
            id: data.user.id,
            role,
            email: data.user.email,
            full_name: name || '',
            status: role === 'agent' ? 'pending' : 'active',
          });
        } catch {
          /* non-fatal */
        }
      }
      if (role === 'agent') {
        throw new Error('Account created. An admin must approve your agent access before you can sign in.');
      }
    } finally {
      setAuthBusy(false);
    }
  };

  const signOut = async () => {
    if (!supabase) return;
    setAuthBusy(true);
    try {
      await supabase.auth.signOut();
      setSession(null);
      setUser(null);
      setAccountRole('agent');
    } finally {
      setAuthBusy(false);
    }
  };

  const resetPassword = async (email: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const { error } = await supabase.auth.resetPasswordForEmail(email.trim());
    if (error) throw friendlyAuthError(error);
  };

  const updateProfile = async (data: Record<string, unknown>) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const { error } = await supabase.auth.updateUser({ data });
    if (error) throw friendlyAuthError(error);
    const { data: sess } = await supabase.auth.getSession();
    setUser(sess.session?.user ?? null);
    setSession(sess.session);
  };

  const updatePassword = async (password: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const { error } = await supabase.auth.updateUser({ password });
    if (error) throw friendlyAuthError(error);
  };

  const updateEmail = async (email: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const { error } = await supabase.auth.updateUser({ email: email.trim() });
    if (error) throw friendlyAuthError(error);
  };

  const value = useMemo(
    () => ({
      session,
      user,
      loading,
      authBusy,
      accountRole,
      configError,
      signIn,
      signUp,
      signOut,
      resetPassword,
      updateProfile,
      updatePassword,
      updateEmail,
    }),
    [session, user, loading, authBusy, accountRole, configError]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
