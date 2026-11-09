/* error-boundary-unlock-v5 — never trap users on 404; always offer login */
import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

function clearLocks() {
  try {
    localStorage.setItem('nexus-site-404-on', '0');
    localStorage.removeItem('nexus-site-404-on');
  } catch { /* ignore */ }
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error) {
    try {
      console.error('[NexusOps]', error);
    } catch { /* ignore */ }
  }

  private recover = () => {
    this.setState({ error: null });
    clearLocks();
    try {
      window.location.hash = '';
      const base = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL || '/';
      window.location.replace(base + '?recover=' + Date.now());
    } catch {
      try {
        window.location.href = '/nexus-support/?recover=' + Date.now();
      } catch {
        window.location.reload();
      }
    }
  };

  render() {
    if (this.state.error) {
      const msg = this.state.error?.message || String(this.state.error);
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            padding: 24,
            background: '#070414',
            color: '#f5f3ff',
            fontFamily: 'system-ui, sans-serif',
          }}
        >
          <div style={{ fontSize: 13, opacity: 0.7 }}>Something went wrong loading the app</div>
          <pre
            style={{
              maxWidth: 520,
              width: '100%',
              fontSize: 11,
              color: '#fda4af',
              background: 'rgba(0,0,0,0.45)',
              border: '1px solid rgba(251,113,133,0.35)',
              borderRadius: 12,
              padding: 12,
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
            }}
          >
            {msg}
          </pre>
          <button
            type="button"
            onClick={this.recover}
            style={{
              padding: '10px 22px',
              borderRadius: 999,
              border: '1px solid rgba(167,139,250,0.5)',
              background: 'linear-gradient(180deg,#7c3aed,#5b21b6)',
              color: '#fff',
              fontWeight: 600,
              fontSize: 14,
              cursor: 'pointer',
            }}
          >
            Reload login
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
