# Feature · admin

## Goal
A separate, segregated admin panel — its **own React bundle**, **own S3 +
CloudFront distribution**, signed in against the **admin Cognito pool**.

## Why a second app, not a route?

| Concern                  | Single-app + `/admin` route        | Two apps                              |
|--------------------------|------------------------------------|---------------------------------------|
| Accidental cross-pool sign-in | possible (runtime swap)        | impossible (admin app never knows about the user pool) |
| Bundle separation        | one big bundle                     | admin bundle never reaches end-user browsers |
| CloudFront WAF / IP allow-list | hard (one CDN)               | trivial (separate distribution)       |
| Deploy cadence           | coupled                            | independent                           |

## Components

| Layer       | Item                                                                 |
|-------------|----------------------------------------------------------------------|
| FE pages    | `LoginPage`, `ForgotPasswordPage`, `AdminDashboardPage`, `UsersListPage` |
| FE state    | `AuthContext` (admin only)                                           |
| FE usecases | `login`, `forgotPassword`, `confirmForgotPassword`, `logout`, `listUsers` |
| BE Lambda   | `admin_list_users` (P1, not yet implemented — see PRD)               |
| AppSync     | `Query.listUsers` resolver gated by admin Cognito pool (P1)          |
| Cognito     | Admin pool (admin-create only, MFA optional)                         |

## Why no sign-up?

Admins are seeded server-side via:

```bash
aws cognito-idp admin-create-user \
  --user-pool-id $ADMIN_POOL_ID \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true \
  --temporary-password 'TempP@ssword12!' \
  --message-action SUPPRESS
```

This means the admin app's auth feature deliberately omits `signUp.js`,
`verify.js`, etc. — they don't compile into the bundle.
