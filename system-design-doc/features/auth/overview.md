# Feature · auth

## Goal
Cover the four classic auth flows for the **user app** plus a login-only flow for the **admin panel**, using two separate Cognito user pools.

## Components

| Layer        | Item                                                                                     |
|--------------|------------------------------------------------------------------------------------------|
| FE pages     | `LoginPage`, `SignUpPage`, `VerifyPage`, `ForgotPasswordPage`, `AdminLoginPage`           |
| FE state     | `AuthContext` (current user, JWT, isAdmin)                                                |
| FE usecases  | `login`, `signUp`, `confirmSignUp`, `resendCode`, `forgotPassword`, `confirmForgotPassword`, `logout`, `adminLogin` |
| BE Lambda    | `post_confirmation_trigger` (Cognito post-confirm hook → seeds `user_profiles`)           |
| BE Lambda    | `get_me` (returns current user profile from JWT claims)                                   |
| Cognito      | User pool (self sign-up, email verification) + Admin pool (admin-create only)            |

## Why a Lambda for `get_me`?

Could be done by AppSync directly, but `get_me` lazily creates a profile row if a user signed up before the trigger Lambda existed (migration-friendly).

## Design notes

- We don't use Hosted UI. Everything happens through Amplify v6 modular Auth APIs.
- `AdminLoginPage` calls `Amplify.configure(adminPoolConfig)` before signing in, then resets to userPool config on logout.
- After `confirmSignUp`, frontend immediately calls `signIn` for a smooth UX.
