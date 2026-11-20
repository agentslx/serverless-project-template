/**
 * Datasource — Amplify Auth (admin pool). The admin app intentionally does
 * NOT expose `signUp` — admin accounts are seeded via Pulumi AdminCreateUser.
 */
import {
  signIn as amplifySignIn,
  signOut as amplifySignOut,
  resetPassword,
  confirmResetPassword,
  getCurrentUser,
  fetchUserAttributes,
} from "aws-amplify/auth";

export const cognitoDatasource = {
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
