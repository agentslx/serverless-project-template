# emergent-serverless-template

Production-ready template for AWS serverless apps.

**Stack:** Rust Lambdas · DynamoDB · Cognito (user + admin) · AppSync (JS resolvers) · React + Amplify · Pulumi (Python) · GitHub Actions · `ap-southeast-2`.

```
┌─────────────────┐   ┌─────────────────┐
│  React user app │   │ React admin app │     each ships as its own
│  (Amplify v6)   │   │  (Amplify v6)   │     S3 + CloudFront bundle
└────────┬────────┘   └────────┬────────┘
         │                     │
         │     ┌──────────────┐│     ┌────────────┐     ┌────────────┐
         └────▶│  AppSync     │┴────▶│  Lambdas   │────▶│  DynamoDB  │
               │  (JS resolv.)│      │  (Rust)    │     │            │
               └──────┬───────┘      └────────────┘     └────────────┘
                      │
               ┌──────▼───────┐   user pool + admin pool
               │  Cognito     │
               └──────────────┘
```

## Quick links

| What | Where |
|---|---|
| Coding guidelines | [`AGENTS.md`](./AGENTS.md) |
| System design docs | [`system-design-doc/`](./system-design-doc/) |
| Backend (Rust) | [`backend/`](./backend/) |
| User app (React) | [`frontend/`](./frontend/) |
| Admin app (React) | [`admin-frontend/`](./admin-frontend/) |
| Infrastructure | [`iac/`](./iac/) |
| CI/CD | [`.github/workflows/`](./.github/workflows/) |

## Getting started

```bash
git clone https://github.com/<you>/emergent-serverless-template
cd emergent-serverless-template

# One-shot: install Rust, Python deps, frontend deps, run smoke tests.
./emergent_env_setup.sh

# Optional — only needed for AWS deploys (~5 min build):
INSTALL_CARGO_LAMBDA=1 ./emergent_env_setup.sh

# Deploy
pip install -r iac/requirements.txt
cd iac && pulumi stack select dev && pulumi up
```

## Local dev (no AWS account, no Docker)

```bash
./emergent_env_setup.sh                          # one-shot env bootstrap

moto_server -p 8000 &                            # DynamoDB stand-in (no Docker)
python backend/scripts/create_table.py           # create user_profiles table
cd backend/local_proxy_py && python main.py &    # :9001 — Python sub-server
cd ../ && cargo run -p local_proxy &             # :9000 — Rust proxy (FE talks here)
cd ../frontend && yarn start &                   # :3000 — user app
cd ../admin-frontend && yarn start               # :3001 — admin app
```

The local proxy simulates API Gateway routing on `http://localhost:9000`. Routes are declared in [`backend/local_proxy/routes.json`](./backend/local_proxy/routes.json) — see AGENTS.md §10.

## Features

- `auth` — Cognito flows: sign-up, verify, login, forgot password (user app); login + forgot password only (admin app).
- `user_profile` — read & update via Lambda **and** via direct AppSync JS resolver against DynamoDB.
- `admin` — admin-only dashboard + users list, gated by the admin Cognito pool.
