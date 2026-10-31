#!/usr/bin/env python3
"""Error → branded 404; refresh recovers to login when healthy."""
from pathlib import Path

Path("src/ErrorBoundary.tsx").write_text(
    """/* error-boundary-404-only-v2 */
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
"""
)
print("ErrorBoundary")

nf = Path("src/components/NotFoundScreen.tsx")
if nf.exists():
    t = nf.read_text()
    if "onGoHome," not in t.split("function NotFoundScreen")[1][:150]:
        t = t.replace(
            "export default function NotFoundScreen({\n  onAdminSignIn,\n}: {",
            "export default function NotFoundScreen({\n  onAdminSignIn,\n  onGoHome,\n}: {",
            1,
        )
    if "nf-home-btn" not in t:
        t = t.replace(
            '<p className="nf-copy">This page doesn\'t exist — or the station got overrun.</p>',
            '''<p className="nf-copy">This page doesn\'t exist — or the station got overrun.</p>
        <div className="nf-actions">
          {onGoHome ? (
            <button type="button" onClick={onGoHome} className="nf-home-btn">
              Back to login
            </button>
          ) : null}
          {onAdminSignIn ? (
            <button type="button" onClick={onAdminSignIn} className="nf-admin-btn">
              Admin sign in
            </button>
          ) : null}
        </div>''',
            1,
        )
        if ".nf-home-btn" not in t:
            t = t.replace(
                ".nf-admin-btn {",
                ".nf-actions { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin-top:18px; }\n        .nf-home-btn { padding:10px 20px; border-radius:999px; border:1px solid rgba(167,139,250,0.45); background:rgba(124,58,237,0.9); color:#f5f3ff; font-size:13px; font-weight:600; cursor:pointer; }\n        .nf-home-btn:hover { background:rgba(139,92,246,0.95); }\n        .nf-admin-btn {",
                1,
            )
    nf.write_text(t)
    print("NotFoundScreen")
print("done")
