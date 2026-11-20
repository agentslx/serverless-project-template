# AGENTS.md — Coding Guidelines for `emergent-serverless-template`

> A reference for both human and AI contributors. Read this **before** writing any code.

---

## 1. Project at a glance

| Layer            | Tech                                                |
|------------------|-----------------------------------------------------|
| Frontends (×2)   | React 19 + TailwindCSS (Material-style) + Amplify   |
| API              | AWS AppSync (GraphQL) + API Gateway → Lambda (Rust) |
| Auth             | Amazon Cognito (2 pools: `user`, `admin`)           |
| Database         | Amazon DynamoDB                                     |
| Hosting (FE)     | Amazon S3 + CloudFront (one distribution per app)   |
| Infra-as-Code    | Pulumi (Python)                                     |
| CI/CD            | GitHub Actions                                      |
| Region (default) | `ap-southeast-2`                                    |

**Two physically separate React apps** — see §5.

Two flavours / environments are first-class everywhere: **`dev`** and **`prod`**.

---

## 2. Repository layout

```
.
├── AGENTS.md                       ← you are here
├── README.md
├── system-design-doc/              ← design / architecture / per-feature docs
│   ├── architecture/
│   ├── coding/
│   └── features/<feature>/
├── backend/                        ← Rust + Python serverless workspace
│   ├── Cargo.toml                  (Rust workspace root)
│   ├── configs/{dev,prod}.toml
│   ├── shared/
│   │   ├── entities_rs/            ← plain types (Rust)
│   │   ├── modules_rs/             ← shared Rust modules (db, common, …)
│   │   ├── entities_py/            ← plain types (Python mirror)
│   │   └── modules_py/             ← shared Python modules
│   ├── feature/<name>_rs/          ← Rust impl  (clean architecture)
│   │   ├── domain/
│   │   │   ├── usecases/           (pure business logic)
│   │   │   └── repository/         (traits / interfaces)
│   │   ├── data/
│   │   │   ├── datasources/        (DynamoDB, Cognito, S3, cache, …)
│   │   │   ├── models/             (DTO ↔ entity transformers)
│   │   │   └── repository/         (impl of domain/repository traits)
│   │   ├── presentation/
│   │   │   ├── lambda_handlers/    (one folder = one Lambda binary, one per protocol)
│   │   │   └── graphql_resolvers/  (APPSYNC_JS, JavaScript)
│   │   └── tests/
│   ├── feature/<name>_py/          ← Python parallel (same shape)
│   │   ├── domain/{usecases,repository}/
│   │   ├── data/{datasources,models,repository}/
│   │   ├── presentation/lambda_handlers/<name>/handler.py
│   │   └── tests/
│   ├── local_proxy/                (Rust binary — single FE entrypoint, port 9000)
│   │   ├── routes.json             ← THE source of truth for routes
│   │   └── src/{main,config,state,router,dispatch_rs,dispatch_py,handlers,proxy_types}.rs
│   └── local_proxy_py/             (Python sub-server, port 9001)
│       ├── main.py                 (FastAPI, reads same routes.json)
│       └── requirements.txt
├── frontend/                       ← User React app (Amplify)
│   └── src/
│       ├── shared/{entities,modules,ui}
│       └── features/<feature>/{domain,data,presentation}
├── admin-frontend/                 ← Admin React app (Amplify, separate bundle)
│   └── src/                          (same shape, admin Cognito pool ONLY)
├── iac/                            ← Pulumi Python
│   ├── __main__.py                 (thin orchestrator only)
│   ├── infrastructure/             (VPC, S3, DynamoDB, Cognito, AppSync, CDN…)
│   └── application/                (Lambdas, FE deployment)
└── .github/workflows/              (CI/CD pipelines)
```

---

## 3. Clean architecture rules (apply to **every** feature, FE & BE)

```
presentation  →  domain  ←  data
                  ↑
            (entities live in shared/)
```

### Hard rules

1. **Direction of dependency is one-way:** `presentation → domain ← data`. Never the reverse.
2. **`domain/`** must be pure. No SDK imports. No `aws-sdk-*`, `dynamodb`, `cognito`, `axios`, `react`, etc.
3. **`domain/repository/`** holds only **traits / interfaces**. Concrete impls go to `data/repository/`.
4. **`data/models/`** holds DTOs and `from_dynamo_item()` / `to_dynamo_item()` style transformers.
   - **Repository inputs/outputs are always `shared/entities/` types**, never models.
