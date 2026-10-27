#!/usr/bin/env python3
"""Icons for guide cards, title-case headings, fill left column under form."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-fill-v1" in c:
    print("already")
    raise SystemExit(0)

old_imp = "  LogOut, User, Star, Home, ExternalLink, Users, ImagePlus, X,\n} from 'lucide-react';"
new_imp = "  LogOut, User, Star, Home, ExternalLink, Users, ImagePlus, X,\n  Flag, ListTree, Lightbulb, Clock3, ClipboardList,\n} from 'lucide-react';"
if old_imp in c:
    c = c.replace(old_imp, new_imp, 1)
    print("imports ok")
else:
    print("imports miss")

old_form_open = """                <div className="grid lg:grid-cols-12 gap-4 items-start">
                  <form
                    onSubmit={submit}
                    className="lg:col-span-5 portal-overview-glass rounded-2xl p-4 sm:p-5 space-y-3.5 relative z-20"
                  >"""

new_form_open = """                <div className="grid lg:grid-cols-12 gap-4 items-start">
                  <div className="lg:col-span-5 space-y-4">
                  <form
                    onSubmit={submit}
                    className="portal-overview-glass rounded-2xl p-4 sm:p-5 space-y-3.5 relative z-20"
                  >"""

if old_form_open in c:
    c = c.replace(old_form_open, new_form_open, 1)
    print("form open ok")
else:
    print("form open miss")

old_form_close = """                    <button type="submit" disabled={saving} className={btnPrimary}>
                      {saving ? 'Submitting…' : 'Submit a Ticket'}
                    </button>
                  </form>

                  <div className="lg:col-span-7 space-y-4">"""

new_form_close = """                    <button type="submit" disabled={saving} className={btnPrimary}>
                      {saving ? 'Submitting…' : 'Submit a Ticket'}
                    </button>
                  </form>

                  <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-sky-500/15 text-sky-600 dark:text-sky-300 flex items-center justify-center">
                        <ClipboardList size={16} />
                      </div>
                      <div>
                        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">How submitting works</h2>
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400">From form to resolution</p>
                      </div>
                    </div>
                    <ol className="space-y-2.5">
                      {[
                        { n: '1', t: 'Fill the form', d: 'Name is locked to your account. Choose branch, subject, details, and priority.' },
                        { n: '2', t: 'We create a ticket ID', d: 'You get a unique ID (for example NX-2841) right after submit.' },
                        { n: '3', t: 'Support triages', d: 'Agents use subject + priority to route your request to the right queue.' },
                        { n: '4', t: 'Track progress', d: 'Open Track Ticket or My Tickets anytime with your ID and account email.' },
                      ].map((s) => (
                        <li key={s.n} className="flex gap-3 items-start rounded-xl border border-white/25 dark:border-white/10 bg-white/20 dark:bg-black/15 px-3 py-2.5">
                          <span className="shrink-0 w-6 h-6 rounded-full bg-brand-600/90 text-white text-[11px] font-bold flex items-center justify-center">{s.n}</span>
                          <div className="min-w-0">
                            <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">{s.t}</div>
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-snug mt-0.5">{s.d}</p>
                          </div>
                        </li>
                      ))}
                    </ol>
                  </section>

                  <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/15 text-amber-600 dark:text-amber-300 flex items-center justify-center">
                        <Lightbulb size={16} />
                      </div>
                      <div>
                        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Tips for a faster response</h2>
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Help agents help you</p>
                      </div>
                    </div>
                    <ul className="space-y-2 text-[11px] sm:text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed">
                      <li className="flex gap-2"><span className="text-violet-500 shrink-0">•</span><span>Include error messages, screenshots, and the exact time the issue started.</span></li>
                      <li className="flex gap-2"><span className="text-violet-500 shrink-0">•</span><span>One main problem per ticket — open a second ticket if you have a separate request.</span></li>
                      <li className="flex gap-2"><span className="text-violet-500 shrink-0">•</span><span>Use <span className="font-medium">Critical</span> only for outages or active security risk.</span></li>
                      <li className="flex gap-2"><span className="text-violet-500 shrink-0">•</span><span>Check Help Articles first for password resets and common how-tos.</span></li>
                    </ul>
                    <div className="mt-3 flex items-start gap-2 rounded-xl border border-white/25 dark:border-white/10 bg-white/20 dark:bg-black/15 px-3 py-2.5">
                      <Clock3 size={14} className="shrink-0 mt-0.5 text-emerald-500" />
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-snug">
                        Typical first response is within <span className="font-medium text-zinc-800 dark:text-zinc-200">one business day</span>. High and Critical tickets are reviewed sooner during support hours.
                      </p>
                    </div>
                  </section>
                  </div>

                  <div className="lg:col-span-7 space-y-4">"""

if old_form_close in c:
    c = c.replace(old_form_close, new_form_close, 1)
    print("form close + left cards ok")
else:
    print("form close miss")

old_pri = """                      <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 mb-1">Priority guide</h2>
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mb-2.5">Match impact at your branch.</p>"""

new_pri = """                      <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                        <div className="flex items-center gap-2 mb-2.5">
                          <div className="w-8 h-8 rounded-lg bg-rose-500/15 text-rose-600 dark:text-rose-300 flex items-center justify-center">
                            <Flag size={16} />
                          </div>
                          <div>
                            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Priority Guide</h2>
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Match impact at your branch</p>
                          </div>
                        </div>"""

if old_pri in c:
    c = c.replace(old_pri, new_pri, 1)
    print("priority header ok")
else:
    print("priority header miss")

old_sub = """                    <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                      <div className="flex items-end justify-between gap-3 mb-3">
                        <div>
                          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Subject guide</h2>
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5">
                            Pick the subject that best describes the main problem, then clarify in Details.
                          </p>
                        </div>
                      </div>"""

new_sub = """                    <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-500/15 text-indigo-600 dark:text-indigo-300 flex items-center justify-center">
                          <ListTree size={16} />
                        </div>
                        <div>
                          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Subject Guide</h2>
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-400">
                            Pick the subject that best describes the main problem, then clarify in Details.
                          </p>
                        </div>
                      </div>"""

if old_sub in c:
    c = c.replace(old_sub, new_sub, 1)
    print("subject header ok")
else:
    print("subject header miss")

c = c.replace(
    ">What is a ticket?</h2>",
    ">What is a Ticket?</h2>",
    1,
)

if "submit-fill-v1" not in c:
    c = c.replace(
        "/* submit-overview-layout-v1 */",
        "/* submit-overview-layout-v1 */ /* submit-fill-v1 */",
        1,
    )

cp.write_text(c)
print("done")
