#!/usr/bin/env python3
"""Ensure release notes survive cloud refresh / realtime / localStorage wipe.

Runs AFTER PlatformContext is restored from a good SHA in deploy.yml.
Merges notes from:
  - in-memory prev state
  - LS.releases
  - nexus-release-notes-by-id-v1 map
  - nexus-last-patch-notes
so empty cloud rows never erase published bullets.
"""
from pathlib import Path

p = Path('src/context/PlatformContext.tsx')
if not p.exists():
    print('no PlatformContext — skip')
    raise SystemExit(0)

s = p.read_text(encoding='utf-8')
if 'NOTES_BACKUP_KEY' in s and 'mergeReleaseNotes' in s:
    print('PlatformContext notes persistence already present')
    raise SystemExit(0)

# --- helpers inserted after save() ---
helpers = r'''
const NOTES_BACKUP_KEY = 'nexus-release-notes-by-id-v1';
const LAST_PATCH_KEY = 'nexus-last-patch-notes';

function readNotesBackup(): Record<string, string> {
  try {
    const raw = localStorage.getItem(NOTES_BACKUP_KEY);
    const obj = raw ? JSON.parse(raw) : {};
    return obj && typeof obj === 'object' ? obj : {};
  } catch {
    return {};
  }
}

function writeNotesBackup(map: Record<string, string>) {
  try {
    localStorage.setItem(NOTES_BACKUP_KEY, JSON.stringify(map));
  } catch { /* ignore */ }
}

function rememberReleaseNotes(r: { id?: string; version?: string; title?: string; notes?: string }) {
  const notes = (r.notes || '').trim();
  if (!notes) return;
  const map = readNotesBackup();
  if (r.id) map[r.id] = notes;
  if (r.version) map[`v:${r.version}`] = notes;
  if (r.version && r.title) map[`vt:${r.version}|${r.title}`] = notes;
  writeNotesBackup(map);
  try {
    localStorage.setItem(
      LAST_PATCH_KEY,
      JSON.stringify({
        id: r.id,
        version: r.version,
        title: r.title,
        notes,
        at: new Date().toISOString(),
      }),
    );
  } catch { /* ignore */ }
}

function notesFromBackup(r: { id?: string; version?: string; title?: string }): string {
  const map = readNotesBackup();
  if (r.id && map[r.id]) return map[r.id];
  if (r.version && r.title && map[`vt:${r.version}|${r.title}`]) return map[`vt:${r.version}|${r.title}`];
  if (r.version && map[`v:${r.version}`]) return map[`v:${r.version}`];
  try {
    const raw = localStorage.getItem(LAST_PATCH_KEY);
    if (raw) {
      const last = JSON.parse(raw) as { version?: string; title?: string; notes?: string };
      if (last?.notes && (!r.version || last.version === r.version)) return last.notes;
    }
  } catch { /* ignore */ }
  return '';
}

function mergeReleaseNotes(cloud: Release[], prev: Release[]): Release[] {
  const byId = new Map(prev.map((x) => [x.id, x]));
  const byVer = new Map(prev.map((x) => [x.version + '|' + (x.title || ''), x]));
  return cloud.map((c) => {
    const local = byId.get(c.id) || byVer.get(c.version + '|' + (c.title || ''));
    const cloudNotes = (c.notes && String(c.notes).trim()) || '';
    if (cloudNotes) {
      rememberReleaseNotes({ ...c, notes: cloudNotes });
      return { ...c, notes: cloudNotes };
    }
    const fromLocal = (local?.notes && String(local.notes).trim()) || '';
    const fromBackup = notesFromBackup(c);
    const notes = fromLocal || fromBackup || '';
    if (notes) rememberReleaseNotes({ ...c, notes });
    return { ...c, notes };
  });
}

'''

# Insert helpers after the first `function save(...`
marker = 'function save(key: string, value: unknown) {\n  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}\n}\n'
if marker in s and 'NOTES_BACKUP_KEY' not in s:
    s = s.replace(marker, marker + '\n' + helpers, 1)
    print('helpers inserted')
else:
    print('helpers insert skipped (marker miss or already present)')

# --- replace full refresh load ---
old_full = 'if (rel.data) setReleases(rel.data as Release[]);'
new_full = '''if (rel.data) {
      const cloud = rel.data as Release[];
      setReleases((prev) => {
        const merged = mergeReleaseNotes(cloud, prev);
        try { save(LS.releases, merged); } catch { /* ignore */ }
        return merged;
      });
    }'''
if old_full in s:
    s = s.replace(old_full, new_full, 1)
    print('refreshPlatform merge patched')
else:
    print('refreshPlatform pattern miss')

# --- replace light refresh load ---
old_light = '''if (rel.data) {
        setReleases(rel.data as Release[]);
        try { save(LS.releases, rel.data); } catch { /* ignore */ }
      }'''
new_light = '''if (rel.data) {
        const cloud = rel.data as Release[];
        setReleases((prev) => {
          const merged = mergeReleaseNotes(cloud, prev);
          try { save(LS.releases, merged); } catch { /* ignore */ }
          return merged;
        });
      }'''
if old_light in s:
    s = s.replace(old_light, new_light, 1)
    print('light refresh merge patched')
else:
    print('light refresh pattern miss')

# --- replace saveRelease ---
old_save = '''  const saveRelease = async (r: { version: string; title: string; notes: string }) => {
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
  };'''

new_save = '''  const saveRelease = async (r: { version: string; title: string; notes: string }) => {
    const notesText = (r.notes || '').trim();
    const optimistic = {
      id: `rel-${Date.now()}`,
      released_at: new Date().toISOString(),
      version: r.version,
      title: r.title,
      notes: notesText,
    };
    rememberReleaseNotes(optimistic);
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
          notes: notesText,
          released_at: optimistic.released_at,
        })
        .select('*')
        .single();
      if (error) throw error;
      const merged = {
        ...(data as Release),
        notes: ((data as any)?.notes && String((data as any).notes).trim()) || notesText,
        title: (data as any)?.title || r.title,
        version: (data as any)?.version || r.version,
      };
      rememberReleaseNotes(merged);
      setReleases((p) => {
        const next = p.map((x) =>
          x.id === optimistic.id || x.id === merged.id ? merged : x,
        );
        const seen = new Set<string>();
        const deduped = next.filter((x) => {
          if (seen.has(x.id)) return false;
          seen.add(x.id);
          return true;
        });
        try { save(LS.releases, deduped); } catch { /* ignore */ }
        return deduped;
      });
      // Do NOT call refreshPlatform() here — it used to wipe notes before the
      // cloud row was readable / before local backup was consulted.
    } catch (err) {
      console.error('saveRelease failed', err);
    }
  };'''

if old_save in s:
    s = s.replace(old_save, new_save, 1)
    print('saveRelease patched')
else:
    print('saveRelease pattern miss')

p.write_text(s, encoding='utf-8')
print('done', p.stat().st_size)
# sanity
text = p.read_text(encoding='utf-8')
for needle in ('NOTES_BACKUP_KEY', 'mergeReleaseNotes', 'rememberReleaseNotes'):
    print(needle, 'OK' if needle in text else 'MISSING')
