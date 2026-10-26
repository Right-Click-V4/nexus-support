import { useMaintenance } from '../context/MaintenanceContext';

export default function AdminFeaturesPage() {
  const { enabled, saving, error, setEnabled } = useMaintenance();

  return (
    <div className="max-w-xl space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Admin features</h2>
        <p className="text-sm text-slate-500 mt-1">
          Controls that only administrators can change. Agents and customers cannot open this page.
        </p>
      </div>
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex items-center justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-slate-900">Maintenance mode</div>
          <p className="text-sm text-slate-500 mt-1">
            When on, agents and customers see the maintenance screen. Admin accounts stay signed in and can turn this off.
          </p>
          {error && <p className="text-sm text-rose-600 mt-2">{error}</p>}
        </div>
        <button
          type="button"
          disabled={saving}
          onClick={() => void setEnabled(!enabled)}
          className={`shrink-0 min-w-[92px] px-4 py-2 rounded-lg text-sm font-semibold ${
            enabled ? 'bg-amber-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
          aria-pressed={enabled}
        >
          {saving ? 'Saving…' : enabled ? 'On' : 'Off'}
        </button>
      </div>
    </div>
  );
}
