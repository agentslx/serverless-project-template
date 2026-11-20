# frontend — user app

End-user React app. Talks to the **user** Cognito pool only — the admin
panel is a separate project at [`../admin-frontend`](../admin-frontend).

See [`../AGENTS.md`](../AGENTS.md) for the full clean-architecture rules.

```
src/
├── App.js                  ← routes + AppShell + AuthProvider
├── LandingPage.jsx
├── aws-config.js           ← USER pool config only
├── shared/
│   ├── entities/
│   ├── modules/            ← amplifyClient (bootstrap, gql)
│   └── ui/                 ← MdButton, MdTextField, AppShell, ProtectedRoute
└── features/
    ├── auth/               ← signup / verify / login / forgot password
    │   ├── domain/{repository,usecases}/
    │   ├── data/{datasources,repository}/
    │   └── presentation/{pages,components,state}/
    └── user_profile/        (same shape)
```

## Run

```bash
yarn install
yarn start              # http://localhost:3000  (.env.development)
yarn build              # production bundle, reads .env.production
```

## Flavours

`.env.development` and `.env.production` are auto-selected by CRA. The
GitHub deploy job rewrites `.env.development` with real Cognito + AppSync
IDs (sourced from `pulumi stack output`) before `yarn build`.

The header has an "Admin app ↗" link controlled by `REACT_APP_ADMIN_APP_URL`
(`http://localhost:3001` in dev).
