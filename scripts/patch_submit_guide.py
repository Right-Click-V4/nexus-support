#!/usr/bin/env python3
"""Right-side Submit Ticket guide: what tickets are, subjects, priorities; scrollable panel."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-guide-v1" in c:
    print("already")
    raise SystemExit(0)

guide_const = """
/** Help text for each subject (keep in sync with SUBJECT_OPTIONS) */
const SUBJECT_GUIDE: { subject: string; tip: string }[] = [
  { subject: 'Access permissions / roles', tip: 'You need a role change, more access, or cannot open a screen you should be able to use.' },
  { subject: 'Account & login issues', tip: 'Problems signing in, locked account, wrong profile details, or account not recognized.' },
  { subject: 'API access / API keys', tip: 'Request new keys, rotate keys, or troubleshoot API authentication.' },
  { subject: 'API rate limits', tip: 'You are hitting request limits or need higher quota for production traffic.' },
  { subject: 'Billing & invoices', tip: 'Questions about charges, invoices, receipts, or payment history.' },
  { subject: 'Branch or location change', tip: 'Transfer your workplace branch, update location assignment, or correct branch mapping.' },
  { subject: 'Bug report', tip: 'Something in the product is broken or behaves incorrectly — include steps to reproduce if you can.' },
  { subject: 'Data export or import', tip: 'You need to download data, bulk upload records, or fix a failed import/export.' },
  { subject: 'Email delivery problems', tip: 'Expected emails (alerts, invoices, resets) are missing, delayed, or going to spam.' },
  { subject: 'Feature request', tip: 'A capability is missing and you want the product team to consider adding it.' },
  { subject: 'Hardware / device issue', tip: 'POS terminal, printer, scanner, or other branch hardware is failing.' },
  { subject: 'Integration help', tip: 'Connecting NexusOps with another system (POS, accounting, SSO, webhooks, etc.).' },
  { subject: 'Mobile app issue', tip: 'Bugs or login problems specific to the mobile app.' },
  { subject: 'Network connectivity', tip: 'Branch network, VPN, or connectivity problems blocking the service.' },
  { subject: 'Notifications & alerts', tip: 'Push, email, or in-app alerts are wrong, too noisy, or not arriving.' },
  { subject: 'Other', tip: 'None of the subjects fit — describe your request clearly in Details.' },
  { subject: 'Password reset / locked out', tip: 'You cannot reset your password or your account is locked after failed attempts.' },
  { subject: 'Payment failed or declined', tip: 'A card or payment method was declined, or a charge did not complete.' },
  { subject: 'Performance / slow response', tip: 'Pages or APIs are unusually slow, timing out, or freezing.' },
  { subject: 'Security concern', tip: 'Suspected unauthorized access, phishing, data exposure, or other security risk — use Critical if active.' },
  { subject: 'Service outage / downtime', tip: 'The product is down or a major feature is unavailable for your branch.' },
  { subject: 'Subscription / plan change', tip: 'Upgrade, downgrade, cancel, or change seats on your plan.' },
  { subject: 'Training / how-to question', tip: 'You need guidance on how to use a feature (not a bug).' },
];

