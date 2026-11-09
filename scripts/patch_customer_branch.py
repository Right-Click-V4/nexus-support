"""Customer branch on signup + Account; options from Branches tab list."""
from pathlib import Path

lib = Path('src/lib/branches.ts')
if not lib.exists():
    lib.parent.mkdir(parents=True, exist_ok=True)
    lib.write_text("""/** Shared branch list — same source as agent Branches tab (localStorage). */
export const BRANCH_LS_KEY = 'nexus-branches-v1';

export type StoredBranch = {
  id?: string;
  name: string;
  email?: string;
  members?: unknown[];
};

/** Branch names available on the agent Branches tab. */
export function loadAvailableBranches(extraNames: string[] = []): string[] {
  const names = new Set<string>();
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(BRANCH_LS_KEY);
      if (raw) {
        const list = JSON.parse(raw) as StoredBranch[];
        if (Array.isArray(list)) {
          for (const b of list) {
            const n = String(b?.name || '').trim().toUpperCase();
            if (n) names.add(n);
          }
        }
      }
    }
  } catch {
    /* ignore */
  }
  for (const x of extraNames) {
    const n = String(x || '').trim().toUpperCase();
    if (n) names.add(n);
  }
  if (names.size === 0) {
    for (const n of ['MAASIN', 'KANANGA', 'AVENIDA', 'CIRIAN', 'SOGOD', 'ORMOC', 'ABUCAY']) {
      names.add(n);
    }
  }
  return Array.from(names).sort((a, b) => a.localeCompare(b));
}
""")
    print('lib written')

auth = Path('src/context/AuthContext.tsx')
if auth.exists():
    s = auth.read_text()
    if 'CUSTOMER_BRANCH_V1' not in s:
        s = s.replace(
"""  signUp: (
    email: string,
    password: string,
    fullName?: string,
    role?: 'agent' | 'customer'
  ) => Promise<void>;""",
"""  signUp: (
    email: string,
    password: string,
    fullName?: string,
    role?: 'agent' | 'customer',
    branch?: string,
  ) => Promise<void>;""",
        )
        s = s.replace(
"""  updateProfile: (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
  }) => Promise<void>;""",
"""  updateProfile: (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
    branch?: string;
  }) => Promise<void>;""",
        )
        old_su = """  const signUp = async (
    email: string,
    password: string,
    fullName?: string,
    role: 'agent' | 'customer' = 'customer'
  ) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    setAuthBusy(true);
    try {
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: { data: { full_name: fullName || '', role } },
      });"""
        new_su = """  const signUp = async (
    email: string,
    password: string,
    fullName?: string,
    role: 'agent' | 'customer' = 'customer',
    branch?: string, // CUSTOMER_BRANCH_V1
  ) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    setAuthBusy(true);
    try {
      const meta: Record<string, unknown> = { full_name: fullName || '', role };
      if (branch && role === 'customer') meta.branch = branch.trim().toUpperCase();
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: { data: meta },
      });"""
        if old_su in s:
            s = s.replace(old_su, new_su, 1)
            print('signUp')
        old_up = """  const updateProfile = async (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
  }) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload: Record<string, unknown> = {};
    if (data.nickname !== undefined) payload.nickname = data.nickname;
    if (data.phone !== undefined) payload.phone = data.phone;
    if (data.job_title !== undefined) payload.job_title = data.job_title;
    if (data.avatar_url !== undefined) payload.avatar_url = data.avatar_url;"""
        new_up = """  const updateProfile = async (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
    branch?: string;
  }) => {
    if (!supabase) throw new Error(configError || 'Supabase is not configured');
    const payload: Record<string, unknown> = {};
    if (data.nickname !== undefined) payload.nickname = data.nickname;
    if (data.phone !== undefined) payload.phone = data.phone;
    if (data.job_title !== undefined) payload.job_title = data.job_title;
    if (data.avatar_url !== undefined) payload.avatar_url = data.avatar_url;
    if (data.branch !== undefined) payload.branch = String(data.branch || '').trim().toUpperCase();"""
        if old_up in s:
            s = s.replace(old_up, new_up, 1)
            print('updateProfile')
        auth.write_text(s)
    else:
        print('auth already')

lp = Path('src/components/LoginPage.tsx')
if lp.exists():
    s = lp.read_text()
    if 'CUSTOMER_BRANCH_V1' not in s:
        if 'loadAvailableBranches' not in s:
            s = s.replace("from 'react';", "from 'react';\nimport { loadAvailableBranches } from '../lib/branches';", 1)
        s = s.replace(
            "const [name, setName] = useState('');",
            "const [name, setName] = useState('');\n  const [branch, setBranch] = useState(''); // CUSTOMER_BRANCH_V1\n  const branchOptions = loadAvailableBranches();",
            1,
        )
        s = s.replace(
            "await signUp(email.trim(), password, name.trim() || undefined, isAgent ? 'agent' : 'customer');",
            "await signUp(email.trim(), password, name.trim() || undefined, isAgent ? 'agent' : 'customer', !isAgent ? branch || undefined : undefined);",
            1,
        )
        s = s.replace(
            "if (!name.trim()) { setError('Please enter your full name.'); return; }",
            "if (!name.trim()) { setError('Please enter your full name.'); return; }\n      if (!isAgent && !branch.trim()) { setError('Please select your branch.'); return; }",
            1,
        )
        s = s.replace(
            '''                  <div><label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Full name</label><input required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" /></div>''',
            '''                  <div><label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Full name</label><input required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" /></div>
                  {!isAgent && (
                    <div>
                      <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Branch</label>
                      <select required className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none" value={branch} onChange={(e) => setBranch(e.target.value)}>
                        <option value="">Select your branch</option>
                        {branchOptions.map((b) => (
                          <option key={b} value={b}>{b}</option>
                        ))}
                      </select>
                    </div>
                  )}''',
            1,
        )
        lp.write_text(s)
        print('LP done')
    else:
        print('LP already')

