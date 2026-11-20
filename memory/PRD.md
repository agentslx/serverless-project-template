# PRD — emergent-serverless-template

## Original problem statement
Build a template app with:
- React frontend (user app + admin panel)
- Rust serverless backend (AWS Lambda) with local proxy simulator
- DynamoDB
- Pulumi (Python) IaC
- Per-Lambda unit + integration tests
- Dev/prod flavours for FE, BE, IaC
- Cognito (user pool + admin pool) auth screens (login/sign-up/verify/forgot password; admin login only)
- AppSync (Amplify) frontend integration
- Clean architecture (domain/data/presentation) per feature on FE & BE
- Shared entities/modules
- IaC split into infrastructure/ and application/, FE deployed via S3+CDN
- GitHub Actions CI/CD
- AGENTS.md + system-design-doc/ for architecture + per-feature docs

## User choices captured
- Scope: Full code template scaffold + local proxy + DynamoDB-local simulator
- Sample features: `auth` + `user_profile`
- AppSync resolver style: APPSYNC_JS
- UI styling: Material design with Tailwind
- Region: `ap-southeast-2`
- Project name: `emergent-serverless-template`
- **Two physically separate React apps** (2026-02): `frontend/` (user) + `admin-frontend/` (admin), each on its own Cognito pool and its own S3+CloudFront distribution.
- **Backend hosts both Rust and Python** in parallel (2026-02): each feature exists as `<name>_rs` and/or `<name>_py`. IaC and proxy default to Rust. Local proxy reads `routes.json` and forwards Python routes to a Python sub-server.

## Status

### 2026-02 initialImplemented:
- Top-level docs (`AGENTS.md`, `README.md`, `.gitignore`)
- `system-design-doc/` (architecture, coding, features/auth + user_profile)
- `.github/workflows/`
- `backend/` Rust workspace with feature/auth, feature/user_profile, local_proxy
- `iac/` Pulumi Python (infrastructure + application split, dev/prod)
- `frontend/` React + Amplify v6 with Material 3 theme

### 2026-02 update — split frontend
- Stripped admin code from `frontend/` (now user-only).
- Created `admin-frontend/` as an independent React app with its own Cognito pool, deep-navy Material theme, port 3001.
- IaC `frontend_hosting.py` and `application/frontend.py` parameterised by `app_name` and instantiated twice.
- Two CloudFront distributions, two Pulumi outputs.

### 2026-02 update — Rust + Python parallel
- **Folder rename**:
  - `shared/entities` → `shared/entities_rs`
  - `shared/modules/{database,common}` → `shared/modules_rs/{database,common}`
  - `feature/{auth,user_profile}` → `feature/{auth_rs,user_profile_rs}`
  - Cargo crate names suffixed with `_rs` (`feature_auth_rs`, …) — bulk-renamed across all `Cargo.toml` and `.rs` files.
- **Python parallels created**:
  - `shared/entities_py/` (UserProfile, UserProfilePatch, AppError) — same shape as Rust.
  - `shared/modules_py/` (boto3 DynamoDB bootstrap, logging, JSON helpers).
  - `feature/auth_py/` (domain + data + presentation) with `get_me` and `post_confirmation_trigger` Lambda handlers exposing both `handler(event,ctx)` (AWS Lambda) and `invoke(req)` (proxy).
  - `feature/user_profile_py/` (same shape) with `get_profile` and `update_profile` handlers.
  - `feature/health_py/` — sample Python-only feature.
  - Pytest tests under each `tests/test_unit.py`.
- **Local proxy refactor (Rust)**:
  - `backend/local_proxy/routes.json` declares method/path/handler/language for every endpoint.
  - `local_proxy/src/` split into `main.rs`, `config.rs`, `state.rs`, `router.rs`, `dispatch_rs.rs`, `handlers.rs`, `dispatch_py.rs`, `proxy_types.rs`.
  - Path matching via `matchit`; one trie per HTTP method.
  - Rust handlers registered through a single `match` in `dispatch_rs.rs`.
  - Python language routes are HTTP-forwarded to `python_subserver_url` from `routes.json`.
- **Python sub-server**:
  - `backend/local_proxy_py/main.py` is a FastAPI app that loads the same `routes.json`, mounts only `language: "python"` entries, and dispatches via a `HANDLERS` registry.
  - Boots cleanly (verified: 4 handlers registered, 1 health route mounted).
- **Docs**:
  - AGENTS.md §1, §3 file-tree, §4 (Rust + Python), §8 quick-start, §10 routes.json convention.
  - `backend/README.md` rewritten for two-language layout.
  - `backend/local_proxy/README.md` updated.
  - `backend/local_proxy_py/README.md` created.

