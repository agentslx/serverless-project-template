# admin · flows

## Login

```
admin-frontend  /login ──signIn(email,pw)──▶ Cognito ADMIN pool
                            ├── SUCCESS  ─▶ /admin (dashboard)
                            ├── NEW_PASSWORD_REQUIRED ─▶ /set-password (TODO)
                            └── 401      ─▶ inline error
```

## List users (P1)

```
admin-frontend  /admin/users
        │
        │  generateClient().graphql({ query: listUsers })
        ▼
AppSync (auth: admin Cognito pool)
        │
        ▼ (Lambda data source)
admin_list_users Lambda (Rust)
        │
        ├── verify caller is in admin pool (header sub + group)
        └── DynamoDB Scan / Query user_profiles
        │
        ▼
React renders Users table.
```

## Forgot password

Same two-step flow as the user app (`resetPassword` → `confirmResetPassword`),
but with a 12-character minimum and gated against the admin pool.
