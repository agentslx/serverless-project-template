import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { useAuth } from "@/features/auth/presentation/state/AuthContext";
import { MdButton } from "@/shared/ui/MdButton";
import { getProfileUseCase } from "@/features/user_profile/domain/usecases/getProfile";
import { appsyncProfileRepository } from "@/features/user_profile/data/repository/appsyncProfileRepository";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const p = await getProfileUseCase(appsyncProfileRepository)(user.userId);
        setProfile(p);
      } catch (e) {
        // In template/local mode AppSync isn't reachable — fall back to a stub.
        setErr(e.message);
        setProfile({
          user_id: user.userId,
          email: user.email,
          display_name: user.email?.split("@")[0] || "user",
          avatar_url: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      } finally {
        setLoading(false);
      }
    })();
  }, [user]);

  if (loading) {
    return <p data-testid="profile-loading" className="text-on-surface-variant">Loading…</p>;
  }

  return (
    <div data-testid="profile-page" className="flex flex-col gap-8">
      <header className="flex items-center justify-between">
        <h1 className="text-3xl font-medium tracking-tight text-on-surface">
          Your profile
        </h1>
        <MdButton variant="text" data-testid="logout-btn" onClick={logout}>
          Sign out
        </MdButton>
      </header>

      {err && (
        <div
          data-testid="profile-warning"
          className="bg-tertiary-container text-on-tertiary-container rounded-2xl px-4 py-3 text-sm"
        >
          AppSync unreachable ({err}). Showing local fallback.
        </div>
      )}

      <section className="bg-surface rounded-3xl shadow-md3-1 p-8 border border-outline-variant flex gap-6 items-center">
        <div className="size-20 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center text-3xl font-medium">
          {profile.display_name?.[0]?.toUpperCase() || "?"}
        </div>
        <div className="flex-1">
          <p data-testid="profile-display-name" className="text-xl font-medium text-on-surface">
            {profile.display_name}
          </p>
          <p data-testid="profile-email" className="text-sm text-on-surface-variant">
            {profile.email}
          </p>
        </div>
        <Link to="/profile/edit">
          <MdButton variant="tonal" data-testid="edit-profile-btn">
            <span className="material-symbols-rounded mr-1.5 text-[18px]">edit</span>
            Edit
          </MdButton>
        </Link>
      </section>

      <Metadata profile={profile} />
    </div>
  );
}

function Metadata({ profile }) {
  const rows = [
    ["User ID", profile.user_id, "user-id"],
    ["Created", new Date(profile.created_at).toLocaleString(), "created-at"],
    ["Last update", new Date(profile.updated_at).toLocaleString(), "updated-at"],
  ];
  return (
    <section className="bg-surface rounded-3xl shadow-md3-1 p-8 border border-outline-variant">
      <h2 className="text-base font-medium text-on-surface">Account details</h2>
      <dl className="mt-4 divide-y divide-outline-variant">
        {rows.map(([k, v, t]) => (
          <div key={k} className="flex justify-between py-3 text-sm">
            <dt className="text-on-surface-variant">{k}</dt>
            <dd
              data-testid={`profile-${t}`}
              className="text-on-surface font-mono text-right break-all max-w-[60%]"
            >
              {v}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
