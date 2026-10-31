/* error-boundary-404-only-v1 */
import { Component, type ReactNode } from 'react';
import NotFoundScreen from './components/NotFoundScreen';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/** Any uncaught render error → branded 404 UI (no reload / debug options). */
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
    try {
      if (!window.location.hash.includes('404')) {
        window.location.hash = '#/404';
      }
    } catch {
      /* ignore */
    }
  }

  render() {
    if (this.state.error) {
      return (
        <NotFoundScreen
          onGoHome={() => {
            this.setState({ error: null });
            try {
              window.location.hash = '#/';
              window.location.reload();
            } catch {
              window.location.href = '/';
            }
          }}
        />
      );
    }
    return this.props.children;
  }
}
