import { useMaintenance } from '../context/MaintenanceContext';
import { useSite404 } from '../context/Site404Context';

export default function AdminFeaturesPage() {
  const { enabled: maintOn, saving: maintSaving, error: maintError, setEnabled: setMaint } = useMaintenance();
  const { enabled: site404On, saving: site404Saving, error: site404Error, setEnabled: setSite404 } = useSite404();

  return (
    <div className="min-h-[calc(100vh-8rem)] flex flex-col gap-4 w-full max-w-3xl mx-auto">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Admin features</h2>
        <p className="text-sm text-slate-500 mt-1">
          Controls that only administrators can change. Agents and customers cannot open this page.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-slate-900">Maintenance mode</div>
          <p className="text-sm text-slate-500 mt-1">
            When on, agents and customers see the maintenance screen. Admins stay signed in and can turn this off.
          </p>
          {maintError && <p className="text-sm text-rose-600 mt-2">{maintError}</p>}
        </div>
        <button
          type="button"
          disabled={maintSaving}
          onClick={() => void setMaint(!maintOn)}
          className={`shrink-0 min-w-[92px] px-4 py-2.5 rounded-lg text-sm font-semibold ${
            maintOn ? 'bg-amber-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
          aria-pressed={maintOn}
        >
          {maintSaving ? 'Saving…' : maintOn ? 'On' : 'Off'}
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-slate-900">404 / Site down mode</div>
          <p className="text-sm text-slate-500 mt-1">
            Force the 404 “station overrun” screen for everyone except admins. Also used automatically for broken or unknown routes.
          </p>
          {site404Error && <p className="text-sm text-rose-600 mt-2">{site404Error}</p>}
        </div>
        <button
          type="button"
          disabled={site404Saving}
          onClick={() => void setSite404(!site404On)}
          className={`shrink-0 min-w-[92px] px-4 py-2.5 rounded-lg text-sm font-semibold ${
            site404On ? 'bg-rose-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
          aria-pressed={site404On}
        >
          {site404Saving ? 'Saving…' : site404On ? 'On' : 'Off'}
        </button>
      </div>

      <div className="flex-1 min-h-[200px] rounded-xl border border-dashed border-violet-400/25 bg-violet-500/5 flex items-center justify-center px-6">
        <p className="text-sm text-slate-500 text-center max-w-md">
          More admin controls can live here — backups, feature flags, and system health.
        </p>
      </div>
    </div>
  );
}
