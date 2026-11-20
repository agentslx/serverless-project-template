export const signUpUseCase = (repo) => async (email, password) => {
  if (!email.includes("@")) throw new Error("Invalid email.");
  if (password.length < 8) throw new Error("Password must be ≥ 8 characters.");
  return repo.signUp(email, password);
};

export const confirmSignUpUseCase = (repo) => async (email, code) => {
  if (!/^[0-9]{4,8}$/.test(code)) throw new Error("Code must be 4-8 digits.");
  return repo.confirmSignUp(email, code);
};

export const resendCodeUseCase = (repo) => async (email) => repo.resendCode(email);
