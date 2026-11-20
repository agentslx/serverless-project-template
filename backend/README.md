# backend (Rust + Python serverless)

Cargo workspace for Rust **plus** a Python parallel for every feature. See [`../AGENTS.md`](../AGENTS.md) §4 + §10 for layering rules and the routes.json convention.

```
backend/
├── Cargo.toml                 ← Rust workspace
├── configs/{dev,prod}.toml
│
├── shared/                    ← language-tagged
│   ├── entities_rs/           ← plain Rust types (UserProfile, AppError…)
│   ├── modules_rs/            ← shared Rust modules (db, common)
│   ├── entities_py/           ← plain Python types (mirrors entities_rs)
│   └── modules_py/            ← shared Python modules (db, common)
│
├── feature/
│   ├── auth_rs/               ← Rust impl  (clean architecture)
│   ├── auth_py/               ← Python parallel
│   ├── user_profile_rs/       ← Rust impl
│   ├── user_profile_py/       ← Python parallel
│   └── health_py/             ← Python-only sample (proxy demo)
│
├── local_proxy/               ← Rust binary on :9000 — single FE entrypoint
│   ├── routes.json            ← THE source of truth (read by both proxies)
│   └── src/{main,config,state,router,dispatch_rs,dispatch_py,handlers,proxy_types}.rs
│
└── local_proxy_py/            ← Python sub-server on :9001
    ├── main.py                  (FastAPI, reads same routes.json)
    └── requirements.txt
```

## Why two languages

Some functions fit Rust (cold start, perf, async fan-out), some fit Python (heavy SDK ecosystem, ML, glue code). The template ships both so a project can pick per function. **By default, IaC and the local proxy use the Rust versions.** Python parallels exist as a working reference; pick `_rs` *or* `_py` per feature in real projects and delete the other.

## Build & test

```bash
# Rust
cargo build --workspace
cargo test  --workspace
cargo install cargo-lambda
cargo lambda build --release --workspace      # → target/lambda/<bin>/bootstrap

# Python
cd local_proxy_py && pip install -r requirements.txt && cd ..
pytest feature/auth_py feature/user_profile_py
```

## Run locally

```bash
# 1. DynamoDB local
docker run -p 8000:8000 amazon/dynamodb-local &

# 2. Rust proxy (port 9000) — the single endpoint your FE talks to
USER_PROFILES_TABLE=est-dev-user-profiles \
DYNAMODB_ENDPOINT=http://localhost:8000 \
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
AWS_REGION=ap-southeast-2 \
cargo run -p local_proxy &

# 3. Python sub-server (port 9001) — only if any routes.json entry uses python
cd local_proxy_py
USER_PROFILES_TABLE=est-dev-user-profiles \
DYNAMODB_ENDPOINT=http://localhost:8000 \
PORT=9001 python main.py
```

```
   FE (3000 / 3001)
        │
        ▼
   local_proxy (Rust :9000)             ← always the FE's URL
        │
        ├── language=rust   → in-process call to feature_*_rs usecases
        └── language=python → HTTP → local_proxy_py (:9001)
                                          │
                                          ▼
                              feature/*_py/.../handler.invoke(req)
```

## Architecture per feature (both languages)

```
feature/<name>_<lang>/
├── (Cargo.toml or __init__.py)
├── domain/
│   ├── repository/   ← traits / abstract base classes
│   └── usecases/     ← pure business logic
├── data/
│   ├── datasources/  ← AWS SDK calls live HERE only
│   ├── models/       ← DTO ↔ entity transformers
│   └── repository/   ← impl of domain/repository
├── presentation/
│   ├── lambda_handlers/   ← one folder = one Lambda
│   └── graphql_resolvers/ ← AppSync APPSYNC_JS files (Rust feature only)
└── tests/
```
