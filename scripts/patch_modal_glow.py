#!/usr/bin/env python3
"""Theme-aware transparent success modal; static stronger form glow (no heartbeat)."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "modal-glow-v2" in c:
    print("cp already")
else:
    old = """                <div className="relative w-full max-w-sm rounded-2xl border border-white/20 dark:border-white/10 bg-white/95 dark:bg-zinc-900/95 shadow-2xl shadow-violet-950/30 px-6 py-7 text-center space-y-4">
                  <div className="mx-auto w-14 h-14 rounded-full bg-emerald-500/15 flex items-center justify-center">
                    <CheckCircle2 className="text-emerald-500" size={36} strokeWidth={2} />
                  </div>
                  <div>
                    <h2 id="ticket-received-title" className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">
                      Request received
                    </h2>
                    <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
                      Your ticket ID is{' '}
                      <span className="font-mono font-semibold text-violet-700 dark:text-violet-300">{created.id}</span>.
                    </p>
                    <p className="mt-1.5 text-xs text-zinc-500 dark:text-zinc-400">
                      We typically respond within one business day. You can track status anytime.
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-2 justify-center pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setTrackId(created.id);
                        setCreated(null);
                        setView('track');
                      }}
                      className="px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-xl hover:bg-brand-700 transition-colors"
                    >
                      Track Ticket
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCreated(null);
                        setView('home');
                      }}
                      className="px-4 py-2.5 border border-zinc-200 dark:border-white/15 text-sm rounded-xl bg-white/80 dark:bg-white/5 text-zinc-800 dark:text-zinc-100 hover:bg-white dark:hover:bg-white/10 transition-colors"
                    >
                      Overview
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCreated(null)}
                    className="text-xs text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 underline-offset-2 hover:underline"
                  >
                    Stay on Submit a Ticket
                  </button>
                </div>"""

    new = """                <div className="portal-success-modal relative w-full max-w-sm rounded-2xl px-6 py-7 text-center space-y-4">
                  <div className="portal-success-modal-icon mx-auto w-14 h-14 rounded-full flex items-center justify-center">
                    <CheckCircle2 size={36} strokeWidth={2} />
                  </div>
                  <div>
                    <h2 id="ticket-received-title" className="portal-success-modal-title text-xl font-semibold tracking-tight">
                      Request received
                    </h2>
                    <p className="portal-success-modal-body mt-2 text-sm leading-relaxed">
                      Your ticket ID is{' '}
                      <span className="portal-success-modal-id font-mono font-semibold">{created.id}</span>.
                    </p>
                    <p className="portal-success-modal-hint mt-1.5 text-xs">
                      We typically respond within one business day. You can track status anytime.
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-2 justify-center pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setTrackId(created.id);
                        setCreated(null);
                        setView('track');
                      }}
                      className="portal-success-modal-primary px-4 py-2.5 text-sm font-medium rounded-xl transition-colors"
                    >
                      Track Ticket
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCreated(null);
                        setView('home');
                      }}
                      className="portal-success-modal-secondary px-4 py-2.5 text-sm rounded-xl transition-colors"
                    >
                      Overview
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCreated(null)}
                    className="portal-success-modal-dismiss text-xs underline-offset-2 hover:underline"
                  >
                    Stay on Submit a Ticket
                  </button>
                </div>"""

    if old in c:
        c = c.replace(old, new, 1)
        print("modal markup ok")
    else:
        print("modal markup miss")

    if "modal-glow-v2" not in c:
        c = c.replace("/* submit-success-modal-v1 */", "/* submit-success-modal-v1 */ /* modal-glow-v2 */", 1)
    cp.write_text(c)
    print("cp done")

css_block = """

/* modal-glow-v2 — success modal theme colors + static form glow */
.portal-success-modal {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.35);
}
html.nexus-light .portal-success-modal {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(109, 40, 217, 0.28);
  color: #1e1b4b;
}
html.nexus-dark .portal-success-modal {
  background: rgba(30, 24, 55, 0.72);
  border: 1px solid rgba(196, 181, 253, 0.28);
  color: #f4f3ff;
}
html.nexus-light .portal-success-modal-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #059669;
}
html.nexus-dark .portal-success-modal-icon {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}
html.nexus-light .portal-success-modal-title {
  color: #1e1b4b !important;
}
html.nexus-dark .portal-success-modal-title {
  color: #f8fafc !important;
}
html.nexus-light .portal-success-modal-body {
  color: #334155 !important;
}
html.nexus-dark .portal-success-modal-body {
  color: #e2e8f0 !important;
}
html.nexus-light .portal-success-modal-id {
  color: #6d28d9 !important;
}
html.nexus-dark .portal-success-modal-id {
  color: #c4b5fd !important;
}
html.nexus-light .portal-success-modal-hint {
  color: #64748b !important;
}
html.nexus-dark .portal-success-modal-hint {
  color: #94a3b8 !important;
}
html.nexus-light .portal-success-modal-primary {
  background: #7c3aed;
  color: #fff !important;
}
html.nexus-light .portal-success-modal-primary:hover {
  background: #6d28d9;
}
html.nexus-dark .portal-success-modal-primary {
  background: #8b5cf6;
  color: #fff !important;
}
html.nexus-dark .portal-success-modal-primary:hover {
  background: #7c3aed;
}
html.nexus-light .portal-success-modal-secondary {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(15, 23, 42, 0.12);
  color: #1e293b !important;
}
html.nexus-light .portal-success-modal-secondary:hover {
  background: #fff;
}
html.nexus-dark .portal-success-modal-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #f1f5f9 !important;
}
html.nexus-dark .portal-success-modal-secondary:hover {
  background: rgba(255, 255, 255, 0.14);
}
html.nexus-light .portal-success-modal-dismiss {
  color: #64748b !important;
}
html.nexus-dark .portal-success-modal-dismiss {
  color: #94a3b8 !important;
}

/* Static stronger glow — no heartbeat animation */
.portal-submit-form-glow {
  animation: none !important;
  border-color: rgba(167, 139, 250, 0.55) !important;
  box-shadow:
    0 0 0 2px rgba(139, 92, 246, 0.45),
    0 0 22px 6px rgba(124, 58, 237, 0.35),
    0 0 48px 12px rgba(139, 92, 246, 0.22),
    0 10px 28px rgba(15, 23, 42, 0.12) !important;
}
html.nexus-light .portal-submit-form-glow {
  border-color: rgba(109, 40, 217, 0.7) !important;
  background: rgba(255, 255, 255, 0.72) !important;
  box-shadow:
    0 0 0 2px rgba(109, 40, 217, 0.55),
    0 0 24px 8px rgba(124, 58, 237, 0.4),
    0 0 52px 14px rgba(139, 92, 246, 0.28),
    0 10px 28px rgba(15, 23, 42, 0.1) !important;
}
html.nexus-dark .portal-submit-form-glow {
  border-color: rgba(196, 181, 253, 0.55) !important;
  background: rgba(30, 24, 55, 0.55) !important;
  box-shadow:
    0 0 0 2px rgba(167, 139, 250, 0.5),
    0 0 26px 8px rgba(139, 92, 246, 0.4),
    0 0 56px 14px rgba(167, 139, 250, 0.28),
    0 10px 28px rgba(0, 0, 0, 0.25) !important;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    t = path.read_text()
    if "modal-glow-v2" in t:
        print(f"{path.name}: already")
        continue
    path.write_text(t + css_block)
    print(f"{path.name}: css ok")

print("done")
