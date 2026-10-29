/* create-ticket-portal-layout-v1 */
import { useState, useMemo } from 'react';
import { X } from 'lucide-react';
import { useTickets } from '../context/TicketContext';
import type { Priority, Channel } from '../types';

interface Props {
  onClose: () => void;
}

const BRANCH_OPTIONS = [
  'Abucay',
  'Abuyog',
  'Avenida',
  'Baybay',
  'Burauen',
  'Calbayog',
  'Carigara',
  'Catarman',
  'Catbalogan',
  'Kananga',
  'Maasin',
  'Ormoc',
  'Palo-Naga',
  'Palo-Pawing',
  'Palo-Schisto',
  'Sogod',
] as const;

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
] as const;

function capitalizeSentences(text: string): string {
  return text.replace(/(^|[.!?]\s+)([a-z])/g, (_, a, b) => a + b.toUpperCase());
}

const field =
  'w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-white/15 bg-white dark:bg-zinc-900/80 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400';

export default function CreateTicketModal({ onClose }: Props) {
  const { createTicket, agents } = useTickets();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority | ''>('');
  const [channel, setChannel] = useState<Channel>('email');
  const [customer, setCustomer] = useState('');
  const [email, setEmail] = useState('');
  const [branch, setBranch] = useState('');
  const [assigneeId, setAssigneeId] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const branchOptions = useMemo(() => {
    const set = new Set<string>([...BRANCH_OPTIONS]);
    try {
      const raw = localStorage.getItem('nexus-branches-v1');
      if (raw) {
        (JSON.parse(raw) as { name: string }[]).forEach((b) => set.add(b.name));
      }
    } catch {}
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !customer.trim() || !branch.trim() || !priority) {
      setError('Contact name, branch, subject, and priority are required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createTicket({
        title: title.trim(),
        description: capitalizeSentences(description.trim()),
        priority: priority as Priority,
        channel,
        customer_name: customer.trim(),
        customer_email: email.trim() || undefined,
        branch: branch.trim(),
        assignee_id: assigneeId || undefined,
      });
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create ticket';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-[2px]">
      <div className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-200 dark:border-white/12 bg-white dark:bg-zinc-950 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-white/10 sticky top-0 bg-white/95 dark:bg-zinc-950/95 backdrop-blur-sm z-10">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-50">New Ticket</h2>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">Same fields as Customer Portal · Channel & Assignee included</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-white/10"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && (
            <div className="text-sm text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-500/30 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Contact name *</label>
            <input
              value={customer}
              onChange={(e) => setCustomer(e.target.value)}
              required
              className={field}
              placeholder="Person who reported"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={field}
              placeholder="customer@email.com"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Branch *</label>
            <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
              <option value="" disabled>
                Select branch…
              </option>
              {branchOptions.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Subject *</label>
            <select value={title} onChange={(e) => setTitle(e.target.value)} required className={field}>
              <option value="" disabled>
                Select a request type…
              </option>
              {SUBJECT_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Choose the closest match — clarify in Details.</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Details</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(capitalizeSentences(e.target.value))}
              onBlur={(e) => setDescription(capitalizeSentences(e.target.value))}
              rows={4}
              placeholder="Describe the issue, steps to reproduce, or what you need…"
              className={field + ' resize-y min-h-[96px]'}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Priority *</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority | '')}
              required
              className={field}
            >
              <option value="" disabled>
                Select priority…
              </option>
              {(
                [
                  { value: 'low', label: 'Low' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'high', label: 'High' },
                  { value: 'critical', label: 'Critical' },
                ] as { value: Priority; label: string }[]
              ).map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Channel</label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value as Channel)}
                className={field}
              >
                <option value="email">Email</option>
                <option value="portal">Portal</option>
                <option value="phone">Phone</option>
                <option value="chat">Chat</option>
                <option value="social">Social</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Assignee</label>
              <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} className={field}>
                <option value="">Unassigned</option>
                {agents.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} ({a.role})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-white/10">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2.5 text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 rounded-lg disabled:opacity-50 shadow-sm"
            >
              {saving ? 'Creating…' : 'Create Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
