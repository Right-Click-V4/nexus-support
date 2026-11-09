/** Realistic communications satellite — bus, solar wings, dish, blinking LEDs. */
export function SatelliteCraft({ uid }: { uid: string }) {
  return (
    <svg
      className="login-ship-svg login-sat-svg"
      width="110"
      height="48"
      viewBox="0 0 140 56"
      fill="none"
      aria-hidden
    >
      <defs>
        <linearGradient id={`${uid}-panel`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#93c5fd" />
          <stop offset="45%" stopColor="#3b82f6" />
          <stop offset="100%" stopColor="#1d4ed8" />
        </linearGradient>
        <linearGradient id={`${uid}-panel-edge`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#e0f2fe" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#1e3a8a" stopOpacity="0.4" />
        </linearGradient>
        <linearGradient id={`${uid}-bus`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f8fafc" />
          <stop offset="55%" stopColor="#cbd5e1" />
          <stop offset="100%" stopColor="#64748b" />
        </linearGradient>
        <linearGradient id={`${uid}-dish`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fef3c7" />
          <stop offset="50%" stopColor="#fbbf24" />
          <stop offset="100%" stopColor="#b45309" />
        </linearGradient>
        <filter id={`${uid}-glow`} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="1.4" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <ellipse cx="70" cy="50" rx="42" ry="3.5" fill="#000" opacity="0.18" />

      <g transform="translate(4, 16)">
        <rect x="0" y="0" width="40" height="22" rx="2" fill={`url(#${uid}-panel)`} stroke="#1e40af" strokeWidth="1" />
        <line x1="10" y1="1" x2="10" y2="21" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="20" y1="1" x2="20" y2="21" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="30" y1="1" x2="30" y2="21" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="1" y1="7.3" x2="39" y2="7.3" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.5" />
        <line x1="1" y1="14.6" x2="39" y2="14.6" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.5" />
        <rect x="0" y="0" width="40" height="22" rx="2" fill={`url(#${uid}-panel-edge)`} opacity="0.25" />
      </g>

      <g transform="translate(96, 16)">
        <rect x="0" y="0" width="40" height="22" rx="2" fill={`url(#${uid}-panel)`} stroke="#1e40af" strokeWidth="1" />
        <line x1="10" y1="1" x2="10" y2="21" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="20" y1="1" x2="20" y2="21" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="30" y1="1" x2="30" y2="21" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.55" />
        <line x1="1" y1="7.3" x2="39" y2="7.3" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.5" />
        <line x1="1" y1="14.6" x2="39" y2="14.6" stroke="#1e3a8a" strokeWidth="0.7" opacity="0.5" />
        <rect x="0" y="0" width="40" height="22" rx="2" fill={`url(#${uid}-panel-edge)`} opacity="0.25" />
      </g>

      <rect x="44" y="24" width="10" height="5" rx="1" fill="#94a3b8" stroke="#64748b" strokeWidth="0.6" />
      <rect x="86" y="24" width="10" height="5" rx="1" fill="#94a3b8" stroke="#64748b" strokeWidth="0.6" />

      <rect
        x="54"
        y="16"
        width="32"
        height="22"
        rx="3.5"
        fill={`url(#${uid}-bus)`}
        stroke="#e2e8f0"
        strokeWidth="1.1"
      />
      <rect x="58" y="20" width="24" height="5" rx="1" fill="#64748b" opacity="0.35" />
      <rect x="58" y="28" width="10" height="6" rx="1" fill="#475569" opacity="0.4" />
      <rect x="70" y="28" width="10" height="6" rx="1" fill="#475569" opacity="0.4" />

      <circle className="login-sat-led login-sat-led-green" cx="60" cy="19" r="1.6" fill="#4ade80" filter={`url(#${uid}-glow)`} />
      <circle className="login-sat-led login-sat-led-amber" cx="66" cy="19" r="1.6" fill="#fbbf24" filter={`url(#${uid}-glow)`} />
      <circle className="login-sat-led login-sat-led-red" cx="72" cy="19" r="1.6" fill="#f87171" filter={`url(#${uid}-glow)`} />
      <circle className="login-sat-led login-sat-led-cyan" cx="78" cy="19" r="1.6" fill="#67e8f9" filter={`url(#${uid}-glow)`} />

      <rect x="68.5" y="6" width="3" height="11" rx="1" fill="#94a3b8" stroke="#64748b" strokeWidth="0.5" />
      <ellipse
        cx="70"
        cy="8"
        rx="11"
        ry="7.5"
        fill={`url(#${uid}-dish)`}
        stroke="#b45309"
        strokeWidth="1.1"
      />
      <ellipse cx="70" cy="8" rx="7" ry="4.8" fill="#fef3c7" opacity="0.55" />
      <path d="M70 8 L66 12 L74 12 Z" fill="#fde68a" stroke="#d97706" strokeWidth="0.7" />
      <circle className="login-sat-led login-sat-led-amber" cx="70" cy="8" r="1.8" fill="#fff7ed" filter={`url(#${uid}-glow)`} />

      <line x1="82" y1="16" x2="88" y2="4" stroke="#cbd5e1" strokeWidth="1.2" strokeLinecap="round" />
      <circle className="login-sat-led login-sat-led-cyan" cx="88" cy="4" r="1.5" fill="#a5f3fc" filter={`url(#${uid}-glow)`} />

      <rect x="64" y="37" width="12" height="3" rx="1" fill="#475569" opacity="0.7" />
    </svg>
  );
}
