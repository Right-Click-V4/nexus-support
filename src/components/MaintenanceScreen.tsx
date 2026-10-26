const src = `${import.meta.env.BASE_URL}maintenance.jpg`;

export default function MaintenanceScreen({
  onAdminSignIn,
  onSignOut,
}: {
  onAdminSignIn?: () => void;
  onSignOut?: () => void;
}) {
  return (
    <div className="min-h-screen bg-[#10182b] text-white flex flex-col items-center justify-center px-4 py-8">
      <img
        src={src}
        alt="System under maintenance. Stay tuned, we're fixing it."
        className="w-full max-w-3xl rounded-2xl shadow-2xl border border-white/10"
      />
      <p className="mt-4 text-sm text-violet-100/80 text-center">
        Nexus Ops is under maintenance. Agents and customers will see this until an admin turns it off.
      </p>
      <div className="mt-4 flex gap-3">
        {onSignOut && (
          <button type="button" onClick={onSignOut} className="text-sm px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15">
            Sign out
          </button>
        )}
        {onAdminSignIn && (
          <button type="button" onClick={onAdminSignIn} className="text-sm px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500">
            Admin sign in
          </button>
        )}
      </div>
    </div>
  );
}