5. **`data/datasources/`** is the only place that may import infrastructure SDKs.
6. **`data/repository/`** orchestrates one or more datasources (e.g. cache + db) and converts models → entities.
7. **`presentation/`** depends **only on `domain/usecases`**, never on `data/*`.
   - For backend, presentation = a Lambda handler binary.
   - For frontend, presentation = pages + state.
8. **No cross-feature imports.** Feature A must **never** import from feature B.
   Shared logic belongs in `shared/`. If two features start needing the same module, lift it to `shared/modules/`.
9. **`shared/entities/`** are plain types. `from_json` / `to_json` / `clone` are OK. `from_dynamo_item` is **NOT** — that lives in `data/models/`.

### Naming conventions

| Layer                 | Rust                          | JS / React                    |
|-----------------------|-------------------------------|-------------------------------|
| usecase               | `get_user_profile.rs`         | `getUserProfile.js`           |
| repository trait      | `UserProfileRepository`       | `UserProfileRepository`       |
| repository impl       | `DynamoUserProfileRepository` | `AppSyncUserProfileRepository`|
| datasource            | `dynamo_datasource.rs`        | `appsync_datasource.js`       |
| model                 | `DynamoUserProfileModel`      | `AppSyncUserProfileModel`     |
| handler / page        | `user_profile_handler/main.rs`| `ProfilePage.jsx`             |

---

## 4. Backend specifics

The backend hosts **two languages side-by-side**: Rust (default) and Python.
Every feature can ship as `<name>_rs` and/or `<name>_py`. The IaC and the
local proxy default to the Rust versions; Python parallels exist so a
project can pick the right tool per function.

### 4.1 Rust (default)

- One Cargo **workspace** at `backend/Cargo.toml`. Each feature is a library crate; each Lambda handler is its own binary crate.
- **One Lambda per feature per communication protocol.** A feature's operations that share the same protocol (e.g. all HTTP/AppSync resolvers) are consolidated into a single Lambda binary that routes internally (by HTTP method, AppSync `action` field, or WebSocket `routeKey`). Split into separate Lambdas only when protocols differ (e.g. AppSync vs Cognito trigger vs WebSocket).
- Each consolidated handler lives at `backend/feature/<f>_rs/presentation/lambda_handlers/<feature>_handler/`. It initialises shared resources (DynamoDB client, repository, use cases) once in `main()` and routes requests to the appropriate use case in the `service_fn` closure.
- Use `lambda_runtime` (or `lambda_http` for API Gateway / AppSync) + `tokio`.
- Logging: `tracing` + `tracing-subscriber` with JSON format.
- Errors: feature-local error enum that maps to `shared_entities_rs::AppError` at the boundary.
- Configuration: read from environment variables only.

### 4.2 Python (parallel)

- No build step — Python is shipped as-is to Lambda. Runtime: `python3.12`.
- **Same "one Lambda per feature per protocol" rule applies.** A consolidated handler routes by HTTP method, AppSync `action` field, or WebSocket `routeKey`.
- Each handler module exposes **both**:
  - `handler(event, context)` — the AWS Lambda entrypoint.
  - `invoke(req)` — the canonical proxy entrypoint (`{method,path,headers,path_params,json_body}`).
  Sharing logic via the same usecase keeps duplication minimal.
- DB access via `boto3.resource("dynamodb")` from `shared/modules_py/database.py`.
- Errors: raise `shared.entities_py.AppError(AppErrorKind.X, "msg")`. The handler converts via `shared/modules_py/common.error_response`.
- Tests: `pytest` under `feature/<f>_py/tests/`.

### 4.3 Cross-language rules

- **Same clean architecture in both languages** — domain/data/presentation, no cross-feature imports, datasources only in `data/datasources/`.
- The **shared/entities_py** type for `UserProfile` MUST stay structurally identical to **shared/entities_rs** — DynamoDB items must be readable by both (`from_item` ↔ `from_item`).
- A given feature can be `_rs` only, `_py` only, or both. Try not to keep both versions long-term; converge on one once the choice is made.

