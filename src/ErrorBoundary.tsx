/* error-boundary-404-only-v2 */
import { Component, type ReactNode } from 'react';
import NotFoundScreen from './components/NotFoundScreen';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/**
 * Uncaught errors → branded 404 UI (no debug/reload buttons).
 * We do NOT force location.hash to #/404, so a full refresh can boot
 * cleanly to the login page once the app is healthy again.
 * If the underlying bug is still present, the error fires again → 404 again.
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error) {
    try {
      console.error('[NexusOps]', error);
    } catch {
      /* ignore */
    }
  }

  private goLogin = () => {
    this.setState({ error: null });
    try {
      window.location.hash = '#/';
      window.location.reload();
    } catch {
      try {
        window.location.href = '/';
      } catch {
        /* ignore */
      }
    }
  };

  render() {
    if (this.state.error) {
      return <NotFoundScreen onGoHome={this.goLogin} />;
    }
    return this.props.children;
  }
}
