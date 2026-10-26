#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
changed = False

m = re.search(r"const dbTitle = [^;]+;", t)
if m and "stripAllMeta" not in m.group(0):
    t = t[: m.start()] + "const dbTitle = (stripAllMeta(title) || stripAllMeta(plainBody).slice(0, 80) || 'Announcement');" + t[m.end() :]
    changed = True
    print("dbTitle fixed")

old = "id: tempId, title, body: storedBody, severity, active, channel,"
new = "id: tempId, title: stripAllMeta(title) || stripAllMeta(plainBody).slice(0, 80), body: storedBody, severity, active, channel,"
if old in t:
    t = t.replace(old, new)
    changed = True
    print("optimistic title cleaned")

if "function stripAllMeta" not in t:
    m2 = re.search(r"function stripChannelMeta\(body\?: string\): string \{[\s\S]*?\n\}", t)
    if m2:
        t = t[: m2.end()] + """

function stripAllMeta(body?: string): string {
  return (body || '')
    .replace(/&lt;!--\\s*nexus:[^&]*--&gt;/gi, '')
    .replace(/<!--\\s*nexus:[^>]*-->/gi, '')
    .trim();
}""" + t[m2.end() :]
        changed = True
        print("stripAllMeta added")

if "notifyAnnounceSync();\n    } catch (err) {\n      console.error('saveAnnouncement failed'" not in t:
    t2 = t.replace(
        "await refreshPlatform();\n    } catch (err) {\n      console.error('saveAnnouncement failed'",
        "await refreshPlatform();\n      notifyAnnounceSync();\n    } catch (err) {\n      console.error('saveAnnouncement failed'",
    )
    if t2 != t:
        t = t2
        changed = True
        print("notify after db")

if changed:
    p.write_text(t)
    print("written", len(t))
else:
    print("no change")
