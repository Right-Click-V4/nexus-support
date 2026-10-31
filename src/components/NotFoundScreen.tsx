const BASE = import.meta.env.BASE_URL || '/';
const src = `${BASE}${encodeURIComponent('404_ Monsters Overran the Station.png')}`;

export default function NotFoundScreen({
  onAdminSignIn,
  onGoHome,
}: {
  onAdminSignIn?: () => void;
  onGoHome?: () => void;
}) {
  return (
    <div className="nf-shell">
      <div className="nf-bg" aria-hidden>
        <div className="nf-grid" />
        <div className="nf-orb nf-orb-a" />
        <div className="nf-orb nf-orb-b" />
        <div className="nf-orb nf-orb-c" />
        <div className="nf-scan" />
        <div className="nf-stars" />
        <div className="nf-ring nf-ring-a" />
        <div className="nf-ring nf-ring-b" />
      </div>

      <div className="nf-content">
        <div className="nf-badge">
          <span className="nf-badge-dot" />
          Error 404 · Page not found
        </div>

        <div className="nf-frame">
          <img
            src={src}
            alt="404 — page not found. Monsters overran the station."
            className="nf-art"
          />
        </div>

        <p className="nf-copy">This page doesn't exist — or the station got overrun.</p>
        <div className="nf-actions">
          {onGoHome ? (
            <button type="button" onClick={onGoHome} className="nf-home-btn">
              Back to login
            </button>
          ) : null}
          {onAdminSignIn ? (
            <button type="button" onClick={onAdminSignIn} className="nf-admin-btn">
              Admin sign in
            </button>
          ) : null}
        </div>

        {onAdminSignIn ? (
          <button type="button" onClick={onAdminSignIn} className="nf-admin-btn">
            Admin sign in
          </button>
        ) : null}
      </div>

      <style>{`
        .nf-shell {
          position: fixed;
          inset: 0;
          z-index: 50;
          overflow: hidden;
          color: #f5f3ff;
          background: #070414;
        }
        .nf-bg {
          position: absolute;
          inset: 0;
          pointer-events: none;
          background:
            radial-gradient(ellipse 80% 55% at 50% 110%, rgba(190, 24, 93, 0.4) 0%, transparent 60%),
            radial-gradient(ellipse 40% 35% at 12% 18%, rgba(56, 189, 248, 0.12) 0%, transparent 55%),
            radial-gradient(ellipse 36% 30% at 88% 12%, rgba(244, 114, 182, 0.12) 0%, transparent 55%),
            linear-gradient(180deg, #050210 0%, #1a0618 48%, #080318 100%);
        }
        .nf-grid {
          position: absolute;
          inset: 0;
          background-image:
            linear-gradient(rgba(251, 113, 133, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(251, 113, 133, 0.07) 1px, transparent 1px);
          background-size: 48px 48px;
          mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 20%, transparent 75%);
          animation: nf-grid-drift 28s linear infinite;
        }
        .nf-orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(40px);
          opacity: 0.55;
        }
        .nf-orb-a {
          width: min(42vw, 420px);
          height: min(42vw, 420px);
          left: -8%;
          top: 18%;
          background: radial-gradient(circle, rgba(244, 63, 94, 0.5), transparent 70%);
          animation: nf-float 16s ease-in-out infinite alternate;
        }
        .nf-orb-b {
          width: min(36vw, 360px);
          height: min(36vw, 360px);
          right: -6%;
          bottom: 12%;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.35), transparent 70%);
          animation: nf-float 19s ease-in-out infinite alternate-reverse;
        }
        .nf-orb-c {
          width: min(28vw, 280px);
          height: min(28vw, 280px);
          left: 40%;
          top: -8%;
          background: radial-gradient(circle, rgba(251, 191, 36, 0.22), transparent 70%);
          animation: nf-float 22s ease-in-out infinite alternate;
        }
        .nf-scan {
          position: absolute;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, transparent, rgba(251, 113, 133, 0.7), transparent);
          box-shadow: 0 0 18px 4px rgba(244, 63, 94, 0.35);
          animation: nf-scan 7s linear infinite;
          opacity: 0.7;
        }
        .nf-stars {
          position: absolute;
          inset: 0;
          background-image:
            radial-gradient(1.5px 1.5px at 8% 20%, rgba(255,255,255,.85) 50%, transparent 52%),
            radial-gradient(1px 1px at 18% 70%, rgba(251,113,133,.9) 50%, transparent 52%),
            radial-gradient(1.5px 1.5px at 32% 35%, rgba(255,255,255,.7) 50%, transparent 52%),
            radial-gradient(1px 1px at 55% 15%, rgba(125,211,252,.8) 50%, transparent 52%),
            radial-gradient(1.2px 1.2px at 72% 62%, rgba(244,114,182,.75) 50%, transparent 52%),
            radial-gradient(1px 1px at 88% 40%, rgba(255,255,255,.65) 50%, transparent 52%);
          animation: nf-twinkle 5s ease-in-out infinite alternate;
        }
        .nf-ring {
          position: absolute;
          border-radius: 50%;
          border: 1px solid rgba(251, 113, 133, 0.16);
        }
        .nf-ring-a {
          width: min(55vw, 560px);
          height: min(55vw, 560px);
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          animation: nf-spin 48s linear infinite;
        }
        .nf-ring-b {
          width: min(38vw, 380px);
          height: min(38vw, 380px);
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          border-color: rgba(244, 63, 94, 0.1);
          animation: nf-spin 32s linear infinite reverse;
        }
        .nf-content {
          position: relative;
          z-index: 2;
          height: 100%;
          width: 100%;
          max-width: 1100px;
          margin: 0 auto;
          padding: clamp(12px, 2.5vh, 28px) clamp(12px, 3vw, 32px);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: clamp(10px, 1.8vh, 18px);
          box-sizing: border-box;
        }
        .nf-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 6px 12px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          color: #ffe4e6;
          background: rgba(244, 63, 94, 0.18);
          border: 1px solid rgba(251, 113, 133, 0.35);
          backdrop-filter: blur(8px);
        }
        .nf-badge-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #fb7185;
          box-shadow: 0 0 0 0 rgba(251, 113, 133, 0.55);
          animation: nf-pulse 1.6s ease-out infinite;
        }
        .nf-frame {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex: 0 1 auto;
          min-height: 0;
        }
        .nf-art {
          display: block;
          width: auto;
          height: auto;
          max-width: min(96vw, 920px);
          max-height: min(68vh, 640px);
          object-fit: contain;
          border-radius: 18px;
          border: 1px solid rgba(251, 113, 133, 0.28);
          box-shadow:
            0 0 0 1px rgba(255, 255, 255, 0.05) inset,
            0 24px 60px rgba(0, 0, 0, 0.55),
            0 0 50px rgba(244, 63, 94, 0.22);
          background: rgba(10, 6, 28, 0.4);
        }
        .nf-copy {
          margin: 0;
          text-align: center;
          font-size: clamp(0.9rem, 2.2vw, 1.05rem);
          line-height: 1.45;
          color: rgba(255, 228, 230, 0.92);
          max-width: 36rem;
          text-shadow: 0 1px 12px rgba(0, 0, 0, 0.45);
        }
        .nf-actions { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin-top:18px; }
        .nf-home-btn { padding:10px 20px; border-radius:999px; border:1px solid rgba(167,139,250,0.45); background:rgba(124,58,237,0.9); color:#f5f3ff; font-size:13px; font-weight:600; cursor:pointer; }
        .nf-home-btn:hover { background:rgba(139,92,246,0.95); }
        .nf-admin-btn {
          margin-top: 2px;
          padding: 0.55rem 1.1rem;
          border-radius: 0.75rem;
          border: 1px solid rgba(251, 113, 133, 0.4);
          background: linear-gradient(180deg, #f43f5e, #be123c);
          color: #fff;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          box-shadow: 0 8px 24px rgba(190, 24, 93, 0.35);
        }
        .nf-admin-btn:hover { filter: brightness(1.08); }

        @keyframes nf-grid-drift {
          from { background-position: 0 0; }
          to { background-position: 48px 48px; }
        }
        @keyframes nf-float {
          from { transform: translate3d(0, 0, 0); }
          to { transform: translate3d(18px, -22px, 0); }
        }
        @keyframes nf-scan {
          0% { top: -2%; opacity: 0; }
          8% { opacity: 0.75; }
          92% { opacity: 0.75; }
          100% { top: 102%; opacity: 0; }
        }
        @keyframes nf-twinkle {
          from { opacity: 0.45; }
          to { opacity: 0.95; }
        }
        @keyframes nf-spin {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        @keyframes nf-pulse {
          0% { box-shadow: 0 0 0 0 rgba(251, 113, 133, 0.55); }
          70% { box-shadow: 0 0 0 8px rgba(251, 113, 133, 0); }
          100% { box-shadow: 0 0 0 0 rgba(251, 113, 133, 0); }
        }

        @media (max-height: 700px) {
          .nf-art { max-height: min(58vh, 480px); }
          .nf-badge { font-size: 10px; padding: 4px 10px; }
        }
        @media (max-width: 640px) {
          .nf-art {
            max-width: 96vw;
            max-height: min(55vh, 420px);
            border-radius: 14px;
          }
          .nf-copy { font-size: 0.9rem; padding: 0 4px; }
        }
        @media (prefers-reduced-motion: reduce) {
          .nf-grid, .nf-orb, .nf-scan, .nf-stars, .nf-ring, .nf-badge-dot {
            animation: none !important;
          }
        }
      `}</style>
    </div>
  );
}
