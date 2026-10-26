import { useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import { useAuth } from '../context/AuthContext';

export default function QualityPage() {
  const { reviews, addReview } = usePlatform();
  const { user } = useAuth();
  const [ticketId, setTicketId] = useState('');
  const [agentName, setAgentName] = useState('');
  const [score, setScore] = useState(4);
  const [notes, setNotes] = useState('');

  const avg = reviews.length
    ? (reviews.reduce((s, r) => s + (Number(r.score) || 0), 0) / reviews.length).toFixed(1)
    : '—';

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await addReview({
      ticket_id: ticketId || undefined,
      agent_name: agentName || undefined,
      score,
      notes: notes.trim() || undefined,
      reviewer: (user?.user_metadata?.full_name as string) || user?.email || 'Reviewer',
    });
    setNotes('');
    setTicketId('');
    setAgentName('');
    setScore(4);
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex flex-col gap-4 w-full max-w-5xl mx-auto">
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-card p-6">
        <div className="flex items-center justify-between mb-4 gap-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="text-brand-600" size={20} />
            <h2 className="text-lg font-semibold text-zinc-900">Quality reviews</h2>
          </div>
          <div className="text-sm text-zinc-500">
            Avg score <span className="font-semibold text-zinc-800">{avg}</span>
          </div>
        </div>
        <form onSubmit={submit} className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input
            value={ticketId}
            onChange={(e) => setTicketId(e.target.value)}
            placeholder="Ticket ID"
            className="px-3 py-2.5 text-sm border border-zinc-200 rounded-xl"
          />
          <input
            value={agentName}
            onChange={(e) => setAgentName(e.target.value)}
            placeholder="Agent name"
            className="px-3 py-2.5 text-sm border border-zinc-200 rounded-xl"
          />
          <div>
            <label className="text-xs text-zinc-500">Score (1–5)</label>
            <input
              type="number"
              min={1}
              max={5}
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
              className="w-full px-3 py-2.5 text-sm border border-zinc-200 rounded-xl"
            />
          </div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notes"
            rows={3}
            className="sm:col-span-2 px-3 py-2.5 text-sm border border-zinc-200 rounded-xl"
          />
          <button
            type="submit"
            className="sm:col-span-2 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-xl hover:bg-brand-700"
          >
            Save review
          </button>
        </form>
      </div>

      <div className="bg-white rounded-2xl border border-zinc-200 divide-y divide-zinc-100 flex-1 min-h-[360px]">
        {reviews.map((r) => (
          <div key={r.id} className="px-5 py-4">
            <div className="flex justify-between text-sm gap-3">
              <span className="font-medium text-zinc-800">
                Score {r.score}/5 · {r.agent_name || 'Agent'}
              </span>
              <span className="text-xs text-zinc-400 shrink-0">
                {r.created_at ? new Date(r.created_at).toLocaleString() : '—'}
              </span>
            </div>
            {r.ticket_id && <div className="text-xs text-zinc-500 mt-0.5">{r.ticket_id}</div>}
            {r.notes && <p className="text-sm text-zinc-600 mt-1 whitespace-pre-wrap">{r.notes}</p>}
            <div className="text-[11px] text-zinc-400 mt-1">by {r.reviewer || '—'}</div>
          </div>
        ))}
        {reviews.length === 0 && (
          <p className="p-16 text-center text-sm text-zinc-500">No reviews yet</p>
        )}
      </div>
    </div>
  );
}