### 4.4 Tests

Each feature has:
- `tests/unit_test.rs` (Rust) / `tests/test_unit.py` (Python) — usecases mocked against a fake repository.
- `tests/integration_test.rs` (Rust) — handler invoked end-to-end with a stub HTTP event and a local DynamoDB. Python integration tests can be added the same way under `tests/test_integration.py`.

---

## 5. Frontend specifics

### Two physically separate apps

| App              | Path                 | Cognito pool   | Routes                                   | Sign-up?           |
|------------------|----------------------|----------------|------------------------------------------|--------------------|
| **User**         | `frontend/`          | `user_pool`    | `/`, `/login`, `/signup`, `/verify`, `/forgot`, `/profile`, `/profile/edit` | yes, self-serve   |
| **Admin**        | `admin-frontend/`    | `admin_pool`   | `/login`, `/forgot`, `/admin`, `/admin/users` | **no** — `AdminCreateUser` only |

They are **independent React projects** with their own `package.json`, `node_modules`, build pipeline and S3+CloudFront distribution. Neither imports from the other; the small set of UI primitives (`MdButton`, `MdTextField`, etc.) is duplicated by design — that beats a half-baked monorepo for a template.

Why two apps?
- A single bundle that swaps Cognito pools at runtime makes accidental cross-pool sign-in trivially easy.
- Different bundles can sit behind different CloudFront / WAF rules (admin behind VPN, IP allow-list, mTLS …).
- Different deploy cadences (admin can ship hourly, user app ships weekly).

### Shared rules (apply to both apps)

- Routing: `react-router-dom` v7.
- Auth: `aws-amplify` v6 (`Auth` for Cognito, `API`/`generateClient` for AppSync).
- Design system: TailwindCSS with a Material-inspired token set. Avoid Inter/Helvetica, purple-on-white gradients, "centered AI hero" patterns. Use `Roboto Flex` (variable) + `Material Symbols Rounded`. The user app uses an **indigo** primary; the admin app uses a **deep-navy** primary so they're visually distinct at a glance.
- State: React context per feature (`features/<f>/presentation/state/`). No global redux.
- Every interactive element gets a `data-testid` (kebab-case, function-not-style).
- Configs:
  - User app `.env.{development,production}` defines `REACT_APP_AWS_REGION`, `REACT_APP_USER_POOL_ID`, `REACT_APP_USER_POOL_CLIENT_ID`, `REACT_APP_APPSYNC_URL`, `REACT_APP_ADMIN_APP_URL`, `REACT_APP_LOCAL_PROXY_URL` (dev only).
  - Admin app `.env.{development,production}` defines `REACT_APP_AWS_REGION`, `REACT_APP_ADMIN_POOL_ID`, `REACT_APP_ADMIN_POOL_CLIENT_ID`, `REACT_APP_APPSYNC_URL`, `REACT_APP_USER_APP_URL`.

---

## 6. Infrastructure-as-Code (Pulumi, Python)

- `__main__.py` is a **thin orchestrator** — just imports & wires.
- `infrastructure/` owns long-lived resources (DynamoDB tables, Cognito user pools, AppSync API, S3 + CloudFront, IAM).
- `application/` owns deployable artefacts (Lambda functions, FE bundle upload, AppSync data sources & resolvers).
- One Pulumi stack per env: `dev`, `prod`. `Pulumi.<stack>.yaml` carries env-specific config.
- Never hardcode account IDs, ARNs, region. Read from stack config or AWS provider.

---

## 7. CI/CD (GitHub Actions)

| Workflow            | Triggers                          | What it does                            |
|---------------------|-----------------------------------|-----------------------------------------|
| `backend-ci.yml`    | PR touching `backend/**`          | `cargo fmt --check`, `clippy`, tests    |
| `frontend-ci.yml`   | PR touching `frontend/**`         | `yarn lint`, `yarn build`, jest tests   |
| `iac-ci.yml`        | PR touching `iac/**`              | `pulumi preview` against `dev`          |
| `deploy-dev.yml`    | push to `develop`                 | build → `pulumi up --stack dev`         |
| `deploy-prod.yml`   | push tag `v*.*.*`                 | build → `pulumi up --stack prod`        |

