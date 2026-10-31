/* error-boundary-404-only-v2 */
import { Component, type ReactNode } from 'react';
import NotFoundScreen from './components/NotFoundScreen';

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

  componentDidCatch(error: Error) {
    try {
      console.error('[NexusOps]', error);
    } catch {}
  }

  private goLogin = () => {
    this.setState({ error: null });
    try {
      window.location.hash = '#/';
      window.location.reload();
    } catch {
      window.location.href = '/';
    }
  };

  render() {
    if (this.state.error) {
      return <NotFoundScreen onGoHome={this.goLogin} />;
    }
    return this.props.children;
  }
}
