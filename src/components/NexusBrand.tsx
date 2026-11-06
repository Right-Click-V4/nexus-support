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

export function NexusWordmark({
  height = 28,
  className = '',
  color = 'currentColor',
}: {
  height?: number;
  className?: string;
  color?: string;
}) {
  const width = Math.round(height * 5.6);
  return (
    <svg
      viewBox="0 0 280 50"
      width={width}
      height={height}
      className={className}
      fill={color}
      role="img"
      aria-label="NeXus Ops"
    >
      <text
        x="0"
        y="36"
        fontFamily="Plus Jakarta Sans, system-ui, -apple-system, sans-serif"
        fontSize="34"
        fontWeight="700"
        letterSpacing="-0.5"
      >
        Ne
      </text>
      <g transform="translate(52, 4)">
        <path
          d="M6 6 L36 36 M36 6 L6 36"
          stroke={color}
          strokeWidth="7"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M21 0 L24.1 15.2 L39.5 18.5 L24.1 21.8 L21 37 L17.9 21.8 L2.5 18.5 L17.9 15.2 Z"
          fill={color}
        />
        <circle cx="21" cy="18.5" r="2.6" fill={color} />
      </g>
      <text
        x="98"
        y="36"
        fontFamily="Plus Jakarta Sans, system-ui, -apple-system, sans-serif"
        fontSize="34"
        fontWeight="700"
        letterSpacing="-0.5"
      >
        us Ops
      </text>
    </svg>
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