Secrets required on the repo:
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `PULUMI_ACCESS_TOKEN`.

---

## 8. Local development quick-start

> **First time on a fresh sandbox / machine?** Run `./emergent_env_setup.sh`
> from the repo root. It installs Rust, Python deps (FastAPI, moto, pytest),
> Pulumi deps, and `yarn install`s both frontends, then verifies everything
> with `cargo build`, `cargo test` and `pytest`. Idempotent — safe to re-run.

```bash
# Backend (terminal 1) — Rust proxy on 9000 (single FE entrypoint)
cd backend
cargo build --workspace
cargo run -p local_proxy

# Backend (terminal 2) — Python sub-server on 9001 (only if you have python routes)
cd backend/local_proxy_py
pip install -r requirements.txt
python main.py

# DynamoDB local (terminal 3)
docker run -p 8000:8000 amazon/dynamodb-local

# User app (terminal 4)
cd frontend && yarn install && yarn start          # http://localhost:3000

# Admin app (terminal 5)
cd admin-frontend && yarn install && yarn start    # http://localhost:3001
```

The frontends talk only to `http://localhost:9000` — language routing is invisible to them.

---

## 9. Do / Don't (cheatsheet)

| ✅ Do                                                | ❌ Don't                                            |
|-----------------------------------------------------|----------------------------------------------------|
| Put SDK calls only in `data/datasources/`           | Import `aws-sdk` / `boto3` inside `domain/`       |
| Return `shared/entities_*` types from repositories  | Return DynamoDB attribute maps from repositories   |
| Add a new `feature/<x>_<lang>/` for new context     | Cross-import between features (incl. across langs) |
| Use env vars for every config value                 | Hardcode account IDs, region, table names          |
| Keep `__main__.py` < 30 lines                       | Stuff all Pulumi resources into `__main__.py`      |
| Document new flows under `system-design-doc/...`    | Land code without updating the design doc          |
| Update `routes.json` whenever you add a route       | Hardcode route paths in `local_proxy/src/...`      |

---

## 10. routes.json convention (local proxy)

`backend/local_proxy/routes.json` is the **single source of truth** for every
route the frontend can call locally. Both `local_proxy` (Rust) and
`local_proxy_py` (Python sub-server) read this file at startup.

```json
{
  "python_subserver_url": "http://localhost:9001",
  "routes": [
    { "method": "GET",   "path": "/api/me",                   "handler": "get_me",         "language": "rust"   },
    { "method": "GET",   "path": "/api/profile/:user_id",     "handler": "get_profile",    "language": "rust"   },
    { "method": "PATCH", "path": "/api/profile/:user_id",     "handler": "update_profile", "language": "rust"   },
    { "method": "GET",   "path": "/api/health",               "handler": "health",         "language": "python" }
  ]
}
```

> Note: even though `get_profile` and `update_profile` are served by the same
> Lambda in production (`handler_user_profile`), the local proxy keeps separate
> handler names for clarity. The proxy's own routing logic already consolidates
> them into a single shared state.

**Path syntax:** `:name` matches a single segment (matchit / FastAPI compatible).

### Adding a Rust route
1. Add the operation to the feature's existing consolidated handler (`feature/<f>_rs/presentation/lambda_handlers/<f>_handler/`). Route by HTTP method or AppSync action field. Only create a new handler binary if the operation uses a different protocol.
2. Add a thin wrapper in `local_proxy/src/handlers.rs` that converts `ProxyRequest` → usecase call → `ProxyResponse`.
3. Add the wrapper name to the `match` in `local_proxy/src/dispatch_rs.rs`.
4. Add the entry to `routes.json` with `"language": "rust"`.

### Adding a Python route
1. Add the operation to the feature's existing consolidated handler (`feature/<f>_py/presentation/lambda_handlers/<f>_handler/handler.py`). Route by HTTP method or action field. Only create a new handler if the operation uses a different protocol. Expose both `handler()` and `invoke()`.
2. Register the handler in `local_proxy_py/main.py` → `HANDLERS`.
3. Add the entry to `routes.json` with `"language": "python"`.

The Rust proxy proxies Python routes over HTTP to `python_subserver_url`. The frontend never knows which language served a route.