const PRIORITY_GUIDE: { level: string; color: string; tip: string }[] = [
  { level: 'Low', color: 'bg-emerald-500', tip: 'Minor inconvenience. Work can continue; no rush.' },
  { level: 'Medium', color: 'bg-sky-500', tip: 'Normal request. Affects work but a workaround exists. Default for most tickets.' },
  { level: 'High', color: 'bg-amber-500', tip: 'Significant impact. A key workflow is blocked for you or your branch.' },
  { level: 'Critical', color: 'bg-rose-500', tip: 'Emergency. Full outage, data risk, or business stopped. Use only when truly urgent.' },
];
"""

marker = "] as const;\n\n\nconst VIEW_META"
if marker in c:
    c = c.replace(marker, "] as const;\n" + guide_const + "\nconst VIEW_META", 1)
    print("guide const ok")
else:
    idx = c.find("SUBJECT_OPTIONS")
    if idx >= 0:
        end = c.find("] as const;", idx)
        if end > 0:
            insert_at = end + len("] as const;")
            c = c[:insert_at] + "\n" + guide_const + c[insert_at:]
            print("guide const insert ok")
        else:
            print("guide const miss end")
    else:
        print("guide const miss")

old_right = """                {/* Right column reserved for upcoming Submit Ticket panel content */}
                <div className="flex-1 min-w-0 hidden lg:block" aria-hidden="true" />"""

new_right = """                <aside className="flex-1 min-w-0 w-full space-y-4">
                  <div className="portal-glass-card rounded-xl p-4 sm:p-5">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center shrink-0 text-violet-600 dark:text-violet-300">
                        <Ticket size={20} strokeWidth={2.1} />
                      </div>
                      <div>
                        <h2 className="text-base sm:text-lg font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">What is a ticket?</h2>
                        <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">A quick guide before you submit</p>
                      </div>
                    </div>
                    <div className="space-y-2.5 text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
                      <p>
                        A <span className="font-medium text-zinc-800 dark:text-zinc-100">ticket</span> is a tracked support request.
                        When you submit one, our team gets a clear record of your issue, branch, and priority so we can respond in order and keep you updated.
                      </p>
                      <p>
                        Use tickets for account problems, outages, billing, bugs, and how-to questions.
                        You will get a ticket ID to follow progress under <span className="font-medium">Track Ticket</span> or <span className="font-medium">My Tickets</span>.
                      </p>
                      <ul className="list-disc pl-5 space-y-1 text-xs sm:text-sm text-zinc-500 dark:text-zinc-400">
                        <li>Pick the closest <span className="font-medium text-zinc-700 dark:text-zinc-200">Subject</span> so the right agent sees it first.</li>
                        <li>Add clear <span className="font-medium text-zinc-700 dark:text-zinc-200">Details</span> and an optional photo.</li>
                        <li>Set <span className="font-medium text-zinc-700 dark:text-zinc-200">Priority</span> honestly — it helps us triage, not skip the queue unfairly.</li>
                      </ul>
                    </div>
                  </div>

                  <div className="portal-glass-card rounded-xl p-4 sm:p-5">
                    <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight mb-1">Priority guide</h2>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-3">Choose the level that matches real impact at your branch.</p>
                    <div className="space-y-2.5">
                      {PRIORITY_GUIDE.map((p) => (
                        <div key={p.level} className="flex gap-3 items-start rounded-lg bg-black/[0.03] dark:bg-white/[0.04] px-3 py-2.5">
                          <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${p.color}`} />
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-zinc-800 dark:text-zinc-100">{p.level}</div>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-snug mt-0.5">{p.tip}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="portal-glass-card rounded-xl p-4 sm:p-5">
                    <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight mb-1">Subject guide</h2>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-3">
                      Match your request to a subject below. If two could fit, pick the one that describes the main problem, then clarify in Details.
                    </p>
                    <div className="space-y-2 max-h-none">
                      {SUBJECT_GUIDE.map((item) => (
                        <div
                          key={item.subject}
                          className={`rounded-lg border px-3 py-2.5 transition-colors ${
                            title === item.subject
                              ? 'border-violet-400/50 bg-violet-500/10'
                              : 'border-zinc-200/60 dark:border-white/10 bg-black/[0.02] dark:bg-white/[0.03]'
                          }`}
                        >
                          <div className="text-sm font-medium text-zinc-800 dark:text-zinc-100">{item.subject}</div>
                          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-snug mt-0.5">{item.tip}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </aside>"""

if old_right in c:
    c = c.replace(old_right, new_right, 1)
    print("right panel ok")
else:
    print("right panel miss")

c = c.replace(
    'className="w-full flex flex-col lg:flex-row lg:items-start gap-6 lg:gap-8"',
    'className="w-full flex flex-col lg:flex-row lg:items-start gap-6 lg:gap-8 pb-4"',
    1,
)

if "submit-guide-v1" not in c:
    c = c.replace("/* submit-left-subject-v1 */", "/* submit-left-subject-v1 */ /* submit-guide-v1 */", 1)
    if "submit-guide-v1" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* submit-guide-v1 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("done")
