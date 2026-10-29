/* agent-portal-preview-v1 */
import type { ReactNode } from 'react';
import { useAuth } from '../context/AuthContext';
import LoginPage from './LoginPage';
import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn } from './PostLoginLoader';

interface Props {
  children: ReactNode;
  onOpenAgent?: () => void;
  onBackToAgent?: () => void;
}

/** Agents/admins may open Customer Portal to preview; customers stay portal-only. */
export default function PortalAuthGate({ children, onOpenAgent, onBackToAgent }: Props) {
  const { user, loading, authBusy, requiresAuth, accountRole, configError } = useAuth();
  const goAgent = onOpenAgent || onBackToAgent;

  if (requiresAuth && loading && !authBusy) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal…" />;
  }

  if (requiresAuth && configError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3 bg-[#0c0128] px-4">
        <p className="text-sm text-amber-200 text-center max-w-md">{configError}</p>
        {goAgent && (
          <button type="button" className="text-sm text-fuchsia-300 hover:text-white" onClick={goAgent}>
            Agent workspace →
          </button>
        )}
      </div>
    );
  }

  if (requiresAuth && (!user || authBusy)) {
    return <LoginPage audience="customer" onOpenAgent={goAgent} />;
  }

  return (
    <PostLoginShell
      ready={!requiresAuth || !!user}
      label="Opening customer portal…"
      variant="customer"
    >
      {children}
    </PostLoginShell>
  );
}
