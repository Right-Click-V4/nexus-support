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

# Compact Still need help — no icon, thinner
new_cta = (
    '                <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-4 max-w-xl mx-auto text-center">\n'
    '                  <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>\n'
    '                  <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5 mb-3">We are here when self-serve is not enough</p>\n'
    '                  <div className="flex flex-wrap justify-center gap-2">'
)
cta_pat = re.compile(
    r'<section className="portal-overview-glass rounded-2xl[^>]*>[\s\S]*?<h2[^>]*>Still need help\?</h2>[\s\S]*?<div className="flex flex-wrap[^>]*>',
    re.M,
)
m2 = cta_pat.search(cp)
if m2:
    cp = cp[: m2.start()] + new_cta + cp[m2.end() :]
    print('CTA compact no-icon')
else:
    print('CTA pattern not found')

p.write_text(cp)
print('CP wired', 'AccountProfilePanel' in cp)

panel = Path('src/components/AccountProfilePanel.tsx')
if panel.exists():
    t = panel.read_text()
    out = []
    for line in t.splitlines():
        if 'truncate' in line and 'email' in line and 'className' in line:
            out.append('              <div className="text-sm text-zinc-600 dark:text-zinc-400 truncate">{email}</div>')
        else:
            out.append(line)
    panel.write_text('\n'.join(out) + ('\n' if t.endswith('\n') else ''))
    print('panel email line normalized')