app = Path('src/components/AccountProfilePanel.tsx')
if app.exists():
    s = app.read_text()
    if 'CUSTOMER_BRANCH_V1' not in s:
        if 'loadAvailableBranches' not in s:
            s = s.replace("from 'react';", "from 'react';\nimport { loadAvailableBranches } from '../lib/branches';", 1)
        s = s.replace(
"""  jobTitle: string;
  requiresAuth: boolean;
  onSignOut: () => void;
  updateProfile: (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
  }) => Promise<void>;""",
"""  jobTitle: string;
  branch?: string;
  requiresAuth: boolean;
  onSignOut: () => void;
  updateProfile: (data: {
    nickname?: string;
    phone?: string;
    job_title?: string;
    avatar_url?: string | null;
    branch?: string;
  }) => Promise<void>;""",
        )
        s = s.replace(
"""  jobTitle: initialJob,
  requiresAuth,
  onSignOut,
  updateProfile,
  updatePassword,
  updateEmail,
}: AccountProfilePanelProps) {""",
"""  jobTitle: initialJob,
  branch: initialBranch = '',
  requiresAuth,
  onSignOut,
  updateProfile,
  updatePassword,
  updateEmail,
}: AccountProfilePanelProps) {""",
        )
        s = s.replace(
            'const [username, setUsername] = useState(initialNick);',
            "const [username, setUsername] = useState(initialNick);\n  const [branch, setBranch] = useState(initialBranch || ''); // CUSTOMER_BRANCH_V1\n  const branchOptions = loadAvailableBranches(initialBranch ? [initialBranch] : []);",
            1,
        )
        s = s.replace(
"""  useEffect(() => {
    setUsername(initialNick);
    setPhone(initialPhone);
    const split = splitJobTitle(initialJob);
    setJobPreset(split.preset);
    setJobOther(split.other);
    const next = initialAvatar || readAvatarCache(email);
    setAvatar(next);
    try { localStorage.removeItem('nexus-portal-avatar'); } catch { /* ignore */ }
  }, [initialNick, initialPhone, initialJob, initialAvatar, email]);""",
"""  useEffect(() => {
    setUsername(initialNick);
    setPhone(initialPhone);
    setBranch(initialBranch || '');
    const split = splitJobTitle(initialJob);
    setJobPreset(split.preset);
    setJobOther(split.other);
    const next = initialAvatar || readAvatarCache(email);
    setAvatar(next);
    try { localStorage.removeItem('nexus-portal-avatar'); } catch { /* ignore */ }
  }, [initialNick, initialPhone, initialJob, initialBranch, initialAvatar, email]);""",
        )
        s = s.replace(
"""        nickname: username.trim() || '',
        phone: phone.trim() || '',
        job_title: combineJobTitle(jobPreset, jobOther),""",
"""        nickname: username.trim() || '',
        phone: phone.trim() || '',
        job_title: combineJobTitle(jobPreset, jobOther),
        branch: branch.trim().toUpperCase() || '',""",
        )
        old_job = """            <div className=\"sm:col-span-2\">
              <label className={label}>
                <span className=\"inline-flex items-center gap-1.5\">
                  <Briefcase size={12} /> Job title
                </span>
              </label>"""
        new_job = """            <div className=\"sm:col-span-2\">
              <label className={label}>Branch</label>
              <select
                className={field + ' cursor-pointer'}
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
              >
                <option value=\"\">Select your branch</option>
                {branchOptions.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>
            <div className=\"sm:col-span-2\">
              <label className={label}>
                <span className=\"inline-flex items-center gap-1.5\">
                  <Briefcase size={12} /> Job title
                </span>
              </label>"""
        if old_job in s:
            s = s.replace(old_job, new_job, 1)
            print('APP field')
        app.write_text(s)
        print('APP done')
    else:
        print('APP already')

cp = Path('src/components/CustomerPortal.tsx')
if cp.exists():
    s = cp.read_text()
    if 'AccountProfilePanel' in s and 'branchMeta' not in s:
        s = s.replace(
            "const nicknameMeta = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';",
            "const nicknameMeta = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';\n  const branchMeta = (user?.user_metadata?.branch as string | undefined)?.trim() || '';",
            1,
        )
        s = s.replace('nickname={nicknameMeta}', 'nickname={nicknameMeta}\n                branch={branchMeta}', 1)
        cp.write_text(s)
        print('CP branch prop')

wap = Path('scripts/wire_account_panel.py')
if wap.exists():
    t = wap.read_text()
    if 'branchMeta' not in t:
        t = t.replace(
            "const nicknameMeta = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';",
            "const nicknameMeta = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';\n  const branchMeta = (user?.user_metadata?.branch as string | undefined)?.trim() || '';",
        )
        t = t.replace('nickname={nicknameMeta}', 'nickname={nicknameMeta}\n                branch={branchMeta}')
        wap.write_text(t)
        print('wire updated')

print('DONE')
