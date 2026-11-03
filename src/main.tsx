import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import ErrorBoundary from './ErrorBoundary.tsx'
import { applyUiPrefs } from './lib/uiPrefs'
import { installPollThrottle } from './lib/pollThrottle'

// Must run before any React tree schedules setInterval polls
installPollThrottle()
applyUiPrefs()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
