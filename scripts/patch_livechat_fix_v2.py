#!/usr/bin/env python3
"""Fix Live Chat startsWith crash; ErrorBoundary; profile success modal."""
from pathlib import Path
import re

att = Path("src/lib/chatAttachments.ts")
if att.exists():
    t = att.read_text()
    if "parse-safe-v1" not in t:
        t = t.replace(
            "export function parseChatAttachment(text: string): { att?: ChatAtt; text: string } {\n  if (!text.startsWith(PREFIX)) return { text };",
            "export function parseChatAttachment(text?: string | null): { att?: ChatAtt; text: string } {\n  if (text == null || typeof text !== 'string' || !text.startsWith(PREFIX)) return { text: text || '' };",
        )
        if "export async function encodeChatFile" not in t:
            t += """
/** Read a File as data-URL then encode as chat attachment payload. */
export async function encodeChatFile(file: File, caption?: string): Promise<string> {
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result || ''));
    r.onerror = () => reject(new Error('Could not read file'));
    r.readAsDataURL(file);
  });
  return encodeChatAttachment(
    { url: dataUrl, name: file.name, mime: file.type || 'application/octet-stream' },
    caption,
  );
}
"""
        t = "/* parse-safe-v1 */\n" + t
        att.write_text(t)
        print("chatAttachments fixed")

plc = Path("src/components/PortalLiveChat.tsx")
if plc.exists():
    p = plc.read_text()
    if "livechat-text-field-v1" not in p:
        p = p.replace(
            "import { encodeChatAttachment, parseChatAttachment, isImageMime } from '../lib/chatAttachments';",
            "import { encodeChatFile, parseChatAttachment, isImageMime } from '../lib/chatAttachments';",
        )
        p = p.replace("await encodeChatAttachment(file)", "await encodeChatFile(file)")
        p = p.replace("ticketHint.startsWith('Found')", "(ticketHint || '').startsWith('Found')")
        p = "/* livechat-text-field-v1 */\n" + p
    if "const parsed = parseChatAttachment(raw)" not in p:
        p2, n = re.subn(
            r"const mine = m\.sender === 'customer';\s*const att = parseChatAttachment\([^;]+;\s*return \(",
            "const mine = m.sender === 'customer';\n"
            "          const raw = m.text || (m as { body?: string }).body || '';\n"
            "          const parsed = parseChatAttachment(raw);\n"
            "          const att = parsed.att;\n"
            "          const bodyText = (parsed.text || raw || '').toString();\n"
            "          return (",
            p,
            count=1,
        )
        if n:
            p = p2
        else:
            p2, n = re.subn(
                r"const mine = m\.sender === 'customer';\s*const att = parseChatAttachment\([^)]+\);",
                "const mine = m.sender === 'customer';\n"
                "          const raw = m.text || (m as { body?: string }).body || '';\n"
                "          const parsed = parseChatAttachment(raw);\n"
                "          const att = parsed.att;\n"
                "          const bodyText = (parsed.text || raw || '').toString();",
                p,
                count=1,
            )
            if n:
                p = p2
    if "bodyText" in p and "m.body" in p:
        p = p.replace("{m.body}", "{bodyText}")
        p = re.sub(r": \(\s*m\.body\s*\)", ": (\n                  bodyText\n                )", p)
    p = p.replace("isImageMime(att.mime)", "isImageMime(att?.mime)")
    p = p.replace("{att.name}", "{att?.name || 'Download file'}")
    plc.write_text(p)
    print("plc written")

lcp = Path("src/components/LiveChatPage.tsx")
if lcp.exists():
    l = lcp.read_text()
    if "livechat-text-field-v1" not in l:
        l = l.replace("m.body?.startsWith('http')", "(m.text || (m as { body?: string }).body || '').startsWith('http')")
        l = l.replace("parseChatAttachment(m.body)", "parseChatAttachment(m.text || (m as { body?: string }).body)")
        l = "/* livechat-text-field-v1 */\n" + l
        lcp.write_text(l)

