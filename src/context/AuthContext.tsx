/* auth-profile-update-v1 */
/* login-speed-auth-v1 */
/* supabase-paused-hint-v1 */
/* ROLE_RESOLVE_V2 */
/* SYNC_CUSTOMER_BRANCH_V2 */
/* signup-approve-branch-v1 */
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
  signUp: (
    email: string,
    password: string,
    name?: string,
    role?: 'agent' | 'customer',
    branch?: string,
  ) => Promise<void>;
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
  const r = String(meta.role || meta.account_role || '').toLowerCase();
  if (r === 'admin') return 'admin';
  if (r === 'customer') return 'customer';
  if (r === 'agent') return 'agent';
  return 'agent';
}

async function resolveRole(user: User, expectedRole?: 'agent' | 'customer'): Promise<AccountRole> {
  const fromMeta = roleFromMetadata(user);
  const hasExplicitMeta = Boolean(
    (user.user_metadata as Record<string, unknown> | undefined)?.role ||
      (user.user_metadata as Record<string, unknown> | undefined)?.account_role,
  );
  if (!supabase) return fromMeta;

  try {
    const { data: prof } = await supabase
      .from('profiles')
      .select('role, is_admin')
      .eq('id', user.id)
      .maybeSingle();
    if (prof?.is_admin || prof?.role === 'admin') return 'admin';

    try {
      const { data: agentRow } = await supabase
        .from('agents')
        .select('id, role, is_admin')
        .eq('user_id', user.id)
        .maybeSingle();
      if (agentRow) {
        if ((agentRow as { is_admin?: boolean }).is_admin) return 'admin';
        const ar = String((agentRow as { role?: string }).role || 'agent');
        if (ar === 'admin') return 'admin';
        return 'agent';
      }
    } catch {
      /* agents table may not exist */
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
  if (!supabase) return;
  const email = (user.email || '').trim().toLowerCase();
  const kind = role === 'customer' ? 'customer' : 'agent';

  try {
    const { data } = await supabase
      .from('profiles')
      .select('status, approved, role')
      .eq('id', user.id)
      .maybeSingle();
    if (data) {
      if (data.status === 'pending' || data.approved === false) {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account is pending approval. Please wait for an admin.'
            : 'Your agent account is pending approval. Please wait for an admin.',
        );
      }
      if (data.status === 'rejected') {
        throw new Error(
          kind === 'customer'
            ? 'Your customer account was rejected. Contact support.'
            : 'Your agent account was rejected. Contact support.',
        );
      }
    }
  } catch (e) {
    if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
  }

  if (kind === 'agent') {
    try {
      let row: { approval_status?: string | null } | null = null;
      const byId = await supabase
        .from('agents')
        .select('approval_status')
        .eq('user_id', user.id)
        .maybeSingle();
      row = byId.data as typeof row;
      if (!row && email) {
        const byEmail = await supabase
          .from('agents')
          .select('approval_status')
          .eq('email', email)
          .maybeSingle();
        row = byEmail.data as typeof row;
      }
      const st = (row?.approval_status || '').toLowerCase();
      if (st === 'pending') {
        throw new Error('Your agent account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your agent account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
  }

  if (kind === 'customer' && email) {
    try {
      const { data: cust } = await supabase
        .from('customers')
        .select('status')
        .ilike('email', email)
        .maybeSingle();
      const st = String((cust as { status?: string } | null)?.status || '').toLowerCase();
      if (st === 'pending') {
        throw new Error('Your customer account is pending approval. Please wait for an admin.');
      }
      if (st === 'rejected') {
        throw new Error('Your customer account was rejected. Contact support.');
      }
    } catch (e) {
      if (e instanceof Error && /pending|rejected/i.test(e.message)) throw e;
    }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authBusy, setAuthBusy] = useState(false);
  const [accountRole, setAccountRole] = useState<AccountRole>('agent');
  const [error, setError] = useState<string | null>(null);
  const configError = getSupabaseConfigError();

  const clearError = () => setError(null);

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
    expectedRole?: 'agent' | 'customer',
  ) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    setAuthBusy(true);
    setError(null);
    try {
      const { data, error: authErr } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });
      if (authErr) throw friendlyAuthError(authErr);
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
            : 'This account is registered as an agent. Use the Agent tab to sign in.',
        );
      }
      try {
        await Promise.race([
          assertApproved(data.user, role),
          new Promise<void>((_, reject) =>
            window.setTimeout(() => reject(new Error('Approval check timed out')), 3500),
          ),
        ]);
      } catch (e) {
        if (e instanceof Error && /pending|rejected/i.test(e.message)) {
          await supabase.auth.signOut();
          throw e;
        }
        // On timeout, still block if profiles says pending — soft continue otherwise
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
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Sign in failed';
      setError(msg);
      throw e instanceof Error ? e : new Error(msg);
    } finally {
      setAuthBusy(false);
    }
  };

  const signUp = async (
    email: string,
    password: string,
    name?: string,
    role: 'agent' | 'customer' = 'customer',
    branch?: string,
  ) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const emailNorm = email.trim().toLowerCase();
    if (!emailNorm) throw new Error('Email is required.');
    if (!password || password.length < 6) throw new Error('Password must be at least 6 characters.');

    let branchNorm = (branch || '').trim().toUpperCase();
    if (branchNorm.endsWith(' BRANCH')) branchNorm = branchNorm.slice(0, -7).trim();

    setAuthBusy(true);
    setError(null);
    try {
      const dupChecks = await Promise.all([
        supabase.from('profiles').select('id').ilike('email', emailNorm).limit(1).maybeSingle(),
        supabase.from('agents').select('id').ilike('email', emailNorm).limit(1).maybeSingle(),
        supabase.from('customers').select('id').ilike('email', emailNorm).limit(1).maybeSingle(),
      ]);
      if (dupChecks.some((r) => r.data)) {
        throw new Error('An account with this email already exists. Sign in or use a different email.');
      }

      const { data, error: authErr } = await supabase.auth.signUp({
        email: emailNorm,
        password,
        options: {
          data: {
            full_name: name || '',
            role,
            account_role: role,
            branch: branchNorm || null,
          },
        },
      });
      if (authErr) {
        const msg = (authErr.message || '').toLowerCase();
        if (
          msg.includes('already') ||
          msg.includes('registered') ||
          msg.includes('exists') ||
          msg.includes('duplicate')
        ) {
          throw new Error('An account with this email already exists. Sign in or use a different email.');
        }
        throw friendlyAuthError(authErr);
      }
      if (data.user && Array.isArray(data.user.identities) && data.user.identities.length === 0) {
        throw new Error('An account with this email already exists. Sign in or use a different email.');
      }
      if (!data.user) throw new Error('Could not create account. Please try again.');

      const displayName = (name || '').trim() || emailNorm.split('@')[0];

      try {
        await supabase.from('profiles').upsert({
          id: data.user.id,
          role,
          email: emailNorm,
          full_name: displayName,
          status: 'pending',
          approved: false,
          branch: branchNorm || null,
        });
      } catch {
        /* non-fatal */
      }

      if (role === 'agent') {
        try {
          const initials =
            displayName
              .split(/\s+/)
              .filter(Boolean)
              .map((w) => w[0])
              .join('')
              .slice(0, 2)
              .toUpperCase() || 'AG';
          await supabase.from('agents').insert({
            name: displayName,
            email: emailNorm,
            user_id: data.user.id,
            initials,
            role: 'agent',
            status: 'offline',
            approval_status: 'pending',
            is_admin: false,
            branch: branchNorm || null,
          });
        } catch {
          /* column may differ */
        }
      } else {
        try {
          await supabase.from('customers').insert({
            name: displayName,
            email: emailNorm,
            status: 'pending',
            branch: branchNorm || null,
          });
        } catch {
          try {
            await supabase.from('customers').upsert(
              {
                name: displayName,
                email: emailNorm,
                status: 'pending',
                branch: branchNorm || null,
              },
              { onConflict: 'email' },
            );
          } catch {
            /* non-fatal */
          }
        }
      }

      try {
        await supabase.auth.signOut();
      } catch {
        /* ignore */
      }
      setSession(null);
      setUser(null);

      const okMsg =
        role === 'agent'
          ? 'Account created. An admin must approve your agent access before you can sign in.'
          : 'Account created. An admin must approve your customer access before you can sign in.';
      setError(okMsg);
      throw new Error(okMsg);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Sign up failed';
      setError(msg);
      throw e instanceof Error ? e : new Error(msg);
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
    const { error: authErr } = await supabase.auth.resetPasswordForEmail(email.trim());
    if (authErr) throw friendlyAuthError(authErr);
  };

  const updateProfile = async (data: Record<string, unknown>) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload = { ...data };
    if (typeof payload.branch === 'string') {
      let b = payload.branch.trim().toUpperCase();
      if (b.endsWith(' BRANCH')) b = b.slice(0, -7).trim();
      payload.branch = b;
    }
    const { error: authErr } = await supabase.auth.updateUser({ data: payload });
    if (authErr) throw friendlyAuthError(authErr);
    const { data: sess } = await supabase.auth.getSession();
    const nextUser = sess.session?.user ?? null;
    setUser(nextUser);
    setSession(sess.session);
    try {
      const email = (nextUser?.email || '').trim().toLowerCase();
      if (email && payload.branch !== undefined) {
        const name =
          String(payload.full_name || payload.name || nextUser?.user_metadata?.full_name || '').trim() ||
          email.split('@')[0];
        let branchVal = String(payload.branch || '').trim().toUpperCase() || null;
        if (branchVal && branchVal.endsWith(' BRANCH')) {
          branchVal = branchVal.slice(0, -7).trim() || null;
        }
        const row = {
          name,
          email,
          branch: branchVal,
        };
        const { data: existing } = await supabase
          .from('customers')
          .select('id')
          .ilike('email', email)
          .maybeSingle();
        if (existing?.id) {
          const { error: upErr } = await supabase
            .from('customers')
            .update({ name, branch: branchVal })
            .eq('id', existing.id);
          if (upErr) console.warn('customer branch update', upErr.message);
        } else {
          const { error: insErr } = await supabase.from('customers').insert(row);
          if (insErr) {
            const { error: upsErr } = await supabase
              .from('customers')
              .upsert(row, { onConflict: 'email' });
            if (upsErr) console.warn('customer branch insert', insErr.message, upsErr.message);
          }
        }
      }
    } catch (e) {
      console.warn('customer branch sync', e);
    }
  };

  const updatePassword = async (password: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const { error: authErr } = await supabase.auth.updateUser({ password });
    if (authErr) throw friendlyAuthError(authErr);
  };

  const updateEmail = async (email: string) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const { error: authErr } = await supabase.auth.updateUser({ email: email.trim() });
    if (authErr) throw friendlyAuthError(authErr);
  };

  const value = useMemo(
    () => ({
      session,
      user,
      loading: loading || authBusy,
      authBusy,
      accountRole,
      configError,
      error,
      clearError,
      signIn,
      signUp,
      signOut,
      resetPassword,
      updateProfile,
      updatePassword,
      updateEmail,
    }),
    [session, user, loading, authBusy, accountRole, configError, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
