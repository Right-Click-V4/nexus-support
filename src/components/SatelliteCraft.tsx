/** Classic communications satellite — clean silhouette, no shadow blob. */
export function SatelliteCraft({ uid }: { uid: string }) {
  return (
    <svg
      className="login-ship-svg login-sat-svg"
      width="120"
      height="40"
      viewBox="0 0 160 48"
      fill="none"
      aria-hidden
    >
      <defs>
        <linearGradient id={`${uid}-panel`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="50%" stopColor="#2563eb" />
          <stop offset="100%" stopColor="#1e3a8a" />
        </linearGradient>
        <linearGradient id={`${uid}-bus`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#e2e8f0" />
          <stop offset="100%" stopColor="#94a3b8" />
        </linearGradient>
        <linearGradient id={`${uid}-gold`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
      </defs>

      <g>
        <rect x="2" y="14" width="52" height="18" rx="1.5" fill={`url(#${uid}-panel)`} stroke="#1e40af" strokeWidth="0.8" />
        <line x1="15" y1="15" x2="15" y2="31" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.55" />
        <line x1="28" y1="15" x2="28" y2="31" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.55" />
        <line x1="41" y1="15" x2="41" y2="31" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.55" />
        <line x1="3" y1="20" x2="53" y2="20" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.45" />
        <line x1="3" y1="26" x2="53" y2="26" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.45" />
        <rect x="54" y="20" width="8" height="4" rx="0.8" fill="#94a3b8" />
      </g>

      <g>
        <rect x="106" y="14" width="52" height="18" rx="1.5" fill={`url(#${uid}-panel)`} stroke="#1e40af" strokeWidth="0.8" />
        <line x1="119" y1="15" x2="119" y2="31" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.55" />
        <line x1="132" y1="15" x2="132" y2="31" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.55" />
        <line x1="145" y1="15" x2="145" y2="31" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.55" />
        <line x1="107" y1="20" x2="157" y2="20" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.45" />
        <line x1="107" y1="26" x2="157" y2="26" stroke="#1e3a8a" strokeWidth="0.6" opacity="0.45" />
        <rect x="98" y="20" width="8" height="4" rx="0.8" fill="#94a3b8" />
      </g>

      <rect x="62" y="12" width="36" height="22" rx="2.5" fill={`url(#${uid}-bus)`} stroke="#cbd5e1" strokeWidth="1" />
      <rect x="66" y="16" width="28" height="4" rx="0.8" fill="#64748b" opacity="0.45" />
      <rect x="66" y="23" width="12" height="6" rx="0.8" fill="#475569" opacity="0.4" />
      <rect x="82" y="23" width="12" height="6" rx="0.8" fill="#475569" opacity="0.4" />

      <circle className="login-sat-led login-sat-led-green" cx="68" cy="14.5" r="1.3" fill="#4ade80" />
      <circle className="login-sat-led login-sat-led-amber" cx="73" cy="14.5" r="1.3" fill="#fbbf24" />
      <circle className="login-sat-led login-sat-led-red" cx="78" cy="14.5" r="1.3" fill="#f87171" />
      <circle className="login-sat-led login-sat-led-cyan" cx="83" cy="14.5" r="1.3" fill="#67e8f9" />

      <line x1="98" y1="16" x2="108" y2="6" stroke="#94a3b8" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="110" cy="5" r="5.5" fill="none" stroke={`url(#${uid}-gold)`} strokeWidth="1.6" />
      <circle cx="110" cy="5" r="2" fill="#fbbf24" />
      <circle className="login-sat-led login-sat-led-amber" cx="110" cy="5" r="1" fill="#fff7ed" />

      <line x1="80" y1="12" x2="80" y2="3" stroke="#cbd5e1" strokeWidth="1.2" strokeLinecap="round" />
      <circle className="login-sat-led login-sat-led-cyan" cx="80" cy="2.5" r="1.4" fill="#a5f3fc" />
    </svg>
  );
}
