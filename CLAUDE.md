# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

Reusable serverless project template for AWS. Python backend (Lambda + clean architecture + vertical slice), two frontend options (React SPA and Next.js), Pulumi infrastructure-as-code, CI/CD pipelines, and operational scripts.

## Commands

### Backend (`backend/`) — managed with `uv`

```bash
# From project root
uv run pytest                          # all backend tests
uv run pytest backend/tests/           # backend tests only
uv run ruff check backend/             # lint
uv run ruff format backend/            # format

# From backend/
cd backend
make test                              # pytest with coverage
make lint                              # ruff check
make format                            # ruff format
make build                             # SAM build
```

### React Frontend (`frontend/react_app/`)

```bash
cd frontend/react_app
npm install
npm run dev                            # dev server
npm run build                          # production build
npm run lint                           # ESLint
npx vitest --run                       # tests (single run)
```

### Next.js Frontend (`frontend/nextjs_app/`)

```bash
cd frontend/nextjs_app
npm install
npm run dev                            # dev server
npm run build                          # production build
npm run lint                           # ESLint
```

### Infrastructure (`infrastructure/`)

```bash
cd infrastructure
pulumi preview                         # preview changes
pulumi up                              # deploy
```

### Deploy Scripts

```bash
./scripts/deploy-backend.sh dev        # deploy backend to dev
./scripts/deploy-frontend.sh dev       # deploy frontend to dev
./scripts/get-lambda-logs.sh <fn>      # fetch Lambda logs
./scripts/run-backend-local.sh         # run backend locally (SAM)
./scripts/run-frontend-local.sh react  # run React frontend locally
```

## Architecture

### Backend — Clean Architecture + Vertical Slice

Each Lambda function is a self-contained vertical slice:

```
functions/<name>/
├── presentation/handler.py    # Lambda entry, DI init, routing
├── domain/
│   ├── repository.py          # Abstract interface (ABC)
│   └── <usecase>.py           # Pure business logic
└── data/
    ├── repository_impl.py     # Concrete repository
    └── dynamodb_ds.py         # Cloud-specific datasource
```

Shared code lives in `core_python/` (entities, config, lambda utils).

**Key rule**: Domain layer must NOT import boto3, botocore, kink, or any cloud SDK.

### Infrastructure — Pulumi Service-per-File

```
infrastructure/
├── __main__.py                # Orchestrator — composes services in dependency order
└── services/
    ├── cognito.py             # Read config (pre-created outside Pulumi)
    ├── dynamodb.py            # Read config (pre-created outside Pulumi)
    ├── s3_cloudfront.py       # S3 + CloudFront
    ├── lambda_functions.py    # Lambda resources
    ├── api_gateway.py         # HTTP API + Cognito authorizer
    └── nextjs_deployment.py   # OpenNext Lambda@Edge
```

Cognito and DynamoDB are NOT created by Pulumi — they're pre-created and referenced via stack config to prevent accidental destruction.

### CI/CD — 3 GitHub Actions Workflows

- `ci.yml` — PR checks (test, lint, typecheck, pulumi preview)
- `deploy-backend.yml` — SAM build + Pulumi deploy on push
- `deploy-frontend.yml` — Build + S3 sync + CloudFront invalidation

Branch mapping: `main` → prod, `staging` → staging, `develop` → dev.

## Key Patterns

- **DI**: `kink` container, initialized at module level in handler.py (once per cold start)
- **Request parsing**: `core_python.utils.lambda_request.parse_event` — handles API GW v1/v2
- **Response formatting**: `core_python.utils.lambda_response.format_response` — includes CORS
- **Error handling**: ValidationError → 400, NotFoundError → 404, unhandled → 500 (generic message)
- **Auth**: Cognito JWT authorizer on API Gateway; Lambda receives pre-validated requests
- **Frontend auth**: React uses Amplify (tokens in memory), Next.js uses AWS SDK (tokens in httpOnly cookies)

## Common Tasks

### Add a new Lambda function

1. Create vertical slice under `backend/src/functions/<name>/`
2. Add tests under `backend/tests/functions/<name>/`
3. Register in `infrastructure/services/lambda_functions.py`
4. Add routes in `infrastructure/services/api_gateway.py`

### Add a new Pulumi resource type

1. Create `infrastructure/services/<resource>.py`
2. Import and compose in `infrastructure/__main__.py`
3. Apply `common_tags` to all resources
