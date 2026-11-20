# auth · flows

## Sign-up

```
LoginPage ─"create account"─▶ SignUpPage
                                  │
                                  ▼
        signUp(email,pw)  ─▶ Cognito user pool
        Cognito sends email with 6-digit code
                                  │
                                  ▼
        VerifyPage ─confirmSignUp(code)─▶ Cognito ─PostConfirm trigger─▶ Lambda
                                                                          │
                                                              DynamoDB Put user_profile
                                  │
                                  ▼
        signIn(email,pw)  ─▶ Cognito ─JWT─▶ AuthContext ─▶ /profile
```

## Login (user)

```
LoginPage ─signIn(email,pw)─▶ Cognito user pool
                ├── SUCCESS  ─▶ /profile
                ├── NEW_PASSWORD_REQUIRED ─▶ /set-password (handled inline)
                └── 401      ─▶ inline error
```

## Login (admin)

```
AdminLoginPage ─signIn─▶ Cognito ADMIN pool
                ├── SUCCESS ─▶ /admin
                └── 401     ─▶ inline error
(No sign-up. Admins are seeded via Pulumi `admin_create_user`.)
```

## Forgot password

```
LoginPage ─"forgot?"─▶ ForgotPasswordPage
              │
              ▼
        resetPassword(email) ─▶ Cognito (sends code)
              │
              ▼
        confirmResetPassword(email, code, newPw)
              │
              ▼
        return to LoginPage with success toast
```
