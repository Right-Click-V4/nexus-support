import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import ErrorBoundary from './ErrorBoundary.tsx'
import { applyUiPrefs } from './lib/uiPrefs'
import { installPollThrottle } from './lib/pollThrottle'

// Must run before any React tree schedules setInterval polls
installPollThrottle()

// ALWAYS_CLEAR_SITE404 — never leave the app stuck on the station-overrun screen
try {
  localStorage.setItem('nexus-site-404-on', '0')
  localStorage.removeItem('nexus-site-404-on')
  const h = (window.location.hash || '').replace(/^#\/?/, '').toLowerCase()
  if (h === '404' || h === 'notfound') {
    window.location.hash = ''
  }
} catch { /* ignore */ }

applyUiPrefs()

/** Runtime theme override — always wins over Tailwind utility order in the built CSS. */
function installForcedThemeStyles() {
  if (typeof document === 'undefined') return
  const id = 'nexus-forced-theme'
  if (document.getElementById(id)) return
  const el = document.createElement('style')
  el.id = id
  el.textContent = `
/* Forced dark surfaces — do not rely on build order */
html.nexus-dark .bg-white,
html.dark .bg-white,
html.nexus-dark [class*="bg-white"],
html.dark [class*="bg-white"],
html.nexus-dark .bg-zinc-50,
html.dark .bg-zinc-50,
html.nexus-dark .bg-slate-50,
html.dark .bg-slate-50 {
  background: rgba(22, 14, 42, 0.94) !important;
  border-color: rgba(167, 139, 250, 0.28) !important;
  color: #ede9fe !important;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35) !important;
}
html.nexus-dark .text-slate-900,
html.dark .text-slate-900,
html.nexus-dark .text-zinc-900,
html.dark .text-zinc-900,
html.nexus-dark .text-slate-800,
html.dark .text-slate-800,
html.nexus-dark .text-zinc-800,
html.dark .text-zinc-800 {
  color: #f5f3ff !important;
}
html.nexus-dark .text-slate-600,
html.dark .text-slate-600,
html.nexus-dark .text-zinc-600,
html.dark .text-zinc-600,
html.nexus-dark .text-slate-500,
html.dark .text-slate-500,
html.nexus-dark .text-zinc-500,
html.dark .text-zinc-500 {
  color: #a1a1aa !important;
}
html.nexus-dark .border-slate-200,
html.dark .border-slate-200,
html.nexus-dark .border-zinc-200,
html.dark .border-zinc-200,
html.nexus-dark .border-slate-100,
html.dark .border-slate-100 {
  border-color: rgba(167, 139, 250, 0.25) !important;
}
html.nexus-dark input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]),
html.dark input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]),
html.nexus-dark textarea,
html.dark textarea,
html.nexus-dark select,
html.dark select {
  background: rgba(10, 6, 24, 0.95) !important;
  border-color: rgba(167, 139, 250, 0.35) !important;
  color: #f4f4f5 !important;
}
html.nexus-dark input::placeholder,
html.dark input::placeholder,
html.nexus-dark textarea::placeholder,
html.dark textarea::placeholder {
  color: rgba(196, 181, 253, 0.45) !important;
}
html.nexus-dark .bg-violet-50,
html.dark .bg-violet-50,
html.nexus-dark .bg-purple-50,
html.dark .bg-purple-50 {
  background: rgba(76, 29, 149, 0.4) !important;
  color: #ede9fe !important;
}
html.nexus-dark .bg-amber-50,
html.dark .bg-amber-50 {
  background: rgba(120, 53, 15, 0.45) !important;
  color: #fef3c7 !important;
}
html.nexus-dark .bg-emerald-50,
html.dark .bg-emerald-50,
html.nexus-dark .bg-green-50,
html.dark .bg-green-50 {
  background: rgba(6, 78, 59, 0.45) !important;
  color: #d1fae5 !important;
}
html.nexus-dark .bg-rose-50,
html.dark .bg-rose-50,
html.nexus-dark .bg-red-50,
html.dark .bg-red-50 {
  background: rgba(127, 29, 29, 0.45) !important;
  color: #fecaca !important;
}
html.nexus-dark body,
html.dark body {
  background-color: #0a0618 !important;
  color: #e4e4e7 !important;
}
`
  document.head.appendChild(el)
}
installForcedThemeStyles()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
