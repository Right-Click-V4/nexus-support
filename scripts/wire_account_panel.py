#!/usr/bin/env python3
"""Wire Account panel + per-email avatar cache + sidebar into CustomerPortal. SAFE."""
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
    'const { user, accountRole, signOut, requiresAuth, updateProfile, updatePassword, updateEmail } = useAuth();',
)
cp = cp.replace(
    'const { user, accountRole, signOut, requiresAuth, updateProfile, updatePassword } = useAuth();',
    'const { user, accountRole, signOut, requiresAuth, updateProfile, updatePassword, updateEmail } = useAuth();',
)

# --- Identity + per-email avatar (never shared localStorage key) ---
old_dn_variants = [
"""  const displayName =
    (user?.user_metadata?.full_name as string) || user?.email?.split('@')[0] || 'Customer';
  const initials = displayName.slice(0, 2).toUpperCase();""",
"""  const legalName =
    (user?.user_metadata?.full_name as string | undefined)?.trim() ||
    (user?.user_metadata?.name as string | undefined)?.trim() ||
    user?.email?.split('@')[0] ||
    'Customer';
  const nicknameMeta = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';
  const displayName = nicknameMeta ? `${legalName} (${nicknameMeta})` : legalName;
  const initials = legalName.slice(0, 2).toUpperCase();
  const avatarUrlMeta =
    (user?.user_metadata?.avatar_url as string | undefined) ||
    (typeof localStorage !== 'undefined' ? localStorage.getItem('nexus-portal-avatar') || '' : '');""",
]

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
    (() => {
      try {
        const e = (user?.email || '').trim().toLowerCase();
        if (!e) return '';
        // Per-account key only — never the legacy shared "nexus-portal-avatar"
        return localStorage.getItem(`nexus-portal-avatar:${e}`) || '';
      } catch {
        return '';
      }
    })();"""

for old_dn in old_dn_variants:
    if old_dn in cp:
        cp = cp.replace(old_dn, new_dn)
        print('displayName/avatar per-email ok')
        break
else:
    if "localStorage.getItem('nexus-portal-avatar')" in cp and 'nexus-portal-avatar:${' not in cp.replace('`', "'"):
        cp = cp.replace(
            "(typeof localStorage !== 'undefined' ? localStorage.getItem('nexus-portal-avatar') || '' : '')",
            """(() => {
      try {
        const e = (user?.email || '').trim().toLowerCase();
        if (!e) return '';
        return localStorage.getItem(`nexus-portal-avatar:${e}`) || '';
      } catch {
        return '';
      }
    })()""",
        )
        print('forced shared avatar key → per-email')

if 'const [sidebarAvatar' not in cp and 'avatarUrlMeta' in cp:
    inject = """
  const [sidebarAvatar, setSidebarAvatar] = useState(avatarUrlMeta || '');
  useEffect(() => {
    setSidebarAvatar(avatarUrlMeta || '');
  }, [avatarUrlMeta]);
  useEffect(() => {
    // Drop legacy shared browser avatar so accounts never cross-contaminate
    try { localStorage.removeItem('nexus-portal-avatar'); } catch { /* ignore */ }
    const onUpd = (e: Event) => {
      const d = (e as CustomEvent).detail as { avatar_url?: string | null; email?: string } | undefined;
      if (d && d.avatar_url) {
        setSidebarAvatar(d.avatar_url);
        return;
      }
      try {
        const em = (user?.email || d?.email || '').trim().toLowerCase();
        if (!em) return;
        const local = localStorage.getItem(`nexus-portal-avatar:${em}`);
        if (local) setSidebarAvatar(local);
      } catch { /* ignore */ }
    };
    window.addEventListener('nexus-profile-updated', onUpd);
    return () => window.removeEventListener('nexus-profile-updated', onUpd);
  }, [user?.email]);
"""
    markers = [
        "        return localStorage.getItem(`nexus-portal-avatar:${e}`) || '';\n      } catch {\n        return '';\n      }\n    })();",
        "    (typeof localStorage !== 'undefined' ? localStorage.getItem('nexus-portal-avatar') || '' : '');",
    ]
    injected = False
    for marker in markers:
        if marker in cp:
            cp = cp.replace(marker, marker + inject, 1)
            print('sidebar avatar state ok')
            injected = True
            break
    if not injected:
        print('sidebar inject marker not found')

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
                updateEmail={updateEmail}
              />
            )}"""
m = acc_pat.search(cp)
if m:
    cp = cp[: m.start()] + acc_new + cp[m.end() :]
    print('account panel ok')
elif "AccountProfilePanel" in cp and "updateEmail={updateEmail}" not in cp:
    cp = cp.replace(
        '                updatePassword={updatePassword}\n              />',
        '                updatePassword={updatePassword}\n                updateEmail={updateEmail}\n              />',
    )
    print('added updateEmail prop')

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

if "localStorage.getItem('nexus-portal-avatar')" in cp:
    cp = cp.replace(
        "localStorage.getItem('nexus-portal-avatar')",
        "localStorage.getItem(`nexus-portal-avatar:${(user?.email || '').trim().toLowerCase()}`)",
    )
    print('replaced remaining shared getItem with per-email')

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
print('CP wired OK', len(cp), 'AccountProfilePanel' in cp, 'sidebarAvatar' in cp, 'updateEmail' in cp)
print('shared get remaining', cp.count("localStorage.getItem('nexus-portal-avatar')"))
