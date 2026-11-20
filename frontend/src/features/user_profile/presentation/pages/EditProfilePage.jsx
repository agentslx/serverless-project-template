import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useAuth } from "@/features/auth/presentation/state/AuthContext";
import { MdButton } from "@/shared/ui/MdButton";
import { MdTextField } from "@/shared/ui/MdTextField";
import { getProfileUseCase } from "@/features/user_profile/domain/usecases/getProfile";
import { updateProfileUseCase } from "@/features/user_profile/domain/usecases/updateProfile";
import { appsyncProfileRepository } from "@/features/user_profile/data/repository/appsyncProfileRepository";

export default function EditProfilePage() {
  const { user } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const p = await getProfileUseCase(appsyncProfileRepository)(user.userId);
        setDisplayName(p.display_name || "");
        setAvatarUrl(p.avatar_url || "");
      } catch {
        setDisplayName(user.email?.split("@")[0] || "");
      }
    })();
  }, [user]);

  const onSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateProfileUseCase(appsyncProfileRepository)(user.userId, {
        display_name: displayName,
        avatar_url: avatarUrl || undefined,
      });
      toast.success("Profile updated.");
      navigate("/profile");
    } catch (err) {
      toast.error(err.message || "Update failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div data-testid="edit-profile-page" className="max-w-xl mx-auto flex flex-col gap-6">
      <h1 className="text-3xl font-medium tracking-tight text-on-surface">
        Edit profile
      </h1>
      <form
        onSubmit={onSave}
        className="bg-surface rounded-3xl shadow-md3-1 p-8 border border-outline-variant flex flex-col gap-5"
      >
        <MdTextField
          label="Display name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
          testid="edit-display-name-input"
        />
        <MdTextField
          label="Avatar URL (optional)"
          value={avatarUrl}
          onChange={(e) => setAvatarUrl(e.target.value)}
          testid="edit-avatar-url-input"
        />
        <div className="flex gap-3 justify-end pt-2">
          <MdButton
            type="button"
            variant="text"
            data-testid="edit-cancel-btn"
            onClick={() => navigate("/profile")}
          >
            Cancel
          </MdButton>
          <MdButton type="submit" disabled={saving} data-testid="edit-save-btn">
            {saving ? "Saving…" : "Save changes"}
          </MdButton>
        </div>
      </form>
    </div>
  );
}
