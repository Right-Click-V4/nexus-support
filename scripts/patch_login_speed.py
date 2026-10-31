#!/usr/bin/env python3
"""Speed up Customer + Agent login (shorter ceremony, timeouts on admin/role checks)."""
from pathlib import Path
import re

pl = Path("src/components/PostLoginLoader.tsx")
if pl.exists():
    t = pl.read_text()
    if "login-speed-v1" not in t:
        t = t.replace("const MIN_MS = 3200;", "const MIN_MS = 900;")
        t = t.replace("const FADE_MS = 900;", "const FADE_MS = 400;")
        t = t.replace(
            """      window.setTimeout(() => setStepIdx(1), 750),
      window.setTimeout(() => setStepIdx(2), 1600),
      window.setTimeout(() => setStepIdx(3), 2500),
      window.setTimeout(() => clearJustLoggedIn(), 3600),""",
            """      window.setTimeout(() => setStepIdx(1), 200),
      window.setTimeout(() => setStepIdx(2), 450),
      window.setTimeout(() => setStepIdx(3), 700),
      window.setTimeout(() => clearJustLoggedIn(), 1200),""",
        )
        t = "/* login-speed-v1 */\n" + t
        pl.write_text(t)
        print("PostLoginLoader")

ua = Path("src/components/useIsAdmin.ts")
if ua.exists() and "admin-ready-timeout-v1" not in ua.read_text():
    ua.write_text(
        """/* admin-ready-timeout-v1 */
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';

export function useIsAdmin() {
  const { user, loading } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!user || !supabase) {
      setIsAdmin(false);
      setReady(true);
      return;
    }
    const metaRole = String(user.user_metadata?.role || '');
    if (metaRole === 'admin') {
      setIsAdmin(true);
      setReady(true);
      return;
    }
    let cancelled = false;
    const failOpen = window.setTimeout(() => {
      if (!cancelled) {
        setIsAdmin(false);
        setReady(true);
      }
    }, 2500);
    (async () => {
      try {
        const { data } = await supabase
          .from('agents')
          .select('is_admin')
          .eq('user_id', user.id)
          .maybeSingle();
        let row = data;
        if (!row && user.email) {
          const { data: byEmail } = await supabase
            .from('agents')
            .select('is_admin')
            .eq('email', user.email)
            .maybeSingle();
          row = byEmail;
        }
        if (!cancelled) {
          setIsAdmin(!!row?.is_admin);
          setReady(true);
        }
      } catch {
        if (!cancelled) {
          setIsAdmin(false);
          setReady(true);
        }
      } finally {
        window.clearTimeout(failOpen);
      }
    })();
    return () => {
      cancelled = true;
      window.clearTimeout(failOpen);
    };
  }, [user, loading]);

  return { isAdmin, adminReady: ready && !loading };
}
"""
    )
    print("useIsAdmin")

ac = Path("src/context/AuthContext.tsx")
if ac.exists():
    t = ac.read_text()
    if "login-speed-auth-v1" not in t:
        t = t.replace(
            "withTimeout(supabase.auth.getSession(), 4000)",
            "withTimeout(supabase.auth.getSession(), 2500)",
        )
        t = t.replace(
            "window.setTimeout(() => {\n      if (!cancelled) setLoading(false);\n    }, 6000);",
            "window.setTimeout(() => {\n      if (!cancelled) setLoading(false);\n    }, 4000);",
        )
        t = t.replace(
            """      const role = await resolveRole(data.user, expectedRole);
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
      setSession(data.session);""",
            """      let role = roleFromMetadata(data.user);
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

      setAccountRole(role);
      setUser(data.user);
      setSession(data.session);""",
            1,
        )
        t = "/* login-speed-auth-v1 */\n" + t
        ac.write_text(t)
        print("AuthContext")

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    t = tc.read_text()
    if "login-speed-tickets-v1" not in t:
        t = t.replace(
            "withTimeout(supabase.from('tickets').select('*').order('created_at', { ascending: false }), 10000)",
            "withTimeout(supabase.from('tickets').select('*').order('created_at', { ascending: false }), 5000)",
            1,
        )
        t = t.replace(
            "withTimeout(supabase.from('agents').select('*'), 10000)",
            "withTimeout(supabase.from('agents').select('*'), 4000)",
            1,
        )
        t = t.replace(
            "withTimeout(supabase.from('customers').select('*'), 10000)",
            "withTimeout(supabase.from('customers').select('*'), 4000)",
            1,
        )
        t = "/* login-speed-tickets-v1 */\n" + t
        tc.write_text(t)
        print("TicketContext")
print("done")
