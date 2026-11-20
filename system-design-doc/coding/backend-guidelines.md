# Backend coding guidelines (Rust)

## Workspace shape

`backend/Cargo.toml` is a virtual workspace. Each feature is a library crate; each Lambda handler is its own binary crate.

```toml
[workspace]
resolver = "2"
members = [
  "shared/entities",
  "shared/modules/*",
  "feature/*",
  "feature/*/presentation/lambda_handlers/*",
  "local_proxy",
]
```

## Lambda consolidation principle

**One Lambda per feature per communication protocol.** All operations within a feature that share the same protocol are served by a single Lambda binary. The handler routes internally based on:

- **HTTP method** (GET, PATCH, POST, …) for API Gateway / `lambda_http` handlers
- **`action` field** in the payload for AppSync Lambda resolvers
- **`routeKey`** (`$connect`, `$disconnect`, custom actions) for WebSocket handlers

Split into a separate Lambda only when the protocol differs (e.g. Cognito trigger vs AppSync) or when runtime requirements diverge (e.g. Docker image vs zip package).

Benefits: warm containers are reused across related operations, DynamoDB clients and SDK connections are shared, and fewer distinct Lambdas means fewer cold starts overall.

## Naming

| Thing                  | Convention                            |
|------------------------|---------------------------------------|
| Crate (feature)        | `feature_<name>` (`feature_auth`)     |
| Crate (handler)        | `handler_<name>` (`handler_user_profile`) |
| Module file            | `snake_case.rs`                       |
| Trait                  | `PascalCase` ending in `Repository`, `DataSource`, etc. |
| Public type            | `PascalCase`                          |
| Function               | `snake_case`                          |

## Async runtime

- Use `tokio` 1.x with `rt` + `macros`. Don't pull in `rt-multi-thread` for Lambdas — single-thread is enough.
- All AWS SDK calls are async; never block.

## Error handling

- Per-feature `Error` enum using `thiserror`.
- Convert into `shared::entities::AppError` at the boundary (handler).
- Don't `unwrap()` outside tests.

## Logging

```rust
use tracing::{info, instrument};

#[instrument(skip(repo))]
pub async fn execute(repo: &impl UserProfileRepository, user_id: &str) -> Result<UserProfile> {
    info!(%user_id, "fetching profile");
    repo.find_by_id(user_id).await
}
```

JSON formatter is initialised once in each handler's `main`:

```rust
tracing_subscriber::fmt()
    .json()
    .with_target(false)
    .with_current_span(false)
    .init();
```

## Lambda handler skeleton (consolidated)

```rust
use lambda_http::{http::Method, run, service_fn, Body, Error, Request, Response};

#[tokio::main]
async fn main() -> Result<(), Error> {
    init_tracing();

    // Shared resources — initialised once, reused across warm invocations
    let repo = build_repo().await;
    let get_uc = GetUseCase::new(repo.clone());
    let update_uc = UpdateUseCase::new(repo);

    run(service_fn(|req| route(req, &get_uc, &update_uc))).await
}

async fn route(req: Request, get_uc: &GetUseCase, update_uc: &UpdateUseCase)
    -> Result<Response<Body>, Error>
{
    match *req.method() {
        Method::GET  => handle_get(req, get_uc).await,
        Method::PATCH => handle_update(req, update_uc).await,
        _ => Ok(error_response(AppError::Validation("method not allowed".into()))),
    }
}
```

## Tests

- `tests/unit_test.rs` — usecase tested with a fake repo (`MockAll` or hand-rolled).
- `tests/integration_test.rs` — handler hit with a stub `Request`, repo backed by DynamoDB-local (`DYNAMODB_ENDPOINT=http://localhost:8000`).
- All tests must pass with `cargo test --workspace` from the project root.

## Configuration

- Read env vars in `main()`. Pass concrete values into the builder of each datasource. Never read env vars deep inside the call stack.
- Keys: `AWS_REGION`, `USER_PROFILES_TABLE`, `USER_POOL_ID`, `LOG_LEVEL`, `DYNAMODB_ENDPOINT` (for local).
