export const listUsersUseCase = (repo) => async () => {
  const all = await repo.listUsers();
  return Array.isArray(all) ? all : [];
};
