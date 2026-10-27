#!/usr/bin/env python3
"""Left-align Submit form, larger 'Submit a Ticket' title, lock name field to account."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-layout-v1" in c:
    print("already")
    raise SystemExit(0)

c = c.replace(
    "submit: { title: 'Submit Ticket', desc:",
    "submit: { title: 'Submit a Ticket', desc:",
    1,
)
c = c.replace(
    "{ id: 'submit', label: 'Submit Ticket', icon: Ticket },",
    "{ id: 'submit', label: 'Submit a Ticket', icon: Ticket },",
    1,
)

old_fx = """  useEffect(() => {
    if (!isCustomerSession || !user) return;
    const display = (user.user_metadata?.full_name as string) || '';
    if (display) setName((n) => n || display);
    if (user.email) setEmail((e) => e || user.email || '');
  }, [isCustomerSession, user]);"""

new_fx = """  useEffect(() => {
    if (!user) return;
    // Locked identity — always mirror the registered account name (prevents shared-account spoofing)
    const display =
      (user.user_metadata?.full_name as string)?.trim() ||
      user.email?.split('@')[0] ||
      'Customer';
    setName(display);
    if (user.email) setEmail(user.email);
  }, [user]);"""

if old_fx in c:
    c = c.replace(old_fx, new_fx, 1)
    print("name lock effect ok")
else:
    print("name lock effect miss")

old_block = """            {view === 'submit' && (
              <div className="max-w-lg">
                <div className="mb-3">
                  <h1 className="text-lg font-semibold text-zinc-900 tracking-tight">Submit Ticket</h1>
                  <p className="text-zinc-500 text-sm mt-1">We typically respond within one business day.</p>
                </div>
                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3.5">
                  {error && <div className="text-sm text-rose-600 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 px-3 py-2 rounded-lg">{error}</div>}
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Your name *</label>
                    <input value={name} onChange={(e) => setName(e.target.value)} required className={field} />
                  </div>"""

new_block = """            {view === 'submit' && (
              <div className="w-full max-w-lg mr-auto">
                <div className="mb-4">
                  <h1 className="text-2xl sm:text-3xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">Submit a Ticket</h1>
                  <p className="text-zinc-500 dark:text-zinc-400 text-sm sm:text-base mt-1.5">We typically respond within one business day.</p>
                </div>
                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3.5">
                  {error && <div className="text-sm text-rose-600 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 px-3 py-2 rounded-lg">{error}</div>}
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Your name</label>
                    <input
                      value={name}
                      readOnly
                      required
                      className={`${field} opacity-90 cursor-not-allowed bg-zinc-100/80 dark:bg-white/5`}
                      title="Filled from your account — cannot be changed"
                    />
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Locked to your registered account name.</p>
                  </div>"""

if old_block in c:
    c = c.replace(old_block, new_block, 1)
    print("layout block ok")
else:
    c = c.replace(
        '<div className="max-w-lg">\n                <div className="mb-3">\n                  <h1 className="text-lg font-semibold text-zinc-900 tracking-tight">Submit Ticket</h1>',
        '<div className="w-full max-w-lg mr-auto">\n                <div className="mb-4">\n                  <h1 className="text-2xl sm:text-3xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">Submit a Ticket</h1>',
        1,
    )
    c = c.replace(
        '<input value={name} onChange={(e) => setName(e.target.value)} required className={field} />',
        '''<input
                      value={name}
                      readOnly
                      required
                      className={`${field} opacity-90 cursor-not-allowed bg-zinc-100/80 dark:bg-white/5`}
                      title="Filled from your account — cannot be changed"
                    />
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Locked to your registered account name.</p>''',
        1,
    )
    print("layout partial")

c = c.replace(
    "{saving ? 'Submitting…' : 'Submit Ticket'}",
    "{saving ? 'Submitting…' : 'Submit a Ticket'}",
    1,
)

if "submit-layout-v1" not in c:
    c = c.replace("/* submit-form-v1 */", "/* submit-form-v1 */ /* submit-layout-v1 */", 1)

cp.write_text(c)
print("done")