eb = Path("src/ErrorBoundary.tsx")
if eb.exists() and "error-boundary-portal-v1" not in eb.read_text():
    eb.write_text('''/* error-boundary-portal-v1 */
import { Component, type ReactNode } from \'react\';

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

  render() {
    if (this.state.error) {
      return (
        <div style={{ minHeight: \'100vh\', display: \'flex\', alignItems: \'center\', justifyContent: \'center\', padding: 24, background: \'#0b0618\', fontFamily: \'system-ui\' }}>
          <div style={{ maxWidth: 480, width: \'100%\', textAlign: \'center\' }}>
            <div style={{ fontSize: 13, letterSpacing: 0.08, color: \'#a78bfa\', marginBottom: 12, textTransform: \'uppercase\' as const }}>Something went wrong</div>
            <pre style={{ background: \'rgba(254,242,242,0.95)\', color: \'#991b1b\', padding: 16, borderRadius: 12, fontSize: 13, overflow: \'auto\', textAlign: \'left\' }}>
              {this.state.error.message}
            </pre>
            <p style={{ color: \'#a1a1aa\', fontSize: 13, marginTop: 12 }}>
              Reload the portal, or open the home screen if this keeps happening.
            </p>
            <div style={{ display: \'flex\', gap: 10, justifyContent: \'center\', marginTop: 16, flexWrap: \'wrap\' as const }}>
              <button
                type="button"
                onClick={() => {
                  this.setState({ error: null });
                  const h = (window.location.hash || \'\').toLowerCase();
                  if (h.includes(\'agent\')) window.location.hash = \'#/agent\';
                  else window.location.hash = \'#/portal\';
                  window.location.reload();
                }}
                style={{ padding: \'10px 18px\', background: \'#7c3aed\', color: \'#fff\', border: \'none\', borderRadius: 10, cursor: \'pointer\', fontWeight: 600 }}
              >
                Reload app
              </button>
              <button
                type="button"
                onClick={() => {
                  this.setState({ error: null });
                  window.location.hash = \'#/\';
                  window.location.reload();
                }}
                style={{ padding: \'10px 18px\', background: \'transparent\', color: \'#e4e4e7\', border: \'1px solid rgba(255,255,255,0.2)\', borderRadius: 10, cursor: \'pointer\' }}
              >
                Go to home / 404 screen
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
''')
    print("ErrorBoundary fixed")

pp = Path("src/components/ProfilePage.tsx")
if pp.exists():
    pr = pp.read_text()
    if "profile-success-modal-v1" not in pr:
        pr = re.sub(
            r"import \{([^}]+)\} from 'lucide-react';",
            lambda m: m.group(0) if "Check" in m.group(1) else "import { " + m.group(1).strip().rstrip(",") + ", Check } from 'lucide-react';",
            pr,
            count=1,
        )
        if "const [successOpen, setSuccessOpen]" not in pr:
            pr = pr.replace(
                "const [saving, setSaving] = useState(false);",
                "const [saving, setSaving] = useState(false);\n  const [successOpen, setSuccessOpen] = useState(false);",
                1,
            )
        pr = pr.replace("setMsg('Profile and password saved.');", "setMsg('Profile and password saved.');\n        setSuccessOpen(true);")
        pr = pr.replace("setMsg('Profile saved.');", "setMsg('Profile saved.');\n        setSuccessOpen(true);")
        modal = """
      {successOpen && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-black/55" role="dialog" aria-modal="true">
          <div className="w-full max-w-sm rounded-2xl border border-white/15 bg-zinc-950/95 backdrop-blur-md shadow-2xl p-6 text-center">
            <div className="mx-auto w-14 h-14 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center mb-3">
              <Check className="text-emerald-400" size={28} strokeWidth={2.5} />
            </div>
            <h3 className="text-lg font-semibold text-white">Successfully Updated</h3>
            <p className="text-sm text-zinc-400 mt-1.5">Your profile photo and details are saved and will show across portals.</p>
            <button
              type="button"
              onClick={() => setSuccessOpen(false)}
              className="mt-5 w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold"
            >
              OK
            </button>
          </div>
        </div>
      )}
"""
        if "{cropSrc && (" in pr:
            pr = pr.replace("{cropSrc && (", modal + "\n      {cropSrc && (", 1)
        pr = "/* profile-success-modal-v1 */\n" + pr
        pp.write_text(pr)
        print("profile success")
print("done")
