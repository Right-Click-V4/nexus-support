#!/usr/bin/env python3
"""Wire star-X BrandMark + useBranding into CustomerPortal."""
from pathlib import Path

p = Path('src/components/CustomerPortal.tsx')
if not p.exists() or p.stat().st_size < 1000:
    raise SystemExit('CP missing or stub')
t = p.read_text()

if 'useBranding' not in t:
    t = t.replace(
        "import { usePlatform } from '../context/PlatformContext';",
        "import { usePlatform } from '../context/PlatformContext';\nimport { useBranding } from '../context/BrandingContext';",
    )

new_brand = '''function BrandMark({ logoUrl, className = 'w-8 h-8' }: { logoUrl?: string; className?: string }) {
  if (logoUrl) {
    return (
      <div className={`${className} rounded-xl overflow-hidden bg-white/10 ring-1 ring-white/15 flex items-center justify-center shrink-0`}>
        <img src={logoUrl} alt="" className="w-full h-full object-contain" />
      </div>
    );
  }
  return (
    <div className={`${className} rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-md shadow-brand-900/40 shrink-0`}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M4 4 L20 20 M20 4 L4 20" stroke="white" strokeWidth="3.2" strokeLinecap="round" />
        <path d="M12 2 L13.6 9.6 L21 11.2 L13.6 12.8 L12 20.5 L10.4 12.8 L3 11.2 L10.4 9.6 Z" fill="white" />
        <circle cx="12" cy="11.2" r="1.4" fill="white" />
      </svg>
    </div>
  );
}'''

if 'function BrandMark' in t:
    start = t.index('function BrandMark')
    i = t.index('{', start)
    depth = 0
    for j in range(i, len(t)):
        if t[j] == '{':
            depth += 1
        elif t[j] == '}':
            depth -= 1
            if depth == 0:
                t = t[:start] + new_brand + t[j + 1:]
                break

if "const { branding } = useBranding()" not in t:
    needle = "export default function CustomerPortal({ onBackToAgent }: Props) {"
    if needle in t:
        idx = t.index(needle) + len(needle)
        t = (
            t[:idx]
            + "\n  const { branding } = useBranding();\n  const logoUrl = (branding.logoUrl || '').trim();\n  const appName = (branding.appName || '').trim() || 'Nexus Ops';"
            + t[idx:]
        )

t = t.replace('<BrandMark />', '<BrandMark logoUrl={logoUrl} />')
t = t.replace('<BrandMark className="w-8 h-8" />', '<BrandMark logoUrl={logoUrl} className="w-8 h-8" />')
p.write_text(t)
print('portal logo patched', p.stat().st_size, 'useBranding' in t)
