# local_proxy_py

Python sub-server that handles every route declared with `language: "python"` in [`../local_proxy/routes.json`](../local_proxy/routes.json).

The Rust **local_proxy** is the single entry-point for the frontend. It links Rust feature crates in-process for `language: "rust"` routes and HTTP-forwards `language: "python"` routes to this sub-server.

```
   FE (port 3000)
        │
        ▼
   local_proxy (Rust, port 9000)        ← single FE entrypoint
        │
        ├── language=rust   → in-process call (zero hop)
        └── language=python → HTTP → local_proxy_py (Python, port 9001)
                                          │
                                          ▼
                              feature/<x>_py/…/handler.invoke(req)
```

## Run

```bash
cd backend/local_proxy_py
pip install -r requirements.txt
USER_PROFILES_TABLE=est-dev-user-profiles \
DYNAMODB_ENDPOINT=http://localhost:8000 \
PORT=9001 \
python main.py
```

Then in another terminal start the Rust proxy on 9000:

```bash
cd backend
USER_PROFILES_TABLE=est-dev-user-profiles \
DYNAMODB_ENDPOINT=http://localhost:8000 \
cargo run -p local_proxy
```

The frontend talks **only** to `http://localhost:9000`.

## Adding a Python handler

1. Implement `feature/<feature>_py/presentation/lambda_handlers/<name>/handler.py` exposing both `handler(event, context)` (Lambda) and `invoke(req)` (local proxy).
2. Register it in `local_proxy_py/main.py` → `HANDLERS`.
3. Add the route to `../local_proxy/routes.json` with `"language": "python"`.

That's it — restart both proxies and the route is live.
