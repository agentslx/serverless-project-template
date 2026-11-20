/** Pure usecase — orchestrates a sign-in via the injected repository. */
export const loginUseCase = (repo) => async (email, password) => {
  if (!email || !password) throw new Error("Email and password are required.");
  return repo.signIn(email, password);
};
