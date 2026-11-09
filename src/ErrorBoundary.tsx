/* error-boundary-unlock-v6 — keep customized monster 404; show real error on top */
import { Component, type ReactNode } from 'react';
import NotFoundScreen from './components/NotFoundScreen';

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

  private goLogin = () => {
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
        <div style={{ position: 'relative', minHeight: '100vh' }}>
          <NotFoundScreen onGoHome={this.goLogin} onAdminSignIn={this.goLogin} />
          {/* Real crash reason — above the art so we can fix it */}
          <div
            style={{
              position: 'fixed',
              left: 0,
              right: 0,
              bottom: 24,
              zIndex: 9999,
              display: 'flex',
              justifyContent: 'center',
              pointerEvents: 'none',
              padding: '0 16px',
            }}
          >
            <pre
              style={{
                maxWidth: 560,
                width: '100%',
                margin: 0,
                fontSize: 11,
                lineHeight: 1.4,
                color: '#fecdd3',
                background: 'rgba(0,0,0,0.75)',
                border: '1px solid rgba(251,113,133,0.4)',
                borderRadius: 12,
                padding: '10px 14px',
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                pointerEvents: 'auto',
              }}
            >
              {msg}
            </pre>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
