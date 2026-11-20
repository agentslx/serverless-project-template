import { cognitoDatasource } from "@/features/auth/data/datasources/cognitoDatasource";

export const cognitoAuthRepository = {
  async signIn(email, password) {
    await cognitoDatasource.signIn(email, password);
    return cognitoDatasource.currentUser();
  },
  async signOut() {
    await cognitoDatasource.signOut();
  },
  async currentSession() {
    try {
      return await cognitoDatasource.currentUser();
    } catch {
      return null;
    }
  },
  async forgotPassword(email) {
    await cognitoDatasource.forgotPassword(email);
  },
  async confirmForgotPassword(email, code, newPassword) {
    await cognitoDatasource.confirmForgotPassword(email, code, newPassword);
  },
};
