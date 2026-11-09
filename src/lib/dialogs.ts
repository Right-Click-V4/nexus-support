/** Imperative confirm + toast API (replaces window.confirm / alert). */

export type ConfirmOptions = {
  title?: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  /** danger = rose destructive button */
  variant?: 'danger' | 'default';
};

export type ToastOptions = {
  message: string;
  variant?: 'info' | 'success' | 'error' | 'warning';
  durationMs?: number;
};

type ConfirmRequest = ConfirmOptions & {
  id: string;
  resolve: (ok: boolean) => void;
};

type ToastItem = ToastOptions & { id: string };

type DialogState = {
  confirm: ConfirmRequest | null;
  toasts: ToastItem[];
};

type Listener = (s: DialogState) => void;

let state: DialogState = { confirm: null, toasts: [] };
const listeners = new Set<Listener>();

function emit() {
  const snap = { ...state, toasts: [...state.toasts] };
  listeners.forEach((l) => l(snap));
}

export function subscribeDialogs(fn: Listener): () => void {
  listeners.add(fn);
  fn(state);
  return () => listeners.delete(fn);
}

export function getDialogState(): DialogState {
  return state;
}

/** Styled replacement for window.confirm */
export function appConfirm(opts: ConfirmOptions | string): Promise<boolean> {
  const options: ConfirmOptions = typeof opts === 'string' ? { message: opts } : opts;
  return new Promise((resolve) => {
    const id = `c-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    state = {
      ...state,
      confirm: {
        id,
        title: options.title || (options.variant === 'danger' ? 'Please confirm' : 'Confirm'),
        message: options.message,
        confirmLabel: options.confirmLabel || (options.variant === 'danger' ? 'Delete' : 'OK'),
        cancelLabel: options.cancelLabel || 'Cancel',
        variant: options.variant || 'default',
        resolve,
      },
    };
    emit();
  });
}

export function resolveConfirm(ok: boolean) {
  const req = state.confirm;
  if (!req) return;
  state = { ...state, confirm: null };
  emit();
  req.resolve(ok);
}

/** Styled replacement for window.alert */
export function appToast(opts: ToastOptions | string) {
  const options: ToastOptions = typeof opts === 'string' ? { message: opts } : opts;
  const id = `t-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const item: ToastItem = {
    id,
    message: options.message,
    variant: options.variant || 'info',
    durationMs: options.durationMs ?? 4200,
  };
  state = { ...state, toasts: [...state.toasts, item] };
  emit();
  const ms = item.durationMs ?? 4200;
  window.setTimeout(() => dismissToast(id), ms);
  return id;
}

export function dismissToast(id: string) {
  state = { ...state, toasts: state.toasts.filter((t) => t.id !== id) };
  emit();
}

/** Drop-in async helpers matching browser API shapes */
export async function confirmAsync(message: string): Promise<boolean> {
  return appConfirm({ message, variant: 'danger' });
}

export function alertAsync(message: string) {
  appToast({ message, variant: 'error' });
}
