#!/usr/bin/env python3
"""Submit Ticket form: no email, subject dropdown, optional image, Priority Title Case."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-form-v1" in c:
    print("already")
    raise SystemExit(0)

if "ImagePlus" not in c:
    c = c.replace(
        "  LogOut, User, Star, Home, ExternalLink, Users,\n} from 'lucide-react';",
        "  LogOut, User, Star, Home, ExternalLink, Users, ImagePlus, X,\n} from 'lucide-react';",
        1,
    )
if "TicketAttachment" not in c:
    c = c.replace(
        "import type { Priority, Ticket as TicketType } from '../types';",
        "import type { Priority, Ticket as TicketType, TicketAttachment } from '../types';\nimport { MAX_ATTACHMENT_BYTES } from '../types';",
        1,
    )

if "SUBJECT_OPTIONS" not in c:
    c = c.replace(
        "const BRANCH_OPTIONS = INITIAL_BRANCHES.map((b) => b.name);",
        """const BRANCH_OPTIONS = INITIAL_BRANCHES.map((b) => b.name);

/** Editable later — common ticket subjects for the portal form */
const SUBJECT_OPTIONS = [
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
];
""",
        1,
    )

c = c.replace(
    "const { createTicket, findTicket, tickets, ticketsForEmail } = useTickets();",
    "const { createTicket, updateTicket, findTicket, tickets, ticketsForEmail } = useTickets();",
    1,
)

if "attachFile" not in c and "attachPreview" not in c:
    c = c.replace(
        "const [priority, setPriority] = useState<Priority>('medium');",
        """const [priority, setPriority] = useState<Priority>('medium');
  const [attachPreview, setAttachPreview] = useState<{ name: string; size: number; mime: string; url: string } | null>(null);
  const [attachError, setAttachError] = useState('');""",
        1,
    )

old_submit = """  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !title.trim() || !branch.trim()) {
      setError('Name, email, branch, and subject are required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const ticket = await createTicket({
        title: title.trim(), description: description.trim(), priority, channel: 'portal',
        customer_name: name.trim(), customer_email: email.trim(), branch: branch.trim(),
      });
      setCreated(ticket);
      setView('success');
      setTitle(''); setDescription(''); setPriority('medium');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not submit request');
    } finally {
      setSaving(false);
    }
  };"""

new_submit = """  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const accountEmail = (user?.email || email || '').trim();
    if (!name.trim() || !title.trim() || !branch.trim()) {
      setError('Name, branch, and subject are required');
      return;
    }
    if (!accountEmail) {
      setError('Your account email is missing. Please sign in again.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const ticket = await createTicket({
        title: title.trim(),
        description: description.trim(),
        priority,
        channel: 'portal',
        customer_name: name.trim(),
        customer_email: accountEmail,
        branch: branch.trim(),
      });
      if (attachPreview) {
        const att: TicketAttachment = {
          id: `att-${Date.now()}`,
          name: attachPreview.name,
          size: attachPreview.size,
          mime: attachPreview.mime,
          url: attachPreview.url,
          created_at: new Date().toISOString(),
          uploaded_by: accountEmail,
        };
        try {
          await updateTicket(ticket.id, { attachments: [...(ticket.attachments || []), att] });
          ticket.attachments = [...(ticket.attachments || []), att];
        } catch {
          /* attachment optional — ticket still created */
        }
      }
      setCreated(ticket);
      setView('success');
      setTitle('');
      setDescription('');
      setPriority('medium');
      setAttachPreview(null);
      setAttachError('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not submit ticket');
    } finally {
      setSaving(false);
    }
  };"""

if old_submit in c:
    c = c.replace(old_submit, new_submit, 1)
    print("submit handler ok")
else:
    print("submit handler miss")

old_form = """                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3">
                  {error && <div className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{error}</div>}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-zinc-600 mb-1.5">Your name *</label>
                      <input value={name} onChange={(e) => setName(e.target.value)} required className={field} />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-600 mb-1.5">Email *</label>
                      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className={field} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Branch *</label>
                    <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                      <option value="">Select branch…</option>
                      {branchOptions.map((b) => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Subject *</label>
                    <input value={title} onChange={(e) => setTitle(e.target.value)} required className={field} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Details</label>
                    <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} className={field} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Priority</label>
                    <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className={field}>
                      {(['low', 'medium', 'high', 'critical'] as Priority[]).map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <button type="submit" disabled={saving} className={btnPrimary}>{saving ? 'Submitting…' : 'Submit Ticket'}</button>
                </form>"""

new_form = """                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3.5">
                  {error && <div className="text-sm text-rose-600 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 px-3 py-2 rounded-lg">{error}</div>}
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Your name *</label>
                    <input value={name} onChange={(e) => setName(e.target.value)} required className={field} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Branch *</label>
                    <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                      <option value="">Select branch…</option>
                      {branchOptions.map((b) => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Subject *</label>
                    <select value={title} onChange={(e) => setTitle(e.target.value)} required className={field}>
                      <option value="">Select a request type…</option>
                      {SUBJECT_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Choose the closest match — you can clarify in Details.</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Details</label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={4}
                      placeholder="Describe what happened, steps to reproduce, and any error messages…"
                      className={field}
                    />
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <label className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-violet-700 dark:text-violet-300 bg-violet-500/10 hover:bg-violet-500/15 border border-violet-500/20 cursor-pointer transition-colors">
                        <ImagePlus size={14} />
                        {attachPreview ? 'Change photo' : 'Add photo'}
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            e.target.value = '';
                            setAttachError('');
                            if (!file) return;
                            if (!file.type.startsWith('image/')) {
                              setAttachError('Please choose an image file.');
                              return;
                            }
                            if (file.size > MAX_ATTACHMENT_BYTES) {
                              setAttachError('Image is too large (max 8 MB).');
                              return;
                            }
                            const reader = new FileReader();
                            reader.onload = () => {
                              setAttachPreview({
                                name: file.name,
                                size: file.size,
                                mime: file.type,
                                url: String(reader.result || ''),
                              });
                            };
                            reader.onerror = () => setAttachError('Could not read that image.');
                            reader.readAsDataURL(file);
                          }}
                        />
                      </label>
                      <span className="text-[11px] text-zinc-500 dark:text-zinc-400">Optional · max 8 MB</span>
                      {attachPreview && (
                        <button
                          type="button"
                          onClick={() => { setAttachPreview(null); setAttachError(''); }}
                          className="inline-flex items-center gap-1 text-[11px] text-zinc-600 dark:text-zinc-300 hover:text-rose-600"
                        >
                          <X size={12} /> Remove
                        </button>
                      )}
                    </div>
                    {attachError && <p className="text-[11px] text-rose-600 mt-1">{attachError}</p>}
                    {attachPreview && (
                      <div className="mt-2 rounded-lg overflow-hidden border border-zinc-200 dark:border-white/10 max-w-xs">
                        <img src={attachPreview.url} alt={attachPreview.name} className="max-h-36 w-full object-contain bg-black/5" />
                        <div className="px-2 py-1 text-[10px] text-zinc-500 truncate">{attachPreview.name}</div>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Priority</label>
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
                  </div>
                  <button type="submit" disabled={saving} className={btnPrimary}>{saving ? 'Submitting…' : 'Submit Ticket'}</button>
                </form>"""

if old_form in c:
    c = c.replace(old_form, new_form, 1)
    print("form ok")
else:
    print("form miss")

if "/* submit-form-v1 */" not in c:
    c = c.replace(
        "/* labels-titlecase-v1 */",
        "/* labels-titlecase-v1 */ /* submit-form-v1 */",
        1,
    )
    if "submit-form-v1" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* submit-form-v1 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("done")
