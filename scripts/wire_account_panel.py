#!/usr/bin/env python3
from pathlib import Path
import re

p = Path('src/components/CustomerPortal.tsx')
cp = p.read_text()

if 'AccountProfilePanel' not in cp:
    cp = cp.replace(
        "import PortalSpaceLoungeBg from './PortalSpaceLoungeBg';",
        "import PortalSpaceLoungeBg from './PortalSpaceLoungeBg';\nimport AccountProfilePanel from './AccountProfilePanel';",
    )

cp = cp.replace(
    'const { user, accountRole, signOut, requiresAuth } = useAuth();',
    'const { user, accountRole, signOut, requiresAuth, updateProfile, updatePassword } = useAuth();',
)

old_dn = """  const displayName =
    (user?.user_metadata?.full_name as string) || user?.email?.split('@')[0] || 'Customer';
  const initials = displayName.slice(0, 2).toUpperCase();"""
new_dn = """  const legalName =
    (user?.user_metadata?.full_name as string | undefined)?.trim() ||
    (user?.user_metadata?.name as string | undefined)?.trim() ||
    user?.email?.split('@')[0] ||
    'Customer';
  const nicknameMeta = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';
  const displayName = nicknameMeta ? `${legalName} (${nicknameMeta})` : legalName;
  const initials = legalName.slice(0, 2).toUpperCase();
  const avatarUrlMeta =
    (user?.user_metadata?.avatar_url as string | undefined) ||
    (typeof localStorage !== 'undefined' ? localStorage.getItem('nexus-portal-avatar') || '' : '');"""
if old_dn in cp:
    cp = cp.replace(old_dn, new_dn)

acc_pat = re.compile(r"\{view === 'account' && \([\s\S]*?\n            \)\}", re.M)
acc_new = """{view === 'account' && (
              <AccountProfilePanel
                legalName={legalName}
                email={user?.email || ''}
                initials={initials}
                avatarUrl={avatarUrlMeta || ''}
                nickname={nicknameMeta}
                phone={(user?.user_metadata?.phone as string | undefined) || ''}
                jobTitle={(user?.user_metadata?.job_title as string | undefined) || ''}
                requiresAuth={requiresAuth}
                onSignOut={() => void signOut()}
                updateProfile={updateProfile}
                updatePassword={updatePassword}
              />
            )}"""
m = acc_pat.search(cp)
if m:
    cp = cp[: m.start()] + acc_new + cp[m.end() :]

old_cta = """                <section className=\"portal-overview-glass rounded-2xl p-4 sm:p-5\">
                  <div className=\"flex items-center gap-2 mb-2\">
                    <div className=\"w-8 h-8 rounded-lg bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center\"><LifeBuoy size={16} /></div>
                    <div>
                      <h2 className=\"text-sm font-semibold text-zinc-900 dark:text-zinc-50\">Still need help?</h2>
                      <p className=\"text-[11px] text-zinc-600 dark:text-zinc-400\">We are here when self-serve is not enough</p>
                    </div>
                  </div>
                  <div className=\"flex flex-wrap gap-2\">"""
new_cta = """                <section className=\"portal-overview-glass rounded-2xl p-5 sm:p-6 max-w-xl mx-auto text-center\">
                  <div className=\"flex flex-col items-center gap-2 mb-3\">
                    <div className=\"w-10 h-10 rounded-xl bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center\"><LifeBuoy size={18} /></div>
                    <div>
                      <h2 className=\"text-sm font-semibold text-zinc-900 dark:text-zinc-50\">Still need help?</h2>
                      <p className=\"text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5\">We are here when self-serve is not enough</p>
                    </div>
                  </div>
                  <div className=\"flex flex-wrap justify-center gap-2\">"""
if old_cta in cp:
    cp = cp.replace(old_cta, new_cta)

p.write_text(cp)
print('CP wired', 'AccountProfilePanel' in cp, 'max-w-xl mx-auto' in cp)

panel = Path('src/components/AccountProfilePanel.tsx')
if panel.exists():
    t = panel.read_text()
    # Fix broken className: space or backslash before {email}
    t = re.sub(r'truncate\\?\s*\{email\}', 'truncate' + chr(123) + 'email' + chr(125), t)
    panel.write_text(t)
    print('panel email line fixed')
