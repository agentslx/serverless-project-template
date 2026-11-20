export const logoutUseCase = (repo) => async () => repo.signOut();
export const currentSessionUseCase = (repo) => async () => repo.currentSession();
