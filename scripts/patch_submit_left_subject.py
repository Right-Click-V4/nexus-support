#!/usr/bin/env python3
"""Left-align submit form for right-side content; subject placeholder + A-Z; no clip."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-left-subject-v1" in c:
    print("already")
    raise SystemExit(0)

old_subj = """const SUBJECT_OPTIONS = [
  'Account & login issues',
  'Password reset / locked out',
  'Billing & invoices',
  'Payment failed or declined',
  'Subscription / plan change',
  'Service outage / downtime',
  'Performance / slow response',
  'Bug report',
  'Feature request',
  'API access / API keys',
  'API rate limits',
  'Integration help',
  'Data export or import',
  'Access permissions / roles',
  'Branch or location change',
  'Hardware / device issue',
  'Network connectivity',
  'Email delivery problems',
  'Notifications & alerts',
  'Mobile app issue',
  'Security concern',
  'Training / how-to question',
  'Other',
];"""

new_subj = """/** Subject list (alphabetical) — editable later */
const SUBJECT_OPTIONS = [
  'Access permissions / roles',
  'Account & login issues',
  'API access / API keys',
  'API rate limits',
  'Billing & invoices',
  'Branch or location change',
  'Bug report',
  'Data export or import',
  'Email delivery problems',
  'Feature request',
  'Hardware / device issue',
  'Integration help',
  'Mobile app issue',
  'Network connectivity',
  'Notifications & alerts',
  'Other',
  'Password reset / locked out',
  'Payment failed or declined',
  'Performance / slow response',
  'Security concern',
  'Service outage / downtime',
  'Subscription / plan change',
  'Training / how-to question',
] as const;"""

if old_subj in c:
    c = c.replace(old_subj, new_subj, 1)
    print("subjects ok")
else:
    t2, n = re.subn(
        r"const SUBJECT_OPTIONS = \[[\s\S]*?\];",
        new_subj.rstrip(),
        c,
        count=1,
    )
    if n:
        c = t2
        print("subjects loose ok")
    else:
        print("subjects miss")

old_wrap = """            {view === 'submit' && (
              <div className="w-full max-w-lg mr-auto">
                <div className="mb-4">
                  <h1 className="text-2xl sm:text-3xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">Submit a Ticket</h1>
                  <p className="text-zinc-500 dark:text-zinc-400 text-sm sm:text-base mt-1.5">We typically respond within one business day.</p>
                </div>
                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3.5">"""

new_wrap = """            {view === 'submit' && (
              <div className="w-full flex flex-col lg:flex-row lg:items-start gap-6 lg:gap-8">
                <div className="w-full max-w-md shrink-0 self-start">
                <div className="mb-4">
                  <h1 className="text-2xl sm:text-3xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">Submit a Ticket</h1>
                  <p className="text-zinc-500 dark:text-zinc-400 text-sm sm:text-base mt-1.5">We typically respond within one business day.</p>
                </div>
                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3.5 relative z-20">"""

if old_wrap in c:
    c = c.replace(old_wrap, new_wrap, 1)
    print("wrap start ok")
else:
    print("wrap start miss")

old_end = """                  <button type="submit" disabled={saving} className={btnPrimary}>{saving ? 'Submitting…' : 'Submit a Ticket'}</button>
                </form>
              </div>
            )}
            {view === 'success' && created && ("""

new_end = """                  <button type="submit" disabled={saving} className={btnPrimary}>{saving ? 'Submitting…' : 'Submit a Ticket'}</button>
                </form>
                </div>
                {/* Right column reserved for upcoming Submit Ticket panel content */}
                <div className="flex-1 min-w-0 hidden lg:block" aria-hidden="true" />
              </div>
            )}
            {view === 'success' && created && ("""

if old_end in c:
    c = c.replace(old_end, new_end, 1)
    print("wrap end ok")
else:
    print("wrap end miss")

old_opt = """                    <select value={title} onChange={(e) => setTitle(e.target.value)} required className={field}>
                      <option value="">Select a request type…</option>
                      {SUBJECT_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>"""

new_opt = """                    <select value={title} onChange={(e) => setTitle(e.target.value)} required className={field}>
                      <option value="" disabled>
                        Select a request type…
                      </option>
                      {SUBJECT_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>"""

if old_opt in c:
    c = c.replace(old_opt, new_opt, 1)
    print("subject placeholder ok")
else:
    c = c.replace(
        '<option value="">Select a request type…</option>',
        '<option value="" disabled>Select a request type…</option>',
        1,
    )
    print("subject placeholder partial")

old_main = """        <main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 ${
            view === 'community' ? 'overflow-hidden flex flex-col' : 'overflow-y-auto'
          }`}
        >"""

new_main = """        <main
          className={`relative z-10 flex-1 min-h-0 ${
            view === 'community'
              ? 'overflow-hidden flex flex-col p-3 lg:p-5'
              : view === 'submit'
                ? 'overflow-y-auto p-3 lg:pl-3 lg:pr-5 lg:py-5'
                : 'overflow-y-auto p-3 lg:p-5'
          }`}
        >"""

if old_main in c:
    c = c.replace(old_main, new_main, 1)
    print("main pad ok")
else:
    print("main pad miss")

if "submit-left-subject-v1" not in c:
    c = c.replace("/* branch-list-v1 */", "/* branch-list-v1 */ /* submit-left-subject-v1 */", 1)
    if "submit-left-subject-v1" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* submit-left-subject-v1 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("done")
