export const loginUseCase = (repo) => async (email, password) => {
  if (!email || !password) throw new Error("Email and password are required.");
  return repo.signIn(email, password);
};
