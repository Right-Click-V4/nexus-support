#!/usr/bin/env python3
"""Remove Customer Portal sidebar Sign out; require confirm on remaining Sign out."""
from pathlib import Path
import re

cp = Path('src/components/CustomerPortal.tsx')
if not cp.exists():
    print('no CP')
else:
    c = cp.read_text()
    if 'signout-confirm-v1' in c:
        print('CP already has signout-confirm-v1')
    else:
        # Remove sidebar full-width Sign out buttons
        patterns = [
            r'\s*\{requiresAuth && \(\s*<button type="button" onClick=\{\(\) => void signOut\(\)\} className="flex items-center justify-center gap-2 w-full[^"]*">\s*<LogOut size=\{16\} /> Sign out\s*</button>\s*\)\}',
            r'\s*\{requiresAuth && \(\s*<button type="button" onClick=\{\(\) => void signOut\(\)\} className="w-full flex items-center gap-3[^"]*">\s*<LogOut size=\{16\} /> Sign out\s*</button>\s*\)\}',
            r'\s*\{requiresAuth && \(\s*<button type="button" onClick=\{\(\) => void signOut\(\)\} className="[^"]*w-full[^"]*">\s*<LogOut size=\{16\} />\s*Sign out\s*</button>\s*\)\}',
        ]
        for pat in patterns:
            c2, n = re.subn(pat, '', c, count=5, flags=re.MULTILINE)
            if n:
                c = c2
                print(f'removed sidebar signout x{n}')

        # Agent-style sidebar footer Sign out (no requiresAuth wrapper)
        c2, n = re.subn(
            r'\s*<button\s+type="button"\s+onClick=\{\(\) => void signOut\(\)\}\s+className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400[^"]*"\s*>\s*<LogOut size=\{16\} /> Sign out\s*</button>',
            '',
            c,
            count=3,
            flags=re.MULTILINE,
        )
        if n:
            c = c2
            print(f'removed agent-style sidebar signout x{n}')

        if 'confirmSignOut' not in c:
            m = re.search(r'const \{ user, accountRole, signOut[^}]*\} = useAuth\(\);', c)
            if m:
                c = c.replace(m.group(0), m.group(0) + '\n  const [confirmSignOut, setConfirmSignOut] = useState(false);', 1)
                print('state ok')
            else:
                print('state insert miss')

        # Topbar: open confirm instead of immediate signOut
        c2, n = re.subn(
            r'onClick=\{\(\) => void signOut\(\)\}(\s+className="[^"]*"\s+title="Sign out")',
            r'onClick={() => setConfirmSignOut(true)}\1',
            c,
            count=3,
        )
        if n:
            c = c2
            print(f'topbar onclick x{n}')
        else:
            c2, n2 = re.subn(
                r'onClick=\{\(\) => void signOut\(\)\}(\s*\n\s*className="[^"]*"\s*\n\s*title="Sign out")',
                r'onClick={() => setConfirmSignOut(true)}\1',
                c,
                count=3,
            )
            if n2:
                c = c2
                print(f'topbar multiline onclick x{n2}')
            else:
                c2, n3 = re.subn(
                    r'<button\n(\s+)type="button"\n(\s+)onClick=\{\(\) => void signOut\(\)\}',
                    r'<button\n\1type="button"\n\2onClick={() => setConfirmSignOut(true)}',
                    c,
                    count=2,
                )
                if n3:
                    c = c2
                    print(f'topbar button onclick x{n3}')
                elif 'title="Sign out"' in c and 'onClick={() => void signOut()}' in c:
                    parts = c.split('title="Sign out"')
                    rebuilt = [parts[0]]
                    for part in parts[1:]:
                        prev = rebuilt[-1]
                        rebuilt[-1] = prev.replace(
                            'onClick={() => void signOut()}',
                            'onClick={() => setConfirmSignOut(true)}',
                            1,
                        )
                        rebuilt.append(part)
                    c = 'title="Sign out"'.join(rebuilt)
                    print('topbar scan replace ok')
                else:
                    print('topbar onclick miss')

        modal = '''
      {confirmSignOut && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="signout-title">
          <div className="w-full max-w-sm rounded-2xl border border-white/20 bg-white dark:bg-zinc-900 shadow-2xl p-5 space-y-4">
            <h2 id="signout-title" className="text-base font-semibold text-zinc-900 dark:text-zinc-50">Sign out?</h2>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              You will need to sign in again to access the Customer Portal.
            </p>
            <div className="flex items-center justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setConfirmSignOut(false)}
                className="px-3.5 py-2 rounded-xl text-sm font-medium border border-zinc-200 dark:border-white/15 text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-white/5"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => { setConfirmSignOut(false); void signOut(); }}
                className="px-3.5 py-2 rounded-xl text-sm font-semibold text-white bg-rose-600 hover:bg-rose-500 shadow-sm"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}
'''
        if 'confirmSignOut &&' not in c:
            if '<PortalAnnouncementMarquee />' in c:
                c = c.replace('<PortalAnnouncementMarquee />', '<PortalAnnouncementMarquee />\n' + modal, 1)
                print('modal after marquee')
            elif '</main>' in c:
                c = c.replace('</main>', modal + '\n        </main>', 1)
                print('modal before /main')
            else:
                print('modal insert miss')

        if 'signout-confirm-v1' not in c:
            c = c.replace(
                'export default function CustomerPortal',
                '/* signout-confirm-v1 */\nexport default function CustomerPortal',
                1,
            )

        cp.write_text(c)
        print('CP patched', len(c))

