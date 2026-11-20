/**
 * Datasource — talks directly to Amplify Auth (Cognito).
 * Lives in `data/datasources/`. The repository wraps this so usecases never
 * see Amplify types.
 */
import {
  signUp as amplifySignUp,
  confirmSignUp as amplifyConfirm,
  resendSignUpCode,
  signIn as amplifySignIn,
  signOut as amplifySignOut,
  resetPassword,
  confirmResetPassword,
  getCurrentUser,
  fetchUserAttributes,
} from "aws-amplify/auth";

export const cognitoDatasource = {
  signUp: (email, password) =>
    amplifySignUp({
      username: email,
      password,
      options: { userAttributes: { email } },
    }),

  confirmSignUp: (email, code) =>
    amplifyConfirm({ username: email, confirmationCode: code }),

  resendCode: (email) => resendSignUpCode({ username: email }),

  signIn: (email, password) => amplifySignIn({ username: email, password }),

  signOut: () => amplifySignOut(),

  forgotPassword: (email) => resetPassword({ username: email }),

  confirmForgotPassword: (email, code, newPassword) =>
    confirmResetPassword({ username: email, confirmationCode: code, newPassword }),

  currentUser: async () => {
    const u = await getCurrentUser();
    const attrs = await fetchUserAttributes().catch(() => ({}));
    return { userId: u.userId, email: attrs.email || u.signInDetails?.loginId || "" };
  },
};
