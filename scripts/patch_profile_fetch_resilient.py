#!/usr/bin/env python3
"""Make profile save + updateAgentStatus survive Failed to fetch."""
from pathlib import Path
import re

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    t = tc.read_text()
    if "status-fetch-resilient-v1" not in t:
        old = """    if (supabase) {
      let { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
      if (error) {
        const minimal: Record<string, unknown> = { status };
        if (statusMessage !== undefined) minimal.status_message = statusMessage;
        const retry = await supabase.from('agents').update(minimal).eq('id', currentAgent.id);
        error = retry.error;
      }
      const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
      try {
        localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
      } catch { /* ignore */ }
      if (error) {
        // non-fatal for UI presence
      }
    } else {
      const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
      setCurrentAgent(next);
      setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    }"""
        new = """    const next = { ...currentAgent, status, status_message: msg, status_emoji: emoji, last_seen_at: seen };
    setCurrentAgent(next);
    setAgents((prev) => prev.map((a) => (a.id === currentAgent.id ? next : a)));
    try {
      localStorage.setItem('nexus-presence-agent-id', currentAgent.id);
    } catch { /* ignore */ }
    if (supabase) {
      try {
        let { error } = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
        if (error) {
          const minimal: Record<string, unknown> = { status };
          if (statusMessage !== undefined) minimal.status_message = statusMessage;
          const retry = await supabase.from('agents').update(minimal).eq('id', currentAgent.id);
          error = retry.error;
        }
        if (error) {
          // non-fatal for UI presence
        }
      } catch {
        // Failed to fetch / network — local status still applied
      }
    }"""
        if old in t:
            t = t.replace(old, new, 1)
            print("updateAgentStatus resilient")
        t = "/* status-fetch-resilient-v1 */\n" + t
        tc.write_text(t)
    else:
        print("tc already")

pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    p = pp.read_text()
    if "profile-fetch-resilient-v1" not in p:
        p = p.replace("characters');\\n", "characters');\n")
        m = re.search(
            r"if \(currentAgent\) \{\s*const parts = name\.trim\(\)\.split\([^)]+\);[\s\S]*?await refresh\(\);[\s\S]*?/\* ignore \*/\s*\}\s*",
            p,
        )
        if m:
            split_m = re.search(r"split\(([^)]+)\)", m.group(0))
            split_arg = split_m.group(1) if split_m else r"/\s+/"
            new = f"""if (currentAgent) {{
          const parts = name.trim().split({split_arg});
          const initials = parts.map((p) => p[0]).join('').slice(0, 2).toUpperCase() || 'AG';
          const base: Record<string, unknown> = {{
            name: name.trim(),
            initials,
            phone: phone.trim() || null,
            bio: bio.trim() || null,
          }};
          let lastErr: string | null = null;
          let ok = false;
          const attempts: Record<string, unknown>[] = [
            {{ ...base, avatar_url: avatarUrl || null }},
            {{ ...base }},
            {{ name: name.trim(), initials, phone: phone.trim() || null }},
            {{ name: name.trim(), initials }},
          ];
          try {{
            for (const patch of attempts) {{
              const {{ error }} = await supabase.from('agents').update(patch).eq('id', currentAgent.id);
              if (!error) {{
                ok = true;
                break;
              }}
              lastErr = error.message || 'Could not save profile';
            }}
          }} catch (netErr: unknown) {{
            lastErr =
              netErr instanceof Error
                ? netErr.message
                : 'Network error talking to Supabase';
          }}
          if (!ok) {{
            const soft = (lastErr || '').toLowerCase();
            if (soft.includes('failed to fetch') || soft.includes('network')) {{
              setErr(
                'Could not reach Supabase (Failed to fetch). Status is updated on this device; ' +
                  'when the database recovers, change Status once more or Save again. ' +
                  'Check Supabase → Status (PostgREST/Auth should be Healthy).',
              );
            }} else if (lastErr) {{
              throw new Error(lastErr);
            }}
          }}
        }}
        try {{
          await refresh();
        }} catch {{
          /* ignore network */
        }}
"""
            p = p[: m.start()] + new + p[m.end() :]
            print("profile save resilient")
        old_catch = """    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Could not save profile');
    } finally {
      setSaving(false);
    }
  };"""
        new_catch = """    } catch (e: unknown) {
      const m = e instanceof Error ? e.message : 'Could not save profile';
      if (/failed to fetch/i.test(m)) {
        setErr(
          'Could not reach Supabase (Failed to fetch). Check Project Status — PostgREST and Auth must be Healthy, then try Save again.',
        );
      } else {
        setErr(m);
      }
    } finally {
      setSaving(false);
    }
  };"""
        if old_catch in p:
            p = p.replace(old_catch, new_catch, 1)
            print("catch softened")
        p = "/* profile-fetch-resilient-v1 */\n" + p
        pp.write_text(p)
    else:
        print("pp already")
print("done")
