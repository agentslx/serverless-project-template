# admin-frontend

Standalone React app for the **admin panel**. Talks to the **admin** Cognito user pool only — *no* awareness of the user pool.

Why a separate app?
- Prevents accidental cross-pool sign-in flows.
- Lets you ship the admin bundle behind its own CloudFront distribution, IP-restricted or VPN-gated.
- Different CSP, different bundle, different deploy cadence.

## Run locally

```bash
cd admin-frontend
yarn install
yarn start          # http://localhost:3001  (PORT is hard-coded in package.json)
```

## Layout

```
src/
├── App.js                    routes + AdminShell + AuthProvider
├── aws-config.js             admin Cognito pool ONLY
├── shared/
│   ├── entities/
│   ├── modules/amplifyClient.js
│   └── ui/{MdButton, MdTextField, AdminShell, ProtectedRoute}
└── features/
    ├── auth/                 (login + forgot-password — NO sign-up)
    │   ├── domain/{repository,usecases}/
    │   ├── data/{datasources,repository}/
    │   └── presentation/{pages,components,state}/
    └── admin/                (dashboard + users list)
        ├── domain/{repository,usecases}/
        ├── data/{datasources,repository}/
        └── presentation/pages/
```

## Environment

`.env.development` and `.env.production` are flavour-specific. The Pulumi
`deploy-dev` workflow rewrites `.env.development` with real `pulumi stack
output` values before `yarn build`.

## Important

There is **no** `signUp` page. Admin accounts are created server-side via:

```bash
aws cognito-idp admin-create-user \
  --user-pool-id $ADMIN_POOL_ID \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true \
  --temporary-password 'TempP@ssword12!' \
  --message-action SUPPRESS
```

(See `iac/application/lambdas.py` for the eventual seeding helper.)
