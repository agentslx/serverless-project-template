export const updateProfileUseCase = (repo) => async (userId, patch) => {
  if (patch.display_name !== undefined && patch.display_name.trim().length < 2) {
    throw new Error("Display name must be ≥ 2 characters.");
  }
  return repo.updateProfile(userId, patch);
};
