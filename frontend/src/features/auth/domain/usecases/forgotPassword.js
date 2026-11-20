export const forgotPasswordUseCase = (repo) => async (email) => {
  if (!email) throw new Error("Email is required.");
  return repo.forgotPassword(email);
};

export const confirmForgotPasswordUseCase =
  (repo) => async (email, code, newPassword) => {
    if (!/^[0-9]{4,8}$/.test(code)) throw new Error("Code must be 4-8 digits.");
    if (newPassword.length < 8) throw new Error("Password must be ≥ 8 chars.");
    return repo.confirmForgotPassword(email, code, newPassword);
  };
