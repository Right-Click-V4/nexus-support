/* error-boundary-unlock-v3 */
import { Component, type ReactNode } from 'react';
import NotFoundScreen from './components/NotFoundScreen';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

function clear404Lock() {
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
    clear404Lock();
    try {
      window.location.hash = '';
      const base = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL || '/';
      window.location.replace(base);
    } catch {
      try { window.location.href = '/nexus-support/'; } catch { window.location.href = '/'; }
    }
  };

  render() {
    if (this.state.error) {
      return <NotFoundScreen onGoHome={this.goLogin} onAdminSignIn={this.goLogin} />;
    }
    return this.props.children;
  }
}
