/** NeXus Ops star-X brand mark and wordmark. */

export function NexusLogoMark({ size = 56, className = '' }: { size?: number; className?: string }) {
  return (
    <div className={`login-logo-mark ${className}`.trim()} style={{ width: size, height: size }}>
      <svg viewBox="0 0 48 48" width={size} height={size} fill="none" aria-hidden>
        <path
          d="M10 10 L38 38 M38 10 L10 38"
          stroke="#ffffff"
          strokeWidth="7.5"
          strokeLinecap="round"
        />
        <path
          d="M24 6 L27.2 20.8 L42 24 L27.2 27.2 L24 42 L20.8 27.2 L6 24 L20.8 20.8 Z"
          fill="#ffffff"
        />
        <circle cx="24" cy="24" r="3.2" fill="#ffffff" />
      </svg>
    </div>
  );
}

/** Letter-sized star-X used inside the wordmark — optically aligned as letter X. */
function LetterX({ size, color }: { size: number; color: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      width={size}
      height={size}
      fill="none"
      aria-hidden
      style={{
        display: 'inline-block',
        // Optical center with capital letters (slight lift, not drop)
        verticalAlign: 'middle',
        position: 'relative',
        top: '-0.02em',
        margin: '0 -0.02em',
      }}
    >
      <path d="M6 6 L26 26 M26 6 L6 26" stroke={color} strokeWidth="5.5" strokeLinecap="round" />
      <path
        d="M16 3 L18 13.5 L28.5 15.5 L18 17.5 L16 28 L14 17.5 L3.5 15.5 L14 13.5 Z"
        fill={color}
      />
      <circle cx="16" cy="15.5" r="1.8" fill={color} />
    </svg>
  );
}

/** Clean wordmark: NeXus Ops with star-X as the letter X (tight, one word). */
export function NexusWordmark({
  height = 28,
  className = '',
  color = 'currentColor',
}: {
  height?: number;
  className?: string;
  color?: string;
}) {
  const xSize = Math.round(height * 0.72);
  return (
    <span
      className={className}
      role="img"
      aria-label="NeXus Ops"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        color,
        fontFamily: 'Plus Jakarta Sans, system-ui, -apple-system, sans-serif',
        fontWeight: 700,
        fontSize: height,
        lineHeight: 1,
        letterSpacing: '-0.045em',
        whiteSpace: 'nowrap',
      }}
    >
      <span style={{ lineHeight: 1 }}>Ne</span>
      <LetterX size={xSize} color={color} />
      <span style={{ lineHeight: 1 }}>
        us
        <span style={{ marginLeft: '0.22em', letterSpacing: '-0.03em' }}>Ops</span>
      </span>
    </span>
  );
}

/** Compact star-X for sidebar / boot. */
export function NexusBrandIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 4 L20 20 M20 4 L4 20" stroke="white" strokeWidth="3.2" strokeLinecap="round" />
      <path d="M12 2 L13.6 9.6 L21 11.2 L13.6 12.8 L12 20.5 L10.4 12.8 L3 11.2 L10.4 9.6 Z" fill="white" />
      <circle cx="12" cy="11.2" r="1.4" fill="white" />
    </svg>
  );
}
