import { useEffect, useState } from 'react';
import { useMaintenance } from '../context/MaintenanceContext';
import { useSite404 } from '../context/Site404Context';
import { useBranding } from '../context/BrandingContext';
import { uploadAttachment } from '../lib/storage';
import { DEFAULT_BRANDING } from '../lib/branding';

export default function AdminFeaturesPage() {
  const { enabled: maintOn, saving: maintSaving, error: maintError, setEnabled: setMaint } = useMaintenance();
  const { enabled: site404On, saving: site404Saving, error: site404Error, setEnabled: setSite404 } = useSite404();
  const { branding, saving: brandSaving, error: brandError, updateBranding } = useBranding();

  const [appName, setAppName] = useState(branding.appName);
  const [primaryColor, setPrimaryColor] = useState(branding.primaryColor);
  const [logoUrl, setLogoUrl] = useState(branding.logoUrl);
  const [faviconUrl, setFaviconUrl] = useState(branding.faviconUrl);
  const [maintenanceMessage, setMaintenanceMessage] = useState(branding.maintenanceMessage);
  const [uploading, setUploading] = useState<'logo' | 'favicon' | null>(null);
  const [localMsg, setLocalMsg] = useState<string | null>(null);

  useEffect(() => {
    setAppName(branding.appName);
    setPrimaryColor(branding.primaryColor);
    setLogoUrl(branding.logoUrl);
    setFaviconUrl(branding.faviconUrl);
    setMaintenanceMessage(branding.maintenanceMessage);
  }, [branding]);

  const saveBranding = async () => {
    setLocalMsg(null);
    await updateBranding({
      appName: appName.trim() || DEFAULT_BRANDING.appName,
      primaryColor,
      logoUrl: logoUrl.trim(),
      faviconUrl: faviconUrl.trim(),
      maintenanceMessage: maintenanceMessage.trim() || DEFAULT_BRANDING.maintenanceMessage,
    });
    setLocalMsg('Branding saved');
  };

  const onUpload = async (kind: 'logo' | 'favicon', file: File) => {
    setUploading(kind);
    setLocalMsg(null);
    try {
      const up = await uploadAttachment(file, 'branding');
      if (kind === 'logo') {
        setLogoUrl(up.url);
        await updateBranding({ logoUrl: up.url });
      } else {
        setFaviconUrl(up.url);
        await updateBranding({ faviconUrl: up.url });
      }
      setLocalMsg(kind === 'logo' ? 'Logo updated' : 'Favicon updated');
    } catch (e) {
      setLocalMsg(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setUploading(null);
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex flex-col gap-4 w-full max-w-3xl mx-auto pb-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Admin features</h2>
        <p className="text-sm text-slate-500 mt-1">
          Controls that only administrators can change. Agents and customers cannot open this page.
        </p>
      </div>

      {/* System modes */}
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

      {/* Maintenance message */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">Maintenance message</div>
          <p className="text-sm text-slate-500 mt-1">
            Text shown under the maintenance artwork (e.g. “Back at 4 PM PST”). Saves with branding and updates in realtime.
          </p>
        </div>
        <textarea
          value={maintenanceMessage}
          onChange={(e) => setMaintenanceMessage(e.target.value)}
          rows={3}
          className="w-full px-3 py-2.5 text-sm border border-slate-200 rounded-xl"
          placeholder={DEFAULT_BRANDING.maintenanceMessage}
        />
        <button
          type="button"
          disabled={brandSaving}
          onClick={() =>
            void updateBranding({
              maintenanceMessage: maintenanceMessage.trim() || DEFAULT_BRANDING.maintenanceMessage,
            }).then(() => setLocalMsg('Maintenance message saved'))
          }
          className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 disabled:opacity-50"
        >
          {brandSaving ? 'Saving…' : 'Save message'}
        </button>
      </div>

      {/* Branding kit */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div>
          <div className="text-sm font-semibold text-slate-900">Branding kit</div>
          <p className="text-sm text-slate-500 mt-1">
            Logo, favicon, app name, and primary purple. Applies across the agent workspace in realtime.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-slate-500">App name</label>
            <input
              value={appName}
              onChange={(e) => setAppName(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg mt-1"
              placeholder="Nexus Ops"
            />
          </div>
          <div>
            <label className="text-xs text-slate-500">Primary color</label>
            <div className="flex items-center gap-2 mt-1">
              <input
                type="color"
                value={/^#[0-9a-fA-F]{6}$/.test(primaryColor) ? primaryColor : '#8b5cf6'}
                onChange={(e) => setPrimaryColor(e.target.value)}
                className="h-10 w-12 rounded border border-slate-200 cursor-pointer bg-transparent"
              />
              <input
                value={primaryColor}
                onChange={(e) => setPrimaryColor(e.target.value)}
                className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg font-mono"
                placeholder="#8b5cf6"
              />
            </div>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500">Logo</label>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-center overflow-hidden shrink-0">
                {logoUrl ? (
                  <img src={logoUrl} alt="Logo" className="w-full h-full object-contain" />
                ) : (
                  <span className="text-[10px] text-slate-400">None</span>
                )}
              </div>
              <div className="flex flex-col gap-1 min-w-0">
                <label className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-100 text-slate-700 cursor-pointer hover:bg-slate-200 w-fit">
                  {uploading === 'logo' ? 'Uploading…' : 'Upload logo'}
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    disabled={!!uploading}
                    onChange={(e) => e.target.files?.[0] && void onUpload('logo', e.target.files[0])}
                  />
                </label>
                {logoUrl && (
                  <button
                    type="button"
                    className="text-[11px] text-rose-500 text-left"
                    onClick={() => {
                      setLogoUrl('');
                      void updateBranding({ logoUrl: '' });
                    }}
                  >
                    Remove logo
                  </button>
                )}
              </div>
            </div>
            <input
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg font-mono"
              placeholder="Or paste logo URL"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-500">Favicon</label>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-center overflow-hidden shrink-0">
                {faviconUrl ? (
                  <img src={faviconUrl} alt="Favicon" className="w-8 h-8 object-contain" />
                ) : (
                  <span className="text-[10px] text-slate-400">Default</span>
                )}
              </div>
              <div className="flex flex-col gap-1 min-w-0">
                <label className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-100 text-slate-700 cursor-pointer hover:bg-slate-200 w-fit">
                  {uploading === 'favicon' ? 'Uploading…' : 'Upload favicon'}
                  <input
                    type="file"
                    accept="image/*,.ico"
                    className="hidden"
                    disabled={!!uploading}
                    onChange={(e) => e.target.files?.[0] && void onUpload('favicon', e.target.files[0])}
                  />
                </label>
                {faviconUrl && (
                  <button
                    type="button"
                    className="text-[11px] text-rose-500 text-left"
                    onClick={() => {
                      setFaviconUrl('');
                      void updateBranding({ faviconUrl: '' });
                    }}
                  >
                    Reset favicon
                  </button>
                )}
              </div>
            </div>
            <input
              value={faviconUrl}
              onChange={(e) => setFaviconUrl(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg font-mono"
              placeholder="Or paste favicon URL"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <button
            type="button"
            disabled={brandSaving}
            onClick={() => void saveBranding()}
            className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 disabled:opacity-50"
          >
            {brandSaving ? 'Saving…' : 'Save branding'}
          </button>
          <button
            type="button"
            disabled={brandSaving}
            onClick={() =>
              void updateBranding({ ...DEFAULT_BRANDING }).then(() => setLocalMsg('Reset to defaults'))
            }
            className="px-4 py-2 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200"
          >
            Reset defaults
          </button>
          {(localMsg || brandError) && (
            <span className={`text-xs ${brandError ? 'text-rose-600' : 'text-emerald-600'}`}>
              {brandError || localMsg}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
