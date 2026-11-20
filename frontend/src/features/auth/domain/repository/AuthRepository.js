/**
 * Domain interface (JSDoc-typed) for the auth feature.
 *
 * @typedef {Object} AuthRepository
 * @property {(email:string, password:string) => Promise<void>} signUp
 * @property {(email:string, code:string) => Promise<void>} confirmSignUp
 * @property {(email:string) => Promise<void>} resendCode
 * @property {(email:string, password:string) => Promise<{userId:string,email:string}>} signIn
 * @property {() => Promise<{userId:string,email:string}|null>} currentSession
 * @property {() => Promise<void>} signOut
 * @property {(email:string) => Promise<void>} forgotPassword
 * @property {(email:string, code:string, newPassword:string) => Promise<void>} confirmForgotPassword
 */

export const AuthRepository = {};
