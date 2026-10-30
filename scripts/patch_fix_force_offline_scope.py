#!/usr/bin/env python3
"""Fix build: forceAgentOffline must be in AuthProvider scope (not only useEffect)."""
from pathlib import Path

ac = Path("src/context/AuthContext.tsx")
a = ac.read_text()
if "force-offline-scope-v1" in a:
    print("already")
    raise SystemExit(0)

helper = '''
  const withTimeout = <T,>(p: Promise<T>, ms: number): Promise<T | null> =>
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
    } catch {
      /* ignore */
    }
  };
'''

inner = '''    let suppressAuthEvents = false;
    const withTimeout = <T,>(p: Promise<T>, ms: number): Promise<T | null> =>
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
    };

    const boot = async () => {'''

outer_boot = '''    let suppressAuthEvents = false;

    const boot = async () => {'''

if inner in a:
    a = a.replace(inner, outer_boot, 1)
    print("removed inner defs")

anchor = "  const configError = getSupabaseConfigError();\n\n  useEffect(() => {"
if anchor in a and "const forceAgentOffline = async" not in a.split("useEffect(() => {")[0]:
    a = a.replace(
        anchor,
        "  const configError = getSupabaseConfigError();\n" + helper + "\n  useEffect(() => {",
        1,
    )
    print("inserted outer helpers")
elif a.find("const forceAgentOffline") > a.find("const signOut = async") or a.find("const forceAgentOffline") < 0:
    if "const forceAgentOffline = async" not in a.split("const signOut = async")[0]:
        a = a.replace(
            "  const signOut = async () => {",
            helper + "\n  const signOut = async () => {",
            1,
        )
        print("inserted before signOut")

a = a.replace(
    "sess = (result as { data: { session: typeof session } }).data?.session ?? null;",
    "sess = (result as { data: { session: Session | null } }).data?.session ?? null;",
)

a = "/* force-offline-scope-v1 */\n" + a
ac.write_text(a)
print("done")
