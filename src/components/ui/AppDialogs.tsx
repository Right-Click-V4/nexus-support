/* nexus-app-dialogs-v1 — custom confirm modal + toasts (replaces native browser dialogs) */
import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from 'lucide-react';
import clsx from 'clsx';
import {
  subscribeDialogs,
  resolveConfirm,
  dismissToast,
  type ConfirmOptions,
  getDialogState,
} from '../../lib/dialogs';

export default function AppDialogs() {
  const [confirm, setConfirm] = useState(getDialogState().confirm);
  const [toasts, setToasts] = useState(getDialogState().toasts);

  useEffect(() => {
    return subscribeDialogs((s) => {
      setConfirm(s.confirm);
      setToasts(s.toasts);
    });
  }, []);

  return (
    <>
      {confirm && <ConfirmModal {...confirm} />}
      <ToastStack toasts={toasts} />
    </>
  );
}

function ConfirmModal({
  title,
  message,
  confirmLabel = 'OK',
  cancelLabel = 'Cancel',
  variant = 'default',
}: ConfirmOptions & { id: string; resolve: (ok: boolean) => void }) {
  const danger = variant === 'danger';

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') resolveConfirm(false);
      if (e.key === 'Enter') resolveConfirm(true);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="nexus-confirm-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-black/45 dark:bg-black/60 backdrop-blur-[6px]"
        aria-label="Dismiss"
        onClick={() => resolveConfirm(false)}
      />
      <div className="relative w-full max-w-[400px] rounded-2xl border border-zinc-200/90 dark:border-white/12 bg-white dark:bg-zinc-900 shadow-2xl shadow-black/25 dark:shadow-black/50 overflow-hidden">
        <div
          className={clsx(
            'h-1 w-full',
            danger
              ? 'bg-gradient-to-r from-rose-500 via-rose-400 to-orange-400'
              : 'bg-gradient-to-r from-violet-500 via-fuchsia-500 to-brand-400',
          )}
        />
        <div className="p-5 sm:p-6">
          <div className="flex gap-4">
            <div
              className={clsx(
                'shrink-0 w-11 h-11 rounded-xl flex items-center justify-center ring-1',
                danger
                  ? 'bg-rose-500/15 text-rose-500 ring-rose-500/25'
                  : 'bg-violet-500/15 text-violet-500 dark:text-violet-300 ring-violet-500/25',
              )}
            >
              {danger ? <AlertTriangle size={22} /> : <Info size={22} />}
            </div>
            <div className="min-w-0 flex-1 pt-0.5">
              <h2
                id="nexus-confirm-title"
                className="text-[15px] font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight"
              >
                {title}
              </h2>
              <p className="mt-1.5 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap">
                {message}
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={() => resolveConfirm(false)}
              className="px-4 py-2 rounded-xl text-sm font-medium border border-zinc-200 dark:border-white/12 text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5 transition-colors"
            >
              {cancelLabel}
            </button>
            <button
              type="button"
              onClick={() => resolveConfirm(true)}
              autoFocus
              className={clsx(
                'px-4 py-2 rounded-xl text-sm font-semibold text-white shadow-sm transition-colors',
                danger
                  ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/25'
                  : 'bg-violet-600 hover:bg-violet-500 shadow-violet-600/25',
              )}
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ToastStack({
  toasts,
}: {
  toasts: { id: string; message: string; variant?: string }[];
}) {
  if (!toasts.length) return null;
  return (
    <div className="fixed top-4 right-4 z-[10000] flex flex-col gap-2 w-[min(100vw-2rem,360px)] pointer-events-none">
      {toasts.map((t) => (
        <ToastCard key={t.id} {...t} />
      ))}
    </div>
  );
}

function ToastCard({
  id,
  message,
  variant = 'info',
}: {
  id: string;
  message: string;
  variant?: string;
}) {
  const icon =
    variant === 'success' ? (
      <CheckCircle2 size={18} className="text-emerald-500" />
    ) : variant === 'error' ? (
      <XCircle size={18} className="text-rose-500" />
    ) : variant === 'warning' ? (
      <AlertTriangle size={18} className="text-amber-500" />
    ) : (
      <Info size={18} className="text-violet-500" />
    );

  const ring =
    variant === 'success'
      ? 'border-emerald-500/25'
      : variant === 'error'
        ? 'border-rose-500/25'
        : variant === 'warning'
          ? 'border-amber-500/25'
          : 'border-violet-500/25';

  return (
    <div
      className={clsx(
        'pointer-events-auto flex items-start gap-3 rounded-2xl border bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md px-4 py-3 shadow-xl shadow-black/10 dark:shadow-black/40',
        ring,
      )}
      role="status"
    >
      <div className="mt-0.5 shrink-0">{icon}</div>
      <p className="flex-1 text-sm text-zinc-800 dark:text-zinc-100 leading-snug">{message}</p>
      <button
        type="button"
        onClick={() => dismissToast(id)}
        className="shrink-0 p-1 rounded-lg text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-white/10"
        aria-label="Dismiss"
      >
        <X size={14} />
      </button>
    </div>
  );
}