**Verified live in sandbox (2026-02 update):**
- ✅ `cargo build --workspace` succeeds (Rust 1.95.0 installed via rustup; reqwest switched to `rustls-tls` to avoid system OpenSSL).
- ✅ `cargo test --workspace` — 15/15 Rust tests pass.
- ✅ `pytest feature/*_py/tests` — 7/7 Python tests pass.
- ✅ End-to-end with `moto_server` standing in for DynamoDB-local:
  - `GET /api/health` (python route) → Rust proxy forwards to Python sub-server, returns 200.
  - `GET /api/me` (rust route) → in-process Rust usecase, lazy-creates DynamoDB row.
  - `PATCH /api/profile/u-demo` → updates row, `updated_at` advances.
  - `GET /api/profile/u-demo` → returns persisted row.
  - `GET /api/profile/u-demo` with mismatched `x-user-sub` → 403 (usecase invariant).

## Backlog
- P1: `cognito-idp:AdminCreateUser` script for seeding admin users.
- P1: EventBridge `ProfileUpdated` event from update_profile Lambda.
- P1: `NEW_PASSWORD_REQUIRED` handling on first-time admin login.
- P2: SAM (or `cargo lambda watch` + `python-lambda-local`) integration as an alternate local runner.
- P2: Storybook for `shared/ui` in both React apps.
- P2: Cypress e2e tests per app.
- P3: WAF web ACL on the admin CloudFront distribution + IP allow-list.
- P3: Switch admin `list_users` from `Scan` to a GSI `Query` (`pk = "USER"`) once table grows.

## 2026-05 update — admin feature + IaC parity
Implemented:
- **`feature/admin_rs/`** Clean Architecture (Domain/Data/Presentation).
  - `domain/repository/AdminRepository` + `ListUsersPage` entity.
  - `domain/usecases/ListUsersUseCase` with `[1, 100]` page-size guardrails.
  - `data/datasources/DynamoAdminDataSource` — paginated DynamoDB `Scan` with
    base64-encoded `next_token` cursor.
  - `data/repository/DynamoAdminRepository`, `data/models/DynamoUserProfileModel`.
  - 4 unit tests (limit clamping, validation, pagination shape).
- **Lambda binary** `handler_list_users` (`presentation/lambda_handlers/list_users/`).
  - Auth checks: `claim_sub` (must be present) + `is_admin` (header-based).
- **AppSync admin schema + resolver** under
  `presentation/graphql_resolvers/{schema.graphql, listUsers.js}`.
- **Local proxy wiring**:
  - `routes.json` adds `GET /api/admin/users` (rust).
  - Added `query_params` to `ProxyRequest` + manual query parser in `router.rs`
    (no new deps); `dispatch_py.rs` forwards query string to the Python
    sub-server.
  - `handlers.rs::list_users` enforces `x-admin: true` *or*
    `x-cognito-groups: ...,admin,...` locally.
  - `dispatch_rs.rs` registers the new handler.
- **Pulumi IaC**:
  - `application/lambdas.py` — added `_PythonLambda` class for `python3.12`
    runtime, optional via the `pythonLambdaArtifactsDir` config key. All
    five Python handlers are wired when the bundle dir exists.
  - Added `handler_list_users` Rust Lambda + AppSync invoke permission.
  - Fixed stale path in `infrastructure/appsync.py`
    (`feature/user_profile` → `feature/user_profile_rs`).
  - New `infrastructure/appsync_admin.py` — second AppSync API, authed by
    the admin Cognito pool, exposing only `Query.listUsers`.
  - Wired in `__main__.py`; new export `admin_appsync_url`.
- **Scripts**:
  - `emergent_env_setup.sh` — `cargo-lambda` install now prefers `cargo-binstall`
    (binary download, seconds) with source-build fallback.
  - `scripts/package_py_lambdas.sh` — fixed missing `mkdir -p` before rsync.

**Verified live in sandbox:**
- ✅ `cargo build --workspace` (incl. `feature_admin_rs`, `handler_list_users`, `local_proxy`).
- ✅ `cargo test --workspace` — 19/19 Rust tests pass (was 15; +4 admin).
- ✅ `pytest backend/feature/*_py` — 7/7 Python tests pass.
- ✅ `scripts/check_routes.sh` — 5 routes (4 rust, 1 python).
- ✅ End-to-end through `dev_up.sh` against `moto_server`:
  - `GET /api/admin/users` without admin header → `403 admin only`.
  - `GET /api/admin/users` with `x-admin: true` → returns both seeded users.
  - `GET /api/admin/users?limit=1` → 1 user + `next_token: "dS0x"` (base64 of `u-1`).
  - `GET /api/admin/users?limit=1&next_token=dS0x` → next user, `next_token: null`.
  - `x-cognito-groups: admin,staff` header also accepted.
- ✅ `scripts/package_py_lambdas.sh` — bundles all 5 Python handlers
  (`get_me`, `get_profile`, `update_profile`, `post_confirmation_trigger`, `health`)
  into `backend/target/python_lambda/<name>/` with `handler.handler`/`handler.invoke`
  importable.
- ✅ `ruff` — `iac/` lint clean.

## Next action items
- Run `cargo build --workspace` outside the sandbox (no Rust toolchain here) to validate the local_proxy refactor compiles.
- Run `pulumi up --stack dev` against an AWS account.
- Replace placeholder Cognito + AppSync values in both frontends' `.env.development` after first deploy.
- Pick a single language per feature when starting a real project (delete the unused `_rs` or `_py` parallel).
