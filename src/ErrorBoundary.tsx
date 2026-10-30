/* error-boundary-portal-v1 */
import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, background: '#0b0618', fontFamily: 'system-ui' }}>
          <div style={{ maxWidth: 480, width: '100%', textAlign: 'center' }}>
            <div style={{ fontSize: 13, letterSpacing: 0.08, color: '#a78bfa', marginBottom: 12, textTransform: 'uppercase' as const }}>Something went wrong</div>
            <pre style={{ background: 'rgba(254,242,242,0.95)', color: '#991b1b', padding: 16, borderRadius: 12, fontSize: 13, overflow: 'auto', textAlign: 'left' }}>
              {this.state.error.message}
            </pre>
            <p style={{ color: '#a1a1aa', fontSize: 13, marginTop: 12 }}>
              Reload the portal, or open the home screen if this keeps happening.
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: 16, flexWrap: 'wrap' as const }}>
              <button
                type="button"
                onClick={() => {
                  this.setState({ error: null });
                  const h = (window.location.hash || '').toLowerCase();
                  if (h.includes('agent')) window.location.hash = '#/agent';
                  else window.location.hash = '#/portal';
                  window.location.reload();
                }}
                style={{ padding: '10px 18px', background: '#7c3aed', color: '#fff', border: 'none', borderRadius: 10, cursor: 'pointer', fontWeight: 600 }}
              >
                Reload app
              </button>
              <button
                type="button"
                onClick={() => {
                  this.setState({ error: null });
                  window.location.hash = '#/';
                  window.location.reload();
                }}
                style={{ padding: '10px 18px', background: 'transparent', color: '#e4e4e7', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 10, cursor: 'pointer' }}
              >
                Go to home / 404 screen
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
