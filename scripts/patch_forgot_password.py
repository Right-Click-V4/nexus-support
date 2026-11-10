#!/usr/bin/env python3
"""Make Forgot Password clickable + working reset flow on LoginPage."""
from pathlib import Path

p = Path('src/components/LoginPage.tsx')
if not p.exists():
    raise SystemExit(0)
s = p.read_text()

s = s.replace(
    "const { signIn, signUp, loading, error, clearError } = useAuth();",
    "const { signIn, signUp, resetPassword, loading, error, clearError } = useAuth();",
    1,
)

s = s.replace(
    "useState<'signin' | 'signup'>('signin')",
    "useState<'signin' | 'signup' | 'forgot'>('signin')",
    1,
)

if 'const [infoMsg' not in s:
    s = s.replace(
        "const [localError, setLocalError] = useState<string | null>(null);",
        "const [infoMsg, setInfoMsg] = useState('');\n  const [localError, setLocalError] = useState<string | null>(null);",
        1,
    )

if "mode === 'forgot'" not in s:
    s = s.replace(
        "    setLocalError(null);\n    clearError?.();\n    if (mode === 'signup') {",
        "    setLocalError(null);\n    clearError?.();\n    if (mode === 'forgot') {\n"
        "      if (!email.trim()) {\n"
        "        setLocalError('Enter your email to reset password.');\n"
        "        return;\n"
        "      }\n"
        "      try {\n"
        "        await resetPassword?.(email.trim());\n"
        "        setInfoMsg('If an account exists for that email, a reset link was sent.');\n"
        "        setMode('signin');\n"
        "      } catch (err) {\n"
        "        setLocalError(err instanceof Error ? err.message : 'Could not send reset email.');\n"
        "      }\n"
        "      return;\n"
        "    }\n"
        "    if (mode === 'signup') {",
        1,
    )

old_fp = '<p className="text-center text-xs text-violet-300/50">Forgot Password?</p>'
new_fp = (
    '<button\n'
    '                type="button"\n'
    '                className="block w-full text-center text-xs text-violet-200/80 hover:text-white hover:underline"\n'
    '                onClick={() => {\n'
    "                  setMode('forgot');\n"
    '                  setLocalError(null);\n'
    "                  setInfoMsg('');\n"
    '                  clearError?.();\n'
    '                }}\n'
    '              >\n'
    '                Forgot Password?\n'
    '              </button>'
)
s = s.replace(old_fp, new_fp, 1)

if "mode === 'forgot' ?" not in s and "{mode === 'signin' ? (" in s:
    forgot_form = (
        "{mode === 'forgot' ? (\n"
        "            <form\n"
        "              onSubmit={onSubmit}\n"
        '              className="login-glass-card w-full max-w-[360px] sm:max-w-[380px] rounded-[22px] px-6 py-7 space-y-3.5"\n'
        '              autoComplete="on"\n'
        "            >\n"
        '              <div className="flex flex-col items-center gap-2 mb-1">\n'
        '                <div className="login-card-logo">\n'
        "                  <NexusLogoMark size={28} />\n"
        "                </div>\n"
        '                <div className="text-center">\n'
        '                  <div className="text-lg font-semibold text-white tracking-tight">Reset password</div>\n'
        '                  <p className="text-xs text-violet-200/70 mt-1">We&apos;ll email you a reset link</p>\n'
        "                </div>\n"
        "              </div>\n"
        "              <div>\n"
        '                <label className="block text-sm font-medium text-fuchsia-100/90 mb-1">Email</label>\n'
        "                <input\n"
        '                  type="email"\n'
        "                  required\n"
        '                  className="login-glass-input w-full rounded-xl px-3 py-2.5 text-sm outline-none"\n'
        "                  value={email}\n"
        "                  onChange={(e) => setEmail(e.target.value)}\n"
        '                  autoComplete="email"\n'
        '                  placeholder="you@company.com"\n'
        "                />\n"
        "              </div>\n"
        "              {(localError || error) && <p className=\"text-sm text-rose-300\">{localError || error}</p>}\n"
        "              {infoMsg ? <p className=\"text-sm text-emerald-300\">{infoMsg}</p> : null}\n"
        "              <button\n"
        '                type="submit"\n'
        "                disabled={loading}\n"
        '                className="login-submit-btn w-full rounded-xl text-white font-semibold text-sm py-2.5 disabled:opacity-60"\n'
        "              >\n"
        "                {loading ? 'Sending…' : 'Send reset link'}\n"
        "              </button>\n"
        "              <button\n"
        '                type="button"\n'
        '                className="block w-full text-center text-xs text-violet-200/80 hover:underline"\n'
        "                onClick={() => { setMode('signin'); setLocalError(null); setInfoMsg(''); }}\n"
        "              >\n"
        "                Back to sign in\n"
        "              </button>\n"
        "            </form>\n"
        "          ) : mode === 'signin' ? ("
    )
    s = s.replace("{mode === 'signin' ? (", forgot_form, 1)

p.write_text(s)
print('forgot password patched')
