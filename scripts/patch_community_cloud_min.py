#!/usr/bin/env python3
"""Minimal Supabase community wiring."""
from pathlib import Path
import re

p = Path("src/components/PortalCommunityChat.tsx")
t = p.read_text()
if "communityApi" in t:
    print("already")
    raise SystemExit(0)

t = t.replace(
    "} from 'lucide-react';",
    """} from 'lucide-react';
import {
  DEFAULT_GROUP_ID as CLOUD_DEFAULT_ID,
  loadLocalStore, saveLocalStore, ensureMember as ensureMemberCloudLocal,
  communityCloudEnabled, fetchCloudStore, ensureDefaultGroupCloud,
  upsertMemberCloud, insertMessageCloud, setPinnedCloud, createGroupCloud,
  renameGroupCloud, removeMemberCloud, subscribeCommunity, subscribeTyping,
  type Message as CloudMessage, type Store as CloudStore,
} from '../lib/communityApi';""",
    1,
)

if "ensureDefaultGroupCloud" not in t:
    needle = "  const bottomRef = useRef<HTMLDivElement>(null);"
    m = re.search(r"  const bottomRef = useRef<[^>]+>\(null\);", t)
    if m:
        needle = m.group(0)
    insert = needle + """

  // Supabase realtime bootstrap
  useEffect(() => {
    let unsub = () => {};
    const pull = async () => {
      if (!communityCloudEnabled()) return;
      await ensureDefaultGroupCloud();
      const cloud = await fetchCloudStore();
      if (cloud?.groups?.length) {
        setStore(cloud as any);
        saveLocalStore(cloud as any);
      }
    };
    void pull();
    if (communityCloudEnabled()) {
      unsub = subscribeCommunity(() => { void pull(); });
    }
    const tick = window.setInterval(() => { void pull(); }, 5000);
    return () => { unsub(); window.clearInterval(tick); };
  }, []);
"""
    if needle in t:
        t = t.replace(needle, insert, 1)
        print("bootstrap ok")
    else:
        print("bootstrap miss")

if "upsertMemberCloud(" not in t:
    t2, n = re.subn(
        r"(saveStore\(next\);\s*return next;\s*\}\);)\s*\}, \[email, displayName, activeId\]\);",
        r"""\1
    void upsertMemberCloud(activeId, displayName, email);
    if (activeId !== DEFAULT_GROUP_ID) void upsertMemberCloud(DEFAULT_GROUP_ID, displayName, email);
  }, [email, displayName, activeId]);""",
        t,
        count=1,
    )
    if n:
        t = t2
        print("join ok")
    else:
        print("join miss")

if t.count("insertMessageCloud") < 1:
    t2, n = re.subn(
        r"(messages: \[\.\.\.g\.messages, msg\],\s*\}\)\);\s*setDraft\(''\);)",
        r"""\1
    void insertMessageCloud(active.id, msg as any);
    void upsertMemberCloud(active.id, displayName, email);""",
        t,
        count=1,
    )
    if n:
        t = t2
        print("send ok")
    else:
        t2, n = re.subn(
            r"(setDraft\(''\);\n  \};)",
            r"""void insertMessageCloud(active.id, msg as any);
    void upsertMemberCloud(active.id, displayName, email);
    setDraft('');
  };""",
            t,
            count=1,
        )
        if n:
            t = t2
            print("send alt")
        else:
            print("send miss")

# GIF path: after gif updateGroup, push cloud
if "gif_url: g.url" in t and t.count("insertMessageCloud") < 2:
    t = t.replace(
        "setGifOpen(false);",
        "void insertMessageCloud(active.id, msg as any); void upsertMemberCloud(active.id, displayName, email); setGifOpen(false);",
        1,
    )
    print("gif cloud")

# Photo path
if "image_data: String(reader.result" in t and t.count("insertMessageCloud") < 3:
    t = t.replace(
        "setDraft('');",
        "void insertMessageCloud(active.id, msg as any); void upsertMemberCloud(active.id, displayName, email); setDraft('');",
        1,
    )
    print("image cloud")

p.write_text(t)
print("done", "communityApi" in t, "upsertMemberCloud" in t, "insertMessageCloud" in t)
