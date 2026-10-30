#!/usr/bin/env python3
"""Fix: detect new session BEFORE startTabSession (heartbeat was resetting idle)."""
from pathlib import Path

ac = Path("src/context/AuthContext.tsx")
a = ac.read_text()
if "session-boot-order-v1" in a:
    print("already")
    raise SystemExit(0)

old = """    // Tab session: keep auth across refresh; clear only on new browser session (see boot)
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
  }, []);"""

new = """    // IMPORTANT: detect new session BEFORE startTabSession — starting the tab
    // session touches the heartbeat and would hide an idle logout.
    let tabCtl: { tabId: string; stop: () => void } | null = null;
    let suppressAuthEvents = false;

    const boot = async () => {
      const isNewSession = await detectNewBrowserSession();
      if (isNewSession) {
        suppressAuthEvents = true;
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
    void boot();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, next) => {
      if (suppressAuthEvents) {
        if (next) {
          void supabase.auth.signOut({ scope: 'local' });
          clearSupabaseAuthStorage();
        }
        return;
      }
      void applySession(next);
    });

    return () => {
      cancelled = true;
      subscription.unsubscribe();
      tabCtl?.stop();
    };
  }, []);"""

if old in a:
    a = a.replace(old, new, 1)
    print("boot order fixed")
else:
    print("boot miss")

a = "/* session-boot-order-v1 */\n" + a
ac.write_text(a)
print("done")
