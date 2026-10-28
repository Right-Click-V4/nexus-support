#!/usr/bin/env python3
"""Show ticket-received as popup modal instead of replacing the whole panel."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-success-modal-v1" in c:
    print("already")
    raise SystemExit(0)

c = c.replace(
    """      setCreated(ticket);
      setView('success');
      setTitle('');
      setDescription('');
      setPriority('');
      setAttachPreview(null);
      setAttachError('');""",
    """      setCreated(ticket);
      setTitle('');
      setDescription('');
      setPriority('');
      setBranch('');
      setAttachPreview(null);
      setAttachError('');""",
    1,
)
print("submit handler ok")

old_success = """            {view === 'success' && created && (
              <div className="max-w-md text-center space-y-4 py-8">
                <CheckCircle2 className="mx-auto text-emerald-500" size={48} />
                <h1 className="text-xl font-semibold text-zinc-900">Request received</h1>
                <p className="text-zinc-500 text-sm">Your ticket ID is <span className="font-mono font-semibold text-violet-700">{created.id}</span>.</p>
                <div className="flex gap-2 justify-center">
                  <button type="button" onClick={() => { setTrackId(created.id); setView('track'); }} className="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700">Track Ticket</button>
                  <button type="button" onClick={() => setView('home')} className="px-4 py-2 border border-zinc-200 text-sm rounded-lg bg-white/80 hover:bg-white">Overview</button>
                </div>
              </div>
            )}"""

new_modal = """            {created && (
              <div
                className="fixed inset-0 z-[80] flex items-center justify-center p-4"
                role="dialog"
                aria-modal="true"
                aria-labelledby="ticket-received-title"
              >
                <button
                  type="button"
                  className="absolute inset-0 bg-black/50 backdrop-blur-[2px]"
                  aria-label="Close"
                  onClick={() => setCreated(null)}
                />
                <div className="relative w-full max-w-sm rounded-2xl border border-white/20 dark:border-white/10 bg-white/95 dark:bg-zinc-900/95 shadow-2xl shadow-violet-950/30 px-6 py-7 text-center space-y-4">
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
                </div>
              </div>
            )}"""

if old_success in c:
    c = c.replace(old_success, new_modal, 1)
    print("modal ok")
else:
    print("success block miss")

if "submit-success-modal-v1" not in c:
    c = c.replace("/* priority-required-v1 */", "/* priority-required-v1 */ /* submit-success-modal-v1 */", 1)
    if "submit-success-modal-v1" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* submit-success-modal-v1 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("done")
