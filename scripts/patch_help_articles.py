#!/usr/bin/env python3
"""Help Articles glass layout for Customer Portal."""
from pathlib import Path
import re

p = Path("src/components/CustomerPortal.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
if "help-articles-glass-v1" in t and "How these articles help" in t:
    print("already")
    raise SystemExit(0)

ARTICLES = """const HELP_ARTICLES = [
  { id: 'reset-password', category: 'Account', title: 'Reset your password',
    body: 'Use Sign in → Forgot password with your account email. Check spam for the reset link. Sign out of shared devices after resetting.',
    tip: 'Still locked out? Submit a ticket under Account & login issues.' },
  { id: 'first-login', category: 'Account', title: 'First-time login & profile',
    body: 'Sign in with the email your branch admin registered. Open Account to confirm your name and contact match your record.',
    tip: 'Your name is locked on forms so agents can identify who submitted each request.' },
  { id: 'submit-ticket', category: 'Tickets', title: 'How to submit a ticket',
    body: 'Go to Submit a Ticket. Choose branch and subject, add clear details, and optional screenshots. Use Critical only when work is blocked.',
    tip: 'One issue per ticket keeps responses faster.' },
  { id: 'track-tickets', category: 'Tickets', title: 'Track & follow up on My Tickets',
    body: 'Open My Tickets for status (Open, Pending, On-hold, Resolved, Closed). Use Action → View for agent responses, or Send Follow-Up for an update.',
    tip: 'Copy the ticket ID (NX-…) when calling or chatting with support.' },
  { id: 'status-meanings', category: 'Tickets', title: 'What each ticket status means',
    body: 'Open = queued. Pending = agent working or waiting on info. On-hold = paused. Resolved = fix applied. Closed = past SLA or finalized.',
    tip: 'Reply in the ticket when status is Pending and the agent asked for more details.' },
  { id: 'live-chat', category: 'Support channels', title: 'When to use Live Chat',
    body: 'Use Live Chat for urgent short questions when an agent is Online in Active Now. Share your ticket ID if it is about an existing case.',
    tip: 'If no agent is online, submit a ticket instead of waiting on chat.' },
  { id: 'community', category: 'Support channels', title: 'Community group chat',
    body: 'Community is for peer tips and general product questions—not private account or billing data. Prefer tickets for personal account issues.',
    tip: 'Search the conversation before posting a question that may already be answered.' },
  { id: 'billing', category: 'Billing', title: 'Billing & invoices',
    body: 'Invoices are emailed around the 1st of each month. Include invoice number, branch, and billing period on Billing tickets.',
    tip: 'Attach a screenshot of the invoice or payment error if something failed to process.' },
  { id: 'api-limits', category: 'Integrations', title: 'API rate limits & keys',
    body: 'Typical free tier allows about 60 requests/minute. Request API access via a ticket and never share keys in Community.',
    tip: 'Rotate keys if they may have been exposed.' },
  { id: 'service-status', category: 'Operations', title: 'Check service status first',
    body: 'Before opening a ticket for outages, check the marquee and Overview. Widespread issues are often already being worked on.',
    tip: 'Mention when the problem started and which branch is affected.' },
  { id: 'attachments', category: 'Tickets', title: 'Screenshots & attachments',
    body: 'On Submit a Ticket you can attach images. Prefer clear screenshots of errors, dates, and the screen where the issue appears.',
    tip: 'Avoid sending passwords or full card numbers in attachments.' },
  { id: 'sla-closed', category: 'Tickets', title: 'Why a ticket was Closed',
    body: 'Tickets past SLA may be marked Closed automatically. You can still open them from My Tickets and send a follow-up if needed.',
    tip: 'Reference the old ticket ID in a new ticket if you need to reopen the same issue.' },
];
"""

HELP_VIEW = r"""            {view === 'help' && (
              <div className="w-full max-w-5xl mx-auto space-y-4 pb-2">
                <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-5">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-700 dark:text-indigo-300/90">Knowledge base</p>
                  <h1 className="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">Help Articles</h1>
                  <p className="mt-1.5 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed max-w-3xl">
                    Short guides for everyday tasks—login, tickets, chat, billing, and more. Read these first to solve common issues yourself or to prepare a clearer ticket so agents can help faster.
                  </p>
                </section>
                <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/15 text-indigo-600 dark:text-indigo-300 flex items-center justify-center"><BookOpen size={16} /></div>
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">How these articles help</h2>
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Self-serve answers · fewer back-and-forths · shared best practices</p>
                    </div>
                  </div>
                  <div className="grid sm:grid-cols-3 gap-2.5">
                    {[
                      { t: 'Solve common issues', d: 'Password resets, status meanings, and where to click—without waiting in queue.' },
                      { t: 'Write better tickets', d: 'Know what details agents need so your request is routed and resolved sooner.' },
                      { t: 'Pick the right channel', d: 'When to use Live Chat, Community, or a formal ticket for account-specific work.' },
                    ].map((x) => (
                      <div key={x.t} className="rounded-xl border border-white/25 dark:border-white/10 bg-white/25 dark:bg-black/20 px-3 py-2.5">
                        <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">{x.t}</div>
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-snug mt-0.5">{x.d}</p>
                      </div>
                    ))}
                  </div>
                </section>
                <div className="grid sm:grid-cols-2 gap-3">
                  {HELP_ARTICLES.map((a) => {
                    const catColor =
                      a.category === 'Account' ? 'bg-pink-500/15 text-pink-700 dark:text-pink-300'
                      : a.category === 'Tickets' ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                      : a.category === 'Support channels' ? 'bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300'
                      : a.category === 'Billing' ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300'
                      : a.category === 'Integrations' ? 'bg-sky-500/15 text-sky-700 dark:text-sky-300'
                      : 'bg-violet-500/15 text-violet-700 dark:text-violet-300';
                    return (
                      <article key={a.id} className="portal-overview-glass rounded-2xl p-4 sm:p-5 flex flex-col gap-2 border border-white/20 dark:border-white/10 bg-white/30 dark:bg-black/25 backdrop-blur-md">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 leading-snug">{a.title}</h3>
                          <span className={`shrink-0 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full ${catColor}`}>{a.category}</span>
                        </div>
                        <p className="text-[13px] text-zinc-700 dark:text-zinc-300 leading-relaxed flex-1">{a.body}</p>
                        {a.tip ? (
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-400 rounded-lg border border-white/20 dark:border-white/10 bg-white/20 dark:bg-white/5 px-2.5 py-1.5">
                            <span className="font-semibold text-indigo-700 dark:text-indigo-300">Tip: </span>{a.tip}
                          </p>
                        ) : null}
                      </article>
                    );
                  })}
                </div>
                <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center"><LifeBuoy size={16} /></div>
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">We are here when self-serve is not enough</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button type="button" onClick={() => setView('submit')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl bg-brand-600 text-white hover:bg-brand-500"><Ticket size={14} /> Submit a Ticket</button>
                    <button type="button" onClick={() => setView('chat')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-800 dark:text-zinc-100"><MessageSquare size={14} /> Live Chat</button>
                    <button type="button" onClick={() => setView('mytickets')} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-xl border border-white/25 dark:border-white/15 bg-white/25 dark:bg-black/20 text-zinc-800 dark:text-zinc-100"><ClipboardList size={14} /> My Tickets</button>
                  </div>
                </section>
              </div>
            )}
"""

if "LifeBuoy" not in t:
    t = t.replace("Copy, Check,", "Copy, Check, LifeBuoy,", 1)
    if "LifeBuoy" not in t:
        t = t.replace("} from 'lucide-react';", ", LifeBuoy } from 'lucide-react';", 1)

art = ARTICLES if ARTICLES.endswith("\n") else ARTICLES + "\n"
t2, n = re.subn(r"const HELP_ARTICLES = \[[\s\S]*?\];\n", art, t, count=1)
print("articles", n)
t = t2 if n else t

pat = re.compile(r"[ \t]*\{view === 'help' && \([\s\S]*?\n[ \t]*\)\}\s*\n(?=[ \t]*\{view === 'account')", re.M)
m = pat.search(t)
if not m:
    print("FAIL help view")
    raise SystemExit(1)
t = t[: m.start()] + HELP_VIEW + "\n" + t[m.end() :]
print("view ok")
if "help-articles-glass-v1" not in t:
    t = "/* help-articles-glass-v1 */\n" + t
p.write_text(t)
print("done", "How these articles help" in t)
print("braces", t.count("{") - t.count("}"))
