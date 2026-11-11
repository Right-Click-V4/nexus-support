#!/usr/bin/env python3
"""Ensure saveRelease persists notes to localStorage and survives cloud refresh."""
from pathlib import Path

p = Path('src/context/PlatformContext.tsx')
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
if 'byVer' in s and 'local.notes' in s:
    print('PlatformContext notes persistence already present')
    raise SystemExit(0)

old = """  const saveRelease = async (r: { version: string; title: string; notes: string }) => {
    const optimistic = {
      id: `rel-${Date.now()}`,
      released_at: new Date().toISOString(),
      version: r.version,
      title: r.title,
      notes: r.notes,
    };
    setReleases((p) => [optimistic, ...p]);
    if (!supabase) return;
    try {
      const { data, error } = await supabase
        .from('releases')
        .insert({ version: r.version, title: r.title, notes: r.notes, released_at: optimistic.released_at })
        .select('*')
        .single();
      if (error) throw error;
      if (data?.id) {
        setReleases((p) => p.map((x) => (x.id === optimistic.id ? (data as Release) : x)));
      }
      await refreshPlatform();
    } catch (err) {
      console.error('saveRelease failed', err);
    }
  };"""

new = """  const saveRelease = async (r: { version: string; title: string; notes: string }) => {
    const optimistic = {
      id: `rel-${Date.now()}`,
      released_at: new Date().toISOString(),
      version: r.version,
      title: r.title,
      notes: r.notes || '',
    };
    setReleases((p) => {
      const next = [optimistic, ...p];
      try { save(LS.releases, next); } catch { /* ignore */ }
      return next;
    });
    if (!supabase) return;
    try {
      const { data, error } = await supabase
        .from('releases')
        .insert({
          version: r.version,
          title: r.title,
          notes: r.notes || '',
          released_at: optimistic.released_at,
        })
        .select('*')
        .single();
      if (error) throw error;
      const merged = {
        ...(data as Release),
        notes: (data as any)?.notes || r.notes || '',
        title: (data as any)?.title || r.title,
        version: (data as any)?.version || r.version,
      };
      setReleases((p) => {
        const next = p.map((x) => (x.id === optimistic.id || x.id === merged.id ? merged : x));
        const seen = new Set<string>();
        const deduped = next.filter((x) => {
          if (seen.has(x.id)) return false;
          seen.add(x.id);
          return true;
        });
        try { save(LS.releases, deduped); } catch { /* ignore */ }
        return deduped;
      });
    } catch (err) {
      console.error('saveRelease failed', err);
    }
  };"""

if old in s:
    s = s.replace(old, new, 1)
    print('saveRelease patched')
else:
    print('saveRelease pattern miss')

old_load = 'if (rel.data) setReleases(rel.data as Release[]);'
new_load = """if (rel.data) {
      const cloud = rel.data as Release[];
      setReleases((prev) => {
        const byVer = new Map(prev.map((x) => [x.version + '|' + x.title, x]));
        const merged = cloud.map((c) => {
          const local = byVer.get(c.version + '|' + c.title) || prev.find((p) => p.id === c.id);
          if (local && (!c.notes || !String(c.notes).trim()) && local.notes) {
            return { ...c, notes: local.notes };
          }
          return c;
        });
        try { save(LS.releases, merged); } catch { /* ignore */ }
        return merged;
      });
    }"""
if old_load in s:
    s = s.replace(old_load, new_load)
    print('load merge patched')
else:
    print('load pattern miss or already patched')

p.write_text(s)
print('done', p.stat().st_size)
