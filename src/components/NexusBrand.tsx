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

/** Inline star used as the letter X inside "NeXus". */
function StarXLetter({ size, color }: { size: number; color: string }) {
  return (
    <svg
      viewBox="0 0 40 40"
      width={size}
      height={size}
      fill="none"
      aria-hidden
      style={{ display: 'block', flexShrink: 0 }}
    >
      <path
        d="M8 8 L32 32 M32 8 L8 32"
        stroke={color}
        strokeWidth="6.5"
        strokeLinecap="round"
      />
      <path
        d="M20 4 L22.6 16.6 L35.5 19.2 L22.6 21.8 L20 34.5 L17.4 21.8 L4.5 19.2 L17.4 16.6 Z"
        fill={color}
      />
      <circle cx="20" cy="19.2" r="2.2" fill={color} />
    </svg>
  );
}

/**
 * Compact wordmark: Ne + star-X + us Ops as one tight unit.
 */
export function NexusWordmark({
  height = 28,
  className = '',
  color = 'currentColor',
}: {
  height?: number;
  className?: string;
  color?: string;
}) {
  const xSize = Math.round(height * 0.92);
  return (
    <span
      className={className}
      role="img"
      aria-label="NeXus Ops"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 1,
        color,
        fontFamily: 'Plus Jakarta Sans, system-ui, -apple-system, sans-serif',
        fontWeight: 700,
        fontSize: height,
        lineHeight: 1,
        letterSpacing: '-0.04em',
        whiteSpace: 'nowrap',
      }}
    >
      <span style={{ letterSpacing: '-0.06em' }}>Ne</span>
      <StarXLetter size={xSize} color={color} />
      <span style={{ letterSpacing: '-0.04em' }}>
        us<span style={{ marginLeft: '0.28em', letterSpacing: '-0.02em' }}>Ops</span>
      </span>
    </span>
  );
}

/** Compact star-X for sidebar / boot (inherits white on brand gradient). */
export function NexusBrandIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 4 L20 20 M20 4 L4 20" stroke="white" strokeWidth="3.2" strokeLinecap="round" />
      <path d="M12 2 L13.6 9.6 L21 11.2 L13.6 12.8 L12 20.5 L10.4 12.8 L3 11.2 L10.4 9.6 Z" fill="white" />
      <circle cx="12" cy="11.2" r="1.4" fill="white" />
    </svg>
  );
}
