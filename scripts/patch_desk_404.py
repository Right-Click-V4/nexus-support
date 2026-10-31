#!/usr/bin/env python3
"""Ensure ErrorBoundary is 404-only (re-apply if restored)."""
from pathlib import Path

eb = Path("src/ErrorBoundary.tsx")
if eb.exists() and "error-boundary-404-only-v1" not in eb.read_text():
    eb.write_text(
        """/* error-boundary-404-only-v1 */
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
    try {
      if (!window.location.hash.includes('404')) {
        window.location.hash = '#/404';
      }
    } catch {}
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
"""
    )
    print("ErrorBoundary fixed")
else:
    print("ErrorBoundary ok")
