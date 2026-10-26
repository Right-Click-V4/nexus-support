const BASE = import.meta.env.BASE_URL || '/';
const ART = '404_ Monsters Overran the Station.png';
const src = `${BASE}${encodeURIComponent(ART)}`;

export default function NotFoundScreen({
  onAdminSignIn,
}: {
  onAdminSignIn?: () => void;
  onGoHome?: () => void;
}) {
  return (
    <div className="maint-shell">
      <div className="maint-bg" aria-hidden>
        <div className="maint-grid" />
        <div className="maint-orb maint-orb-a" />
        <div className="maint-orb maint-orb-b" />
        <div className="maint-orb maint-orb-c" />
        <div className="maint-scan" />
        <div className="maint-stars" />
      </div>

      <div className="maint-content">
        <div className="maint-badge">
          <span className="maint-badge-dot" />
          Error 404 · Page not found
        </div>

        <div className="maint-frame">
          <img
            src={src}
            alt="404 — page not found. Monsters overran the station."
            className="maint-art"
            onError={(e) => {
              const el = e.currentTarget;
              el.style.display = 'none';
              const hint = el.nextElementSibling as HTMLElement | null;
              if (hint) hint.style.display = 'block';
            }}
          />
          <div className="maint-missing" style={{ display: 'none' }}>
            <div className="maint-missing-title">404</div>
            <div className="maint-missing-sub">Station overrun</div>
          </div>
        </div>

        <p className="maint-copy">
          This page doesn't exist — or the station got overrun.
        </p>

        {onAdminSignIn ? (
          <div className="maint-actions">
            <button type="button" onClick={onAdminSignIn} className="maint-admin-btn">
              Admin sign in
            </button>
          </div>
        ) : null}
      </div>

      <style>{`
        .maint-shell {
          position: fixed; inset: 0; z-index: 50; overflow: hidden;
          color: #f5f3ff; background: #070414;
        }
        .maint-bg {
          position: absolute; inset: 0; pointer-events: none;
          background:
            radial-gradient(ellipse 80% 55% at 50% 110%, rgba(190, 24, 93, 0.35) 0%, transparent 60%),
            radial-gradient(ellipse 40% 35% at 12% 18%, rgba(56, 189, 248, 0.12) 0%, transparent 55%),
            linear-gradient(180deg, #050210 0%, #1a0618 48%, #080318 100%);
        }
        .maint-grid {
          position: absolute; inset: 0;
          background-image:
            linear-gradient(rgba(251, 113, 133, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(251, 113, 133, 0.07) 1px, transparent 1px);
          background-size: 48px 48px;
          mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 20%, transparent 75%);
          animation: maint-grid-drift 28s linear infinite;
        }
        .maint-orb { position: absolute; border-radius: 50%; filter: blur(40px); opacity: 0.55; }
        .maint-orb-a {
          width: min(42vw, 420px); height: min(42vw, 420px); left: -8%; top: 18%;
          background: radial-gradient(circle, rgba(244, 63, 94, 0.45), transparent 70%);
          animation: maint-float 16s ease-in-out infinite alternate;
        }
        .maint-orb-b {
          width: min(36vw, 360px); height: min(36vw, 360px); right: -6%; bottom: 12%;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.35), transparent 70%);
          animation: maint-float 19s ease-in-out infinite alternate-reverse;
        }
        .maint-orb-c {
          width: min(28vw, 280px); height: min(28vw, 280px); left: 40%; top: -8%;
          background: radial-gradient(circle, rgba(251, 191, 36, 0.22), transparent 70%);
          animation: maint-float 22s ease-in-out infinite alternate;
        }
        .maint-scan {
          position: absolute; left: 0; right: 0; height: 2px;
          background: linear-gradient(90deg, transparent, rgba(251, 113, 133, 0.7), transparent);
          box-shadow: 0 0 18px 4px rgba(244, 63, 94, 0.35);
          animation: maint-scan 7s linear infinite; opacity: 0.7;
        }
        .maint-stars {
          position: absolute; inset: 0;
          background-image:
            radial-gradient(1.5px 1.5px at 8% 20%, rgba(255,255,255,.85) 50%, transparent 52%),
            radial-gradient(1px 1px at 18% 70%, rgba(251,113,133,.9) 50%, transparent 52%),
            radial-gradient(1.5px 1.5px at 32% 35%, rgba(255,255,255,.7) 50%, transparent 52%),
            radial-gradient(1px 1px at 55% 15%, rgba(125,211,252,.8) 50%, transparent 52%);
          animation: maint-twinkle 5s ease-in-out infinite alternate;
        }
        .maint-content {
          position: relative; z-index: 2;
          height: 100%; width: 100%;
          max-width: 1200px; margin: 0 auto;
          padding: clamp(8px, 1.5vh, 16px) clamp(10px, 2vw, 20px);
          display: flex; flex-direction: column; align-items: center; justify-content: center;
          gap: clamp(8px, 1.2vh, 14px); box-sizing: border-box;
        }
        .maint-badge {
          display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 999px;
          font-size: 11px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase;
          color: #ffe4e6; background: rgba(244, 63, 94, 0.18); border: 1px solid rgba(251, 113, 133, 0.35);
          flex-shrink: 0;
        }
        .maint-badge-dot {
          width: 7px; height: 7px; border-radius: 50%; background: #fb7185;
          animation: maint-pulse 1.6s ease-out infinite;
        }
        .maint-frame {
          width: min(92vw, 720px);
          height: min(68vh, 680px);
          flex: 0 1 auto;
          display: flex; align-items: center; justify-content: center;
          overflow: hidden;
          background: transparent;
          border: none;
          box-shadow: none;
          padding: 0;
        }
        .maint-art {
          display: block;
          width: 100%;
          height: 100%;
          object-fit: cover;
          /* Mild scale crops gray/silver border without blowing past the viewport */
          transform: scale(1.1);
          transform-origin: center center;
          border: none;
          border-radius: 0;
          box-shadow: none;
          background: transparent;
          outline: none;
        }
        .maint-missing {
          text-align: center; padding: 2rem 1.5rem;
          border-radius: 18px; border: 1px solid rgba(251, 113, 133, 0.25);
          background: rgba(10, 6, 28, 0.55);
        }
        .maint-missing-title {
          font-size: clamp(3rem, 12vw, 5rem); font-weight: 800; line-height: 1;
          background: linear-gradient(180deg, #fb7185, #f43f5e);
          -webkit-background-clip: text; background-clip: text; color: transparent;
        }
        .maint-missing-sub { margin-top: 0.5rem; color: #fecdd3; font-size: 0.95rem; }
        .maint-copy {
          margin: 0; text-align: center; font-size: clamp(0.85rem, 2vw, 1rem); line-height: 1.4;
          color: rgba(255, 228, 230, 0.92); max-width: 36rem;
          flex-shrink: 0;
        }
        .maint-actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; flex-shrink: 0; }
        .maint-admin-btn {
          padding: 0.55rem 1.1rem; border-radius: 0.75rem;
          border: 1px solid rgba(251, 113, 133, 0.4);
          background: linear-gradient(180deg, #f43f5e, #be123c);
          color: #fff; font-size: 0.875rem; font-weight: 600; cursor: pointer;
        }
        .maint-admin-btn:hover { filter: brightness(1.08); }
        @keyframes maint-grid-drift { from { background-position: 0 0; } to { background-position: 48px 48px; } }
        @keyframes maint-float { from { transform: translate3d(0,0,0); } to { transform: translate3d(18px,-22px,0); } }
        @keyframes maint-scan { 0% { top: -2%; opacity: 0; } 8% { opacity: 0.75; } 92% { opacity: 0.75; } 100% { top: 102%; opacity: 0; } }
        @keyframes maint-twinkle { from { opacity: 0.45; } to { opacity: 0.95; } }
        @keyframes maint-pulse {
          0% { box-shadow: 0 0 0 0 rgba(251, 113, 133, 0.55); }
          70% { box-shadow: 0 0 0 8px rgba(251, 113, 133, 0); }
          100% { box-shadow: 0 0 0 0 rgba(251, 113, 133, 0); }
        }
        @media (max-width: 640px) {
          .maint-frame {
            width: min(94vw, 420px);
            height: min(58vh, 480px);
          }
          .maint-art { transform: scale(1.12); }
        }
      `}</style>
    </div>
  );
}
