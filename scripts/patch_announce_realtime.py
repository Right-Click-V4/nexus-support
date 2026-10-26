#!/usr/bin/env python3
"""Wire Supabase Realtime + 2s poll for announcements so incognito/other browsers sync."""
from pathlib import Path

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
if "nexus-announcements-rt" in t and "refreshAnnouncementsLight" in t:
    print("realtime already present")
    raise SystemExit(0)

marker = "  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);"
if marker not in t:
    marker2 = "useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);"
    if marker2 not in t:
        raise SystemExit("refreshPlatform effect marker not found")
    marker = marker2

block = """  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);

  // Lightweight announcements/releases refresh — works across normal + incognito tabs
  const refreshAnnouncementsLight = useCallback(async () => {
    if (!isSupabaseConfigured || !supabase) return;
    try {
      const [ann, rel] = await Promise.all([
        supabase.from('announcements').select('*').order('created_at', { ascending: false }),
        supabase.from('releases').select('*').order('released_at', { ascending: false }),
      ]);
      if (ann.data) {
        const fromDb = mergeAnnouncementChannels(ann.data as Announcement[]);
        setAnnouncements((prev) => {
          const temps = prev.filter(
            (x) =>
              String(x.id).startsWith('an-') &&
              !fromDb.some((d) => stripAllMeta(d.body) === stripAllMeta(x.body)),
          );
          const merged = [...temps, ...fromDb];
          const seen = new Set<string>();
          const out: Announcement[] = [];
          for (const a of merged) {
            if (seen.has(a.id)) continue;
            seen.add(a.id);
            out.push(a);
          }
          try { save(LS.announce, out); } catch { /* ignore */ }
          return out;
        });
      } else if (!ann.error) {
        setAnnouncements((prev) => {
          const temps = prev.filter((x) => String(x.id).startsWith('an-'));
          try { save(LS.announce, temps); } catch { /* ignore */ }
          return temps;
        });
      }
      if (rel.data) {
        setReleases(rel.data as Release[]);
        try { save(LS.releases, rel.data); } catch { /* ignore */ }
      }
    } catch (err) {
      console.error('refreshAnnouncementsLight', err);
    }
  }, []);

  // Supabase Realtime + 2s poll so every browser context (incl. incognito) stays in sync
  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) return;

    void refreshAnnouncementsLight();

    let channel: ReturnType<NonNullable<typeof supabase>['channel']> | null = null;
    try {
      channel = supabase
        .channel('nexus-announcements-rt')
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'announcements' },
          () => { void refreshAnnouncementsLight(); },
        )
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'releases' },
          () => { void refreshAnnouncementsLight(); },
        )
        .subscribe();
    } catch (err) {
      console.warn('announcements realtime unavailable', err);
    }

    const poll = window.setInterval(() => {
      void refreshAnnouncementsLight();
    }, 2000);

    return () => {
      window.clearInterval(poll);
      try {
        if (channel && supabase) void supabase.removeChannel(channel);
      } catch { /* ignore */ }
    };
  }, [refreshAnnouncementsLight]);
"""

t = t.replace(marker, block, 1)
if "nexus-announcements-rt" not in t:
    raise SystemExit("inject failed")
p.write_text(t)
print("realtime+poll written", len(t))