# Agent Sidebar: confirm before sign out (keep button in agent workspace)
sb = Path('src/components/Sidebar.tsx')
if not sb.exists():
    print('no Sidebar')
else:
    s = sb.read_text()
    if 'signout-confirm-v1' in s:
        print('Sidebar already confirm')
    else:
        m = re.search(r"import\s+\{([^}]+)\}\s+from\s+'react'", s)
        if m and 'useState' not in m.group(1):
            s = s.replace(m.group(0), m.group(0).replace('{', '{ useState, ', 1), 1)
            print('Sidebar useState import')

        if 'confirmSignOut' not in s:
            m = re.search(r'\}: SidebarProps\) \{\s*', s)
            if m:
                s = s[: m.end()] + '\n  const [confirmSignOut, setConfirmSignOut] = useState(false);\n' + s[m.end() :]
                print('Sidebar state ok')
            else:
                print('Sidebar state miss')

        old_click = """onClick={() => {
            if (onSignOut) onSignOut();
            else window.location.hash = '';
          }}"""
        if old_click in s:
            s = s.replace(old_click, 'onClick={() => setConfirmSignOut(true)}', 1)
            print('Sidebar click ok')
        else:
            c2, n = re.subn(
                r"onClick=\{\(\) => \{\s*if \(onSignOut\) onSignOut\(\);\s*else window\.location\.hash = '';\s*\}\}",
                'onClick={() => setConfirmSignOut(true)}',
                s,
                count=1,
            )
            if n:
                s = c2
                print('Sidebar click regex ok')
            else:
                print('Sidebar click miss')

        modal = '''
      {confirmSignOut && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl border border-white/15 bg-zinc-900 shadow-2xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-zinc-50">Sign out?</h2>
            <p className="text-sm text-zinc-400">You will need to sign in again to access the agent workspace.</p>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setConfirmSignOut(false)} className="px-3.5 py-2 rounded-xl text-sm border border-white/15 text-zinc-200 hover:bg-white/5">Cancel</button>
              <button type="button" onClick={() => { setConfirmSignOut(false); if (onSignOut) onSignOut(); else window.location.hash = ''; }} className="px-3.5 py-2 rounded-xl text-sm font-semibold text-white bg-rose-600 hover:bg-rose-500">Sign out</button>
            </div>
          </div>
        </div>
      )}
'''
        if 'confirmSignOut &&' not in s and '</aside>' in s:
            s = s.replace('</aside>', modal + '\n    </aside>', 1)
            print('Sidebar modal ok')

        if 'signout-confirm-v1' not in s:
            s = s.replace(
                'export default function Sidebar',
                '/* signout-confirm-v1 */\nexport default function Sidebar',
                1,
            )

        sb.write_text(s)
        print('Sidebar patched', len(s))

print('done')
