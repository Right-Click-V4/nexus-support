#!/usr/bin/env python3
"""Priority required + placeholder; stronger light-mode form glow."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "priority-required-v1" in c:
    print("cp already")
else:
    c = c.replace(
        "const [priority, setPriority] = useState<Priority>('medium');",
        "const [priority, setPriority] = useState<Priority | ''>('');",
        1,
    )
    c = c.replace(
        "if (!name.trim() || !title.trim() || !branch.trim()) {\n      setError('Name, branch, and subject are required');\n      return;\n    }",
        "if (!name.trim() || !title.trim() || !branch.trim() || !priority) {\n      setError('Name, branch, subject, and priority are required');\n      return;\n    }",
        1,
    )
    c = c.replace(
        "        priority,\n        channel: 'portal',",
        "        priority: priority as Priority,\n        channel: 'portal',",
        1,
    )
    c = c.replace("setPriority('medium');", "setPriority('');", 1)

    old_sel = """                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Priority</label>
                      <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className={field}>
                        {([
                          { value: 'low', label: 'Low' },
                          { value: 'medium', label: 'Medium' },
                          { value: 'high', label: 'High' },
                          { value: 'critical', label: 'Critical' },
                        ] as { value: Priority; label: string }[]).map((p) => (
                          <option key={p.value} value={p.value}>{p.label}</option>
                        ))}
                      </select>
                    </div>"""

    new_sel = """                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Priority *</label>
                      <select
                        value={priority}
                        onChange={(e) => setPriority(e.target.value as Priority | '')}
                        required
                        className={field}
                      >
                        <option value="" disabled>
                          Select priority…
                        </option>
                        {([
                          { value: 'low', label: 'Low' },
                          { value: 'medium', label: 'Medium' },
                          { value: 'high', label: 'High' },
                          { value: 'critical', label: 'Critical' },
                        ] as { value: Priority; label: string }[]).map((p) => (
                          <option key={p.value} value={p.value}>{p.label}</option>
                        ))}
                      </select>
                    </div>"""

    if old_sel in c:
        c = c.replace(old_sel, new_sel, 1)
        print("priority select ok")
    else:
        print("priority select miss")

    if "priority-required-v1" not in c:
        c = c.replace("/* submit-glow-v1 */", "/* submit-glow-v1 */ /* priority-required-v1 */", 1)
    cp.write_text(c)
    print("cp done")

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    t = path.read_text()
    if "portal-submit-heartbeat-light" in t:
        print(f"{path.name}: already strong")
        continue

    old_light = """html.nexus-light .portal-submit-form-glow {
  --submit-glow-ring: rgba(124, 58, 237, 0.4);
  --submit-glow-ring-strong: rgba(109, 40, 217, 0.65);
  --submit-glow-soft: rgba(167, 139, 250, 0.35);
  --submit-glow-mid: rgba(139, 92, 246, 0.32);
  border-color: rgba(139, 92, 246, 0.45) !important;
  background: rgba(255, 255, 255, 0.62) !important;
}"""

    new_light = """html.nexus-light .portal-submit-form-glow {
  --submit-glow-ring: rgba(109, 40, 217, 0.7);
  --submit-glow-ring-strong: rgba(91, 33, 182, 0.95);
  --submit-glow-soft: rgba(124, 58, 237, 0.55);
  --submit-glow-mid: rgba(139, 92, 246, 0.5);
  border-color: rgba(109, 40, 217, 0.65) !important;
  background: rgba(255, 255, 255, 0.7) !important;
  animation: portal-submit-heartbeat-light 2.4s ease-in-out infinite;
}

@keyframes portal-submit-heartbeat-light {
  0%, 100% {
    box-shadow:
      0 0 0 2px rgba(109, 40, 217, 0.55),
      0 0 16px 4px rgba(139, 92, 246, 0.4),
      0 0 36px 8px rgba(167, 139, 250, 0.35),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  14% {
    box-shadow:
      0 0 0 3px rgba(91, 33, 182, 0.85),
      0 0 24px 8px rgba(124, 58, 237, 0.5),
      0 0 48px 14px rgba(139, 92, 246, 0.4),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  28% {
    box-shadow:
      0 0 0 2px rgba(109, 40, 217, 0.5),
      0 0 14px 4px rgba(139, 92, 246, 0.35),
      0 0 32px 8px rgba(167, 139, 250, 0.28),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  42% {
    box-shadow:
      0 0 0 3px rgba(91, 33, 182, 0.9),
      0 0 28px 10px rgba(124, 58, 237, 0.55),
      0 0 56px 16px rgba(139, 92, 246, 0.42),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
  56%, 100% {
    box-shadow:
      0 0 0 2px rgba(109, 40, 217, 0.55),
      0 0 16px 4px rgba(139, 92, 246, 0.4),
      0 0 36px 8px rgba(167, 139, 250, 0.35),
      0 8px 28px rgba(15, 23, 42, 0.08);
  }
}"""

    if old_light in t:
        t = t.replace(old_light, new_light, 1)
        if "priority-required-v1" not in t:
            t = t.replace("/* submit-glow-v1", "/* priority-required-v1 */\n/* submit-glow-v1", 1)
        path.write_text(t)
        print(f"{path.name}: stronger light glow ok")
    else:
        print(f"{path.name}: light block miss")

print("done")
