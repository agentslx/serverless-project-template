# local_proxy (Rust)

Single FE entrypoint that simulates **API Gateway → Lambda** routing for local development. Reads [`routes.json`](./routes.json) at startup and dispatches each request based on the route's `language`:

- `language: "rust"` → calls a registered handler **in-process** (zero network hop).
- `language: "python"` → forwards the request over HTTP to `local_proxy_py` on port 9001.

```
src/
├── main.rs          bootstrap (read routes.json, build state, start axum)
├── config.rs        routes.json schema + loader
├── state.rs         AppState (rust usecases, http client, route table)
├── router.rs        matchit-based path matcher + axum fallback
├── dispatch_rs.rs   handler-name → registered Rust function (one match arm each)
├── handlers.rs      the actual Rust handler functions
├── dispatch_py.rs   forwards to local_proxy_py (HTTP)
└── proxy_types.rs   ProxyRequest / ProxyResponse — language-agnostic shapes
```

See [`../AGENTS.md`](../../AGENTS.md) §10 for the routes.json schema and the workflow when adding a route.

## Run

```bash
docker run -p 8000:8000 amazon/dynamodb-local &

aws dynamodb create-table \
    --endpoint-url http://localhost:8000 \
    --table-name est-dev-user-profiles \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

USER_PROFILES_TABLE=est-dev-user-profiles \
DYNAMODB_ENDPOINT=http://localhost:8000 \
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
AWS_REGION=ap-southeast-2 \
cargo run -p local_proxy
```

The proxy listens on **`http://localhost:9000`**. Python routes are forwarded to the URL declared in `routes.json` → `python_subserver_url` (default `http://localhost:9001`).

## Calling endpoints

```bash
# Auth is approximated by an `x-user-sub` header in dev.
curl -H 'x-user-sub: u-1' -H 'x-user-email: a@b.c' http://localhost:9000/api/me

curl -H 'x-user-sub: u-1' http://localhost:9000/api/profile/u-1

curl -X PATCH -H 'x-user-sub: u-1' -H 'content-type: application/json' \
     -d '{"display_name":"Alice"}' \
     http://localhost:9000/api/profile/u-1

# Python-served route (forwarded transparently to :9001)
curl http://localhost:9000/api/health
```

In production the same Lambda binaries are deployed behind real API Gateway with a Cognito JWT authoriser.
