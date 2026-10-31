#!/usr/bin/env python3
"""Wire Account panel + compact Help CTA + sidebar avatar into CustomerPortal. SAFE."""
from pathlib import Path
import re

p = Path('src/components/CustomerPortal.tsx')
cp = p.read_text()

if 'PortalLiveChat' not in cp or len(cp) < 50000:
    print('SKIP wire: CustomerPortal missing or too small', len(cp))
    raise SystemExit(0)

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
    print('displayName ok')

if 'const [sidebarAvatar' not in cp and 'avatarUrlMeta' in cp:
    inject = """
  const [sidebarAvatar, setSidebarAvatar] = useState(avatarUrlMeta || '');
  useEffect(() => {
    setSidebarAvatar(avatarUrlMeta || '');
  }, [avatarUrlMeta]);
  useEffect(() => {
    const onUpd = (e: Event) => {
      const d = (e as CustomEvent).detail as { avatar_url?: string | null } | undefined;
      if (d && d.avatar_url) setSidebarAvatar(d.avatar_url);
      else if (typeof localStorage !== 'undefined') {
        const local = localStorage.getItem('nexus-portal-avatar');
        if (local) setSidebarAvatar(local);
      }
    };
    window.addEventListener('nexus-profile-updated', onUpd);
    return () => window.removeEventListener('nexus-profile-updated', onUpd);
  }, []);
"""
    marker = "    (typeof localStorage !== 'undefined' ? localStorage.getItem('nexus-portal-avatar') || '' : '');"
    if marker in cp:
        cp = cp.replace(marker, marker + inject, 1)
        print('sidebar avatar state ok')

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
    print('account panel ok')

old_side = (
    '            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 '
    'flex items-center justify-center text-white text-xs font-semibold shrink-0">\n'
    '              {initials}\n'
    '            </div>'
)
new_side = (
    '            {sidebarAvatar ? (\n'
    '              <img src={sidebarAvatar} alt="" className="w-9 h-9 rounded-full object-cover shrink-0 ring-1 ring-white/20" />\n'
    '            ) : (\n'
    '              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-xs font-semibold shrink-0">\n'
    '                {initials}\n'
    '              </div>\n'
    '            )}'
)
if old_side in cp:
    cp = cp.replace(old_side, new_side, 1)
    print('sidebar avatar UI ok')
else:
    print('sidebar pattern not found / already patched')

old_cta = (
    '                <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">\n'
    '                  <div className="flex items-center gap-2 mb-2">\n'
    '                    <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center"><LifeBuoy size={16} /></div>\n'
    '                    <div>\n'
    '                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>\n'
    '                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400">We are here when self-serve is not enough</p>\n'
    '                    </div>\n'
    '                  </div>\n'
    '                  <div className="flex flex-wrap gap-2">'
)
new_cta = (
    '                <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-4 max-w-xl mx-auto text-center">\n'
    '                  <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Still need help?</h2>\n'
    '                  <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5 mb-3">We are here when self-serve is not enough</p>\n'
    '                  <div className="flex flex-wrap justify-center gap-2">'
)
if old_cta in cp:
    cp = cp.replace(old_cta, new_cta, 1)
    print('CTA compact applied')
else:
    print('CTA already updated or pattern differs')

for v in ("view === 'submit'", "view === 'help'", "view === 'mytickets'", 'PortalLiveChat', 'HELP_ARTICLES'):
    if v not in cp:
        print('ABORT: missing', v, '— not writing')
        raise SystemExit(1)
if len(cp) < 90000:
    print('ABORT: file too small', len(cp))
    raise SystemExit(1)

p.write_text(cp)
print('CP wired OK', len(cp), 'AccountProfilePanel' in cp, 'sidebarAvatar' in cp)
