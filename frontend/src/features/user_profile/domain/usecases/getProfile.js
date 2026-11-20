export const getProfileUseCase = (repo) => async (userId) => {
  if (!userId) throw new Error("Missing userId.");
  const p = await repo.getProfile(userId);
  if (!p) throw new Error("Profile not found.");
  return p;
};
