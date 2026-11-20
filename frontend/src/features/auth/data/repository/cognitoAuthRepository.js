/**
 * Concrete `AuthRepository` impl backed by Cognito (via Amplify).
 */
import { cognitoDatasource } from "@/features/auth/data/datasources/cognitoDatasource";

export const cognitoAuthRepository = {
  async signUp(email, password) {
    await cognitoDatasource.signUp(email, password);
  },
  async confirmSignUp(email, code) {
    await cognitoDatasource.confirmSignUp(email, code);
  },
  async resendCode(email) {
    await cognitoDatasource.resendCode(email);
  },
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
