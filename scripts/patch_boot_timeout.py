#!/usr/bin/env python3
"""Prevent infinite Loading: timeouts on auth boot + maintenance/site404 ready."""
from pathlib import Path

mc = Path("src/context/MaintenanceContext.tsx")
if mc.exists():
    t = mc.read_text()
    if "boot-timeout-v1" not in t:
        t = t.replace(
            """    fetchMaintenance()
      .then(apply)
      .finally(() => {
        if (!cancelled) setReady(true);
      });""",
            """    const readyTimer = window.setTimeout(() => {
      if (!cancelled) setReady(true);
    }, 2500);
    fetchMaintenance()
      .then(apply)
      .finally(() => {
        window.clearTimeout(readyTimer);
        if (!cancelled) setReady(true);
      });""",
        )
        t = "/* boot-timeout-v1 */\n" + t
        mc.write_text(t)
        print("maintenance")
    else:
        print("maintenance already")

s404 = Path("src/context/Site404Context.tsx")
if s404.exists():
    t = s404.read_text()
    if "boot-timeout-v1" not in t:
        t = t.replace(
            """    fetchSite404()
      .then(apply)
      .finally(() => {
        if (!cancelled) setReady(true);
      });""",
            """    const readyTimer = window.setTimeout(() => {
      if (!cancelled) setReady(true);
    }, 2500);
    fetchSite404()
      .then(apply)
      .finally(() => {
        window.clearTimeout(readyTimer);
        if (!cancelled) setReady(true);
      });""",
        )
        t = "/* boot-timeout-v1 */\n" + t
        s404.write_text(t)
        print("site404")
    else:
        print("site404 already")

ac = Path("src/context/AuthContext.tsx")
if ac.exists():
    a = ac.read_text()
    if "auth-boot-timeout-v1" not in a:
        if "forceAgentOffline" in a and "withTimeout" not in a:
            a = a.replace(
                """    const forceAgentOffline = async () => {
      try {
        const id = localStorage.getItem('nexus-presence-agent-id');
        if (!id || !supabase) return;
        await supabase.from('agents').update({ status: 'offline', last_seen_at: null }).eq('id', id);
        localStorage.removeItem('nexus-presence-agent-id');
      } catch { /* ignore */ }
    };""",
                """    const withTimeout = <T,>(p: Promise<T>, ms: number): Promise<T | null> =>
      Promise.race([
        p.then((v) => v as T | null).catch(() => null),
        new Promise<null>((resolve) => window.setTimeout(() => resolve(null), ms)),
      ]);

    const forceAgentOffline = async () => {
      try {
        const id = localStorage.getItem('nexus-presence-agent-id');
        if (!id || !supabase) return;
        await withTimeout(
          supabase.from('agents').update({ status: 'offline', last_seen_at: null }).eq('id', id).then(() => null),
          2000,
        );
        localStorage.removeItem('nexus-presence-agent-id');
      } catch { /* ignore */ }
    };""",
            )
            print("auth timeout helper")

        old_boot = """    const boot = async () => {
      const isNewSession = await detectNewBrowserSession();
      if (isNewSession) {
        suppressAuthEvents = true;
        await forceAgentOffline();
        clearSupabaseAuthStorage();
        try {
          await supabase.auth.signOut({ scope: 'local' });
        } catch {
          /* ignore */
        }
        clearSupabaseAuthStorage();
        if (!cancelled) {
          setSession(null);
          setUser(null);
          setLoading(false);
        }
        tabCtl = startTabSession();
        window.setTimeout(() => {
          suppressAuthEvents = false;
        }, 1500);
        return;
      }
      tabCtl = startTabSession();
      markTabSessionLive();
      const { data } = await supabase.auth.getSession();
      await applySession(data.session);
    };
    void boot();"""
        new_boot = """    const boot = async () => {
      try {
        const isNewSession = await detectNewBrowserSession();
        if (isNewSession) {
          suppressAuthEvents = true;
          await forceAgentOffline();
          clearSupabaseAuthStorage();
          try {
            await withTimeout(supabase.auth.signOut({ scope: 'local' }), 2000);
          } catch {
            /* ignore */
          }
          clearSupabaseAuthStorage();
          if (!cancelled) {
            setSession(null);
            setUser(null);
            setLoading(false);
          }
          tabCtl = startTabSession();
          window.setTimeout(() => {
            suppressAuthEvents = false;
          }, 1500);
          return;
        }
        tabCtl = startTabSession();
        markTabSessionLive();
        let sess = null;
        try {
          const result = await withTimeout(supabase.auth.getSession(), 4000);
          if (result && typeof result === 'object' && result !== null && 'data' in result) {
            sess = (result as { data: { session: typeof session } }).data?.session ?? null;
          }
        } catch { /* ignore */ }
        await applySession(sess);
      } catch {
        if (!cancelled) {
          setSession(null);
          setUser(null);
          setLoading(false);
        }
        if (!tabCtl) tabCtl = startTabSession();
      }
    };
    void boot();
    window.setTimeout(() => {
      if (!cancelled) setLoading(false);
    }, 6000);"""
        if old_boot in a:
            a = a.replace(old_boot, new_boot, 1)
            print("auth boot")
        else:
            print("auth boot miss")
            if "Hard stop: never leave" not in a and "void boot();" in a and "setLoading(false);\n    }, 6000)" not in a:
                a = a.replace(
                    "void boot();",
                    """void boot();
    window.setTimeout(() => {
      if (!cancelled) setLoading(false);
    }, 6000);""",
                    1,
                )
                print("auth hard timeout only")

        a = "/* auth-boot-timeout-v1 */\n" + a
        ac.write_text(a)
    else:
        print("auth already")
print("done")
